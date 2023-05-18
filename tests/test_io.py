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


def test_hasbucket(test_app, bucket_name):
    assert test_app.state.io.bucket_exists(bucket_name) is True
