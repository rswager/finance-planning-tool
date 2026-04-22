from datetime import date
from typing import Union

from models.accountInformation import AccountInformation
from models.bankAccount import BankAccount
from models.enumType import AccountType, FrequencyType
from models.interest import Interest
from models.ledger import Ledger
from models.revolving_credit_bill import RevolvingCreditBill
from models.triggerDays import TriggerDays
from models.utils import MajorUnit, MinorUnit, round_value


class FinancedBill:
    """
    Represents a financed bill or loan with interest accrual, minimum payments,
    and an associated ledger to track all transactions and interest applied.
    """

    def __init__(
        self,
        name_in: str,
        balance_in: MinorUnit,
        account_type_in: AccountType,
        initial_pay_date_in: date,
        frequency_type_in: FrequencyType,
        minimum_payment_in: MinorUnit,
        payment_method_in: Union["RevolvingCreditBill", "BankAccount"],
        apr_rate_in: float,
        round_up: bool = False,
    ) -> None:
        """
        Initialize a FinancedBill instance.

        Parameters
        ----------
            name_in : str
                The name of the bill/loan.
            balance_in : MinorUnit
                The initial balance owed. Positive balances are treated as debt.
            account_type_in : AccountType
                The type of account (e.g., LOAN, REVOLVING).
            initial_pay_date_in : date
                The first date a payment is due.
            frequency_type_in : FrequencyType
                The frequency with which payments are due (e.g., MONTHLY, BI_WEEKLY).
            minimum_payment_in : MinorUnit
                The minimum amount to pay each cycle in minor units.
            payment_method_in : Union[RevolvingCreditBill, BankAccount]
                The account or credit source used to make payments.
            apr_rate_in : float
                The annual percentage rate as a fraction (e.g., 0.05 for 5% APR).
            round_up : bool, optional
                Whether to round up the minimum payment for conservative budgeting.
        """
        self._interest = Interest(apr_rate_in)
        self._minimum_payment: MinorUnit = (
            minimum_payment_in if not round_up else round_value(minimum_payment_in, round_up=round_up)
        )
        self._accountInfo = AccountInformation(
            name_in=name_in,
            balance_in=-balance_in if balance_in > 0 else balance_in,
            account_type_in=account_type_in,
        )
        self._ledger = Ledger(["No.", "Date", "Description", "Credit", "Debit", "Balance", "Interest To Date"])
        self._trigger_days = TriggerDays(frequency_in=frequency_type_in)
        self._trigger_days.trigger_date = initial_pay_date_in
        self._payment_method: Union["RevolvingCreditBill", "BankAccount"] = payment_method_in

    @property
    def raw_copy_ledger(self) -> list:
        """list: A deep copy of the ledger for safe inspection or external use."""
        return self._ledger.raw_copy_ledger

    @property
    def ledger_col_count(self) -> int:
        """int: The number of columns defined in the ledger."""
        return self._ledger.col_count

    @property
    def loan_balance_minor(self) -> MinorUnit:
        """MinorUnit: The current outstanding balance in minor units (e.g. cents)."""
        return self._accountInfo.balance

    @property
    def loan_balance_major(self) -> MajorUnit:
        """MajorUnit: The current outstanding balance in major units (e.g. dollars)."""
        return self._accountInfo.balance.to_major()

    @property
    def account_name(self) -> str:
        """str: The name of this financed bill."""
        return self._accountInfo.account_name

    @property
    def account_type(self) -> AccountType:
        """AccountType: The type of this account (e.g., LOAN, REVOLVING)."""
        return self._accountInfo.account_type

    def make_payment(self, date_in: date) -> None:
        """
        Apply the minimum payment to the bill and record the transaction.

        If the remaining balance is less than the minimum payment, only the
        remaining balance is paid.
        """
        if self._accountInfo.balance != 0:
            min_payment = self._minimum_payment
            if abs(self._accountInfo.balance) < self._minimum_payment:
                min_payment = abs(self._accountInfo.balance)

            self.make_a_transaction(date_in=date_in, action="Minimum Payment", credit=min_payment, debit=MinorUnit(0))
            self._payment_method.make_a_transaction(
                date_in=date_in,
                action=f"{self.account_name}-Payment",
                credit=MinorUnit(0),
                debit=min_payment,
            )

    def apply_daily_interest(self, date_in: date) -> None:
        """Calculate and apply daily interest to the outstanding balance."""
        if self.loan_balance_minor != 0:
            self.make_a_transaction(
                date_in=date_in,
                action="Daily Interest",
                credit=MinorUnit(0),
                debit=self._interest.calculate_daily_interest(balance_in=self.loan_balance_minor, date_in=date_in),
            )

    def process_day(self, date_in: date) -> None:
        """
        Process all activities for a single day: apply interest and make scheduled payments.

        Daily interest is always applied. If today is a scheduled payment day, the
        minimum payment is also applied.
        """
        self.apply_daily_interest(date_in=date_in)
        if self._trigger_days.date_triggered(date_in):
            self.make_payment(date_in=date_in)

    def make_a_transaction(self, date_in: date, action: str, credit: MinorUnit, debit: MinorUnit) -> None:
        """
        Record a transaction in the ledger and update the account balance.

        Parameters
        ----------
            date_in : date
                The date of the transaction.
            action : str
                A description of the transaction.
            credit : MinorUnit
                Amount added to the account.
            debit : MinorUnit
                Amount subtracted from the account.
        """
        self._accountInfo.update_balance(credit=credit, debit=debit)
        self._ledger.add_entry_to_ledger(
            [
                self._ledger.row_number,
                date_in,
                action,
                credit.to_major(),
                debit.to_major(),
                self.loan_balance_major,
                self._interest.interest_to_date.to_major(),
            ]
        )
