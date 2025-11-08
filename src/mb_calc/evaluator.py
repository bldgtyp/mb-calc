"""Safe evaluation of arithmetic expressions for the toolbar calculator."""

from __future__ import annotations

import ast
import math
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Final, Protocol

Number = int | float


class MathFunction(Protocol):
    """Protocol capturing callable math helpers without keyword args."""

    def __call__(self, *values: float) -> float: ...


BinaryOperator = Callable[[float, float], float]
UnaryOperator = Callable[[float], float]


@dataclass(frozen=True)
class EvaluationConfig:
    """Configuration describing allowed operators, functions, and constants."""

    binary_operators: Mapping[type[ast.operator], BinaryOperator]
    unary_operators: Mapping[type[ast.unaryop], UnaryOperator]
    constants: Mapping[str, float]
    functions: Mapping[str, MathFunction]


def _build_default_config() -> EvaluationConfig:
    """Create the default evaluation configuration."""

    binary_ops: dict[type[ast.operator], BinaryOperator] = {
        ast.Add: lambda left, right: left + right,
        ast.Sub: lambda left, right: left - right,
        ast.Mult: lambda left, right: left * right,
        ast.Div: lambda left, right: left / right,
        ast.FloorDiv: lambda left, right: math.floor(left / right),
        ast.Mod: lambda left, right: left % right,
        ast.Pow: lambda left, right: left**right,
    }

    unary_ops: dict[type[ast.unaryop], UnaryOperator] = {
        ast.UAdd: lambda value: +value,
        ast.USub: lambda value: -value,
    }

    constants: dict[str, float] = {
        "pi": math.pi,
        "tau": math.tau,
        "e": math.e,
    }

    def _abs(*values: float) -> float:
        if len(values) != 1:
            raise ValueError("abs expects exactly one argument")
        (value,) = values
        return float(abs(value))

    def _wrap(func: Callable[..., float]) -> MathFunction:
        def _inner(*values: float) -> float:
            return float(func(*values))

        return _inner

    functions: dict[str, MathFunction] = {
        "sqrt": _wrap(math.sqrt),
        "log": _wrap(math.log),
        "sin": _wrap(math.sin),
        "cos": _wrap(math.cos),
        "tan": _wrap(math.tan),
        "asin": _wrap(math.asin),
        "acos": _wrap(math.acos),
        "atan": _wrap(math.atan),
        "abs": _abs,
    }

    return EvaluationConfig(
        binary_operators=binary_ops,
        unary_operators=unary_ops,
        constants=constants,
        functions=functions,
    )


_DEFAULT_CONFIG: Final[EvaluationConfig] = _build_default_config()


_COMMA_IN_NUMBER = re.compile(r"(?<=\d),(?=\d)")


class _ExpressionEvaluator:
    """Recursively walk the AST and compute a numeric result."""

    def __init__(self, config: EvaluationConfig) -> None:
        self._config = config

    def evaluate(self, expression: str) -> float:
        try:
            parsed = ast.parse(expression, mode="eval")
        except SyntaxError as exc:  # pragma: no cover - defensive, but tested via public API
            raise ValueError("Invalid expression") from exc
        return self._eval_node(parsed.body)

    def _eval_node(self, node: ast.AST) -> float:
        if isinstance(node, ast.BinOp):
            binary_type = type(node.op)
            binary_operation = self._config.binary_operators.get(binary_type)
            if binary_operation is None:
                raise ValueError("Unsupported operator")
            return binary_operation(
                self._eval_node(node.left),
                self._eval_node(node.right),
            )

        if isinstance(node, ast.UnaryOp):
            unary_type = type(node.op)
            unary_operation = self._config.unary_operators.get(unary_type)
            if unary_operation is None:
                raise ValueError("Unsupported unary operator")
            return unary_operation(self._eval_node(node.operand))

        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)

        if isinstance(node, ast.Name):
            constant = self._config.constants.get(node.id)
            if constant is None:
                raise ValueError("Unknown identifier")
            return constant

        if isinstance(node, ast.Call):
            return self._evaluate_call(node)

        raise ValueError("Unsupported expression")

    def _evaluate_call(self, node: ast.Call) -> float:
        if not isinstance(node.func, ast.Name):
            raise ValueError("Unsupported function call")

        function = self._config.functions.get(node.func.id)
        if function is None:
            raise ValueError("Unsupported function")

        if node.keywords:
            raise ValueError("Keyword arguments are not supported")

        arguments = [self._eval_node(arg) for arg in node.args]
        try:
            return float(function(*arguments))
        except TypeError as exc:  # pragma: no cover - re-raised as ValueError
            raise ValueError("Invalid arguments for function") from exc


def evaluate_expression(expression: str, *, config: EvaluationConfig | None = None) -> float:
    """Safely evaluate an arithmetic expression returning a float."""

    stripped = expression.strip()
    if not stripped:
        raise ValueError("Expression cannot be empty")

    normalized = _COMMA_IN_NUMBER.sub("", stripped)

    evaluator = _ExpressionEvaluator(config or _DEFAULT_CONFIG)
    return evaluator.evaluate(normalized)


def evaluate_lines(lines: Iterable[str]) -> Sequence[float | None]:
    """Evaluate multiple expressions, preserving order and blanks."""

    results: list[float | None] = []
    for line in lines:
        expression = line.strip()
        if not expression:
            results.append(None)
            continue

        try:
            results.append(evaluate_expression(expression))
        except ValueError:
            results.append(None)
    return results


__all__ = ["evaluate_expression", "evaluate_lines", "EvaluationConfig"]
