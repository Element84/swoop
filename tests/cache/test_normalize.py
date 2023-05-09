import pytest
import json
from swoop.cache.types import JSONFilter


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
    print(json.dumps(f.asdict(), indent=4))
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
    print(json.dumps(f.asdict(), indent=4))
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


# TODO need a test for each exception in types.py
