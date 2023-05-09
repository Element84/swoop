from swoop.cache.types import KeyNode, IndexNode
from swoop.cache.exceptions import ParsingError


def parse_expression(expression: str, include: bool):
    i = iter(expression)

    # we do not support an array directly under the root
    root = KeyNode(next(i))

    if root.name != ".":
        raise ValueError(f"Expression must begin with '.': {expression}")

    parent = root
    char: str = ""
    index = 1

    def lnext() -> bool:
        nonlocal char
        nonlocal i
        nonlocal index
        try:
            char = next(i)
            index += 1
            return True
        except StopIteration:
            char = "."
            return False

    while lnext():
        current: str = ""
        quoted = False
        if char == '"':
            quoted = True
            escaped = False
            while True:
                if not lnext():
                    raise ParsingError(f"Unterminated '\"': {expression}")

                if not escaped and char == '"':
                    break

                current += char
                if char == "\\":
                    escaped = True
                else:
                    escaped = False
            lnext()
        else:
            while char not in (".", "[", "]"):
                if char == '"':
                    raise ParsingError(
                        f"Error pos {index}: '\"' not allowed unescaped "
                        "outside quoted identifier: {expression}",
                    )
                current += char
                lnext()

        if char == ".":
            if not current:
                raise ParsingError(
                    f"Error pos {index}: unparsable expression: {expression}",
                )
            parent = parent.add_node(KeyNode(current, quoted=quoted))

        elif char == "[":
            _slice = ""
            while True:
                if not lnext():
                    raise ParsingError(f"Unterminated slice: {expression}")

                if char == "]":
                    break

                _slice += char

            lnext()

            if char != ".":
                raise ParsingError(
                    f"Error pos {index}: unparsable expression: {expression}",
                )

            # coerce the slice into a start, stop, and step values
            splt: list[int | None] = []
            for ele in _slice.split(":"):
                if ele == "":
                    splt.append(None)
                    continue
                try:
                    splt.append(int(ele))
                except ValueError:
                    raise ParsingError(
                        f"Error around pos {index}: unparsable slice {_slice}"
                    )

            if len(splt) > 3:
                raise ParsingError(
                    f"Error around pos {index}: unparsable slice {_slice}"
                )

            # ensure we end up with a value for each
            # start, stop, step, defaulting to None
            start, stop, step = splt + [None] * (3 - len(splt))

            if current:
                parent = parent.add_node(KeyNode(current, quoted=quoted))
            # TODO: rename indexnode to slicenode
            # TODO: what if we have consecutive slices without dots? [][][]...
            parent = parent.add_node(IndexNode(start, stop, step))

        else:
            raise ParsingError(
                f"Error pos {index}: unparsable expression: {expression}",
            )

    # parent is actually the leaf node
    parent.include = include

    return root
