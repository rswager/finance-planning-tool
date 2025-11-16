import pytest
from models.enumType import FrequencyType, AccountType


# ----------------------------
# FrequencyType Tests
# ----------------------------

def test_frequencytype_values():
    """Ensure FrequencyType enum members have correct assigned values."""
    assert FrequencyType.MONTHLY.value == 1
    assert FrequencyType.BI_WEEKLY.value == 2
    assert FrequencyType.WEEKLY.value == 3
    assert FrequencyType.DAILY.value == 4
    assert FrequencyType.YEARLY.value == 5
    assert FrequencyType.SINGULAR.value == 6


def test_frequencytype_names():
    """Ensure enum names are correctly set."""
    assert FrequencyType.MONTHLY.name == "MONTHLY"
    assert FrequencyType.BI_WEEKLY.name == "BI_WEEKLY"
    assert FrequencyType.WEEKLY.name == "WEEKLY"
    assert FrequencyType.DAILY.name == "DAILY"
    assert FrequencyType.YEARLY.name == "YEARLY"
    assert FrequencyType.SINGULAR.name == "SINGULAR"


def test_frequencytype_member_count():
    """Ensure that FrequencyType contains exactly 6 members."""
    assert len(FrequencyType) == 6


def test_frequencytype_uniqueness():
    """Ensure all enum values are unique."""
    values = [member.value for member in FrequencyType]
    assert len(values) == len(set(values))


def test_frequencytype_membership():
    """Ensure membership testing works properly."""
    assert FrequencyType.MONTHLY in FrequencyType
    assert 1 in [m.value for m in FrequencyType]
    assert "MONTHLY" in [m.name for m in FrequencyType]


# ----------------------------
# AccountType Tests
# ----------------------------

def test_accounttype_values():
    """Ensure AccountType enum members have correct assigned values."""
    assert AccountType.CHECKING.value == 1
    assert AccountType.SAVINGS.value == 2
    assert AccountType.LOAN.value == 3
    assert AccountType.REVOLVING.value == 4
    assert AccountType.SUBSCRIPTION.value == 5
    assert AccountType.REOCCURRING.value == 6


def test_accounttype_names():
    """Ensure enum names are correctly set."""
    assert AccountType.CHECKING.name == "CHECKING"
    assert AccountType.SAVINGS.name == "SAVINGS"
    assert AccountType.LOAN.name == "LOAN"
    assert AccountType.REVOLVING.name == "REVOLVING"
    assert AccountType.SUBSCRIPTION.name == "SUBSCRIPTION"
    assert AccountType.REOCCURRING.name == "REOCCURRING"


def test_accounttype_member_count():
    """Ensure that AccountType contains exactly 6 members."""
    assert len(AccountType) == 6


def test_accounttype_uniqueness():
    """Ensure all enum values are unique."""
    values = [member.value for member in AccountType]
    assert len(values) == len(set(values))


def test_accounttype_membership():
    """Ensure membership testing works properly."""
    assert AccountType.CHECKING in AccountType
    assert 1 in [m.value for m in AccountType]
    assert "CHECKING" in [m.name for m in AccountType]
