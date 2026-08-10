from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

from core.requester import Requester
from examples.example import app


def test_put_example_preserves_prefix_and_reproduces_ssrf():
    request_file = Path(__file__).parents[1] / "examples" / "request8.txt"
    requester = Requester(request_file, None, False, None)
    client = app.test_client()

    assert requester.method == "PUT"
    assert requester.data == {"url": "test;*FUZZ*"}

    def send_to_example(url, **kwargs):
        return client.open(
            path=urlsplit(url).path,
            method="PUT",
            headers=kwargs["headers"],
            data=kwargs["data"],
        )

    with (
        patch("core.requester.requests.put", side_effect=send_to_example),
        patch("examples.example.command", return_value=b"PUT SSRF reproduced") as command,
    ):
        response = requester.do_request("url", "file:///etc/issue")

    assert response.status_code == 200
    assert response.data == b"PUT SSRF reproduced"
    command.assert_called_once_with("curl file:///etc/issue")


def test_put_json_example_reproduces_ssrf_using_url_parameter():
    request_file = Path(__file__).parents[1] / "examples" / "request9.txt"
    requester = Requester(request_file, None, False, None)
    client = app.test_client()

    assert requester.method == "PUT"
    assert requester.media_type == "application/json"
    assert requester.data == {"url": "http://example.com"}

    def send_to_example(url, **kwargs):
        return client.open(
            path=urlsplit(url).path,
            method="PUT",
            headers=kwargs["headers"],
            data=kwargs["data"],
        )

    with (
        patch("core.requester.requests.put", side_effect=send_to_example),
        patch("examples.example.command", return_value=b"PUT JSON SSRF reproduced") as command,
    ):
        response = requester.do_request("url", "file:///etc/issue")

    assert response.status_code == 200
    assert response.data == b"PUT JSON SSRF reproduced"
    command.assert_called_once_with("curl file:///etc/issue")
