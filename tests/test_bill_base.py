from datetime import date

import pytest

from models.accounts.bank_account import BankAccount
from models.bills.bill_base import BillBase
from models.core.enum_type import AccountType, FrequencyType
from models.core.ledger import StandardLedgerRow
from models.core.utils import MinorUnit


@pytest.fixture
def bank_account():
    return BankAccount("Checking", MinorUnit.from_major(1_000.00), AccountType.CHECKING)


@pytest.fixture
def saving_account():
    return BankAccount("Saving", MinorUnit.from_major(1_000.00), AccountType.SAVINGS)


@pytest.fixture
def bill(bank_account):
    return BillBase(
        name_in="Test Bill",
        balance_in=MinorUnit(0),
        minimum_payment_in=MinorUnit.from_major(50.00),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 10),
        frequency_type_in=FrequencyType.WEEKLY,
        payment_method_in=bank_account,
        ledger_row_type=StandardLedgerRow,
    )


def test_account_name(bill):
    assert bill.account_name == "Test Bill"


def test_account_type(bill):
    assert bill.account_type == AccountType.REOCCURRING


def test_ledger_starts_empty(bill):
    assert len(bill.raw_copy_ledger) == 0


def test_ledger_col_count(bill):
    assert bill.ledger_col_count == len(StandardLedgerRow.COLUMNS)


def test_ledger_header(bill):
    assert bill.ledger_header == StandardLedgerRow.COLUMNS


def test_payment_method_valid(bill):
    assert bill.payment_method == bill._payment_method


def test_payment_method_invalid(bill):
    bill._payment_method = None
    with pytest.raises(ValueError):
        _ = bill.payment_method


def test_initialize_simulation_date(bank_account):
    bill = BillBase(
        name_in="Test Bill",
        balance_in=MinorUnit(0),
        minimum_payment_in=MinorUnit.from_major(50.00),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 10),
        frequency_type_in=FrequencyType.WEEKLY,
        payment_method_in=bank_account,
        ledger_row_type=StandardLedgerRow,
    )
    bill.initialize_simulation_date(date(2025, 12, 1))
    assert not bill._trigger_days.date_triggered(date(2025, 11, 10))


def test_to_dict_raises_not_implemented(bill):
    with pytest.raises(NotImplementedError):
        bill.to_dict()


def test_from_dict_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        BillBase.from_dict({}, {})


def test_update_payment_method(bill, bank_account, saving_account):
    assert bill.payment_method == bank_account
    bill.update_payment_method(saving_account)
    assert bill.payment_method == saving_account


def test_update_payment_method_null(bill, bank_account):
    bill.update_payment_method(None)
    # Cannot call property without ValueError
    bill._payment_method = None
