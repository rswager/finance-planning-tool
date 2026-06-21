from datetime import date

import pytest

from models.accounts.account_information import AccountInformation
from models.accounts.bank_account import BankAccount
from models.bills.bill_base import BillBase
from models.bills.bill_financed import FinancedBill
from models.bills.bill_recurring import RecurringBill
from models.bills.bill_revolving_credit import RevolvingCreditBill
from models.core.enum_type import AccountType, FrequencyType
from models.core.interest import Interest
from models.core.ledger import Ledger, StandardLedgerRow
from models.core.trigger_days import TriggerDays
from models.core.utils import MinorUnit
from models.income.income import Income


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
def bank_accounts(checking_account, saving_account):
    return checking_account, saving_account


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


@pytest.fixture
def all_bills(financed_bill, recurring_bill, credit_bill):
    return financed_bill, recurring_bill, credit_bill


@pytest.fixture
def income(bank_accounts):
    acc1, acc2 = bank_accounts
    return Income(
        name_in="Salary",
        income_in=MinorUnit.from_major(1_000.00),
        initial_pay_date_in=date(2025, 11, 8),
        account_contributions_in=[(acc1, 0.6), (acc2, 0.4)],
        frequency_type_in=FrequencyType.WEEKLY,
    )


@pytest.fixture
def interest_instance():
    return Interest(0.05)


@pytest.fixture
def ledger():
    """Ledger instance initialized with default columns."""
    return Ledger(ledger_row_type=StandardLedgerRow)


@pytest.fixture
def monthly_trigger():
    return TriggerDays(FrequencyType.MONTHLY)


@pytest.fixture
def biweekly_trigger():
    return TriggerDays(FrequencyType.BI_WEEKLY)


@pytest.fixture
def weekly_trigger():
    return TriggerDays(FrequencyType.WEEKLY)


@pytest.fixture()
def valid_file_path(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    return d / "temp.json"


@pytest.fixture()
def invalid_dir_file_path(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    return d


@pytest.fixture()
def invalid_missing_file_path(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    return tmp_path / "subs" / "temp.json"


@pytest.fixture()
def full_dict_entry():
    return [
        {"id": 1, "name": "hello"},
        {"id": 2, "name": "world"},
    ]


@pytest.fixture()
def empty_dict_entry():
    return []
