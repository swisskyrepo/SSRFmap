from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

from core.requester import Requester
from examples.example import app


def test_multipart_example_reproduces_ssrf_and_preserves_file():
    request_file = Path(__file__).parents[1] / "examples" / "request7.txt"
    requester = Requester(request_file, None, False, None)
    client = app.test_client()

    assert requester.data["url"] == "http://example.com"
    assert requester.data["proof"].startswith("This file part must remain unchanged")

    def send_to_example(url, **kwargs):
        return client.open(
            path=urlsplit(url).path,
            method="POST",
            headers=kwargs["headers"],
            data=kwargs["data"],
        )

    with (
        patch("core.requester.requests.post", side_effect=send_to_example),
        patch("examples.example.command", return_value=b"multipart SSRF reproduced") as command,
    ):
        response = requester.do_request("url", "file:///etc/issue")

    assert response.status_code == 200
    assert response.data == b"multipart SSRF reproduced"
    command.assert_called_once_with("curl file:///etc/issue")
