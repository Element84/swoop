import pytest

from swoop.cache.parser import parse_expression


# TODO test for actual exception, should match custom classes
def test_parsing_no_root():
    with pytest.raises(ValueError) as exc_info:
        parse_expression("features[].id", True)
    assert str(exc_info.value) == ""


def test_parsing_unterminated_quote():
    with pytest.raises(ValueError):
        parse_expression('."features"[::]."id', False)


def test_parsing_unterminated_slice():
    with pytest.raises(ValueError):
        parse_expression('."features"[::.id', False)


def test_parsing_unescaped_quote():
    with pytest.raises(ValueError):
        parse_expression('."feat"ures"', False)


def test_parsing_invalid_slice1():
    with pytest.raises(ValueError):
        parse_expression(".features[-1].id", False)


def test_parsing_invalid_slice2():
    with pytest.raises(ValueError):
        parse_expression(".features[0].id", False)


def test_parsing_invalid_slice3():
    with pytest.raises(ValueError):
        parse_expression('."features[]"[0].id', False)


def test_parsing_invalid_slice4():
    with pytest.raises(ValueError):
        parse_expression(".features[0:1].id", False)


def test_parsing_chars_after_quote():
    with pytest.raises(ValueError):
        parse_expression('."features[-1]"rgrg.id', False)


def test_parsing_chars_after_slice():
    with pytest.raises(ValueError):
        parse_expression(".features[]rgrg.id", False)


def test_parsing_root():
    parsed = parse_expression(".", True)
    assert parsed.asdict() == {
        "name": ".",
        "include": True,
        "nodes": [],
    }


def test_parsing1():
    parsed = parse_expression(".features[].id", True)
    assert parsed.asdict() == {
        "name": ".",
        "include": None,
        "nodes": [
            {
                "name": "features",
                "include": None,
                "nodes": [
                    {
                        "name": "::1",
                        "include": None,
                        "nodes": [
                            {
                                "name": "id",
                                "include": True,
                                "nodes": [],
                            },
                        ],
                    },
                ],
            },
        ],
    }


def test_parsing3():
    parsed = parse_expression(".features[::].id", False)
    assert parsed.asdict() == {
        "name": ".",
        "include": None,
        "nodes": [
            {
                "name": "features",
                "include": None,
                "nodes": [
                    {
                        "name": "::1",
                        "include": None,
                        "nodes": [{"name": "id", "include": False, "nodes": []}],
                    }
                ],
            }
        ],
    }


def test_parsing4():
    parsed = parse_expression('."fea.tu.r[]es"[::].id', False)
    assert parsed.asdict() == {
        "name": ".",
        "include": None,
        "nodes": [
            {
                "name": "fea.tu.r[]es",
                "include": None,
                "nodes": [
                    {
                        "name": "::1",
                        "include": None,
                        "nodes": [{"name": "id", "include": False, "nodes": []}],
                    }
                ],
            }
        ],
    }


def test_parsing5():
    parsed = parse_expression('."featu\\"res"', False)
    assert parsed.asdict() == {
        "name": ".",
        "include": None,
        "nodes": [{"name": 'featu\\"res', "include": False, "nodes": []}],
    }


def test_parsing6():
    parsed = parse_expression(".features", False)
    assert parsed.asdict() == {
        "name": ".",
        "include": None,
        "nodes": [{"name": "features", "include": False, "nodes": []}],
    }


def test_parsing_array_of_arrays():
    parsed = parse_expression(".features[].[].id", True)
    assert parsed.asdict() == {
        "name": ".",
        "include": None,
        "nodes": [
            {
                "name": "features",
                "include": None,
                "nodes": [
                    {
                        "name": "::1",
                        "include": None,
                        "nodes": [
                            {
                                "name": "::1",
                                "include": None,
                                "nodes": [{"name": "id", "include": True, "nodes": []}],
                            }
                        ],
                    }
                ],
            }
        ],
    }


# TODO need at least one test for each exception in parser.py
