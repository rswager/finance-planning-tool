from __future__ import annotations

from enum import Enum

from models.accounts.bank_account import BankAccount
from models.bills.bill_financed import FinancedBill
from models.bills.bill_recurring import RecurringBill
from models.bills.bill_revolving_credit import RevolvingCreditBill
from models.income.income import Income


class SerialTypeLookup(Enum):
    """
    Enumeration of different types of serial accounts supported in the system.
    """

    bank_account = BankAccount
    bill_recurring = RecurringBill
    bill_financed = FinancedBill
    bill_revolving_credit = RevolvingCreditBill
    income = Income
