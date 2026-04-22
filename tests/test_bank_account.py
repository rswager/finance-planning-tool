from datetime import date

import pytest

from models.bankAccount import BankAccount
from models.enumType import AccountType
from models.utils import dollars_to_cents, money_cents, money_dollars


@pytest.fixture
def bank_account():
    """Returns a BankAccount with starting balance 1000 and type CHECKING."""
    return BankAccount("Test Account", dollars_to_cents(money_dollars(1000.00)), AccountType.CHECKING)


# --- Initialization ---
def test_initialization(bank_account):
    assert bank_account.account_name == "Test Account"
    assert bank_account.account_type == AccountType.CHECKING
    # Ledger should have only header initially
    assert bank_account.ledger_col_count == 6
    assert len(bank_account.raw_copy_ledger) == 1  # header only


# --- Ledger immutability ---
def test_raw_copy_ledger_is_copy(bank_account):
    ledger_copy = bank_account.raw_copy_ledger
    # Modify the copy
    ledger_copy.append([999, date.today(), "Hack", 0, 0, 0])
    # Original ledger should not change
    assert len(bank_account.raw_copy_ledger) == 1


# --- Transaction updates balance and ledger ---
def test_make_transaction_updates_ledger_and_balance(bank_account):
    tx_date = date(2025, 11, 8)
    bank_account.make_a_transaction(tx_date, "Deposit", credit=money_cents(500_00), debit=money_cents(0))

    ledger = bank_account.raw_copy_ledger
    # Ledger has header + 1 entry
    assert len(ledger) == 2

    entry = ledger[1]
    # Check ledger entry content
    assert entry[1] == tx_date
    assert entry[2] == "Deposit"
    assert entry[3] == money_dollars(500.00)
    assert entry[4] == money_dollars(0.00)
    # Balance updated correctly
    assert entry[5] == money_dollars(1500.00)


# --- Multiple transactions ---
def test_multiple_transactions(bank_account):
    tx_date1 = date(2025, 11, 8)
    tx_date2 = date(2025, 11, 9)

    # Deposit 500
    bank_account.make_a_transaction(tx_date1, "Deposit", credit=money_cents(500_00), debit=money_cents(0))
    # Withdraw 200
    bank_account.make_a_transaction(tx_date2, "Withdrawal", credit=money_cents(0), debit=money_cents(200_00))

    ledger = bank_account.raw_copy_ledger
    # Ledger has header + 2 entries
    assert len(ledger) == 3

    # First entry
    assert ledger[1][5] == money_dollars(1500.00)
    # Second entry
    assert ledger[2][5] == money_dollars(1300.00)


# --- Zero transaction ---
def test_zero_transaction(bank_account):
    tx_date = date(2025, 11, 8)
    bank_account.make_a_transaction(tx_date, "No Change", credit=money_cents(0), debit=money_cents(0))
    ledger = bank_account.raw_copy_ledger
    assert ledger[1][5] == money_dollars(1000.00)  # balance unchanged
