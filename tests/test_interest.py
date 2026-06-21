from datetime import date
from math import ceil

import pytest

from models.core.interest import Interest
from models.core.utils import MinorUnit


def test_daily_interest_non_leap(interest_instance):
    bal = MinorUnit.from_major(1_000.00)
    test_date = date(2025, 11, 8)
    expected_interest = ceil(int(abs(bal)) * (0.05 / 365))
    assert interest_instance.calculate_daily_interest(bal, test_date) == expected_interest


def test_daily_interest_leap_year(interest_instance):
    bal = MinorUnit.from_major(1_000.00)
    test_date = date(2024, 2, 29)
    expected_interest = ceil(int(abs(bal)) * (0.05 / 366))
    assert interest_instance.calculate_daily_interest(bal, test_date) == expected_interest


def test_zero_balance_no_interest(interest_instance):
    interest = interest_instance.calculate_daily_interest(MinorUnit(0), date(2025, 11, 8))
    assert interest == MinorUnit(0)


def test_negative_balance_interest_positive(interest_instance):
    bal = MinorUnit.from_major(-2_000.00)
    test_date = date(2025, 11, 8)
    expected_interest = ceil(int(abs(bal)) * (0.05 / 365))
    assert interest_instance.calculate_daily_interest(bal, test_date) == expected_interest


def test_cumulative_interest_multiple_calls(interest_instance):
    bal = MinorUnit.from_major(1_000.00)
    test_date = date(2025, 11, 8)
    interest1 = interest_instance.calculate_daily_interest(bal, test_date)
    interest2 = interest_instance.calculate_daily_interest(bal, test_date)
    assert interest_instance._interest_to_date == interest1 + interest2


def test_small_balance_rounding(interest_instance):
    bal = MinorUnit(1)
    interest = interest_instance.calculate_daily_interest(bal, date(2025, 11, 8))
    assert interest == ceil(int(bal) * (0.05 / 365))


def test_valid_apr_does_not_raise():
    try:
        Interest(0.05)
        Interest(0.0)
        Interest(1.0)
    except ValueError:
        pytest.fail("Valid APR raised ValueError unexpectedly")


@pytest.mark.parametrize("invalid_apr", [-0.01, -5, 1.01, 2, 100])
def test_invalid_apr_raises_value_error(invalid_apr):
    with pytest.raises(ValueError):
        Interest(invalid_apr)
