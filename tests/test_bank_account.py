from datetime import date

import pytest

from models.bankAccount import BankAccount
from models.enumType import AccountType
from models.ledger import BankAccountLedgerRow
from models.utils import MajorUnit, MinorUnit


@pytest.fixture
def bank_account():
    return BankAccount("Test Account", MinorUnit.from_major(1_000.00), AccountType.CHECKING)


def test_initialization(bank_account):
    assert bank_account.account_name == "Test Account"
    assert bank_account.account_type == AccountType.CHECKING
    assert bank_account.ledger_col_count == 6
    assert len(bank_account.raw_copy_ledger) == 0  # empty


def test_raw_copy_ledger_is_copy(bank_account):
    ledger_copy = bank_account.raw_copy_ledger
    ledger_copy.append(
        BankAccountLedgerRow(
            row_number=1,
            date=date(2025, 11, 8),
            description="hack",
            credit=MajorUnit(0),
            debit=MajorUnit(0),
            balance=MajorUnit(10),
        )
    )
    assert len(bank_account.raw_copy_ledger) == 0


def test_make_transaction_updates_ledger_and_balance(bank_account):
    tx_date = date(2025, 11, 8)
    bank_account.make_a_transaction(
        date_in=tx_date, action="Deposit", credit=MinorUnit.from_major(500.00), debit=MinorUnit(0)
    )

    ledger = bank_account.raw_copy_ledger
    assert len(ledger) == 1

    entry = ledger[0]
    assert entry.date == tx_date
    assert entry.description == "Deposit"
    assert entry.credit == MajorUnit(500.00)
    assert entry.debit == MajorUnit(0.00)
    assert entry.balance == MajorUnit(1500.00)


def test_multiple_transactions(bank_account):
    tx_date1 = date(2025, 11, 8)
    tx_date2 = date(2025, 11, 9)

    bank_account.make_a_transaction(
        date_in=tx_date1, action="Deposit", credit=MinorUnit.from_major(500.00), debit=MinorUnit(0)
    )
    bank_account.make_a_transaction(
        date_in=tx_date2, action="Withdrawal", credit=MinorUnit(0), debit=MinorUnit.from_major(200.00)
    )

    ledger = bank_account.raw_copy_ledger
    assert len(ledger) == 2
    assert ledger[0].balance == MajorUnit(1_500.00)
    assert ledger[1].balance == MajorUnit(1_300.00)


def test_zero_transaction(bank_account):
    tx_date = date(2025, 11, 8)
    bank_account.make_a_transaction(date_in=tx_date, action="No Change", credit=MinorUnit(0), debit=MinorUnit(0))
    ledger = bank_account.raw_copy_ledger
    assert ledger[0].balance == MajorUnit(1_000.00)
