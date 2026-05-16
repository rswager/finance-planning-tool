from datetime import date
from typing import Union, cast

from models.account_information import AccountInformation
from models.bank_account import BankAccount
from models.enum_type import AccountType, FrequencyType
from models.interest import Interest
from models.ledger import InterestLedgerRow, Ledger
from models.trigger_days import TriggerDays
from models.utils import MajorUnit, MinorUnit, round_value


class RevolvingCreditBill:
    """
    Represents a revolving credit bill, such as a credit card, that accrues daily interest
    and requires minimum payments at specified intervals. Payments are applied to a linked
    BankAccount or another RevolvingCreditBill.
    """

    def __init__(
        self,
        name_in: str,
        balance_in: MinorUnit,
        account_type_in: AccountType,
        initial_pay_date_in: date,
        frequency_type_in: FrequencyType,
        minimum_payment_in: MinorUnit,
        payment_method_in: Union["RevolvingCreditBill", BankAccount],
        apr_rate_in: float,
        credit_limit_in: MinorUnit,
        round_up: bool = False,
    ) -> None:
        """
        Initialize a RevolvingCreditBill instance.

        Parameters
        ----------
        name_in : str
            The name of the revolving credit account.
        balance_in : MinorUnit
            The starting balance (amount owed) in minor units.
        account_type_in : AccountType
            Type of the account (e.g., REVOLVING).
        initial_pay_date_in : date
            The first date a minimum payment is due.
        frequency_type_in : FrequencyType
            Payment frequency (e.g., MONTHLY, BI_WEEKLY).
        minimum_payment_in : MinorUnit
            The required minimum payment per period in minor units.
        payment_method_in : BankAccount | RevolvingCreditBill
            The account used to make the payment.
        apr_rate_in : float
            The annual percentage rate as a decimal (e.g., 0.05 for 5% APR).
        credit_limit_in : MinorUnit
            Maximum credit allowed on this account in minor units.
        round_up : bool, optional
            Whether to round the minimum payment up for conservative budgeting.
        """
        self._interest = Interest(apr_rate_in)
        self._minimum_payment: MinorUnit = (
            minimum_payment_in if not round_up else round_value(minimum_payment_in, round_up=round_up)
        )
        self._credit_limit: MinorUnit = credit_limit_in
        self._accountInfo = AccountInformation(
            name_in=name_in,
            balance_in=-balance_in if balance_in > 0 else balance_in,
            account_type_in=account_type_in,
        )
        self._ledger = Ledger(columns=InterestLedgerRow.COLUMNS)
        self._trigger_days = TriggerDays(frequency_in=frequency_type_in)
        self._trigger_days.trigger_date = initial_pay_date_in
        self._payment_method: Union["RevolvingCreditBill", BankAccount] = payment_method_in

    @property
    def raw_copy_ledger(self) -> list[InterestLedgerRow]:
        """list: A deep copy of the ledger to prevent accidental modification."""
        return cast(list[InterestLedgerRow], self._ledger.raw_copy_ledger)

    @property
    def ledger_col_count(self) -> int:
        """int: The number of columns in the ledger."""
        return self._ledger.col_count

    @property
    def ledger_header(self) -> list[str]:
        return self._ledger.header

    @property
    def loan_balance_minor(self) -> MinorUnit:
        """MinorUnit: The current balance owed in minor units."""
        return self._accountInfo.balance

    @property
    def loan_balance_major(self) -> MajorUnit:
        """MajorUnit: The current balance owed in major units."""
        return self._accountInfo.balance.to_major()

    @property
    def exceeded_credit_limit(self) -> bool:
        """bool: True if the current balance exceeds the credit limit."""
        return abs(self._accountInfo.balance) > self._credit_limit

    @property
    def account_name(self) -> str:
        """str: The name of the account."""
        return self._accountInfo.account_name

    @property
    def account_type(self) -> AccountType:
        """AccountType: The type of account."""
        return self._accountInfo.account_type

    def make_payment(self, date_in: date) -> None:
        """
        Apply the minimum payment to the balance and record the transaction.

        If the remaining balance is less than the minimum payment, only the
        remaining balance is paid.
        """
        if self._accountInfo.balance != 0:
            min_payment: MinorUnit = self._minimum_payment
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
        """Calculate and apply daily interest to the account balance."""
        if self._accountInfo.balance != 0:
            self.make_a_transaction(
                date_in=date_in,
                action="Daily Interest",
                credit=MinorUnit(0),
                debit=self._interest.calculate_daily_interest(balance_in=self._accountInfo.balance, date_in=date_in),
            )

    def process_day(self, date_in: date) -> None:
        """
        Process a single day: apply daily interest and make a minimum payment if it is a trigger date.
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
                Description of the transaction.
            credit : MinorUnit
                Amount credited to the account.
            debit : MinorUnit
                Amount debited from the account.
        """
        self._accountInfo.update_balance(credit=credit, debit=debit)
        self._ledger.add_entry_to_ledger(
            InterestLedgerRow(
                row_number=self._ledger.row_number,
                date=date_in,
                description=action,
                credit=credit.to_major(),
                debit=debit.to_major(),
                balance=self._accountInfo.balance.to_major(),
                interest_to_date=self._interest.interest_to_date.to_major(),
            )
        )

    def initialize_simulation_date(self, simulation_start_date: date) -> None:
        """
        Align the trigger date to the simulation start date before the simulation runs.

        Parameters
        ----------
        simulation_start_date : date
            The date the simulation begins. The trigger date will be advanced or
            rewound to the first scheduled occurrence on or after this date.
        """
        self._trigger_days.bring_trigger_date_to_target_date(simulation_start_date)
