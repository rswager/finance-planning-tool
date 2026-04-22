from datetime import date

import pytest

from models.bankAccount import BankAccount
from models.enumType import AccountType, FrequencyType
from models.financed_bill import FinancedBill
from models.utils import MinorUnit


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


def test_initialization(financed_bill, bank_account):
    assert financed_bill.account_name == "Test Loan"
    assert financed_bill.account_type == AccountType.LOAN
    assert financed_bill.ledger_col_count == 7
    assert len(financed_bill.raw_copy_ledger) == 1
    assert bank_account.balance_minor == MinorUnit.from_major(1000.00)


def test_apply_daily_interest(financed_bill):
    start_balance = financed_bill.loan_balance_major
    financed_bill.apply_daily_interest(date(2025, 11, 8))
    assert len(financed_bill.raw_copy_ledger) == 2
    entry = financed_bill.raw_copy_ledger[-1]
    assert entry[2] == "Daily Interest"
    assert abs(entry[5]) > abs(start_balance)


def test_make_payment(financed_bill, bank_account):
    initial_loan_balance = financed_bill.loan_balance_minor
    initial_bank_balance = bank_account.balance_minor

    financed_bill.make_payment(date(2025, 11, 10))

    assert financed_bill.raw_copy_ledger[-1][2] == "Minimum Payment"
    assert abs(financed_bill.loan_balance_minor) < abs(initial_loan_balance)
    assert bank_account.balance_minor < initial_bank_balance
    assert bank_account.raw_copy_ledger[-1][4] > 0


def test_process_day_no_trigger(financed_bill):
    initial_loan_balance = financed_bill.loan_balance_minor
    financed_bill.process_day(date(2025, 11, 8))
    assert len(financed_bill.raw_copy_ledger) == 2
    assert abs(financed_bill.loan_balance_minor) > abs(initial_loan_balance)


def test_process_day_with_trigger(financed_bill, bank_account):
    initial_loan_balance = financed_bill.loan_balance_minor
    initial_bank_balance = bank_account._accountInfo.balance

    financed_bill.process_day(date(2025, 11, 10))

    assert len(financed_bill.raw_copy_ledger) == 3
    assert abs(financed_bill.loan_balance_minor) < abs(initial_loan_balance)
    assert bank_account.balance_minor < initial_bank_balance
    assert bank_account.raw_copy_ledger[-1][4] > 0


def test_min_payment_capped(financed_bill, bank_account):
    financed_bill._accountInfo._balance = MinorUnit.from_major(-30.00)
    financed_bill.make_payment(date(2025, 11, 10))

    assert financed_bill.loan_balance_minor == 0
    assert bank_account.raw_copy_ledger[-1][4] == 30
