from datetime import date

import pytest

from models.accounts.bank_account import BankAccount
from models.bills.bill_financed import FinancedBill
from models.core.enum_type import AccountType, FrequencyType, SerialAccountType
from models.core.utils import MinorUnit


@pytest.fixture
def bank_account():
    return BankAccount("Checking", MinorUnit.from_major(1000.00), AccountType.CHECKING)


@pytest.fixture
def financed_bill(bank_account):
    return FinancedBill(
        name_in="Test Loan",
        balance_in=MinorUnit.from_major(500.00),
        account_type_in=AccountType.LOAN,
        initial_pay_date_in=date(2025, 11, 10),
        frequency_type_in=FrequencyType.WEEKLY,
        minimum_payment_in=MinorUnit.from_major(50.00),
        payment_method_in=bank_account,
        apr_rate_in=0.05,
    )


def test_type_key_in_serialized_account_type(financed_bill):
    assert SerialAccountType[financed_bill.TYPE_KEY] == FinancedBill


def test_initialization(financed_bill, bank_account):
    assert financed_bill.ledger_col_count == 7
    assert bank_account.balance_minor == MinorUnit.from_major(1_000.00)


def test_apply_daily_interest(financed_bill):
    start_balance = financed_bill.loan_balance_major
    financed_bill.apply_daily_interest(date(2025, 11, 8))
    assert len(financed_bill.raw_copy_ledger) == 1
    entry = financed_bill.raw_copy_ledger[-1]
    assert entry.description == "Daily Interest"
    assert abs(entry.balance) > abs(start_balance)


def test_make_payment(financed_bill, bank_account):
    initial_loan_balance = financed_bill.loan_balance_minor
    initial_bank_balance = bank_account.balance_minor

    financed_bill.make_payment(date(2025, 11, 10))

    assert financed_bill.raw_copy_ledger[-1].description == "Minimum Payment"
    assert abs(financed_bill.loan_balance_minor) < abs(initial_loan_balance)
    assert bank_account.balance_minor < initial_bank_balance
    assert bank_account.raw_copy_ledger[-1].debit > 0


def test_process_day_no_trigger(financed_bill):
    initial_loan_balance = financed_bill.loan_balance_minor
    financed_bill.process_day(date(2025, 11, 8))
    assert len(financed_bill.raw_copy_ledger) == 1
    assert abs(financed_bill.loan_balance_minor) > abs(initial_loan_balance)


def test_process_day_with_trigger(financed_bill, bank_account):
    initial_loan_balance = financed_bill.loan_balance_minor
    initial_bank_balance = bank_account.balance_minor

    financed_bill.process_day(date(2025, 11, 10))

    assert len(financed_bill.raw_copy_ledger) == 2
    assert abs(financed_bill.loan_balance_minor) < abs(initial_loan_balance)
    assert bank_account.balance_minor < initial_bank_balance
    assert bank_account.raw_copy_ledger[-1].debit > 0


def test_min_payment_capped(financed_bill, bank_account):
    financed_bill._accountInfo._balance = MinorUnit.from_major(-30.00)
    financed_bill.make_payment(date(2025, 11, 10))

    assert financed_bill.loan_balance_minor == 0
    assert bank_account.raw_copy_ledger[-1].debit == 30


def test_to_dict(financed_bill, bank_account):
    d = financed_bill.to_dict()
    assert set(d.keys()) == {
        "name_in",
        "balance_in",
        "account_type_in",
        "initial_pay_date_in",
        "frequency_type_in",
        "minimum_payment_in",
        "payment_method_in",
        "apr_rate_in",
        "round_up",
        "serial_type_in",
    }
    assert d["name_in"] == "Test Loan"
    assert d["balance_in"] == -int(MinorUnit.from_major(500.00))
    assert d["account_type_in"] == AccountType.LOAN.value
    assert d["initial_pay_date_in"] == "2025-11-10"
    assert d["frequency_type_in"] == FrequencyType.WEEKLY.value
    assert d["minimum_payment_in"] == int(MinorUnit.from_major(50.00))
    assert d["payment_method_in"] == bank_account.account_name
    assert d["apr_rate_in"] == 0.05
    assert d["round_up"] is False
    assert d["serial_type_in"] == SerialAccountType.bill_financed


def test_from_dict_round_trip(financed_bill, bank_account):
    registry = {bank_account.account_name: bank_account}
    reconstructed = FinancedBill.from_dict(financed_bill.to_dict(), registry)
    assert reconstructed.to_dict() == financed_bill.to_dict()


def test_from_dict_missing_key_raises(financed_bill, bank_account):
    d = financed_bill.to_dict()
    del d["apr_rate_in"]
    with pytest.raises(KeyError):
        FinancedBill.from_dict(d, {bank_account.account_name: bank_account})
