import pytest
from datetime import date, timedelta
from models.revolving_credit_bill import RevolvingCreditBill
from models.bankAccount import BankAccount
from models.enumType import AccountType, FrequencyType

# -------------------------------------------------------
# Fixtures
# -------------------------------------------------------

@pytest.fixture
def bank_account():
    return BankAccount("Checking", 5000.0, AccountType.CHECKING)

@pytest.fixture
def credit_bill(bank_account):
    # Starting balance = $1000 owed
    return RevolvingCreditBill(
        name_in="Visa",
        balance_in=1000.0,
        account_type_in=AccountType.REVOLVING,
        initial_pay_date_in=date(2025, 1, 10),
        frequency_type_in=FrequencyType.MONTHLY,
        minimum_payment_in=200.0,
        payment_method_in=bank_account,
        apr_rate_in=0.12,          # 12% APR
        credit_limit_in=5000.0
    )

# -------------------------------------------------------
# Initialization Tests
# -------------------------------------------------------

def test_initialization(credit_bill):
    assert credit_bill.account_name == "Visa"
    assert credit_bill.account_type == AccountType.REVOLVING
    assert credit_bill.loan_balance == -1000.0  # stored as negative (owed)
    assert credit_bill.ledger_col_count == 7
    assert len(credit_bill.raw_copy_ledger) == 1  # header only


# -------------------------------------------------------
# Credit Limit Tests
# -------------------------------------------------------

def test_credit_limit_not_exceeded(credit_bill):
    assert credit_bill.exceeded_credit_limit is False

def test_credit_limit_exceeded(bank_account):
    bill = RevolvingCreditBill(
        name_in="Card",
        balance_in=6000.0,   # over the 5000 limit
        account_type_in=AccountType.REVOLVING,
        initial_pay_date_in=date(2025, 1, 10),
        frequency_type_in=FrequencyType.MONTHLY,
        minimum_payment_in=200.0,
        payment_method_in=bank_account,
        apr_rate_in=0.15,
        credit_limit_in=5000.0
    )
    assert bill.exceeded_credit_limit is True


# -------------------------------------------------------
# Daily Interest Tests
# -------------------------------------------------------

def test_daily_interest_applied(credit_bill):
    day = date(2025, 1, 5)
    credit_bill.apply_daily_interest(day)

    # Ledger now has header + 1 entry
    assert len(credit_bill.raw_copy_ledger) == 2

    entry = credit_bill.raw_copy_ledger[-1]
    assert entry[2] == "Daily Interest"
    assert entry[3] == 0      # credit
    assert entry[4] > 0       # debit (interest added)


# -------------------------------------------------------
# Minimum Payment Tests
# -------------------------------------------------------

def test_make_payment_reduces_balance_and_updates_ledgers(credit_bill, bank_account):
    pay_date = date(2025, 1, 10)
    old_balance = credit_bill.loan_balance
    bank_start = bank_account._accountInfo.balance

    credit_bill.make_payment(pay_date)

    # Ledger updated
    assert len(credit_bill.raw_copy_ledger) == 2
    entry = credit_bill.raw_copy_ledger[-1]
    assert entry[2] == "Minimum Payment"

    # Balance increases (toward zero, because negative)
    assert credit_bill.loan_balance == old_balance + 200.0

    # Bank account was charged
    bank_entry = bank_account.raw_copy_ledger[-1]
    assert bank_entry[4] == 200.0
    assert bank_account._accountInfo.balance == bank_start - 200.0


def test_payment_smaller_when_balance_less_than_minimum(bank_account):
    bill = RevolvingCreditBill(
        name_in="SmallDebt",
        balance_in=50.0,     # only owes $50
        account_type_in=AccountType.REVOLVING,
        initial_pay_date_in=date(2025, 1, 10),
        frequency_type_in=FrequencyType.MONTHLY,
        minimum_payment_in=200.0,
        payment_method_in=bank_account,
        apr_rate_in=0.1,
        credit_limit_in=2000.0
    )

    bill.make_payment(date(2025, 1, 10))

    # Only charged $50
    assert bill.loan_balance == 0
    assert bill.raw_copy_ledger[-1][3] == 50.0
    assert bank_account.raw_copy_ledger[-1][4] == 50.0


# -------------------------------------------------------
# Process Day Tests
# -------------------------------------------------------

def test_process_day_no_trigger(credit_bill):
    non_trigger_day = date(2025, 1, 5)
    credit_bill.process_day(non_trigger_day)

    # Only daily interest applied
    assert len(credit_bill.raw_copy_ledger) == 2
    assert credit_bill.raw_copy_ledger[-1][2] == "Daily Interest"


def test_process_day_trigger(credit_bill):
    trigger_day = date(2025, 1, 10)
    credit_bill.process_day(trigger_day)

    # Interest + Payment recorded
    assert len(credit_bill.raw_copy_ledger) == 3

    descriptions = [row[2] for row in credit_bill.raw_copy_ledger]
    assert "Daily Interest" in descriptions
    assert "Minimum Payment" in descriptions


def test_multiple_day_processing_until_payment(credit_bill):
    """
    Simulate 10 days of processing including interest accumulation
    and a payment on the trigger day.
    """
    start = date(2025, 1, 1)
    for i in range(10):
        credit_bill.process_day(start + timedelta(days=i))

    # Should have 9 days of interest + 1 day interest + payment + Header = 12 ledger rows
    assert len(credit_bill.raw_copy_ledger) == 12
