import pytest

from models.utils import CurrencyType, MinorUnit, _calculate_rounded_value, round_value


@pytest.mark.parametrize(
    "value,mod,round_up,expected",
    [
        (MinorUnit(123_00), 10_00, True, MinorUnit(130_00)),
        (MinorUnit(123_00), 10_00, False, MinorUnit(120_00)),
        (MinorUnit(120_00), 10_00, True, MinorUnit(120_00)),
        (MinorUnit(120_00), 10_00, False, MinorUnit(120_00)),
        (MinorUnit(1050_00), 100_00, True, MinorUnit(1100_00)),
        (MinorUnit(1050_00), 100_00, False, MinorUnit(1000_00)),
    ],
)
def test_calculate_rounded_value(value, mod, round_up, expected):
    assert _calculate_rounded_value(value, mod, round_up) == expected


@pytest.mark.parametrize(
    "amount,round_up,expected",
    [
        (MinorUnit(123_00), True, MinorUnit(130_00)),  # < 1000 → nearest 10
        (MinorUnit(123_00), False, MinorUnit(120_00)),
        (MinorUnit(999_00), True, MinorUnit(1000_00)),
        (MinorUnit(999_00), False, MinorUnit(990_00)),
        (MinorUnit(1000_00), True, MinorUnit(1000_00)),  # >= 1000 → nearest 100
        (MinorUnit(1050_00), True, MinorUnit(1100_00)),
        (MinorUnit(1050_00), False, MinorUnit(1000_00)),
    ],
)
def test_round_value(amount, round_up, expected):
    assert round_value(amount, round_up) == expected


@pytest.mark.parametrize(
    "minor,expected_major",
    [
        (MinorUnit(99), 0.99),
        (MinorUnit(150), 1.50),
        (MinorUnit(101), 1.01),
        (MinorUnit(10000), 100.00),
    ],
)
def test_to_major(minor, expected_major):
    assert minor.to_major() == expected_major


@pytest.mark.parametrize(
    "major,expected_minor",
    [
        (0.99, MinorUnit(99)),
        (1.50, MinorUnit(150)),
        (1.01, MinorUnit(101)),
        (100.00, MinorUnit(10000)),
        (-0.99, MinorUnit(-99)),
        (-1.50, MinorUnit(-150)),
        (-1.01, MinorUnit(-101)),
        (-100.00, MinorUnit(-10000)),
    ],
)
def test_from_major(major, expected_minor):
    assert MinorUnit.from_major(major) == expected_minor


def test_minor_unit_constructor_truncates_float():
    assert MinorUnit(3.9) == 3
    assert MinorUnit(1.0) == 1
    assert MinorUnit(-2.7) == -2


def test_minor_unit_arithmetic_preserves_type():
    a = MinorUnit(500)
    b = MinorUnit(300)
    assert isinstance(a + b, MinorUnit)
    assert isinstance(a - b, MinorUnit)
    assert isinstance(-a, MinorUnit)
    assert isinstance(abs(-a), MinorUnit)
    assert isinstance(a * 2, MinorUnit)
    assert isinstance(a * 0.5, MinorUnit)
    assert isinstance(a / 2, MinorUnit)
    assert isinstance(a / 0.5, MinorUnit)


def test_minor_unit_arithmetic_correctness():
    assert MinorUnit(500) + MinorUnit(300) == MinorUnit(800)
    assert MinorUnit(500) - MinorUnit(300) == MinorUnit(200)
    assert -MinorUnit(500) == MinorUnit(-500)
    assert abs(MinorUnit(-500)) == MinorUnit(500)


@pytest.mark.parametrize(
    "value,factor,expected",
    [
        (MinorUnit(500), 2, MinorUnit(1000)),
        (MinorUnit(500), 0.5, MinorUnit(250)),
        (MinorUnit(333), 0.5, MinorUnit(166)),  # truncates, not rounds
        (MinorUnit(0), 99.9, MinorUnit(0)),
    ],
)
def test_mul_correctness(value, factor, expected):
    assert value * factor == expected


@pytest.mark.parametrize(
    "value,divisor,expected",
    [
        (MinorUnit(1000), 2, MinorUnit(500)),
        (MinorUnit(1000), 2.0, MinorUnit(500)),
        (MinorUnit(333), 2, MinorUnit(166)),  # truncates, not rounds
        (MinorUnit(500), 0.5, MinorUnit(1000)),
    ],
)
def test_truediv_correctness(value, divisor, expected):
    assert value / divisor == expected


@pytest.mark.parametrize(
    "minor,expected_major",
    [
        (MinorUnit(-99), -0.99),
        (MinorUnit(-150), -1.50),
        (MinorUnit(-10000), -100.00),
    ],
)
def test_to_major_negative(minor, expected_major):
    assert minor.to_major() == expected_major


def test_set_currency_changes_conversion():
    MinorUnit.set_currency(CurrencyType.JPY)
    try:
        assert MinorUnit.from_major(500) == MinorUnit(500)
        assert MinorUnit(500).to_major() == 500.0
        assert MinorUnit(1).symbol == "¥"
    finally:
        MinorUnit.set_currency(CurrencyType.USD)


def test_set_currency_usd_restored():
    assert MinorUnit.from_major(1.00) == MinorUnit(100)
    assert MinorUnit(100).to_major() == 1.00
    assert MinorUnit(1).symbol == "$"
