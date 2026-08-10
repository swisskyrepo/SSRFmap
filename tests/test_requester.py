import json
from unittest.mock import Mock, patch

import pytest

from core.requester import Requester


def write_request(tmp_path, content):
    request_file = tmp_path / "request.txt"
    request_file.write_text(content)
    return request_file


def test_parses_get_request_and_overrides_user_agent(tmp_path):
    path = write_request(
        tmp_path,
        "GET /fetch?url=old HTTP/1.1\nHost: example.test\nUser-Agent: old-agent\n\n",
    )

    requester = Requester(path, "new-agent", True, {"https": "http://proxy.test"})

    assert requester.method == "GET"
    assert requester.action == "/fetch?url=old"
    assert requester.host == "example.test"
    assert requester.headers["User-Agent"] == "new-agent"
    assert requester.protocol == "https"
    assert requester.proxies == {"https": "http://proxy.test"}


def test_parses_urlencoded_post_data(tmp_path):
    path = write_request(
        tmp_path,
        "POST /fetch HTTP/1.1\nHost: example.test\n"
        "Content-Type: application/x-www-form-urlencoded\n\n"
        "url=https%3A%2F%2Fexample.com&name=hello%20world",
    )

    requester = Requester(path, None, False, None)

    assert requester.data == {"url": "https://example.com", "name": "hello world"}


def test_parses_json_and_xml_post_data(tmp_path):
    json_path = write_request(
        tmp_path,
        "POST /json HTTP/1.1\nHost: example.test\nContent-Type: application/json\n\n"
        '{"url": "old", "count": 2}',
    )
    json_requester = Requester(json_path, None, False, None)
    assert json_requester.data == {"url": "old", "count": 2}

    xml_path = write_request(
        tmp_path,
        "POST /xml HTTP/1.1\nHost: example.test\nContent-Type: application/xml\n\n"
        "<url>*FUZZ*</url>",
    )
    xml_requester = Requester(xml_path, None, False, None)
    assert xml_requester.data == {"__xml__": "<url>*FUZZ*</url>"}


def test_request_instances_do_not_share_mutable_state(tmp_path):
    first_path = write_request(
        tmp_path,
        "POST /first HTTP/1.1\nHost: first.test\nContent-Type: application/x-www-form-urlencoded\n"
        "X-First: present\n\nfirst=value",
    )
    first = Requester(first_path, None, False, None)

    second_path = write_request(
        tmp_path,
        "GET /second?url=value HTTP/1.1\nHost: second.test\n\n",
    )
    second = Requester(second_path, None, False, None)

    assert first.data == {"first": "value"}
    assert "X-First" not in second.headers
    assert second.data == {}


def test_get_request_injects_query_and_header(tmp_path):
    path = write_request(
        tmp_path,
        "GET /fetch?url=old HTTP/1.1\nHost: example.test\nX-Target: old\n\n",
    )
    requester = Requester(path, None, False, {"http": "http://proxy.test"})
    response = Mock()

    with patch("core.requester.requests.get", return_value=response) as request_get:
        result = requester.do_request("url", "http://127.0.0.1/a b", timeout=5, stream=True)

    assert result is response
    request_get.assert_called_once_with(
        "http://example.test/fetch?url=http%3A%2F%2F127.0.0.1%2Fa%20b",
        headers={"Host": "example.test", "X-Target": "old"},
        timeout=5,
        stream=True,
        verify=False,
        proxies={"http": "http://proxy.test"},
    )

    with patch("core.requester.requests.get", return_value=response) as request_get:
        requester.do_request("X-Target", "injected")
    assert request_get.call_args.kwargs["headers"]["X-Target"] == "injected"


def test_form_post_injects_selected_parameter(tmp_path):
    path = write_request(
        tmp_path,
        "POST /fetch HTTP/1.1\nHost: example.test\n"
        "Content-Type: application/x-www-form-urlencoded\n\nurl=old&keep=value",
    )
    requester = Requester(path, None, False, None)
    response = Mock()

    with patch("core.requester.requests.post", return_value=response) as request_post:
        result = requester.do_request("url", "new")

    assert result is response
    assert request_post.call_args.kwargs["data"] == {"url": "new", "keep": "value"}
    assert requester.data == {"url": "old", "keep": "value"}


def test_json_post_serializes_injected_data(tmp_path):
    path = write_request(
        tmp_path,
        "POST /fetch HTTP/1.1\nHost: example.test\nContent-Type: application/json\n\n"
        '{"url": "old"}',
    )
    requester = Requester(path, None, False, None)

    with patch("core.requester.requests.post", return_value=Mock()) as request_post:
        requester.do_request("url", "new")

    assert json.loads(request_post.call_args.kwargs["data"]) == {"url": "new"}


def test_xml_post_replaces_fuzz_marker(tmp_path):
    path = write_request(
        tmp_path,
        "POST /fetch HTTP/1.1\nHost: example.test\nContent-Type: application/xml\n\n"
        "<url>*FUZZ*</url>",
    )
    requester = Requester(path, None, False, None)

    with patch("core.requester.requests.post", return_value=Mock()) as request_post:
        requester.do_request("url", "new")

    assert request_post.call_args.kwargs["data"] == "<url>new</url>"


def test_network_error_returns_none(tmp_path):
    path = write_request(
        tmp_path,
        "GET /fetch?url=old HTTP/1.1\nHost: example.test\n\n",
    )
    requester = Requester(path, None, False, None)

    with patch("core.requester.requests.get", side_effect=OSError("offline")):
        assert requester.do_request("url", "new") is None


def test_missing_request_file_exits(tmp_path):
    with pytest.raises(SystemExit):
        Requester(tmp_path / "missing.txt", None, False, None)
