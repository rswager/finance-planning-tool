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
    assert credit_bill.account_name == "Visa"
    assert credit_bill.account_type == AccountType.REVOLVING
    assert credit_bill.loan_balance_major == MajorUnit(-1000.0)  # stored as negative (owed)
    assert credit_bill.ledger_col_count == 7
    assert len(credit_bill.raw_copy_ledger) == 0


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


def test_daily_interest_applied(credit_bill):
    credit_bill.apply_daily_interest(date(2025, 1, 5))
    assert len(credit_bill.raw_copy_ledger) == 1
    entry = credit_bill.raw_copy_ledger[-1]
    assert entry.description == "Daily Interest"
    assert entry.credit == 0
    assert entry.debit > 0


def test_make_payment_reduces_balance_and_updates_ledgers(credit_bill, bank_account):
    old_balance = credit_bill.loan_balance_minor
    bank_start = bank_account.balance_minor

    credit_bill.make_payment(date(2025, 1, 10))

    assert len(credit_bill.raw_copy_ledger) == 1
    assert credit_bill.raw_copy_ledger[-1].description == "Minimum Payment"
    assert credit_bill.loan_balance_minor == old_balance + MinorUnit.from_major(200.00)
    assert bank_account.raw_copy_ledger[-1].debit == MajorUnit(200.00)
    assert bank_account.balance_minor == bank_start - MinorUnit.from_major(200.00)


def test_payment_smaller_when_balance_less_than_minimum(bank_account):
    bill = RevolvingCreditBill(
        name_in="SmallDebt",
        balance_in=MinorUnit.from_major(50.00),
        account_type_in=AccountType.REVOLVING,
        initial_pay_date_in=date(2025, 1, 10),
        frequency_type_in=FrequencyType.MONTHLY,
        minimum_payment_in=MinorUnit.from_major(200.00),
        payment_method_in=bank_account,
        apr_rate_in=0.1,
        credit_limit_in=MinorUnit.from_major(2000.00),
    )
    bill.make_payment(date(2025, 1, 10))
    assert bill.loan_balance_minor == 0
    assert bill.raw_copy_ledger[-1].credit == MajorUnit(50.00)
    assert bank_account.raw_copy_ledger[-1].debit == MajorUnit(50.00)


def test_process_day_no_trigger(credit_bill):
    credit_bill.process_day(date(2025, 1, 5))
    assert len(credit_bill.raw_copy_ledger) == 1
    assert credit_bill.raw_copy_ledger[-1].description == "Daily Interest"


def test_process_day_trigger(credit_bill):
    credit_bill.process_day(date(2025, 1, 10))
    assert len(credit_bill.raw_copy_ledger) == 2
    descriptions = [row.description for row in credit_bill.raw_copy_ledger]
    assert "Daily Interest" in descriptions
    assert "Minimum Payment" in descriptions


def test_multiple_day_processing_until_payment(credit_bill):
    start = date(2025, 1, 1)
    for i in range(10):
        credit_bill.process_day(start + timedelta(days=i))
    assert len(credit_bill.raw_copy_ledger) == 11
