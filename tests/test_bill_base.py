from datetime import date

import pytest

from models.bills.bill_base import BillBase
from models.core.enum_type import AccountType, FrequencyType
from models.core.ledger import StandardLedgerRow
from models.core.utils import MinorUnit


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


def test_initialize_simulation_date(checking_account):
    bill = BillBase(
        name_in="Test Bill",
        balance_in=MinorUnit(0),
        minimum_payment_in=MinorUnit.from_major(50.00),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 10),
        frequency_type_in=FrequencyType.WEEKLY,
        payment_method_in=checking_account,
        ledger_row_type=StandardLedgerRow,
    )
    bill.initialize_simulation_date(date(2025, 12, 1))
    assert not bill._trigger_days.date_triggered(date(2025, 11, 10))


def test_to_dict_raises_not_implemented(bill_base):
    with pytest.raises(NotImplementedError):
        bill_base.to_dict()


def test_from_dict_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        BillBase.from_dict({})


def test_update_payment_method(bill_base, checking_account, saving_account):
    assert bill_base.payment_method == checking_account
    bill_base.update_payment_method(saving_account)
    assert bill_base.payment_method == saving_account
