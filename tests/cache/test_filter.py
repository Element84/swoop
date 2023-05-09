# ruff: noqa: E501
import json

from swoop.cache.types import JSONFilter


def test_includes():
    includes = [
        ".process.workflow",
        ".features[:].id",
        ".features[:].collection",
        ".features[:].assets.image",
    ]
    excludes = ["."]
    f = JSONFilter(includes, excludes)
    result = f(payload_1)
    assert result == {
        "features": [
            {
                "assets": {
                    "image": {
                        "href": "s3://naip-analytic/ny/2019/60cm/rgbir_cog/41071/m_4107157_sw_19_060_20190811.tif",
                        "ref": "s3://naip-analytic/ny/2019/60cm/rgbir_cog/41071/m_4107157_sw_19_060_20190811.tif",
                        "roles": ["data"],
                        "title": "RGBIR COG tile",
                        "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                    }
                },
                "collection": "collection-b",
                "id": "b-item",
            },
            {
                "assets": {
                    "image": {
                        "href": "https://naipeuwest.blob.core.windows.net/naip/v002/tx/2020/tx_060cm_2020/26097/m_2609719_se_14_060_20201217.tif",
                        "roles": ["data"],
                        "title": "RGBIR COG tile",
                        "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                    }
                },
                "collection": "collection-a",
                "id": "a_item",
            },
        ],
        "process": {"workflow": "copy-assets"},
    }


def test_excludes():
    includes = [
        ".process.workflow",
        ".features[].id",
        ".features[].collection",
        ".features[].assets.image",
    ]
    excludes = [
        ".features[].assets.image.href",
    ]
    f = JSONFilter(includes, excludes)
    result = f(payload_1)
    assert json.dumps(result) == json.dumps(
        {
            "features": [
                {
                    "assets": {
                        "image": {
                            "ref": "s3://naip-analytic/ny/2019/60cm/rgbir_cog/41071/m_4107157_sw_19_060_20190811.tif",
                            "roles": ["data"],
                            "title": "RGBIR COG tile",
                            "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                        }
                    },
                    "collection": "collection-b",
                    "id": "b-item",
                },
                {
                    "assets": {
                        "image": {
                            "roles": ["data"],
                            "title": "RGBIR COG tile",
                            "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                        }
                    },
                    "collection": "collection-a",
                    "id": "a_item",
                },
            ],
            "process": {"workflow": "copy-assets"},
        }
    )


def test_inc_exc_1():
    includes = [
        ".process.workflow",
        ".features[].id",
        ".features[].collection",
        ".features[].properties.some",
    ]
    excludes = [
        ".features[].properties",
    ]
    f = JSONFilter(includes, excludes)
    result = f(payload_1)
    assert json.dumps(result) == json.dumps(
        {
            "features": [
                {
                    "collection": "collection-b",
                    "id": "b-item",
                    "properties": {"some": "thing"},
                },
                {
                    "collection": "collection-a",
                    "id": "a_item",
                    "properties": {"some": "task"},
                },
            ],
            "process": {"workflow": "copy-assets"},
        }
    )


def test_inc_exc_2():
    includes = [
        ".process.workflow",
        ".features[::1].id",
        ".features[].collection",
        ".features[].properties",
    ]
    excludes = [
        ".features[].properties.a_value",
    ]
    f = JSONFilter(includes, excludes)
    result = f(payload_2)
    assert json.dumps(result) == json.dumps(
        {
            "features": [
                {
                    "collection": "collection-b",
                    "id": "b-item",
                    "properties": {"some": "thing"},
                },
                {
                    "collection": "collection-a",
                    "id": "a_item",
                    "properties": {"some": "task"},
                },
            ]
        }
    )


def test_inc_exc_3():
    includes = [
        ".process.workflow",
        ".features[].id",
        ".features[].collection",
        ".process.upload_options",
        ".process.tasks.copy-assets.drop_assets",
    ]
    excludes = [
        ".process.upload_options.public_assets",
        ".process.tasks.copy-assets",
    ]
    f = JSONFilter(includes, excludes)
    result = f(payload_3)
    assert json.dumps(result) == json.dumps(
        {
            "features": [
                {
                    "collection": "collection-h",
                    "id": "h-item",
                },
                {
                    "collection": "collection-d",
                    "id": "d_item",
                },
            ],
            "process": {
                "tasks": {"copy-assets": {"drop_assets": ["image"]}},
                "upload_options": {
                    "path_template": "s3://payloadtest/data/${collection}/${id}/",
                    "s3_urls": False,
                },
                "workflow": "copy-assets",
            },
        }
    )


def test_crazykey():
    includes = [
        ".process.workflow",
        ".features[:].id",
        ".features[:].collection",
        '.features[:]."crazy.key[0]"[]',
    ]
    excludes = ["."]
    f = JSONFilter(includes, excludes)
    result = f(payload_4)
    assert json.dumps(result) == json.dumps(
        {
            "features": [
                {
                    "collection": "collection-b",
                    "crazy.key[0]": [
                        {"city": "la", "state": "ca"},
                        {"city": "sf", "state": "ca"},
                    ],
                    "id": "b-item",
                },
                {
                    "collection": "collection-a",
                    "crazy.key[0]": [
                        {"city": "aus", "state": "tx"},
                        {
                            "city": "dal",
                            "state": "tx",
                        },
                    ],
                    "id": "a_item",
                },
            ]
        }
    )


def test_outer_array():
    includes = [
        ".[]",
    ]
    excludes = [
        ".[].excluded",
    ]
    f = JSONFilter(includes, excludes)
    result = f(
        [
            {"id": "id1", "excluded": "value"},
            {"id": "id2", "excluded": "value"},
            {"id": "id3", "excluded": "value"},
        ]
    )
    assert json.dumps(result) == json.dumps(
        [
            {"id": "id1"},
            {"id": "id2"},
            {"id": "id3"},
        ]
    )


payload_1 = {
    "id": "test",
    "type": "FeatureCollection",
    "features": [
        {
            "id": "b-item",
            "collection": "collection-b",
            "properties": {"a_value": 10, "some": "thing"},
            "assets": {
                "image": {
                    "href": "s3://naip-analytic/ny/2019/60cm/rgbir_cog/"
                    "41071/m_4107157_sw_19_060_20190811.tif",
                    "ref": "s3://naip-analytic/ny/2019/60cm/rgbir_cog/"
                    "41071/m_4107157_sw_19_060_20190811.tif",
                    "type": "image/tiff; application=geotiff; "
                    "profile=cloud-optimized",
                    "title": "RGBIR COG tile",
                    "roles": ["data"],
                }
            },
        },
        {
            "id": "a_item",
            "collection": "collection-a",
            "properties": {"some": "task", "a_value": 15},
            "assets": {
                "image": {
                    "type": "image/tiff; application=geotiff; "
                    "profile=cloud-optimized",
                    "href": "https://naipeuwest.blob.core.windows."
                    "net/naip/v002/tx/2020/tx_060cm_2020/26097/"
                    "m_2609719_se_14_060_20201217.tif",
                    "roles": ["data"],
                    "title": "RGBIR COG tile",
                },
                "thumbnail": {
                    "href": "https://naipeuwest.blob.core.windows.net"
                    "/naip/v002/tx/2020/tx_060cm_2020/26097/"
                    "m_2609719_se_14_060_20201217.200.jpg",
                    "type": "image/jpeg",
                    "roles": ["thumbnail"],
                    "title": "Thumbnail",
                },
            },
        },
    ],
    "process": {
        "workflow": "copy-assets",
        "upload_options": {
            "path_template": "s3://payloadtest/data/${collection}/${id}/",
            "public_assets": [],
            "s3_urls": False,
        },
        "tasks": {"copy-assets": {"assets": ["thumbnail"], "drop_assets": ["image"]}},
    },
}


payload_2 = {
    "features": [
        {
            "id": "b-item",
            "collection": "collection-b",
            "properties": {"a_value": 10, "some": "thing"},
        },
        {
            "id": "a_item",
            "collection": "collection-a",
            "properties": {"some": "task", "a_value": 15},
        },
    ]
}


payload_3 = {
    "features": [
        {
            "id": "h-item",
            "collection": "collection-h",
            "assets": {
                "image": {
                    "href": "s3://naip-analytic/ny/2019/60cm/rgbir_cog/41071/m_4107157_sw_19_060_20190811.tif",
                    "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                    "title": "RGBIR COG tile",
                    "roles": ["data"],
                }
            },
        },
        {
            "id": "d_item",
            "collection": "collection-d",
            "properties": {"some": "task", "a_value": 15},
        },
    ],
    "process": {
        "workflow": "copy-assets",
        "upload_options": {
            "path_template": "s3://payloadtest/data/${collection}/${id}/",
            "public_assets": [],
            "s3_urls": False,
        },
        "tasks": {"copy-assets": {"assets": ["thumbnail"], "drop_assets": ["image"]}},
    },
}


payload_4 = {
    "features": [
        {
            "id": "b-item",
            "collection": "collection-b",
            "crazy.key[0]": [
                {"city": "la", "state": "ca"},
                {"city": "sf", "state": "ca"},
            ],
        },
        {
            "id": "a_item",
            "collection": "collection-a",
            "crazy.key[0]": [
                {"city": "aus", "state": "tx"},
                {"city": "dal", "state": "tx"},
            ],
        },
    ]
}
