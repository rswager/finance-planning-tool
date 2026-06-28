from __future__ import annotations

from enum import Enum

from ..accounts import (
    BankAccount,
)
from ..bills import (
    FinancedBill,
    RecurringBill,
    RevolvingCreditBill,
)
from ..income import (
    Income,
)


class SerialTypeLookup(Enum):
    """
    Enumeration of different types of serial accounts supported in the system.
    """

    bank_account = BankAccount
    bill_recurring = RecurringBill
    bill_financed = FinancedBill
    bill_revolving_credit = RevolvingCreditBill
    income = Income
