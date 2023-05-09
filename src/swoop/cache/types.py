from abc import ABC
from copy import deepcopy
from typing import Type, Union

from swoop.cache.exceptions import ConfigError, ParsingError


# TODO turn into ABC
class FilterNode(ABC):
    _include_dot = True

    def __init__(self, name: str, quoted: bool = False):
        self.name: str = name
        self._include: bool | None = None
        self.nodes: dict[str, "KeyNode" | "SliceNode"] = {}
        self.parent: "FilterNode" | None = None
        self.quoted = quoted
        self.nodes_type: Type["KeyNode"] | Type["SliceNode"] | None = None

    @property
    def display_name(self):
        return f'"{self.name}"' if self.quoted else self.name

    @property
    def path(self):
        if self.parent:
            dot = (
                "."
                if self._include_dot and self.parent and self.parent.path != "."
                else ""
            )
            return f"{self.parent.path}{dot}{self.display_name}"
        else:
            return self.display_name

    @property
    def is_leaf(self):
        return not bool(len(self.nodes))

    @property
    def include(self):
        return self._include

    @include.setter
    def include(self, include: bool):
        if self._include is not None:
            raise ConfigError(f"Duplicate expressions for node: '{self.path}")
        self._include = include

    def add_node(self, node: Union["KeyNode", "SliceNode"]):
        if node.name in self.nodes:
            raise ConfigError(
                f"Cannot add node to '{self.path}': already exists '{node.name}'",
            )

        if self.nodes_type is None:
            self.nodes_type = node.__class__
        elif self.nodes_type != node.__class__:
            raise ConfigError(
                f"Invalid mixed types: cannot mix keys and arrays under '{self.path}'",
            )

        self.nodes[node.name] = node
        node.parent = self
        return node

    def remove_node(self, node):
        try:
            del self.nodes[node.name]
        except KeyError:
            pass

    def update(self, node: "FilterNode"):
        # maybe this isn't possible?
        if not isinstance(self, node.__class__):
            raise ConfigError(
                f"Invalid mixed types: '{self.path}', '{node.display_name}'"
            )

        if node.include is not None:
            self.include = node.include

        for node_name, _node in node.nodes.items():
            try:
                self.nodes[node_name].update(_node)
            except KeyError:
                self.add_node(_node)

    def asdict(self):
        return {
            "name": self.name,
            "include": self.include,
            "nodes": [node.asdict() for node in self.nodes.values()],
        }

    def __call__(self, obj):
        if self.nodes_type is not None:
            self.nodes_type.process(self, obj)
        elif self.include:
            # if we are including this value and
            # it is not a container we can just return
            return
        else:
            # if we are excluding this value then something went wrong,
            # as it should have been filtered from the parent container
            raise TypeError(f"Cannot process object of type {type(obj)}")

    def __str__(self):
        return str(self.asdict())


class KeyNode(FilterNode):
    @classmethod
    def process(cls, node, obj):
        is_dict = isinstance(obj, dict)
        is_list = isinstance(obj, list)

        if is_list:
            raise RuntimeError(
                f"Filter error: cannot filter list with {node.nodes_type}",
            )

        if not is_dict:
            if node.include:
                # if we are including this value and
                # it is not a container we can just return
                return
            else:
                # if we are excluding this value then something went wrong,
                # as it should have been filtered from the parent container
                raise TypeError(f"Cannot process object of type {type(obj)}")

        keyset = set(obj.keys())

        if node.include:
            # we know that child leaf nodes must be excludes,
            # so we can remove them from the object
            to_remove = {_node.name for _node in node.nodes.values() if _node.is_leaf}
        else:
            # we know that child leaf nodes must be includes,
            # so therefore that any child node must be retained,
            # so we want to keep all keys that correspond to node names
            to_keep = {_node.name for _node in node.nodes.values()}
            to_remove = keyset - to_keep

        for key in to_remove:
            try:
                del obj[key]
            except KeyError:
                pass

        # remaining keys need to be processed by their
        # corresponding node, if there is one
        remaining_keys = keyset - to_remove
        for key in remaining_keys:
            try:
                _node = node.nodes[key]
            except KeyError:
                pass
            else:
                val = obj[key]
                # we sort dicts to ensure they hash deterministically
                if isinstance(val, dict):
                    val = obj[key] = dict(sorted(val.items()))
                _node(val)


class SliceNode(FilterNode):
    _include_dot = False

    def __init__(
        self, start: int | None, stop: int | None, step: int | None, *args, **kwargs
    ):
        _start = start if start is not None else ""
        _stop = stop if stop is not None else ""
        _step = step if step is not None else 1
        name = f"{_start}:{_stop}:{_step}"

        # Note we currently do not allow arbitrary slices,
        # to simplify parsing logic. Otherwise we'd:
        #   - have to handle overlaps between slices
        #   - have to handle conflicts between slices
        #   - may not be able to do either without a bounded array, i.e., at filter time
        #     - consider [-1]...
        if name != "::1":
            raise ParsingError(
                f"Invalid slice '[{name}]'; "
                "supported values: '[]', '[:]', '[::]', '[::1]'",
            )

        super().__init__(name, *args, **kwargs)

        self.start = start
        self.stop = stop
        self.step = step

    @classmethod
    def process(cls, node, obj):
        is_dict = isinstance(obj, dict)
        is_list = isinstance(obj, list)

        if is_dict:
            raise RuntimeError(
                f"Filter error: cannot filter dict with {node.nodes_type}",
            )

        if not is_list:
            if node.include:
                # if we are including this value and
                # it is not a container we can just return
                return
            else:
                # if we are excluding this value then something went wrong,
                # as it should have been filtered from the parent container
                raise TypeError(f"Cannot process object of type {type(obj)}")

        if not (node.nodes or node.include):
            obj.clear()
        else:
            for index, ele in enumerate(obj):
                # we sort dicts to ensure they hash deterministically
                if isinstance(ele, dict):
                    ele = obj[index] = dict(sorted(ele.items()))

                # we should only ever have one child node
                # because we only allow a single slice value
                list(node.nodes.values())[0](ele)

    @property
    def display_name(self):
        return f"[{self.name}]"


class JSONFilter(KeyNode):
    def __init__(self, include_patterns: list[str], exclude_patterns: list[str]):
        super().__init__(".")
        self._add_patterns(include_patterns, True)
        self._add_patterns(exclude_patterns, False)
        self._normalize()

    def _add_patterns(self, patterns: list[str], include: bool):
        from swoop.cache.parser import parse_expression

        for pattern in patterns:
            self.update(parse_expression(pattern, include))

    def _normalize(self):
        if self.include is None:
            self.include = False

        # self here is whatever node we're at when recursing
        def recurse(self: FilterNode):
            if self.parent and self.parent.include is not None and self.include is None:
                self.include = self.parent.include

            for node in list(self.nodes.values()):
                recurse(node)

            if self.parent and self.is_leaf and self.include == self.parent.include:
                self.parent.remove_node(self)

        recurse(self)

    def __call__(self, obj):
        obj = deepcopy(obj)
        super().__call__(obj)
        return obj
