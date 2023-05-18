import json

import pytest

from .conftest import inject_io_fixture

inject_io_fixture(
    [
        {
            "source": "base_01",
            "destination": "/execution/2595f2da-81a6-423c-84db-935e6791046e",
        },
        {
            "source": "base_02",
            "destination": "/execution/81842304-0aa9-4609-89f0-1c86819b0752",
        },
    ],
    __name__,
)


@pytest.fixture
def single_object():
    return {"process_id": "2595f2da-81a6-423c-84db-935e6791046e", "payload": "test_io"}


def test_hasbucket(test_app, bucket_name):
    assert test_app.state.io.bucket_exists(bucket_name) is True


def test_add_remove_object(test_app, single_object):
    test_app.state.io.put_object(
        "/execution/2595f2da-81a6-423c-84db-935e6791046e/io.json",
        json.dumps(single_object),
    )
    test_app.state.io.delete_object(
        "/execution/2595f2da-81a6-423c-84db-935e6791046e/io.json"
    )
    assert True
