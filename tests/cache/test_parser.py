import pytest

from swoop.cache.parser import parse_expression
from swoop.cache.exceptions import ParsingError


def test_parsing_no_root():
    with pytest.raises(ValueError) as exc_info:
        parse_expression("features[].id", True)
    assert str(exc_info.value) == """Expression must begin with '.': features[].id"""


def test_parsing_unterminated_quote():
    with pytest.raises(ParsingError) as exc_info:
        parse_expression('."features"[::]."id', False)
    assert str(exc_info.value) == """Unterminated '"': ."features"[::]."id"""


def test_parsing_unterminated_slice():
    with pytest.raises(ParsingError) as exc_info:
        parse_expression('."features"[::.id', False)
    assert str(exc_info.value) == """Unterminated slice: ."features"[::.id"""


def test_parsing_unescaped_quote():
    with pytest.raises(ParsingError) as exc_info:
        parse_expression('."feat"ures"', False)
    assert str(exc_info.value) == '''Error pos 8: unparsable expression: ."feat"ures"'''


def test_parsing_invalid_slice1():
    with pytest.raises(ParsingError) as exc_info:
        parse_expression(".features[-1].id", False)
    assert (
        str(exc_info.value)
        == "Invalid slice '[-1::1]'; supported values: '[]', '[:]', '[::]', '[::1]'"
    )


def test_parsing_invalid_slice2():
    with pytest.raises(ParsingError) as exc_info:
        parse_expression(".features[0].id", False)
    assert (
        str(exc_info.value)
        == "Invalid slice '[0::1]'; supported values: '[]', '[:]', '[::]', '[::1]'"
    )


def test_parsing_invalid_slice3():
    with pytest.raises(ParsingError) as exc_info:
        parse_expression('."features[]"[0].id', False)
    assert (
        str(exc_info.value)
        == "Invalid slice '[0::1]'; supported values: '[]', '[:]', '[::]', '[::1]'"
    )


def test_parsing_invalid_slice4():
    with pytest.raises(ParsingError) as exc_info:
        parse_expression(".features[0:1].id", False)
    assert (
        str(exc_info.value)
        == "Invalid slice '[0:1:1]'; supported values: '[]', '[:]', '[::]', '[::1]'"
    )


def test_parsing_chars_after_quote():
    with pytest.raises(ParsingError) as exc_info:
        parse_expression('."features[-1]"rgrg.id', False)
    assert (
        str(exc_info.value)
        == """Error pos 16: unparsable expression: ."features[-1]"rgrg.id"""
    )


def test_parsing_chars_after_slice():
    with pytest.raises(ParsingError) as exc_info:
        parse_expression(".features[]rgrg.id", False)
    assert (
        str(exc_info.value)
        == """Error pos 12: unparsable expression: .features[]rgrg.id"""
    )


def test_parsing_array_of_arrays1():
    with pytest.raises(ParsingError) as exc_info:
        parse_expression(".features[].[].id", True)
    assert (
        str(exc_info.value)
        == """Error pos 13: unparsable expression: .features[].[].id"""
    )


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


def test_parsing_array_of_arrays2():
    parsed = parse_expression(".features[][].id", True)
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


def test_parsing_unparsable_slice():
    with pytest.raises(ParsingError) as exc_info:
        parse_expression('."features"[0:@:4]', False)
    assert str(exc_info.value) == """Error around pos 18: unparsable slice 0:@:4"""


def test_parsing_unparsable_slice2():
    with pytest.raises(ParsingError) as exc_info:
        parse_expression('."features"[::1:2]', False)
    assert str(exc_info.value) == """Error around pos 18: unparsable slice ::1:2"""


def test_parsing_unescaped_quote2():
    with pytest.raises(ParsingError) as exc_info:
        parse_expression('''."features"[::].\\""id"''', False)
        assert str(exc_info.value) == (
            '''Error pos 18: '"' not allowed unescaped outside
            quoted identifier: ."features"[::].\\""id"'''
        )
