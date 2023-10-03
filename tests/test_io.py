import json

import pytest

from swoop.api.io import split_endpoint_protocol

from .conftest import inject_io_fixture

inject_io_fixture(
    [
        {
            "source": "base_01",
            "destination": "/executions/2595f2da-81a6-423c-84db-935e6791046e",
        },
        {
            "source": "base_02",
            "destination": "/executions/81842304-0aa9-4609-89f0-1c86819b0752",
        },
    ],
    __name__,
)


@pytest.fixture
def single_object():
    return {"process_id": "2595f2da-81a6-423c-84db-935e6791046e", "payload": "test_io"}


@pytest.mark.parametrize(
    "endpoint,expected_secure,expected_endpoint",
    [
        ("https://example.com:80", True, "example.com:80"),
        ("http://example.com", False, "example.com"),
        ("s3.amazonaws.com", True, "s3.amazonaws.com"),
    ],
)
def test_split_endpoint_protocol(endpoint, expected_secure, expected_endpoint):
    assert (expected_secure, expected_endpoint) == split_endpoint_protocol(endpoint)


def test_hasbucket(test_client):
    assert test_client.app.state.io.bucket_exists() is True


def test_add_object(test_client, single_object):
    test_client.app.state.io.put_object(
        "/executions/2595f2da-81a6-423c-84db-935e6791046e/io.json",
        json.dumps(single_object),
    )
    assert True


def test_remove_object(test_client):
    test_client.app.state.io.delete_object(
        "/executions/2595f2da-81a6-423c-84db-935e6791046e/io.json"
    )
    assert True
