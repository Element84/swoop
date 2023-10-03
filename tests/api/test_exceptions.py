import json

from swoop.api import exceptions


def test_http_exception():
    title = "test_title"
    instance = "test_instance"

    exc = json.loads(
        exceptions.HTTPException(
            status_code=404,
            title=title,
            instance=instance,
        )
        .to_json()
        .body.decode(),
    )

    assert exc["status"] == 404
    assert exc["title"] == title
    assert exc["instance"] == instance
    assert exc["detail"] == "Not Found"
