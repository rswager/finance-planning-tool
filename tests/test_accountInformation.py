from models.accountInformation import AccountInformation
from models.enumType import AccountType
import pytest
from models.utils import money_dollars,money_cents


@pytest.fixture
def sample_account():
    """Create a sample account fixture."""
    return AccountInformation("Primary_Checking", money_cents(100_00), AccountType.CHECKING)


def test_initial_balance_and_attributes(sample_account):
    """Verify initial values are set correctly."""
    assert sample_account.account_name == "Primary_Checking"
    assert sample_account.account_type == AccountType.CHECKING
    assert sample_account.balance == money_cents(100_00)


def test_update_balance_adds_amount(sample_account):
    """Ensure update_balance correctly increases balance."""
    sample_account.update_balance(credit=money_cents(25_50))
    assert sample_account.balance == money_cents(125_50)


def test_update_balance_handles_negative_transactions(sample_account):
    """Ensure update_balance correctly handles negative (withdrawal) transactions."""
    sample_account.update_balance(debit=money_cents(40_25))
    assert sample_account.balance == money_cents(59_75)


def test_balance_property_is_money_cents(sample_account):
    """Ensure balance is always stored as a money_cents."""
    assert type(sample_account.balance) == int


def test_update_balance_multiple_times(sample_account):
    """Ensure cumulative balance updates correctly."""
    sample_account.update_balance(credit=money_cents(20_00))
    sample_account.update_balance(credit=money_cents(30_00))
    sample_account.update_balance(debit=money_cents(10_00))
    assert sample_account.balance == money_cents(140_00)


def test_balance_independent_of_bill_name_and_type():
    """Ensure name/type don’t affect balance behavior."""
    acc = AccountInformation("Electric", money_cents(200_00), AccountType.REOCCURRING)
    acc.update_balance(debit=money_cents(50_00))
    assert acc.balance == money_cents(150_00)
    assert acc.account_name == "Electric"
    assert acc.account_type == AccountType.REOCCURRING

def test_is_overdrafted_initial_false(sample_account):
    """Account with positive balance is not overdrafted."""
    assert sample_account.is_overdrafted is False


def test_is_overdrafted_true_when_negative_balance(sample_account):
    """Account with negative balance is overdrafted."""
    sample_account.update_balance(debit=money_cents(150_00))  # bring balance below zero
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
    sample_account.update_balance(debit=money_cents(200_00))
    assert sample_account.is_overdrafted is True

    # Deposit back to positive
    sample_account.update_balance(credit=money_cents(300_00))
    assert sample_account.is_overdrafted is False

@pytest.mark.parametrize("name,balance,type,expected", [
    ('Primary_Checking' , money_cents(-100_00)  , AccountType.CHECKING      , True),
    ('Primary_Checking' , money_cents(100_00)   , AccountType.CHECKING      , False),
    ('Primary_Checking' , money_cents(0)     , AccountType.CHECKING      , False),
    ('Primary_Savings'  , money_cents(-100_00)  , AccountType.SAVINGS       , True),
    ('Primary_Savings'  , money_cents(100_00)   , AccountType.SAVINGS       , False),
    ('Primary_Savings'  , money_cents(0)     , AccountType.SAVINGS       , False),
    ('Netflix'          , money_cents(-100_00)  , AccountType.SUBSCRIPTION  , False),
    ('Netflix'          , money_cents(100_00)   , AccountType.SUBSCRIPTION  , False),
    ('Netflix'          , money_cents(0)     , AccountType.SUBSCRIPTION  , False),
    ('Utilities'        , money_cents(-100_00)  , AccountType.REOCCURRING   , False),
    ('Utilities'        , money_cents(100_00)   , AccountType.REOCCURRING   , False),
    ('Utilities'        , money_cents(0)     , AccountType.REOCCURRING   , False),
    ('Car-Loan'         , money_cents(-100_00)  , AccountType.LOAN          , False),
    ('Car-Loan'         , money_cents(100_00)   , AccountType.LOAN          , False),
    ('Car-Loan'         , money_cents(0)     , AccountType.LOAN          , False),
    ('Discover'         , money_cents(-100_00)  , AccountType.REVOLVING     , False),
    ('Discover'         , money_cents(100_00)   , AccountType.REVOLVING, False),
    ('Discover'         , money_cents(0)    , AccountType.REVOLVING, False)
])
def test_is_overdrafted(name,balance,type,expected):
    account = AccountInformation(name, balance, type)
    assert account.is_overdrafted == expected
