from datetime import date

import pytest

from finance_planning_tool.models.core import (
    FrequencyType,
    MinorUnit,
)
from finance_planning_tool.models.income import (
    Income,
)
from finance_planning_tool.models.persistence import (
    SerialTypeLookup,
)


def test_type_key_in_serialized_account_type(income):
    assert SerialTypeLookup[income.TYPE_KEY].value == Income


def test_initialization(income, bank_accounts):
    acc1, acc2 = bank_accounts
    assert income._income_name == "Salary"
    assert income._account_contributions[0][0] == acc1
    assert income._account_contributions[0][1] == 0.6
    assert income._account_contributions[1][0] == acc2
    assert income._account_contributions[1][1] == 0.4


def test_invalid_contribution_percentage(bank_accounts):
    acc1, _ = bank_accounts
    with pytest.raises(ValueError):
        Income(
            name_in="Salary",
            income_in=MinorUnit.from_major(1_000.00),
            initial_pay_date_in=date(2025, 11, 8),
            account_contributions_in=[(acc1, 1.5)],
            frequency_type_in=FrequencyType.WEEKLY,
        )


def test_total_contribution_exceeds_1(bank_accounts):
    acc1, acc2 = bank_accounts
    with pytest.raises(ValueError):
        Income(
            name_in="Salary",
            income_in=MinorUnit.from_major(1_000.00),
            initial_pay_date_in=date(2025, 11, 8),
            account_contributions_in=[(acc1, 0.7), (acc2, 0.5)],
            frequency_type_in=FrequencyType.WEEKLY,
        )


def test_deposit_updates_accounts(income, bank_accounts):
    acc1, acc2 = bank_accounts
    income_minor = MinorUnit.from_major(1_000.00)
    income.deposit(date(2025, 11, 8))

    assert acc1.balance_minor == MinorUnit.from_major(1_000.00) + income_minor * 0.6
    assert acc2.balance_minor == MinorUnit.from_major(1_000.00) + income_minor * 0.4
    assert acc1.raw_copy_ledger[-1].description == "Salary - Check"
    assert acc2.raw_copy_ledger[-1].description == "Salary - Check"


def test_deposit_preserves_full_amount(bank_accounts):
    acc1, acc2 = bank_accounts
    income = Income(
        name_in="Paycheck",
        income_in=MinorUnit.from_major(2_557.31),
        initial_pay_date_in=date(2025, 11, 6),
        account_contributions_in=[(acc1, 0.9), (acc2, 0.1)],
        frequency_type_in=FrequencyType.BI_WEEKLY,
    )
    income.deposit(date(2025, 11, 6))
    total_deposited = (acc1.balance_minor - MinorUnit.from_major(1_000.00)) + (
        acc2.balance_minor - MinorUnit.from_major(500.00)
    )
    assert total_deposited == MinorUnit.from_major(3_057.31)


def test_process_day_triggers_deposit(income, bank_accounts):
    acc1, acc2 = bank_accounts

    income.process_day(date(2025, 11, 7))
    assert len(acc1.raw_copy_ledger) == 0
    assert len(acc2.raw_copy_ledger) == 0

    income.process_day(date(2025, 11, 8))
    assert len(acc1.raw_copy_ledger) == 1
    assert len(acc2.raw_copy_ledger) == 1
    assert acc1.raw_copy_ledger[-1].credit == 1_000 * 0.6
    assert acc2.raw_copy_ledger[-1].credit == 1_000 * 0.4


def test_to_dict(income, bank_accounts):
    acc1, acc2 = bank_accounts
    d = income.to_dict()
    assert set(d.keys()) == {
        "name_in",
        "income_in",
        "initial_pay_date_in",
        "account_contributions_in",
        "frequency_type_in",
        "round_down_in",
        "serial_type_in",
    }
    assert d["name_in"] == "Salary"
    assert d["income_in"] == int(MinorUnit.from_major(1_000.00))
    assert d["initial_pay_date_in"] == date(2025, 11, 8).isoformat()
    assert d["account_contributions_in"] == [
        {"account_name": acc1.account_name, "contribution": 0.6},
        {"account_name": acc2.account_name, "contribution": 0.4},
    ]
    assert d["frequency_type_in"] == FrequencyType.WEEKLY.value
    assert d["round_down_in"] is False
    # We assert that serial_type_in is IN SerialTypeLookup by not catching a raise
    SerialTypeLookup[d["serial_type_in"]]


def test_from_dict_round_trip(income, bank_accounts):
    acc1, acc2 = bank_accounts
    income_dict = income.to_dict()
    reconstructed = Income.from_dict(income_dict)
    reconstructed.set_account_contribution([(acc1, 0.6), (acc2, 0.4)])
    assert reconstructed.to_dict() == income_dict


def test_from_dict_missing_key_raises(income, bank_accounts):
    d = income.to_dict()
    del d["round_down_in"]
    with pytest.raises(KeyError):
        Income.from_dict(d)


def test_initialize_simulation_date(income):
    income.initialize_simulation_date(date(2025, 11, 14))
    assert income._trigger_days.trigger_date == date(2025, 11, 15)
