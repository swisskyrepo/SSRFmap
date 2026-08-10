from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

from core.requester import Requester
from examples.example import app


def test_post_example_preserves_signature_before_injected_url():
    request_file = Path(__file__).parents[1] / "examples" / "request10.txt"
    requester = Requester(request_file, None, False, None)
    client = app.test_client()

    assert requester.method == "POST"
    assert requester.data == {"url": "SIGNATURE*FUZZ*"}

    def send_to_example(url, **kwargs):
        return client.open(
            path=urlsplit(url).path,
            method="POST",
            headers=kwargs["headers"],
            data=kwargs["data"],
        )

    with (
        patch("core.requester.requests.post", side_effect=send_to_example),
        patch("examples.example.command", return_value=b"POST SSRF reproduced") as command,
    ):
        response = requester.do_request("url", "file:///etc/issue")

    assert response.status_code == 200
    assert response.data == b"POST SSRF reproduced"
    command.assert_called_once_with("curl file:///etc/issue")
    assert requester.data["url"] == "SIGNATURE*FUZZ*"


def test_post_example_rejects_url_without_signature():
    client = app.test_client()

    with patch("examples.example.command") as command:
        response = client.post("/ssrf9", data={"url": "http://example.com"})

    assert response.status_code == 400
    assert response.data == b"SIGNATURE is missing from url"
    command.assert_not_called()
