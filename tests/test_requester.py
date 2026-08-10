import json
from unittest.mock import Mock, patch

import pytest

from core.requester import Requester


def write_request(tmp_path, content):
    request_file = tmp_path / "request.txt"
    request_file.write_text(content)
    return request_file


def write_binary_request(tmp_path, content):
    request_file = tmp_path / "request.txt"
    request_file.write_bytes(content)
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


def test_parses_headers_and_multiline_body_without_truncation(tmp_path):
    path = write_binary_request(
        tmp_path,
        b"POST /json HTTP/1.1\r\n"
        b"host: example.test\r\n"
        b"content-type: application/problem+json; charset=utf-8\r\n"
        b"X-Long: first\r\n"
        b"  second\r\n"
        b"\r\n"
        b'{\r\n  "url": "old",\r\n  "enabled": true\r\n}',
    )

    requester = Requester(path, None, False, None)

    assert requester.host == "example.test"
    assert requester.headers["X-Long"] == "first second"
    assert requester.data == {"url": "old", "enabled": True}


def test_parses_multipart_form_fields_and_file_content(tmp_path):
    boundary = "----SSRFmapBoundary"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="url"\r\n'
        "\r\n"
        "http://example.com/old\r\n"
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="upload"; filename="payload.txt"\r\n'
        "Content-Type: text/plain\r\n"
        "\r\n"
        "first line\r\nsecond line\r\n"
        f"--{boundary}--\r\n"
    ).encode()
    path = write_binary_request(
        tmp_path,
        b"POST /upload HTTP/1.1\r\n"
        b"Host: example.test\r\n"
        + f'Content-Type: multipart/form-data; boundary="{boundary}"\r\n'.encode()
        + b"Content-Length: 999\r\n\r\n"
        + body,
    )

    requester = Requester(path, None, False, None)

    assert requester.media_type == "multipart/form-data"
    assert requester.multipart_boundary == boundary
    assert requester.data == {
        "url": "http://example.com/old",
        "upload": "first line\r\nsecond line",
    }
    assert requester.body == body


def test_multipart_post_replaces_only_target_field_and_preserves_file(tmp_path):
    boundary = "AaB03x"
    file_content = b"binary:\x00\xff\r\nstill-the-file"
    body = (
        b"--AaB03x\r\n"
        b'Content-Disposition: form-data; name="url"\r\n\r\n'
        b"http://example.com/old\r\n"
        b"--AaB03x\r\n"
        b'Content-Disposition: form-data; name="upload"; filename="payload.bin"\r\n'
        b"Content-Type: application/octet-stream\r\n\r\n" + file_content + b"\r\n--AaB03x--\r\n"
    )
    path = write_binary_request(
        tmp_path,
        b"POST /upload HTTP/1.1\r\n"
        b"Host: example.test\r\n"
        b"Content-Type: multipart/form-data; boundary=AaB03x\r\n"
        + f"Content-Length: {len(body)}\r\n\r\n".encode()
        + body,
    )
    requester = Requester(path, None, False, None)
    response = Mock()

    with patch("core.requester.requests.post", return_value=response) as request_post:
        result = requester.do_request("url", "http://169.254.169.254/latest")

    assert result is response
    sent_body = request_post.call_args.kwargs["data"]
    sent_headers = request_post.call_args.kwargs["headers"]
    assert b"http://169.254.169.254/latest" in sent_body
    assert b"http://example.com/old" not in sent_body
    assert file_content in sent_body
    assert sent_body.endswith(b"\r\n--AaB03x--\r\n")
    assert sent_headers["Content-Type"] == "multipart/form-data; boundary=AaB03x"
    assert "Content-Length" not in sent_headers
    assert requester.body == body


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


def test_get_request_replaces_fuzz_marker_without_scrubbing_value_prefix(tmp_path):
    path = write_request(
        tmp_path,
        "GET /fetch?url=test;%2AFUZZ%2A&keep=1 HTTP/1.1\nHost: example.test\n\n",
    )
    requester = Requester(path, None, False, None)

    with patch("core.requester.requests.get", return_value=Mock()) as request_get:
        requester.do_request("url", "http://127.0.0.1/a b")

    assert request_get.call_args.args[0] == (
        "http://example.test/fetch?url=test;http%3A%2F%2F127.0.0.1%2Fa%20b&keep=1"
    )


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


def test_put_form_preserves_context_around_fuzz_marker(tmp_path):
    path = write_request(
        tmp_path,
        "PUT /fetch HTTP/1.1\nHost: example.test\n"
        "Content-Type: application/x-www-form-urlencoded\nContent-Length: 1\n\n"
        "url=test%3B*FUZZ*%3Bend&keep=value",
    )
    requester = Requester(path, None, False, None)
    response = Mock()

    with patch("core.requester.requests.put", return_value=response) as request_put:
        result = requester.do_request("url", "file:///etc/issue")

    assert result is response
    assert request_put.call_args.kwargs["data"] == {
        "url": "test;file:///etc/issue;end",
        "keep": "value",
    }
    assert "Content-Length" not in request_put.call_args.kwargs["headers"]
    assert requester.data["url"] == "test;*FUZZ*;end"


def test_put_json_serializes_injected_url(tmp_path):
    path = write_request(
        tmp_path,
        "PUT /fetch HTTP/1.1\nHost: example.test\nContent-Type: application/json\n\n"
        '{"url": "http://example.com", "keep": true}',
    )
    requester = Requester(path, None, False, None)
    response = Mock()

    with patch("core.requester.requests.put", return_value=response) as request_put:
        result = requester.do_request("url", "file:///etc/issue")

    assert result is response
    assert json.loads(request_put.call_args.kwargs["data"]) == {
        "url": "file:///etc/issue",
        "keep": True,
    }
    assert requester.data == {"url": "http://example.com", "keep": True}


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


def test_json_post_replaces_only_fuzz_marker(tmp_path):
    path = write_request(
        tmp_path,
        "POST /fetch HTTP/1.1\nHost: example.test\nContent-Type: application/json\n\n"
        '{"url": "prefix;*FUZZ*;suffix", "keep": true}',
    )
    requester = Requester(path, None, False, None)

    with patch("core.requester.requests.post", return_value=Mock()) as request_post:
        requester.do_request("url", "file:///etc/issue")

    assert json.loads(request_post.call_args.kwargs["data"]) == {
        "url": "prefix;file:///etc/issue;suffix",
        "keep": True,
    }


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
