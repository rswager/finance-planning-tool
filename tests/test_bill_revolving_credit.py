from datetime import date, timedelta

import pytest

from models.bank_account import BankAccount
from models.bill_revolving_credit import RevolvingCreditBill
from models.enum_type import AccountType, FrequencyType
from models.utils import MajorUnit, MinorUnit


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
