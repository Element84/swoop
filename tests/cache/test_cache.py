from swoop.cache.hashing import transform_payload, hash
import pytest


def test_default():
    includes = ["process.workflow", "features[*].id", "features[*].collection"]
    excludes = ["*"]
    result = transform_payload(payload_1, includes, excludes)
    assert result == {
        "process": {"workflow": "copy-assets"},
        "features": [
            {"id": "b-item", "collection": "collection-b"},
            {"id": "a_item", "collection": "collection-a"},
        ],
    }


def test_includes():
    includes = [
        "process.workflow",
        "features[*].id",
        "features[*].collection",
        "features[*].assets.image",
    ]
    excludes = ["*"]
    result = transform_payload(payload_1, includes, excludes)
    assert result == {
        "process": {"workflow": "copy-assets"},
        "features": [
            {
                "id": "b-item",
                "collection": "collection-b",
                "assets": {
                    "image": {
                        "href": "s3://naip-analytic/ny/2019/60cm/rgbir_cog/41071/m_4107157_sw_19_060_20190811.tif",
                        "ref": "s3://naip-analytic/ny/2019/60cm/rgbir_cog/41071/m_4107157_sw_19_060_20190811.tif",
                        "roles": ["data"],
                        "title": "RGBIR COG tile",
                        "type": "image/tiff; application=geotiff; "
                        "profile=cloud-optimized",
                    }
                },
            },
            {
                "id": "a_item",
                "collection": "collection-a",
                "assets": {
                    "image": {
                        "href": "https://naipeuwest.blob.core.windows.net/naip/v002/tx/2020/tx_060cm_2020/26097/m_2609719_se_14_060_20201217.tif",
                        "roles": ["data"],
                        "title": "RGBIR COG tile",
                        "type": "image/tiff; application=geotiff; "
                        "profile=cloud-optimized",
                    }
                },
            },
        ],
    }


def test_excludes():
    includes = [
        "process.workflow",
        "features[*].id",
        "features[*].collection",
        "features[*].assets.image",
    ]
    excludes = ["features[*].assets.image.href"]
    result = transform_payload(payload_1, includes, excludes)

    assert result == {
        "process": {"workflow": "copy-assets"},
        "features": [
            {
                "id": "b-item",
                "collection": "collection-b",
                "assets": {
                    "image": {
                        "ref": "s3://naip-analytic/ny/2019/60cm/rgbir_cog/41071/m_4107157_sw_19_060_20190811.tif",
                        "roles": ["data"],
                        "title": "RGBIR COG tile",
                        "type": "image/tiff; application=geotiff; "
                        "profile=cloud-optimized",
                    }
                },
            },
            {
                "id": "a_item",
                "collection": "collection-a",
                "assets": {
                    "image": {
                        "roles": ["data"],
                        "title": "RGBIR COG tile",
                        "type": "image/tiff; application=geotiff; "
                        "profile=cloud-optimized",
                    }
                },
            },
        ],
    }


def test_inc_exc_1():
    includes = [
        "process.workflow",
        "features[*].id",
        "features[*].collection",
        "features[*].properties.some",
    ]
    excludes = ["features[*].properties"]
    result = transform_payload(payload_1, includes, excludes)
    assert result == {
        "process": {"workflow": "copy-assets"},
        "features": [
            {
                "id": "b-item",
                "collection": "collection-b",
                "properties": {"some": "thing"},
            },
            {
                "id": "a_item",
                "collection": "collection-a",
                "properties": {"some": "task"},
            },
        ],
    }


def test_inc_exc_2():
    includes = [
        "process.workflow",
        "features[*].id",
        "features[*].collection",
        "features[*].properties",
    ]
    excludes = ["features[*].properties.a_value"]
    result = transform_payload(payload_2, includes, excludes)
    assert result == {
        "features": [
            {
                "id": "b-item",
                "collection": "collection-b",
                "properties": {"some": "thing"},
            },
            {
                "id": "a_item",
                "collection": "collection-a",
                "properties": {"some": "task"},
            },
        ]
    }


def test_inc_exc_3():
    includes = [
        "process.workflow",
        "features[*].id",
        "features[*].collection",
        "process.upload_options",
        "process.tasks.copy-assets.drop_assets",
    ]
    excludes = ["process.upload_options.public_assets", "process.tasks.copy-assets"]
    result = transform_payload(payload_3, includes, excludes)

    assert result == {
        "process": {
            "workflow": "copy-assets",
            "upload_options": {
                "path_template": "s3://payloadtest/data/${collection}/${id}/",
                "s3_urls": False,
            },
            "tasks": {"copy-assets": {"drop_assets": ["image"]}},
        },
        "features": [
            {"id": "h-item", "collection": "collection-h"},
            {"id": "d_item", "collection": "collection-d"},
        ],
    }


def test_hashing():
    includes = [
        "process.workflow",
        "features[*].id",
        "features[*].collection",
        "process.upload_options",
    ]
    excludes = ["process.upload_options.public_assets"]
    result = transform_payload(payload_3, includes, excludes)
    hashed = hash(result)
    assert hashed == b'"\xd7\x19[\xf09\xa6\xd8\xe7\xb4\xc2m\xea\x9b%\x0f\xf5*\xdf\x0c'


def test_error_includes_int_index():
    includes = ["process.workflow", "features[*].id", "features[0].collection"]
    excludes = ["*"]
    with pytest.raises(ValueError):
        transform_payload(payload_3, includes, excludes)


def test_error_excludes_int_index():
    includes = [
        "process.workflow",
        "features[*].id",
        "features[*].collection",
    ]
    excludes = ["features[0].collection"]
    with pytest.raises(ValueError):
        transform_payload(payload_3, includes, excludes)


def test_error_same_path_inc_exc():
    includes = ["features[*].id", "features[*].properties.a_value"]
    excludes = ["features[*].collection", "features[*].properties.a_value"]
    with pytest.raises(ValueError):
        transform_payload(payload_2, includes, excludes)


def test_badkey_intindex():
    includes = [
        "process.workflow",
        "features[*].id",
        "features[*].collection",
        'features[*]."crazy_key[0]"[0]',
    ]
    excludes = ["*"]
    with pytest.raises(ValueError):
        transform_payload(payload_4, includes, excludes)


def test_badkey_rangeindex():
    includes = [
        "process.workflow",
        "features[*].id",
        "features[*].collection",
        'features[*]."crazy_key[0]"[0:1]',
    ]
    excludes = ["*"]
    with pytest.raises(ValueError):
        transform_payload(payload_4, includes, excludes)


def test_badkey_specialchar():
    includes = [
        'features[*]."crazy.key[0]"[*]',
    ]
    excludes = ["*"]
    result = transform_payload(payload_4, includes, excludes)
    assert result == {
        "features": [
            {'"crazy.key[0]"': [{"city": "la"}]},
            {'"crazy.key[0]"': [{"city": "aus"}]},
        ]
    }


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
            '"crazy.key[0]"': [{"city": "la"}],
        },
        {
            "id": "a_item",
            "collection": "collection-a",
            '"crazy.key[0]"': [{"city": "aus"}],
        },
    ]
}
