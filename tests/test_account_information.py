import pytest

from models.account_information import AccountInformation
from models.enum_type import AccountType
from models.utils import MinorUnit


@pytest.fixture
def sample_account():
    return AccountInformation("Primary_Checking", MinorUnit.from_major(100.00), AccountType.CHECKING)


def test_initial_balance_and_attributes(sample_account):
    assert sample_account.account_name == "Primary_Checking"
    assert sample_account.account_type == AccountType.CHECKING
    assert sample_account.balance == MinorUnit.from_major(100.00)


def test_update_balance_adds_amount(sample_account):
    sample_account.update_balance(credit=MinorUnit.from_major(25.50))
    assert sample_account.balance == MinorUnit.from_major(125.50)


def test_update_balance_handles_negative_transactions(sample_account):
    sample_account.update_balance(debit=MinorUnit.from_major(40.25))
    assert sample_account.balance == MinorUnit.from_major(59.75)


def test_balance_property_is_minor_unit(sample_account):
    assert isinstance(sample_account.balance, MinorUnit)


def test_update_balance_multiple_times(sample_account):
    sample_account.update_balance(credit=MinorUnit.from_major(20.00))
    sample_account.update_balance(credit=MinorUnit.from_major(30.00))
    sample_account.update_balance(debit=MinorUnit.from_major(10.00))
    assert sample_account.balance == MinorUnit.from_major(140.00)


def test_balance_independent_of_bill_name_and_type():
    acc = AccountInformation("Electric", MinorUnit.from_major(200.00), AccountType.REOCCURRING)
    acc.update_balance(debit=MinorUnit.from_major(50.00))
    assert acc.balance == MinorUnit.from_major(150.00)
    assert acc.account_name == "Electric"
    assert acc.account_type == AccountType.REOCCURRING


def test_is_overdrafted_initial_false(sample_account):
    assert sample_account.is_overdrafted is False


def test_is_overdrafted_true_when_negative_balance(sample_account):
    sample_account.update_balance(debit=MinorUnit.from_major(150.00))
    assert sample_account.balance < 0
    assert sample_account.is_overdrafted is True


def test_is_overdrafted_false_when_balance_zero():
    acc = AccountInformation("Utility", MinorUnit(0), AccountType.REOCCURRING)
    assert acc.is_overdrafted is False


def test_is_overdrafted_property_updates_with_balance(sample_account):
    assert sample_account.is_overdrafted is False
    sample_account.update_balance(debit=MinorUnit.from_major(200.00))
    assert sample_account.is_overdrafted is True
    sample_account.update_balance(credit=MinorUnit.from_major(300.00))
    assert sample_account.is_overdrafted is False


@pytest.mark.parametrize(
    "name,balance,type,expected",
    [
        ("Primary_Checking", MinorUnit.from_major(-100.00), AccountType.CHECKING, True),
        ("Primary_Checking", MinorUnit.from_major(100.00), AccountType.CHECKING, False),
        ("Primary_Checking", MinorUnit(0), AccountType.CHECKING, False),
        ("Primary_Savings", MinorUnit.from_major(-100.00), AccountType.SAVINGS, True),
        ("Primary_Savings", MinorUnit.from_major(100.00), AccountType.SAVINGS, False),
        ("Primary_Savings", MinorUnit(0), AccountType.SAVINGS, False),
        ("Netflix", MinorUnit.from_major(-100.00), AccountType.SUBSCRIPTION, False),
        ("Netflix", MinorUnit.from_major(100.00), AccountType.SUBSCRIPTION, False),
        ("Netflix", MinorUnit(0), AccountType.SUBSCRIPTION, False),
        ("Utilities", MinorUnit.from_major(-100.00), AccountType.REOCCURRING, False),
        ("Utilities", MinorUnit.from_major(100.00), AccountType.REOCCURRING, False),
        ("Utilities", MinorUnit(0), AccountType.REOCCURRING, False),
        ("Car-Loan", MinorUnit.from_major(-100.00), AccountType.LOAN, False),
        ("Car-Loan", MinorUnit.from_major(100.00), AccountType.LOAN, False),
        ("Car-Loan", MinorUnit(0), AccountType.LOAN, False),
        ("Discover", MinorUnit.from_major(-100.00), AccountType.REVOLVING, False),
        ("Discover", MinorUnit.from_major(100.00), AccountType.REVOLVING, False),
        ("Discover", MinorUnit(0), AccountType.REVOLVING, False),
    ],
)
def test_is_overdrafted(name, balance, type, expected):
    account = AccountInformation(name, balance, type)
    assert account.is_overdrafted == expected
