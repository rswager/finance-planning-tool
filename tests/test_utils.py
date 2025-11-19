from models.utils import (_calculate_rounded_value,cents_to_dollars,dollars_to_cents,
                          money_cents, money_dollars, round_value)
import pytest


@pytest.mark.parametrize("value,mod,round_up,expected", [
    (money_cents(123_00), 10_00, True, money_cents(130_00)),
    (money_cents(123_00), 10_00, False, money_cents(120_00)),
    (money_cents(120_00), 10_00, True, money_cents(120_00)),
    (money_cents(120_00), 10_00, False, money_cents(120_00)),
    (money_cents(1050_00), 100_00, True, money_cents(1100_00)),
    (money_cents(1050_00), 100_00, False, money_cents(1000_00)),
])
def test_calculate_rounded_value(value, mod, round_up, expected):
    assert _calculate_rounded_value(value, mod, round_up) == expected


@pytest.mark.parametrize("amount,round_up,expected", [
    (money_cents(123_00), True, money_cents(130_00)),      # < 1000 → nearest 10
    (money_cents(123_00), False, money_cents(120_00)),
    (money_cents(999_00), True, money_cents(1000_00)),
    (money_cents(999_00), False, money_cents(990_00)),
    (money_cents(1000_00), True, money_cents(1000_00)),    # >= 1000 → nearest 100
    (money_cents(1050_00), True, money_cents(1100_00)),
    (money_cents(1050_00), False, money_cents(1000_00)),
])
def test_round_value(amount, round_up, expected):
    assert round_value(amount, round_up) == expected


@pytest.mark.parametrize("amount,expected" , [
    (money_cents(99), money_dollars(.99)),
    (money_cents(150), money_dollars(1.50)),
    (money_cents(101), money_dollars(1.01)),
    (money_cents(10000), money_dollars(100.00))
])
def test_cents_to_dollars(amount, expected):
    assert cents_to_dollars(amount) == expected

@pytest.mark.parametrize("amount,expected" , [
    (money_dollars(.99),money_cents(99)),
    (money_dollars(1.50),money_cents(150)),
    (money_dollars(1.01), money_cents(101)),
    (money_dollars(100.00), money_cents(10000)),
    (money_dollars(-.99),money_cents(-99)),
    (money_dollars(-1.50),money_cents(-150)),
    (money_dollars(-1.01), money_cents(-101)),
    (money_dollars(-100.00), money_cents(-10000)),
])
def test_cents_to_dollars(amount, expected):
    assert dollars_to_cents(amount) == expected