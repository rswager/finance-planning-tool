from datetime import date

import pytest

from models.bankAccount import BankAccount
from models.enumType import AccountType
from models.utils import MinorUnit


@pytest.fixture
def bank_account():
    return BankAccount("Test Account", MinorUnit.from_major(1000.00), AccountType.CHECKING)


def test_initialization(bank_account):
    assert bank_account.account_name == "Test Account"
    assert bank_account.account_type == AccountType.CHECKING
    assert bank_account.ledger_col_count == 6
    assert len(bank_account.raw_copy_ledger) == 1  # header only


def test_raw_copy_ledger_is_copy(bank_account):
    ledger_copy = bank_account.raw_copy_ledger
    ledger_copy.append([999, date.today(), "Hack", 0, 0, 0])
    assert len(bank_account.raw_copy_ledger) == 1


def test_make_transaction_updates_ledger_and_balance(bank_account):
    tx_date = date(2025, 11, 8)
    bank_account.make_a_transaction(tx_date, "Deposit", credit=MinorUnit(500_00), debit=MinorUnit(0))

    ledger = bank_account.raw_copy_ledger
    assert len(ledger) == 2

    entry = ledger[1]
    assert entry[1] == tx_date
    assert entry[2] == "Deposit"
    assert entry[3] == 500.00
    assert entry[4] == 0.00
    assert entry[5] == 1500.00


def test_multiple_transactions(bank_account):
    tx_date1 = date(2025, 11, 8)
    tx_date2 = date(2025, 11, 9)

    bank_account.make_a_transaction(tx_date1, "Deposit", credit=MinorUnit(500_00), debit=MinorUnit(0))
    bank_account.make_a_transaction(tx_date2, "Withdrawal", credit=MinorUnit(0), debit=MinorUnit(200_00))

    ledger = bank_account.raw_copy_ledger
    assert len(ledger) == 3
    assert ledger[1][5] == 1500.00
    assert ledger[2][5] == 1300.00


def test_zero_transaction(bank_account):
    tx_date = date(2025, 11, 8)
    bank_account.make_a_transaction(tx_date, "No Change", credit=MinorUnit(0), debit=MinorUnit(0))
    ledger = bank_account.raw_copy_ledger
    assert ledger[1][5] == 1000.00
