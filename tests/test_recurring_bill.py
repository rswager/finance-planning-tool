from datetime import date

import pytest

from models.bankAccount import BankAccount
from models.enumType import AccountType, FrequencyType
from models.recurring_bill import RecurringBill
from models.utils import cents_to_dollars, dollars_to_cents, money_cents, money_dollars


@pytest.fixture
def bank_account():
    return BankAccount("Checking", dollars_to_cents(money_dollars(1_000.00)), AccountType.CHECKING)


@pytest.fixture
def recurring_bill(bank_account):
    return RecurringBill(
        name_in="Electric Bill",
        minimum_payment_in=dollars_to_cents(money_dollars(100.00)),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 10),
        frequency_type_in=FrequencyType.WEEKLY,
        payment_method_in=bank_account,
    )


# --- Initialization ---
def test_initialization(recurring_bill, bank_account):
    assert recurring_bill.account_name == "Electric Bill"
    assert recurring_bill.account_type == AccountType.REOCCURRING
    # Ledger should have only the header
    assert recurring_bill.ledger_col_count == 5
    assert len(recurring_bill.raw_copy_ledger) == 1
    # Bank account balance unchanged initially
    assert bank_account.balance_dollars == money_dollars(1_000.00)


# --- Make payment ---
def test_make_payment_updates_ledger_and_bank_account(recurring_bill, bank_account):
    pay_date = date(2025, 11, 10)
    initial_bank_balance = bank_account._accountInfo.balance

    recurring_bill.make_payment(pay_date)

    # RecurringBill ledger updated
    assert len(recurring_bill.raw_copy_ledger) == 2
    entry = recurring_bill.raw_copy_ledger[-1]
    assert entry[2] == "Minimum Payment"
    assert entry[3] == cents_to_dollars(money_cents(recurring_bill._minimum_payment))

    # BankAccount ledger updated
    bank_entry = bank_account.raw_copy_ledger[-1]
    assert bank_entry[2] == "Electric Bill-Payment"
    assert bank_entry[4] == cents_to_dollars(money_cents(recurring_bill._minimum_payment))
    # Bank balance decreased
    assert bank_account._accountInfo.balance == initial_bank_balance - recurring_bill._minimum_payment


# --- Process a non-trigger day ---
def test_process_day_no_trigger(recurring_bill, bank_account):
    normal_day = date(2025, 11, 9)  # day before trigger
    recurring_bill.process_day(normal_day)

    # No ledger entries should be added
    assert len(recurring_bill.raw_copy_ledger) == 1
    assert len(bank_account.raw_copy_ledger) == 1


# --- Process a trigger day ---
def test_process_day_trigger(recurring_bill, bank_account):
    trigger_day = date(2025, 11, 10)
    recurring_bill.process_day(trigger_day)

    # Ledger entries added
    assert len(recurring_bill.raw_copy_ledger) == 2
    assert recurring_bill.raw_copy_ledger[-1][2] == "Minimum Payment"
    # Bank account debited correctly
    assert bank_account.raw_copy_ledger[-1][4] == cents_to_dollars(money_cents(recurring_bill._minimum_payment))
