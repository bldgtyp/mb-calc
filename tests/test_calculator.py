import math

from mb_calc.app import update_results
from mb_calc.calculator import render_results


def test_render_results_formats_values() -> None:
    outputs = render_results(["2", "2.5", ""])
    assert outputs == ["2", "2.5", ""]


def test_render_results_handles_functions() -> None:
    result = render_results(["sqrt(2)"])[0]
    assert result == format(math.sqrt(2), "g")


def test_render_results_suppresses_errors() -> None:
    assert render_results(["bad input"]) == [""]


def test_update_results_splits_input() -> None:
    text = "1 + 1\n\ninvalid\nsqrt(4)"
    assert update_results(text) == ["2", "", "", "2"]


def test_render_results_handles_infinite_numbers() -> None:
    assert render_results(["1e309", "-1e309"]) == ["inf", "-inf"]


def test_render_results_supports_commas_in_input_and_output() -> None:
    assert render_results(["1,000 * 5"]) == ["5,000"]


def test_render_results_formats_large_floats_with_grouping() -> None:
    assert render_results(["1234.5"]) == ["1,234.5"]
