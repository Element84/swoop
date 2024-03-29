# ruff: noqa: E501

from swoop.cache.types import JSONFilter
from swoop.cache.uuid import generate_payload_uuid


def test_generate_payload_uuid():
    includes = [
        ".process.workflow",
        ".features[].id",
        ".features[::].collection",
        ".process.upload_options",
    ]
    excludes = [
        ".process.upload_options.public_assets",
    ]
    f = JSONFilter(includes, excludes)
    result = f(payload_3)
    payload_uuid = generate_payload_uuid(
        payload_3["process"]["workflow"],
        result,
    )
    assert str(payload_uuid) == "6db45591-11ba-5638-9e8c-96ab5fc7cda3"


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
