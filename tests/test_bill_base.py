from datetime import date

import pytest

from src.finance_planning_tool.models.core import (
    AccountType,
    StandardLedgerRow,
)


def test_account_name(bill_base):
    assert bill_base.account_name == "Test Bill"


def test_account_type(bill_base):
    assert bill_base.account_type == AccountType.REOCCURRING


def test_ledger_starts_empty(bill_base):
    assert len(bill_base.raw_copy_ledger) == 0


def test_ledger_col_count(bill_base):
    assert bill_base.ledger_col_count == len(StandardLedgerRow.COLUMNS)


def test_ledger_header(bill_base):
    assert bill_base.ledger_header == StandardLedgerRow.COLUMNS


def test_payment_method_valid(bill_base):
    assert bill_base.payment_method == bill_base._payment_method


def test_payment_method_invalid(bill_base):
    bill_base._payment_method = None
    with pytest.raises(ValueError):
        _ = bill_base.payment_method


def test_initialize_simulation_date(bill_base, checking_account):
    bill_base.initialize_simulation_date(date(2025, 12, 1))
    assert not bill_base._trigger_days.date_triggered(date(2025, 11, 10))


def test_to_dict_raises_not_implemented(bill_base):
    with pytest.raises(NotImplementedError):
        bill_base.to_dict()


def test_from_dict_raises_not_implemented(bill_base):
    with pytest.raises(NotImplementedError):
        bill_base.from_dict({})


def test_update_payment_method(bill_base, checking_account, saving_account):
    assert bill_base.payment_method == checking_account
    bill_base.update_payment_method(saving_account)
    assert bill_base.payment_method == saving_account
