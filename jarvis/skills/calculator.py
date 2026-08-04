"""Arithmetic and unit conversion, both fully rule-based.

Arithmetic is evaluated with a small `ast`-based interpreter that only
allows numbers and +, -, *, /, //, %, ** -- never Python's `eval()`, so
there's no code-injection risk from spoken/typed input.
"""
from __future__ import annotations

import ast
import operator
import re

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_WORDS_TO_SYMBOLS = [
    (r"\bplus\b", "+"),
    (r"\bminus\b", "-"),
    (r"\btimes\b", "*"),
    (r"\bmultiplied by\b", "*"),
    (r"\bdivided by\b", "/"),
    (r"\bover\b", "/"),
    (r"\bto the power of\b", "**"),
    (r"\bsquared\b", "**2"),
    (r"\bcubed\b", "**3"),
    (r"[xX](?=\s*\d)", "*"),
]


class CalculatorError(ValueError):
    pass


def _normalize(expr: str) -> str:
    for pattern, replacement in _WORDS_TO_SYMBOLS:
        expr = re.sub(pattern, replacement, expr, flags=re.IGNORECASE)
    return expr


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise CalculatorError("I can only handle numbers and + - * / // % ** with parentheses.")


def safe_eval(expr: str) -> float:
    expr = _normalize(expr)
    try:
        node = ast.parse(expr, mode="eval").body
    except SyntaxError as exc:
        raise CalculatorError(f"I couldn't parse '{expr.strip()}' as math.") from exc
    try:
        return _eval_node(node)
    except ZeroDivisionError as exc:
        raise CalculatorError("Division by zero.") from exc


def _format_number(value: float) -> str:
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value)


def _calculate(match, ctx) -> str:
    expr = match.group("expr")
    result = safe_eval(expr)
    return f"That's {_format_number(result)}."


_UNIT_ALIASES = {
    "km": "km", "kilometer": "km", "kilometers": "km", "kilometre": "km", "kilometres": "km",
    "mile": "miles", "miles": "miles",
    "kg": "kg", "kilogram": "kg", "kilograms": "kg",
    "lb": "lbs", "lbs": "lbs", "pound": "lbs", "pounds": "lbs",
    "c": "celsius", "celsius": "celsius",
    "f": "fahrenheit", "fahrenheit": "fahrenheit",
    "m": "m", "meter": "m", "meters": "m", "metre": "m", "metres": "m",
    "ft": "feet", "foot": "feet", "feet": "feet",
}

_CONVERSIONS = {
    ("km", "miles"): lambda v: v * 0.621371,
    ("miles", "km"): lambda v: v / 0.621371,
    ("kg", "lbs"): lambda v: v * 2.20462,
    ("lbs", "kg"): lambda v: v / 2.20462,
    ("celsius", "fahrenheit"): lambda v: v * 9 / 5 + 32,
    ("fahrenheit", "celsius"): lambda v: (v - 32) * 5 / 9,
    ("m", "feet"): lambda v: v * 3.28084,
    ("feet", "m"): lambda v: v / 3.28084,
}


def _convert(match, ctx) -> str:
    value = float(match.group("value"))
    from_unit = _UNIT_ALIASES.get(match.group("from_unit").lower())
    to_unit = _UNIT_ALIASES.get(match.group("to_unit").lower())
    if not from_unit or not to_unit:
        return "I don't know that unit yet. Try km, miles, kg, lbs, celsius, fahrenheit, m, or feet."
    fn = _CONVERSIONS.get((from_unit, to_unit))
    if fn is None:
        return f"I don't know how to convert {from_unit} to {to_unit}."
    result = fn(value)
    return f"{_format_number(value)} {from_unit} is about {_format_number(round(result, 2))} {to_unit}."


def register(engine) -> None:
    engine.register(
        "unit_convert",
        r"\bconvert\s+(?P<value>-?\d+(\.\d+)?)\s*(?P<from_unit>[a-zA-Z]+)\s+(to|into)\s+(?P<to_unit>[a-zA-Z]+)",
        _convert,
        "'convert 10 km to miles' - unit conversion (km/miles, kg/lbs, celsius/fahrenheit, m/feet).",
    )
    engine.register(
        "calculate",
        r"\b(calculate|compute|what('?s| is))\s+(?P<expr>[-+*/0-9().,\s]*\d[-+*/0-9().,\s]*"
        r"|.*?(plus|minus|times|multiplied by|divided by|over|squared|cubed).*)$",
        _calculate,
        "'calculate 12 * (3 + 4)' or 'what is 9 plus 10' - arithmetic.",
    )
