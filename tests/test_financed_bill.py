import pytest
from datetime import date
from models.financed_bill import FinancedBill
from models.enumType import AccountType, FrequencyType
from models.bankAccount import BankAccount
from models.utils import dollars_to_cents, money_dollars


@pytest.fixture
def bank_account():
    return BankAccount("Checking", dollars_to_cents(money_dollars(1000.00)), AccountType.CHECKING)

@pytest.fixture
def financed_bill(bank_account):
    return FinancedBill(
        name_in="Test Loan",
        balance_in=dollars_to_cents(money_dollars(500.00)),
        account_type_in=AccountType.LOAN,
        initial_pay_date_in=date(2025, 11, 10),
        frequency_type_in=FrequencyType.WEEKLY,
        minimum_payment_in=dollars_to_cents(money_dollars(50.00)),
        payment_method_in=bank_account,
        apr_rate_in=0.05
    )

# --- Initialization ---
def test_initialization(financed_bill, bank_account):
    assert financed_bill.account_name == "Test Loan"
    assert financed_bill.account_type == AccountType.LOAN
    # Ledger should have only header
    assert financed_bill.ledger_col_count == 7
    assert len(financed_bill.raw_copy_ledger) == 1
    # Bank account balance unchanged
    assert bank_account.balance_cents == dollars_to_cents(money_dollars(1000.00))

# --- Daily interest application ---
def test_apply_daily_interest(financed_bill):
    start_balance = financed_bill.loan_balance_dollars
    test_date = date(2025, 11, 8)
    financed_bill.apply_daily_interest(test_date)
    # Ledger should have header + 1 entry
    assert len(financed_bill.raw_copy_ledger) == 2
    entry = financed_bill.raw_copy_ledger[-1]
    assert entry[2] == "Daily Interest"
    # Balance should increase by interest
    assert abs(entry[5]) > abs(start_balance)

# --- Minimum payment application ---
def test_make_payment(financed_bill, bank_account):
    test_date = date(2025, 11, 10)
    initial_loan_balance = financed_bill.loan_balance_cents
    initial_bank_balance = bank_account.balance_cents

    financed_bill.make_payment(test_date)

    # Ledger should have 2 entries for the payment: loan + bank
    assert financed_bill.raw_copy_ledger[-1][2] == "Minimum Payment"
    # Loan balance reduced
    assert abs(financed_bill.loan_balance_cents) < abs(initial_loan_balance)
    # Bank account balance reduced
    assert bank_account.balance_cents < initial_bank_balance
    # Bank account recorded transaction
    assert bank_account.raw_copy_ledger[-1][4] > 0  # debit recorded

# --- Process a day that is not a trigger day ---
def test_process_day_no_trigger(financed_bill):
    test_date = date(2025, 11, 8)
    initial_loan_balance = financed_bill.loan_balance_cents
    financed_bill.process_day(test_date)
    # Only interest applied
    assert len(financed_bill.raw_copy_ledger) == 2
    assert abs(financed_bill.loan_balance_cents) > abs(initial_loan_balance)

# --- Process a trigger day (payment day) ---
def test_process_day_with_trigger(financed_bill, bank_account):
    # Set date to the initial pay date (trigger)
    trigger_date = date(2025, 11, 10)
    initial_loan_balance = financed_bill.loan_balance_cents
    initial_bank_balance = bank_account._accountInfo.balance

    financed_bill.process_day(trigger_date)

    # Loan ledger: interest + payment
    assert len(financed_bill.raw_copy_ledger) == 3
    # Loan balance decreased
    assert abs(financed_bill.loan_balance_cents) < abs(initial_loan_balance)
    # Bank account balance reduced
    assert bank_account.balance_cents < initial_bank_balance
    # Bank account recorded transaction
    assert bank_account.raw_copy_ledger[-1][4] > 0  # debit recorded

# --- Minimum payment capped at remaining balance ---
def test_min_payment_capped(financed_bill, bank_account):
    # Set loan balance smaller than minimum payment
    financed_bill._accountInfo._balance = dollars_to_cents(money_dollars(-30.00))  # small negative balance
    test_date = date(2025, 11, 10)

    financed_bill.make_payment(test_date)

    # Ledger should reduce balance to 0
    assert financed_bill.loan_balance_cents == 0
    # Bank account debited by 30, not 50
    assert bank_account.raw_copy_ledger[-1][4] == 30
