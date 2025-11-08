import pytest

from mb_calc.evaluator import evaluate_expression, evaluate_lines


def test_evaluate_expression_arithmetic() -> None:
    result = evaluate_expression("1 + 2 * 3")
    assert result == pytest.approx(7.0)


def test_evaluate_expression_with_functions() -> None:
    result = evaluate_expression("sin(pi / 2) + cos(0)")
    assert result == pytest.approx(2.0)


def test_evaluate_expression_with_unary_operators() -> None:
    assert evaluate_expression("-sqrt(4)") == pytest.approx(-2.0)


def test_evaluate_expression_with_abs_function() -> None:
    assert evaluate_expression("abs(-3)") == pytest.approx(3.0)


def test_evaluate_expression_supports_grouped_numbers() -> None:
    assert evaluate_expression("1,000 * 5") == pytest.approx(5_000.0)


@pytest.mark.parametrize(
    "expression",
    [
        "unknown",
        "sin()",
        "__import__('os')",
        "1 << 2",
        "~1",
        "(lambda x: x)(1)",
        "log(x=1)",
        "abs(1, 2)",
        "[1, 2]",
        " ",
    ],
)
def test_evaluate_expression_rejects_invalid(expression: str) -> None:
    with pytest.raises(ValueError):
        evaluate_expression(expression)


def test_evaluate_lines_handles_blanks_and_errors() -> None:
    results = evaluate_lines(["1 + 1", "  ", "bad", "tau / tau"])
    first, second, third, fourth = results

    assert first == pytest.approx(2.0)
    assert second is None
    assert third is None
    assert fourth == pytest.approx(1.0)
