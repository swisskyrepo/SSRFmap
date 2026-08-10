from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from core.utils import loot_path, safe_loot_name
from modules.readfiles import exploit


def test_loot_path_sanitizes_target_and_filename(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    output_path = loot_path("../../target:5000", "../../etc/passwd")

    assert output_path.parent.parent == Path("loot")
    assert output_path.parent.name == safe_loot_name("../../target:5000")
    assert output_path.name == safe_loot_name("../../etc/passwd")
    assert "/" not in output_path.parent.name
    assert "/" not in output_path.name


def test_readfiles_writes_downloads_under_loot(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    requester = Mock()
    requester.host = "127.0.0.1:5000"
    requester.do_request.side_effect = [
        Mock(text="baseline"),
        Mock(text="baseline\nretrieved file contents"),
    ]
    args = SimpleNamespace(param="url", targetfiles="/etc/issue")

    exploit(requester, args)

    output_path = tmp_path / "loot" / "127.0.0.1_5000" / "_etc_issue"
    assert output_path.read_text() == "retrieved file contents\n"
    assert not (tmp_path / "127.0.0.1_5000").exists()
