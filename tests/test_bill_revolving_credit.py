from datetime import date, timedelta

import pytest

from models.accounts.bank_account import BankAccount
from models.bills.bill_revolving_credit import RevolvingCreditBill
from models.core.enum_type import AccountType, FrequencyType, SerialAccountType
from models.core.utils import MajorUnit, MinorUnit


@pytest.fixture
def bank_account():
    return BankAccount("Checking", MinorUnit.from_major(5000.00), AccountType.CHECKING)


@pytest.fixture
def credit_bill(bank_account):
    return RevolvingCreditBill(
        name_in="Visa",
        balance_in=MinorUnit.from_major(1000.00),
        account_type_in=AccountType.REVOLVING,
        initial_pay_date_in=date(2025, 1, 10),
        frequency_type_in=FrequencyType.MONTHLY,
        minimum_payment_in=MinorUnit.from_major(200.00),
        payment_method_in=bank_account,
        apr_rate_in=0.12,
        credit_limit_in=MinorUnit.from_major(5000.00),
    )


def test_type_key_in_serialized_account_type(credit_bill):
    assert SerialAccountType[credit_bill.TYPE_KEY] == RevolvingCreditBill


def test_initialization(credit_bill):
    assert credit_bill.loan_balance_major == MajorUnit(-1000.0)
    assert credit_bill.ledger_col_count == 7


def test_credit_limit_not_exceeded(credit_bill):
    assert credit_bill.exceeded_credit_limit is False


def test_credit_limit_exceeded(bank_account):
    bill = RevolvingCreditBill(
        name_in="Card",
        balance_in=MinorUnit.from_major(6000.00),
        account_type_in=AccountType.REVOLVING,
        initial_pay_date_in=date(2025, 1, 10),
        frequency_type_in=FrequencyType.MONTHLY,
        minimum_payment_in=MinorUnit.from_major(200.00),
        payment_method_in=bank_account,
        apr_rate_in=0.15,
        credit_limit_in=MinorUnit.from_major(5000.00),
    )
    assert bill.exceeded_credit_limit is True


def test_multiple_day_processing_until_payment(credit_bill):
    start = date(2025, 1, 1)
    for i in range(10):
        credit_bill.process_day(start + timedelta(days=i))
    assert len(credit_bill.raw_copy_ledger) == 11


def test_to_dict(credit_bill, bank_account):
    d = credit_bill.to_dict()
    assert set(d.keys()) == {
        "name_in",
        "balance_in",
        "account_type_in",
        "initial_pay_date_in",
        "frequency_type_in",
        "minimum_payment_in",
        "payment_method_in",
        "apr_rate_in",
        "credit_limit_in",
        "round_up",
        "serial_type_in",
    }
    assert d["name_in"] == "Visa"
    assert d["balance_in"] == -int(MinorUnit.from_major(1000.00))
    assert d["account_type_in"] == AccountType.REVOLVING.value
    assert d["initial_pay_date_in"] == "2025-01-10"
    assert d["frequency_type_in"] == FrequencyType.MONTHLY.value
    assert d["minimum_payment_in"] == int(MinorUnit.from_major(200.00))
    assert d["payment_method_in"] == bank_account.account_name
    assert d["apr_rate_in"] == 0.12
    assert d["credit_limit_in"] == int(MinorUnit.from_major(5000.00))
    assert d["round_up"] is False
    assert d["serial_type_in"] == SerialAccountType.bill_revolving_credit


def test_from_dict_round_trip(credit_bill, bank_account):
    registry = {bank_account.account_name: bank_account}
    reconstructed = RevolvingCreditBill.from_dict(credit_bill.to_dict(), registry)
    assert reconstructed.to_dict() == credit_bill.to_dict()


def test_from_dict_missing_key_raises(credit_bill, bank_account):
    d = credit_bill.to_dict()
    del d["credit_limit_in"]
    with pytest.raises(KeyError):
        RevolvingCreditBill.from_dict(d, {bank_account.account_name: bank_account})
