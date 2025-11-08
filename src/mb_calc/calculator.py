"""Helpers that convert free-form text into evaluated calculator results."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence

from .evaluator import evaluate_expression


def render_results(lines: Iterable[str]) -> Sequence[str]:
    """Evaluate each provided line and return printable results."""

    outputs: list[str] = []
    for line in lines:
        expression = line.strip()
        if not expression:
            outputs.append("")
            continue

        try:
            value = evaluate_expression(expression)
        except ValueError:
            outputs.append("")
            continue

        outputs.append(_format_number(value))
    return outputs


def _format_number(value: float) -> str:
    """Format numbers for display, trimming trailing zeros where possible."""

    if math.isnan(value) or math.isinf(value):
        return str(value)

    if value.is_integer():
        return format(int(value), ",d")

    return format(value, ",g")


__all__ = ["render_results"]
