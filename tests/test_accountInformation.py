import pytest

from models.accountInformation import AccountInformation
from models.enumType import AccountType
from models.utils import dollars_to_cents, money_cents, money_dollars


@pytest.fixture
def sample_account():
    """Create a sample account fixture."""
    return AccountInformation("Primary_Checking", dollars_to_cents(money_dollars(100.00)), AccountType.CHECKING)


def test_initial_balance_and_attributes(sample_account):
    """Verify initial values are set correctly."""
    assert sample_account.account_name == "Primary_Checking"
    assert sample_account.account_type == AccountType.CHECKING
    assert sample_account.balance == dollars_to_cents(money_dollars(100.00))


def test_update_balance_adds_amount(sample_account):
    """Ensure update_balance correctly increases balance."""
    sample_account.update_balance(credit=dollars_to_cents(money_dollars(25.50)))
    assert sample_account.balance == dollars_to_cents(money_dollars(125.50))


def test_update_balance_handles_negative_transactions(sample_account):
    """Ensure update_balance correctly handles negative (withdrawal) transactions."""
    sample_account.update_balance(debit=dollars_to_cents(money_dollars(40.25)))
    assert sample_account.balance == dollars_to_cents(money_dollars(59.75))


def test_balance_property_is_money_cents(sample_account):
    """Ensure balance is always stored as a money_cents."""
    assert type(sample_account.balance) is int


def test_update_balance_multiple_times(sample_account):
    """Ensure cumulative balance updates correctly."""
    sample_account.update_balance(credit=dollars_to_cents(money_dollars(20.00)))
    sample_account.update_balance(credit=dollars_to_cents(money_dollars(30.00)))
    sample_account.update_balance(debit=dollars_to_cents(money_dollars(10.00)))
    assert sample_account.balance == dollars_to_cents(money_dollars(140.00))


def test_balance_independent_of_bill_name_and_type():
    """Ensure name/type don’t affect balance behavior."""
    acc = AccountInformation("Electric", dollars_to_cents(money_dollars(200.00)), AccountType.REOCCURRING)
    acc.update_balance(debit=dollars_to_cents(money_dollars(50.00)))
    assert acc.balance == dollars_to_cents(money_dollars(150.00))
    assert acc.account_name == "Electric"
    assert acc.account_type == AccountType.REOCCURRING


def test_is_overdrafted_initial_false(sample_account):
    """Account with positive balance is not overdrafted."""
    assert sample_account.is_overdrafted is False


def test_is_overdrafted_true_when_negative_balance(sample_account):
    """Account with negative balance is overdrafted."""
    sample_account.update_balance(debit=dollars_to_cents(money_dollars(150.00)))  # bring balance below zero
    assert sample_account.balance < money_cents(0)
    assert sample_account.is_overdrafted is True


def test_is_overdrafted_false_when_balance_zero():
    """Zero balance is not considered overdrafted."""
    acc = AccountInformation("Utility", money_cents(0), AccountType.REOCCURRING)
    assert acc.is_overdrafted is False


def test_is_overdrafted_property_updates_with_balance(sample_account):
    """Overdrafted property reflects changes to balance dynamically."""
    # Initially positive
    assert sample_account.is_overdrafted is False

    # Withdraw to negative
    sample_account.update_balance(debit=dollars_to_cents(money_dollars(200.00)))
    assert sample_account.is_overdrafted is True

    # Deposit back to positive
    sample_account.update_balance(credit=dollars_to_cents(money_dollars(300.00)))
    assert sample_account.is_overdrafted is False


@pytest.mark.parametrize(
    "name,balance,type,expected",
    [
        ("Primary_Checking", dollars_to_cents(money_dollars(-100.00)), AccountType.CHECKING, True),
        ("Primary_Checking", dollars_to_cents(money_dollars(100.00)), AccountType.CHECKING, False),
        ("Primary_Checking", dollars_to_cents(money_dollars(0)), AccountType.CHECKING, False),
        ("Primary_Savings", dollars_to_cents(money_dollars(-100.00)), AccountType.SAVINGS, True),
        ("Primary_Savings", dollars_to_cents(money_dollars(100.00)), AccountType.SAVINGS, False),
        ("Primary_Savings", dollars_to_cents(money_dollars(0)), AccountType.SAVINGS, False),
        ("Netflix", dollars_to_cents(money_dollars(-100.00)), AccountType.SUBSCRIPTION, False),
        ("Netflix", dollars_to_cents(money_dollars(100.00)), AccountType.SUBSCRIPTION, False),
        ("Netflix", dollars_to_cents(money_dollars(0)), AccountType.SUBSCRIPTION, False),
        ("Utilities", dollars_to_cents(money_dollars(-100.00)), AccountType.REOCCURRING, False),
        ("Utilities", dollars_to_cents(money_dollars(100.00)), AccountType.REOCCURRING, False),
        ("Utilities", dollars_to_cents(money_dollars(0)), AccountType.REOCCURRING, False),
        ("Car-Loan", dollars_to_cents(money_dollars(-100.00)), AccountType.LOAN, False),
        ("Car-Loan", dollars_to_cents(money_dollars(100.00)), AccountType.LOAN, False),
        ("Car-Loan", dollars_to_cents(money_dollars(0)), AccountType.LOAN, False),
        ("Discover", dollars_to_cents(money_dollars(-100.00)), AccountType.REVOLVING, False),
        ("Discover", dollars_to_cents(money_dollars(100.00)), AccountType.REVOLVING, False),
        ("Discover", dollars_to_cents(money_dollars(0)), AccountType.REVOLVING, False),
    ],
)
def test_is_overdrafted(name, balance, type, expected):
    account = AccountInformation(name, balance, type)
    assert account.is_overdrafted == expected
