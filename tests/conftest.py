from datetime import date

import pytest

from models.accounts.account_information import AccountInformation
from models.accounts.bank_account import BankAccount
from models.bills.bill_base import BillBase
from models.bills.bill_financed import FinancedBill
from models.bills.bill_recurring import RecurringBill
from models.bills.bill_revolving_credit import RevolvingCreditBill
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


@pytest.fixture
def financed_bill(checking_account):
    return FinancedBill(
        name_in="Test Loan",
        balance_in=MinorUnit.from_major(500.00),
        account_type_in=AccountType.LOAN,
        initial_pay_date_in=date(2025, 11, 10),
        frequency_type_in=FrequencyType.WEEKLY,
        minimum_payment_in=MinorUnit.from_major(50.00),
        payment_method_in=checking_account,
        apr_rate_in=0.05,
    )


@pytest.fixture
def recurring_bill(checking_account):
    return RecurringBill(
        name_in="Electric Bill",
        minimum_payment_in=MinorUnit.from_major(100.00),
        account_type_in=AccountType.REOCCURRING,
        initial_pay_date_in=date(2025, 11, 10),
        frequency_type_in=FrequencyType.WEEKLY,
        payment_method_in=checking_account,
    )


@pytest.fixture
def credit_bill(checking_account):
    return RevolvingCreditBill(
        name_in="Visa",
        balance_in=MinorUnit.from_major(1_000.00),
        account_type_in=AccountType.REVOLVING,
        initial_pay_date_in=date(2025, 1, 10),
        frequency_type_in=FrequencyType.MONTHLY,
        minimum_payment_in=MinorUnit.from_major(200.00),
        payment_method_in=checking_account,
        apr_rate_in=0.12,
        credit_limit_in=MinorUnit.from_major(5_000.00),
    )
