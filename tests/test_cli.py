import os
import subprocess
import sys
from pathlib import Path

from home_buyer_placement.cli import main

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_writes_to_the_output_file_when_asked(tmp_path, capsys):
    target = tmp_path / "placements.txt"
    assert main([str(EXAMPLES / "input.txt"), "-o", str(target)]) == 0
    assert capsys.readouterr().out == ""
    assert target.read_text() == (EXAMPLES / "expected_output.txt").read_text()


def test_bad_input_exits_non_zero_with_the_line_number(tmp_path, capsys):
    source = tmp_path / "bad.txt"
    source.write_text("N N0 E:1 W:1 R:1\nH H0 E:1 W:1 N0\n")
    assert main([str(source)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "bad.txt: line 2: H line needs 6 fields, got 5" in captured.err


def test_missing_file_exits_non_zero(tmp_path, capsys):
    assert main([str(tmp_path / "nope.txt")]) == 1
    assert "No such file" in capsys.readouterr().err


def test_help_describes_the_command(capsys):
    try:
        main(["--help"])
    except SystemExit as exit_:
        assert exit_.code == 0
    assert "usage: home-buyer-placement" in capsys.readouterr().out


def test_output_is_identical_across_hash_seeds():
    outputs = set()
    for seed in ("0", "1", "12345"):
        env = {**os.environ, "PYTHONHASHSEED": seed}
        run = subprocess.run(
            [sys.executable, "-m", "home_buyer_placement", str(EXAMPLES / "input.txt")],
            capture_output=True,
            text=True,
            check=True,
            env=env,
        )
        outputs.add(run.stdout)
    assert outputs == {(EXAMPLES / "expected_output.txt").read_text()}
