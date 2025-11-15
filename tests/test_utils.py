from models.utils import _calculate_rounded_value, round_value
import pytest


@pytest.mark.parametrize("value,mod,round_up,expected", [
    (123, 10, True, 130),
    (123, 10, False, 120),
    (120, 10, True, 120),
    (120, 10, False, 120),
    (1050, 100, True, 1100),
    (1050, 100, False, 1000),
])
def test_calculate_rounded_value(value, mod, round_up, expected):
    assert _calculate_rounded_value(value, mod, round_up) == expected


@pytest.mark.parametrize("amount,round_up,expected", [
    (123, True, 130),      # < 1000 → nearest 10
    (123, False, 120),
    (999, True, 1000),
    (999, False, 990),
    (1000, True, 1000),    # >= 1000 → nearest 100
    (1050, True, 1100),
    (1050, False, 1000),
])
def test_round_value(amount, round_up, expected):
    assert round_value(amount, round_up) == expected

if __name__ == '__main__':
    pytest.main([__file__])