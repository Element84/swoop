from swoop.cache.exceptions import ParsingError
from swoop.cache.types import KeyNode, SliceNode


def parse_expression(expression: str, include: bool):
    """
    Parses an input expression written in dot notation to determine
    whether it is an appropriately written expression, else returns
    ParsingError exceptions.

    Parameters:
            expression (str): An expression to parse for any errors.
            include: A boolean value.

    Returns:
            None
    """

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

        # quoted key identifier
        if char == '"':
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
            if char not in (".", "["):
                raise ParsingError(
                    f"Error pos {index}: unparsable expression: {expression}",
                )

            parent = parent.add_node(KeyNode(current, quoted=True))

        # not a slice identifier
        # should be non-quoted key identifier
        elif char != "[":
            while char not in (".", "["):
                if char == '"':
                    raise ParsingError(
                        f"Error pos {index}: '\"' not allowed unescaped "
                        f"outside quoted identifier: {expression}",
                    )
                current += char
                lnext()
            parent = parent.add_node(KeyNode(current))

        while char == "[" and (current or parent.name == "."):
            _slice = ""
            while True:
                if not lnext():
                    raise ParsingError(f"Unterminated slice: {expression}")

                if char == "]":
                    break

                _slice += char

            lnext()

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
            parent = parent.add_node(SliceNode(start, stop, step))

        if char != ".":
            raise ParsingError(
                f"Error pos {index}: unparsable expression: {expression}",
            )

    # parent is actually the leaf node
    parent.include = include

    return root
