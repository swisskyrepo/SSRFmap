import pytest

from core import utils


def test_protocol_wrappers():
    assert utils.wrapper_file("/etc/passwd") == "file:///etc/passwd"
    assert utils.wrapper_unc("share", "192.0.2.1") == "\\\\192.0.2.1\\share"
    assert utils.wrapper_gopher("payload", "127.0.0.1", 6379) == (
        "gopher://127.0.0.1:6379/_payload"
    )
    assert utils.wrapper_dict("show", "127.0.0.1", 11211) == ("dict://show:127.0.0.1/11211")
    assert utils.wrapper_http("status", "localhost", 8080) == ("http://localhost:8080/status")
    assert utils.wrapper_http("", "localhost", 80, "user", "pass") == (
        "http://user:pass@localhost:80/"
    )
    assert utils.wrapper_https("health", "localhost", 443) == ("https://localhost:443/health")


def test_diff_text_returns_lines_missing_from_second_text():
    assert utils.diff_text("same\nremoved\n", "same\nkept") == "removed\n"


@pytest.mark.parametrize(
    ("level", "expected"),
    [
        (1, {"127.0.0.1"}),
        (2, {"127.0.0.1", "0.0.0.0", "localhost", "[::]", "0000::1", "0", "127.1", "127.0.1"}),
        (
            3,
            {
                "127.0.0.0",
                "127.0.1.3",
                "127.42.42.42",
                "127.127.127.127",
                "localtest.me",
                "customer1.app.localhost.my.company.127.0.0.1.nip.io",
                "localtest$google.me",
            },
        ),
    ],
)
def test_gen_ip_list_basic_levels(level, expected):
    assert set(utils.gen_ip_list("127.0.0.1", level)) == expected


def test_gen_ip_list_numeric_encodings():
    level_four = set(utils.gen_ip_list("127.0.0.1", 4))
    assert 2_130_706_433 in level_four
    assert "①②⑦.⓪.⓪.①" in level_four

    assert set(utils.gen_ip_list("127.0.0.1", 5)) == {
        "383.256.256.257",
        "2130706433",
        "0x7f.0x0.0x0.0x1",
        "0177.00.00.01",
    }


def test_invalid_ip_skips_numeric_encodings():
    assert set(utils.gen_ip_list("not-an-ip", 5)) == set()
