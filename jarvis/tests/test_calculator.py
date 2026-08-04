import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from jarvis.skills.calculator import CalculatorError, safe_eval


def test_basic_arithmetic():
    assert safe_eval("2 + 3") == 5
    assert safe_eval("10 / 4") == 2.5
    assert safe_eval("2 ** 3") == 8
    assert safe_eval("(2 + 3) * 4") == 20


def test_word_operators_are_normalized():
    assert safe_eval("9 plus 10") == 19
    assert safe_eval("9 minus 4") == 5
    assert safe_eval("6 times 7") == 42
    assert safe_eval("20 divided by 4") == 5


def test_division_by_zero_raises_calculator_error():
    with pytest.raises(CalculatorError):
        safe_eval("5 / 0")


def test_non_math_input_raises_calculator_error():
    with pytest.raises(CalculatorError):
        safe_eval("import os")


def test_only_numeric_operators_allowed():
    # this must never be able to execute arbitrary python
    with pytest.raises(CalculatorError):
        safe_eval("__import__('os').system('echo hi')")
