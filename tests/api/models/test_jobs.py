import pytest

from swoop.api.models.jobs import StatusCode, SwoopStatusCode


@pytest.mark.parametrize("swoop_status", [s for s in SwoopStatusCode])
def test_statuscode_from_swoop_status(swoop_status):
    sc = StatusCode.from_swoop_status(swoop_status)
    assert isinstance(sc, StatusCode)
