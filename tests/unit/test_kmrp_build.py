import subprocess
from pathlib import Path

from modshop.kotor.kmrp_build import OUTPUTS, hand_over, hook_count, label


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout.strip()  # fmt: skip


def test_label_names_the_upstream_base_and_the_commits_on_top(tmp_path: Path) -> None:
    git(tmp_path, "init", "-q")
    git(tmp_path, "commit", "-q", "--allow-empty", "-m", "upstream")
    base = git(tmp_path, "rev-parse", "HEAD")
    git(tmp_path, "update-ref", "refs/remotes/origin/master", base)
    for n in range(3):
        git(tmp_path, "commit", "-q", "--allow-empty", "-m", f"ours {n}")
    assert label(tmp_path) == f"{base[:7]}+linux3"


def test_hook_count_reads_either_table_form() -> None:
    assert hook_count("[[hooks]]\naddress = 1\n\n[[hooks.parameters]]\n[[patches.hooks]]\n") == 2


def outputs(d: Path, text: str) -> None:
    d.mkdir(parents=True, exist_ok=True)
    for name in OUTPUTS:
        (d / name).write_text(text)


def test_hand_over_keeps_the_previous_build_under_its_commit(tmp_path: Path) -> None:
    out = tmp_path / "kmrp-build"
    outputs(tmp_path / "first", "one")
    assert hand_over(tmp_path / "first", out, "a" * 40) is None
    outputs(tmp_path / "second", "two")
    previous = hand_over(tmp_path / "second", out, "b" * 40)
    assert previous is not None and previous == out / "previous-aaaaaaa"
    assert all((previous / n).read_text() == "one" for n in OUTPUTS)
    assert all((out / n).read_text() == "two" for n in OUTPUTS)
    assert (out / "COMMIT").read_text() == "b" * 40 + "\n"


def test_hand_over_at_the_same_commit_replaces_in_place(tmp_path: Path) -> None:
    out = tmp_path / "kmrp-build"
    outputs(tmp_path / "first", "one")
    hand_over(tmp_path / "first", out, "a" * 40)
    outputs(tmp_path / "again", "again")
    assert hand_over(tmp_path / "again", out, "a" * 40) is None
    assert (out / OUTPUTS[0]).read_text() == "again"
    assert not list(out.glob("previous-*"))
