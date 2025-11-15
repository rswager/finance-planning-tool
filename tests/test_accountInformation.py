from models.accountInformation import AccountInformation
from models.enumType import AccountType
import pytest


@pytest.fixture
def sample_account():
    """Create a sample account fixture."""
    return AccountInformation("Primary_Checking", 100.00, AccountType.CHECKING)


def test_initial_balance_and_attributes(sample_account):
    """Verify initial values are set correctly."""
    assert sample_account.account_name == "Primary_Checking"
    assert sample_account.account_type == AccountType.CHECKING
    assert sample_account.balance == 100.00


def test_update_balance_adds_amount(sample_account):
    """Ensure update_balance correctly increases balance."""
    sample_account.update_balance(credit=25.50)
    assert sample_account.balance == 125.50


def test_update_balance_handles_negative_transactions(sample_account):
    """Ensure update_balance correctly handles negative (withdrawal) transactions."""
    sample_account.update_balance(debit=40.25)
    assert sample_account.balance == 59.75


def test_balance_setter_overwrites_balance(sample_account):
    """Ensure balance setter overwrites the previous balance."""
    sample_account.balance = 500.00
    assert sample_account.balance == 500.00


def test_balance_property_is_float(sample_account):
    """Ensure balance is always stored as a float."""
    assert isinstance(sample_account.balance, float)


def test_update_balance_multiple_times(sample_account):
    """Ensure cumulative balance updates correctly."""
    sample_account.update_balance(credit=20.00)
    sample_account.update_balance(credit=30.00)
    sample_account.update_balance(debit=10.00)
    assert sample_account.balance == 140.00


def test_balance_independent_of_bill_name_and_type():
    """Ensure name/type don’t affect balance behavior."""
    acc = AccountInformation("Electric", 200.00, AccountType.REOCCURRING)
    acc.update_balance(debit=50.00)
    assert acc.balance == 150.00
    assert acc.account_name == "Electric"
    assert acc.account_type == AccountType.REOCCURRING

def test_is_overdrafted_initial_false(sample_account):
    """Account with positive balance is not overdrafted."""
    assert sample_account.is_overdrafted is False


def test_is_overdrafted_true_when_negative_balance(sample_account):
    """Account with negative balance is overdrafted."""
    sample_account.update_balance(debit=150.00)  # bring balance below zero
    assert sample_account.balance < 0
    assert sample_account.is_overdrafted is True


def test_is_overdrafted_false_when_balance_zero():
    """Zero balance is not considered overdrafted."""
    acc = AccountInformation("Utility", 0.00, AccountType.REOCCURRING)
    assert acc.is_overdrafted is False


def test_is_overdrafted_property_updates_with_balance(sample_account):
    """Overdrafted property reflects changes to balance dynamically."""
    # Initially positive
    assert sample_account.is_overdrafted is False

    # Withdraw to negative
    sample_account.update_balance(debit=200.00)
    assert sample_account.is_overdrafted is True

    # Deposit back to positive
    sample_account.update_balance(credit=300.00)
    assert sample_account.is_overdrafted is False

@pytest.mark.parametrize("name,balance,type,expected", [
    ('Primary_Checking' , -100  , AccountType.CHECKING      , True),
    ('Primary_Checking' , 100   , AccountType.CHECKING      , False),
    ('Primary_Checking' , 0     , AccountType.CHECKING      , False),
    ('Primary_Savings'  , -100  , AccountType.SAVINGS       , True),
    ('Primary_Savings'  , 100   , AccountType.SAVINGS       , False),
    ('Primary_Savings'  , 0     , AccountType.SAVINGS       , False),
    ('Netflix'          , -100  , AccountType.SUBSCRIPTION  , False),
    ('Netflix'          , 100   , AccountType.SUBSCRIPTION  , False),
    ('Netflix'          , 0     , AccountType.SUBSCRIPTION  , False),
    ('Utilities'        , -100  , AccountType.REOCCURRING   , False),
    ('Utilities'        , 100   , AccountType.REOCCURRING   , False),
    ('Utilities'        , 0     , AccountType.REOCCURRING   , False),
    ('Car-Loan'         , -100  , AccountType.LOAN          , False),
    ('Car-Loan'         , 100   , AccountType.LOAN          , False),
    ('Car-Loan'         , 0     , AccountType.LOAN          , False),
    ('Discover'         , -100  , AccountType.REVOLVING     , False),
    ('Discover'         , 100   , AccountType.REVOLVING, False),
    ('Discover'         , 0     , AccountType.REVOLVING, False)
])
def test_is_overdrafted(name,balance,type,expected):
    account = AccountInformation(name, balance, type)
    assert account.is_overdrafted == expected

if __name__ == '__main__':
    pytest.main([__file__])