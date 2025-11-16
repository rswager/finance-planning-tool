import pytest
from datetime import date
from models.interest import Interest

@pytest.fixture
def interest_instance():
    """Create an Interest instance with 5% APR."""
    return Interest(0.05)


# --- Basic Daily Interest Calculation ---
def test_daily_interest_non_leap(interest_instance):
    bal = 1000.0
    test_date = date(2025, 11, 8)  # non-leap year
    expected_interest = round(abs(bal) * (0.05 / 365), 2)

    interest = interest_instance.calculate_daily_interest(bal, test_date)
    assert interest == expected_interest


# --- Leap Year Handling ---
def test_daily_interest_leap_year(interest_instance):
    bal = 1000.0
    test_date = date(2024, 2, 29)  # leap year
    expected_interest = round(abs(bal) * (0.05 / 366), 2)

    interest = interest_instance.calculate_daily_interest(bal, test_date)
    assert interest == expected_interest



# --- Zero Balance ---
def test_zero_balance_no_ledger_entry(interest_instance):
    bal = 0.0
    test_date = date(2025, 11, 8)
    interest = interest_instance.calculate_daily_interest(bal, test_date)

    assert interest == 0


# --- Negative Balance ---
def test_negative_balance_interest_positive(interest_instance):
    bal = -2000.0
    test_date = date(2025, 11, 8)
    expected_interest = round(abs(bal) * (0.05 / 365), 2)

    interest = interest_instance.calculate_daily_interest(bal, test_date)
    assert interest == expected_interest


# --- Cumulative Interest Tracking ---
def test_cumulative_interest_multiple_calls(interest_instance):
    bal = 1000.0
    test_date = date(2025, 11, 8)

    interest1 = interest_instance.calculate_daily_interest(bal, test_date)
    interest2 = interest_instance.calculate_daily_interest(bal, test_date)

    assert interest_instance._interest_to_date == round(interest1 + interest2, 2)


# --- Rounding Edge Case ---
def test_small_balance_rounding(interest_instance):
    bal = 0.01
    test_date = date(2025, 11, 8)
    interest = interest_instance.calculate_daily_interest(bal, test_date)

    # Should round to 2 decimal places
    assert interest == round(0.01 * (0.05 / 365), 2)


def test_valid_apr_does_not_raise():
    """APR between 0 and 1 should initialize correctly."""
    try:
        _ = Interest(0.05)  # 5%
        _ = Interest(0.0)  # 0%
        _ = Interest(1.0)  # 100%
    except ValueError:
        pytest.fail("Valid APR raised ValueError unexpectedly")


@pytest.mark.parametrize("invalid_apr", [-0.01, -5, 1.01, 2, 100])
def test_invalid_apr_raises_value_error(invalid_apr):
    """APR outside 0-1 should raise ValueError."""
    with pytest.raises(ValueError):
        Interest(invalid_apr)
