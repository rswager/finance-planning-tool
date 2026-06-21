from datetime import date

import pytest
from dateutil.relativedelta import relativedelta

from models.core.enum_type import FrequencyType
from models.core.trigger_days import TriggerDays


# --- Tests ---
def test_trigger_date_setter(monthly_trigger):
    """Dates <= 28 should be added as-is."""
    d = date(2025, 1, 20)
    monthly_trigger.trigger_date = d
    assert monthly_trigger.trigger_date == d


def test_date_triggered_removes_and_adds_next_monthly(monthly_trigger):
    """When triggered, the current date is removed and next month added."""
    d = date(2025, 1, 15)
    monthly_trigger.trigger_date = d

    # Trigger that date
    result = monthly_trigger.date_triggered(d)
    assert result is True

    # The original date should be removed
    assert d != monthly_trigger.trigger_date

    # The new date should be one month later, capped to 28
    expected = d + relativedelta(months=1)
    assert monthly_trigger.trigger_date.month == expected.month
    assert monthly_trigger.trigger_date.day == min(expected.day, 28)


def test_date_triggered_removes_and_adds_next_biweekly(biweekly_trigger):
    """When triggered, it should remove and add +14 days."""
    d = date(2025, 1, 1)
    biweekly_trigger.trigger_date = d

    # Trigger that date
    result = biweekly_trigger.date_triggered(d)
    assert result is True

    # The old date should be removed
    assert d != biweekly_trigger.trigger_date

    # The new date should be +14 days later
    expected = d + relativedelta(days=14)
    assert biweekly_trigger.trigger_date == expected


def test_date_triggered_removes_and_adds_next_weekly(weekly_trigger):
    """When triggered, it should remove and add +7 days."""
    d = date(2025, 1, 8)
    weekly_trigger.trigger_date = d

    # Trigger that date
    result = weekly_trigger.date_triggered(d)
    assert result is True

    # The old date should be removed
    assert d != weekly_trigger.trigger_date

    # The new date should be +7 days later
    expected = d + relativedelta(days=7)
    assert weekly_trigger.trigger_date == expected


def test_date_triggered_returns_false_when_not_found(weekly_trigger):
    """Should return False if date not in trigger_days."""
    d = date(2025, 3, 1)
    assert weekly_trigger.date_triggered(d) is False
    # Nothing new should be added
    assert weekly_trigger.trigger_date is None


@pytest.mark.parametrize(
    "target_date,init_date,final_date,trigger",
    [
        # Weekly, already on target
        (date(2025, 1, 1), date(2025, 1, 1), date(2025, 1, 1), TriggerDays(FrequencyType.WEEKLY)),
        # Weekly backward overshoot -> correction forward
        (date(2025, 1, 1), date(2025, 1, 2), date(2025, 1, 2), TriggerDays(FrequencyType.WEEKLY)),
        # Multiple Weekly forward
        (date(2025, 1, 1), date(2024, 12, 2), date(2025, 1, 6), TriggerDays(FrequencyType.WEEKLY)),
        # forward, lands exactly on target
        (date(2025, 1, 1), date(2024, 12, 25), date(2025, 1, 1), TriggerDays(FrequencyType.WEEKLY)),
        # backward, lands exactly on target
        (date(2025, 1, 1), date(2025, 2, 5), date(2025, 1, 1), TriggerDays(FrequencyType.WEEKLY)),
        # backward overshoot -> correction forward
        (date(2025, 1, 2), date(2025, 1, 10), date(2025, 1, 3), TriggerDays(FrequencyType.WEEKLY)),
        # monthly forward, multiple steps
        (date(2025, 3, 1), date(2025, 1, 15), date(2025, 3, 15), TriggerDays(FrequencyType.MONTHLY)),
        # monthly backward, overshoot -> correction forward
        (date(2025, 3, 1), date(2025, 6, 15), date(2025, 3, 15), TriggerDays(FrequencyType.MONTHLY)),
        # singular: early return, trigger unchanged
        (date(2025, 2, 1), date(2025, 1, 1), date(2025, 1, 1), TriggerDays(FrequencyType.SINGULAR)),
    ],
)
def test_bring_trigger_date_to_target_date(target_date: date, init_date: date, final_date: date, trigger: TriggerDays):
    trigger.trigger_date = init_date
    trigger.bring_trigger_date_to_target_date(target_date)
    assert trigger.trigger_date == final_date


def test_bring_trigger_date_to_target_date_raises_when_trigger_not_set(weekly_trigger: TriggerDays):
    with pytest.raises(ValueError):
        weekly_trigger.bring_trigger_date_to_target_date(date(2025, 1, 1))


def test_bring_trigger_date_to_target_date_raises_on_invalid_target_type(weekly_trigger: TriggerDays):
    weekly_trigger.trigger_date = date(2025, 1, 1)
    with pytest.raises(TypeError):
        weekly_trigger.bring_trigger_date_to_target_date("2025/1/1")  # type: ignore


@pytest.mark.parametrize(
    "init_date,final_date,forwards,trigger",
    [
        (date(2025, 1, 1), None, True, TriggerDays(FrequencyType.SINGULAR)),
        (date(2025, 1, 1), None, False, TriggerDays(FrequencyType.SINGULAR)),
        (date(2025, 1, 1), date(2025, 1, 2), True, TriggerDays(FrequencyType.DAILY)),
        (date(2025, 1, 1), date(2024, 12, 31), False, TriggerDays(FrequencyType.DAILY)),
        (date(2025, 1, 1), date(2025, 1, 8), True, TriggerDays(FrequencyType.WEEKLY)),
        (date(2025, 1, 1), date(2024, 12, 25), False, TriggerDays(FrequencyType.WEEKLY)),
        (date(2025, 1, 1), date(2025, 1, 15), True, TriggerDays(FrequencyType.BI_WEEKLY)),
        (date(2025, 1, 1), date(2024, 12, 18), False, TriggerDays(FrequencyType.BI_WEEKLY)),
        (date(2025, 1, 1), date(2025, 2, 1), True, TriggerDays(FrequencyType.MONTHLY)),
        (date(2025, 1, 1), date(2024, 12, 1), False, TriggerDays(FrequencyType.MONTHLY)),
        (date(2025, 1, 1), date(2026, 1, 1), True, TriggerDays(FrequencyType.YEARLY)),
        (date(2025, 1, 1), date(2024, 1, 1), False, TriggerDays(FrequencyType.YEARLY)),
        (date(2025, 1, 1), date(2026, 1, 1), True, TriggerDays(FrequencyType.YEARLY)),
        (date(2025, 1, 1), date(2024, 1, 1), False, TriggerDays(FrequencyType.YEARLY)),
    ],
)
def test_set_next_trigger_date(init_date: date, final_date: date, forwards: bool, trigger: TriggerDays):
    trigger.trigger_date = init_date
    trigger._set_next_trigger_date(current_trigger_date=init_date, forwards=forwards)
    assert trigger.trigger_date == final_date


def test_set_next_trigger_day_raises_when_trigger_not_set(weekly_trigger: TriggerDays):
    weekly_trigger._frequency = None  # ty: ignore[invalid-assignment]
    with pytest.raises(ValueError):
        weekly_trigger._set_next_trigger_date(date(2025, 1, 1))


def test_set_next_trigger_day_raises_when_frequency_invalid(weekly_trigger: TriggerDays):
    weekly_trigger._frequency = "Invalid"  # ty: ignore[invalid-assignment]
    with pytest.raises(ValueError):
        weekly_trigger._set_next_trigger_date(date(2025, 1, 1))
