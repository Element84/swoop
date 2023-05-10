import pytest
from swoop.cache.types import JSONFilter
from swoop.cache.exceptions import ParsingError, ConfigError


def test_exclude():
    includes = [
        ".process.workflow",
        ".features[::].id",
        ".features[:].collection",
    ]
    excludes = [
        ".features[].id.value",
    ]
    f = JSONFilter(includes, excludes)
    assert f.asdict() == {
        "name": ".",
        "include": False,
        "nodes": [
            {
                "name": "process",
                "include": False,
                "nodes": [{"name": "workflow", "include": True, "nodes": []}],
            },
            {
                "name": "features",
                "include": False,
                "nodes": [
                    {
                        "name": "::1",
                        "include": False,
                        "nodes": [
                            {
                                "name": "id",
                                "include": True,
                                "nodes": [
                                    {"name": "value", "include": False, "nodes": []}
                                ],
                            },
                            {"name": "collection", "include": True, "nodes": []},
                        ],
                    }
                ],
            },
        ],
    }


def test_pruning():
    includes = [
        ".features",
        ".features[::].id",
        ".features[:].collection",
    ]
    f = JSONFilter(includes, [])
    assert f.asdict() == {
        "name": ".",
        "include": False,
        "nodes": [{"name": "features", "include": True, "nodes": []}],
    }


def test_duplicates1():
    includes = [
        ".features",
        ".features",
    ]
    with pytest.raises(ValueError):
        JSONFilter(includes, [])


def test_duplicates2():
    includes = [".features"]
    excludes = [".features"]
    with pytest.raises(ValueError):
        JSONFilter(includes, excludes)


def test_invalidslice():
    includes = [".features[1:5:2].workflow"]
    excludes = []
    with pytest.raises(ParsingError) as exc_info:
        JSONFilter(includes, excludes)
    assert (
        str(exc_info.value)
        == "Invalid slice '[1:5:2]'; supported values: '[]', '[:]', '[::]', '[::1]'"
    )


def test_keyarray():
    includes = [".features[::].workflow", ".[::]"]
    excludes = []
    with pytest.raises(ConfigError) as exc_info:
        JSONFilter(includes, excludes)
    assert (
        str(exc_info.value)
        == "Invalid mixed types: cannot mix keys and arrays under '.'"
    )


def test_keyarray2():
    includes = ['."::1"', ".[::]"]
    excludes = []
    with pytest.raises(ConfigError) as exc_info:
        JSONFilter(includes, excludes)
    assert str(exc_info.value) == """Invalid mixed types: '."::1"', '[::1]'"""
