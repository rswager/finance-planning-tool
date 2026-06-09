from enum import Enum

from models.accounts.bank_account import BankAccount
from models.bills.bill_financed import FinancedBill
from models.bills.bill_recurring import RecurringBill
from models.bills.bill_revolving_credit import RevolvingCreditBill
from models.income.income import Income


class FrequencyType(Enum):
    """
    Enumeration of schedule frequencies used to determine how often an event
    or trigger should occur.

    Members
    -------
    MONTHLY : int
        Trigger occurs once every month.
    BI_WEEKLY : int
        Trigger occurs once every two weeks.
    WEEKLY : int
        Trigger occurs once every week.
    DAILY : int
        Trigger occurs every day.
    YEARLY : int
        Trigger occurs once per year.
    SINGULAR : int
        Trigger occurs only once and does not repeat.
    """

    MONTHLY = 1
    BI_WEEKLY = 2
    WEEKLY = 3
    DAILY = 4
    YEARLY = 5
    SINGULAR = 6


class AccountType(Enum):
    """
    Enumeration of different types of financial accounts supported in the system.

    Members
    -------
    CHECKING : int
        Standard checking account.
    SAVINGS : int
        Savings account intended for storing funds with interest.
    LOAN : int
        Loan account tracking borrowed amounts and repayments.
    REVOLVING : int
        Revolving credit account, such as a credit card.
    SUBSCRIPTION : int
        Account representing ongoing subscription-based charges.
    REOCCURRING : int
        Account for recurring charges or payments that repeat on a schedule.
    """

    CHECKING = 1
    SAVINGS = 2
    LOAN = 3
    REVOLVING = 4
    SUBSCRIPTION = 5
    REOCCURRING = 6


class SerialAccountType(Enum):
    """
    Enumeration of different types of serial accounts supported in the system.
    """

    bank_account = BankAccount
    bill_recurring = RecurringBill
    bill_financed = FinancedBill
    bill_revolving_credit = RevolvingCreditBill
    income = Income
