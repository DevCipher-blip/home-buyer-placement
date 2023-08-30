from pathlib import Path

from home_buyer_placement.cli import main

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_sample_input_matches_expected_output(capsys):
    assert main([str(EXAMPLES / "input.txt")]) == 0
    assert capsys.readouterr().out == (EXAMPLES / "expected_output.txt").read_text()
