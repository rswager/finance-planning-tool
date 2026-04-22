from datetime import date
from math import floor

import pytest

from models.bankAccount import BankAccount
from models.enumType import AccountType, FrequencyType
from models.income import Income
from models.utils import dollars_to_cents, money_cents, money_dollars


@pytest.fixture
def bank_accounts():
    acc1 = BankAccount("Checking", dollars_to_cents(money_dollars(1_000.00)), AccountType.CHECKING)
    acc2 = BankAccount("Savings", dollars_to_cents(money_dollars(500.00)), AccountType.SAVINGS)
    return acc1, acc2


@pytest.fixture
def income(bank_accounts):
    acc1, acc2 = bank_accounts
    return Income(
        name_in="Salary",
        income_in=dollars_to_cents(money_dollars(1_000.00)),
        initial_pay_date_in=date(2025, 11, 8),
        account_contributions_in=[(acc1, 0.6), (acc2, 0.4)],
        frequency_type_in=FrequencyType.WEEKLY,
    )


# --- Initialization ---
def test_initialization(income, bank_accounts):
    acc1, acc2 = bank_accounts
    assert income._income_name == "Salary"
    # Contributions assigned correctly
    assert income._account_contributions[0][0] == acc1
    assert income._account_contributions[0][1] == 0.6
    assert income._account_contributions[1][0] == acc2
    assert income._account_contributions[1][1] == 0.4


# --- Contribution validation ---
def test_invalid_contribution_percentage(bank_accounts):
    acc1, _ = bank_accounts
    # Contribution > 1 should raise ValueError
    with pytest.raises(ValueError):
        Income(
            name_in="Salary",
            income_in=dollars_to_cents(money_dollars(1_000.00)),
            initial_pay_date_in=date(2025, 11, 8),
            account_contributions_in=[(acc1, 1.5)],
            frequency_type_in=FrequencyType.WEEKLY,
        )


def test_total_contribution_exceeds_1(bank_accounts):
    acc1, acc2 = bank_accounts
    # Total contributions > 1 should raise ValueError
    with pytest.raises(ValueError):
        Income(
            name_in="Salary",
            income_in=dollars_to_cents(money_dollars(1_000.00)),
            initial_pay_date_in=date(2025, 11, 8),
            account_contributions_in=[(acc1, 0.7), (acc2, 0.5)],
            frequency_type_in=FrequencyType.WEEKLY,
        )


# --- Deposit ---
def test_deposit_updates_accounts(income, bank_accounts):
    acc1, acc2 = bank_accounts
    deposit_date = date(2025, 11, 8)
    income.deposit(deposit_date)
    # Check balances updated correctly
    assert acc1.balance_cents == dollars_to_cents(money_dollars(1_000.00)) + money_cents(
        floor(float(dollars_to_cents(money_dollars(1_000.00))) * 0.6)
    )
    assert acc2.balance_cents == dollars_to_cents(money_dollars(500.00)) + money_cents(
        floor(float(dollars_to_cents(money_dollars(1_000.00))) * 0.4)
    )

    # Check ledger entries
    assert acc1.raw_copy_ledger[-1][2] == "Salary - Check"
    assert acc2.raw_copy_ledger[-1][2] == "Salary - Check"


# --- process_day triggers deposit only on trigger date ---
def test_process_day_triggers_deposit(income, bank_accounts):
    acc1, acc2 = bank_accounts
    normal_date = date(2025, 11, 7)
    income.process_day(normal_date)
    # Ledger should not change
    assert len(acc1.raw_copy_ledger) == 1
    assert len(acc2.raw_copy_ledger) == 1

    trigger_date = date(2025, 11, 8)
    income.process_day(trigger_date)
    # Ledger updated on trigger day
    assert len(acc1.raw_copy_ledger) == 2
    assert len(acc2.raw_copy_ledger) == 2
    assert acc1.raw_copy_ledger[-1][3] == 1_000 * 0.6
    assert acc2.raw_copy_ledger[-1][3] == 1_000 * 0.4
