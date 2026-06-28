from datetime import date

import pytest

from finance_planning_tool.models.accounts import (
    BankAccount,
)
from finance_planning_tool.models.core import (
    AccountType,
    BankAccountLedgerRow,
    MajorUnit,
    MinorUnit,
)
from finance_planning_tool.models.persistence import (
    SerialTypeLookup,
)


def test_type_key_in_serialized_account_type(checking_account):
    assert SerialTypeLookup[checking_account.TYPE_KEY].value == BankAccount


def test_initialization(checking_account):
    assert checking_account.account_name == "Checking"
    assert checking_account.account_type == AccountType.CHECKING
    assert checking_account.ledger_col_count == 6
    assert len(checking_account.raw_copy_ledger) == 0  # empty


def test_raw_copy_ledger_is_copy(checking_account):
    ledger_copy = checking_account.raw_copy_ledger
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
    assert len(checking_account.raw_copy_ledger) == 0


def test_ledger_header(checking_account):
    assert checking_account.ledger_header == BankAccountLedgerRow.COLUMNS


def test_make_transaction_updates_ledger_and_balance(checking_account):
    tx_date = date(2025, 11, 8)
    checking_account.make_a_transaction(
        date_in=tx_date, action="Deposit", credit=MinorUnit.from_major(500.00), debit=MinorUnit(0)
    )

    ledger = checking_account.raw_copy_ledger
    assert len(ledger) == 1

    entry = ledger[0]
    assert entry.date == tx_date
    assert entry.description == "Deposit"
    assert entry.credit == MajorUnit(500.00)
    assert entry.debit == MajorUnit(0.00)
    assert entry.balance == MajorUnit(1500.00)


def test_multiple_transactions(checking_account):
    tx_date1 = date(2025, 11, 8)
    tx_date2 = date(2025, 11, 9)

    checking_account.make_a_transaction(
        date_in=tx_date1, action="Deposit", credit=MinorUnit.from_major(500.00), debit=MinorUnit(0)
    )
    checking_account.make_a_transaction(
        date_in=tx_date2, action="Withdrawal", credit=MinorUnit(0), debit=MinorUnit.from_major(200.00)
    )

    ledger = checking_account.raw_copy_ledger
    assert len(ledger) == 2
    assert ledger[0].balance == MajorUnit(1_500.00)
    assert ledger[1].balance == MajorUnit(1_300.00)


def test_zero_transaction(checking_account):
    tx_date = date(2025, 11, 8)
    checking_account.make_a_transaction(date_in=tx_date, action="No Change", credit=MinorUnit(0), debit=MinorUnit(0))
    ledger = checking_account.raw_copy_ledger
    assert ledger[0].balance == MajorUnit(1_000.00)


def test_to_dict(checking_account):
    d = checking_account.to_dict()
    assert set(d.keys()) == {"name_in", "balance_in", "account_type_in", "serial_type_in"}
    assert d["name_in"] == "Checking"
    assert d["balance_in"] == MinorUnit.from_major(1_000.00)
    assert d["account_type_in"] == AccountType.CHECKING.value
    # We assert that serial_type_in is IN SerialTypeLookup by not catching a raise
    SerialTypeLookup[d["serial_type_in"]]


def test_from_dict_round_trip(checking_account):
    reconstructed = BankAccount.from_dict(checking_account.to_dict())
    assert reconstructed.account_name == checking_account.account_name
    assert reconstructed.account_type == checking_account.account_type
    assert reconstructed.balance_minor == checking_account.balance_minor


def test_from_dict_missing_key_raises(checking_account):
    d = checking_account.to_dict()
    del d["name_in"]
    with pytest.raises(KeyError):
        BankAccount.from_dict(d)
