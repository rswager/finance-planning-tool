from datetime import date

import pytest

from models.bank_account import BankAccount
from models.bill_recurring import RecurringBill
from models.enum_type import AccountType, FrequencyType
from models.utils import MajorUnit, MinorUnit


@pytest.fixture
def bank_account():
    return BankAccount("Checking", MinorUnit.from_major(1_000.00), AccountType.CHECKING)


@pytest.fixture
def recurring_bill(bank_account):
    return RecurringBill(
        name_in="Electric Bill",
        minimum_payment_in=MinorUnit.from_major(100.00),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 10),
        frequency_type_in=FrequencyType.WEEKLY,
        payment_method_in=bank_account,
    )


def test_initialization(recurring_bill, bank_account):
    assert recurring_bill.ledger_col_count == 6
    assert bank_account.balance_major == MajorUnit(1_000.00)


def test_make_payment_updates_ledger_and_bank_account(recurring_bill, bank_account):
    initial_bank_balance = bank_account.balance_minor

    recurring_bill.make_payment(date(2025, 11, 10))

    assert len(recurring_bill.raw_copy_ledger) == 1
    entry = recurring_bill.raw_copy_ledger[-1]
    assert entry.description == "Minimum Payment"
    assert entry.credit == recurring_bill._minimum_payment.to_major()

    bank_entry = bank_account.raw_copy_ledger[-1]
    assert bank_entry.description == "Electric Bill-Payment"
    assert bank_entry.debit == recurring_bill._minimum_payment.to_major()
    assert bank_account.balance_minor == initial_bank_balance - recurring_bill._minimum_payment


def test_process_day_no_trigger(recurring_bill, bank_account):
    recurring_bill.process_day(date(2025, 11, 9))
    assert len(recurring_bill.raw_copy_ledger) == 0
    assert len(bank_account.raw_copy_ledger) == 0


def test_process_day_trigger(recurring_bill, bank_account):
    recurring_bill.process_day(date(2025, 11, 10))
    assert len(recurring_bill.raw_copy_ledger) == 1
    assert recurring_bill.raw_copy_ledger[-1].description == "Minimum Payment"
    assert bank_account.raw_copy_ledger[-1].debit == recurring_bill._minimum_payment.to_major()


def test_to_dict(recurring_bill, bank_account):
    d = recurring_bill.to_dict()
    assert set(d.keys()) == {
        "name_in",
        "minimum_payment_in",
        "account_type_in",
        "initial_pay_date_in",
        "frequency_type_in",
        "payment_method_in",
        "round_up",
    }
    assert d["name_in"] == "Electric Bill"
    assert d["minimum_payment_in"] == int(MinorUnit.from_major(100.00))
    assert d["account_type_in"] == AccountType.REOCCURRING.value
    assert d["initial_pay_date_in"] == "2025-11-10"
    assert d["frequency_type_in"] == FrequencyType.WEEKLY.value
    assert d["payment_method_in"] == bank_account.account_name
    assert d["round_up"] is False


def test_from_dict_round_trip(recurring_bill, bank_account):
    registry = {bank_account.account_name: bank_account}
    reconstructed = RecurringBill.from_dict(recurring_bill.to_dict(), registry)
    assert reconstructed.to_dict() == recurring_bill.to_dict()


def test_from_dict_missing_key_raises(recurring_bill, bank_account):
    d = recurring_bill.to_dict()
    del d["minimum_payment_in"]
    with pytest.raises(KeyError):
        RecurringBill.from_dict(d, {bank_account.account_name: bank_account})
