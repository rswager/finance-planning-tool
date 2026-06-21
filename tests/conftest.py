from datetime import date

import pytest

from models.accounts.account_information import AccountInformation
from models.accounts.bank_account import BankAccount
from models.bills.bill_base import BillBase
from models.core.enum_type import AccountType, FrequencyType
from models.core.ledger import StandardLedgerRow
from models.core.utils import MinorUnit


@pytest.fixture
def sample_account():
    return AccountInformation("Primary_Checking", MinorUnit.from_major(100.00), AccountType.CHECKING)


@pytest.fixture
def checking_account():
    return BankAccount("Checking", MinorUnit.from_major(1_000.00), AccountType.CHECKING)


@pytest.fixture
def saving_account():
    return BankAccount("Saving", MinorUnit.from_major(1_000.00), AccountType.SAVINGS)


@pytest.fixture
def bill_base(checking_account):
    return BillBase(
        name_in="Test Bill",
        balance_in=MinorUnit(0),
        minimum_payment_in=MinorUnit.from_major(50.00),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 10),
        frequency_type_in=FrequencyType.WEEKLY,
        payment_method_in=checking_account,
        ledger_row_type=StandardLedgerRow,
    )
