from datetime import date
from typing import Union, cast

from models.account_information import AccountInformation
from models.bank_account import BankAccount
from models.bill_revolving_credit import RevolvingCreditBill
from models.enum_type import AccountType, FrequencyType
from models.ledger import Ledger, RecurringLedgerRow
from models.trigger_days import TriggerDays
from models.utils import MajorUnit, MinorUnit, round_value


class RecurringBill:
    """
    Represents a recurring bill with a fixed minimum payment that is applied at
    a specified frequency to a designated payment method (BankAccount or RevolvingCreditBill).
    """

    def __init__(
        self,
        name_in: str,
        minimum_payment_in: MinorUnit,
        account_type_in: AccountType,
        initial_pay_date_in: date,
        frequency_type_in: FrequencyType,
        payment_method_in: Union[RevolvingCreditBill, BankAccount],
        round_up: bool = False,
    ) -> None:
        """
        Initialize a RecurringBill instance.

        Parameters
        ----------
            name_in : str
                The name of the bill.
            minimum_payment_in : MinorUnit
                The minimum payment amount per period in minor units (e.g. cents).
            account_type_in : AccountType
                Type of account associated with the bill.
            initial_pay_date_in : date
                The first date the payment should be applied.
            frequency_type_in : FrequencyType
                How often the payment is made (e.g., MONTHLY, BI_WEEKLY).
            payment_method_in : BankAccount | RevolvingCreditBill
                The account or credit bill that receives the payment.
            round_up : bool, optional
                If True, rounds the minimum payment up for conservative budgeting.
        """
        self._accountInfo = AccountInformation(
            name_in=name_in, balance_in=MinorUnit(0), account_type_in=account_type_in
        )
        self._ledger = Ledger(columns=RecurringLedgerRow.COLUMNS)
        self._minimum_payment = (
            minimum_payment_in if not round_up else round_value(minimum_payment_in, round_up=round_up)
        )
        self._trigger_days = TriggerDays(frequency_in=frequency_type_in)
        self._trigger_days.trigger_date = initial_pay_date_in
        self._payment_method: Union[RevolvingCreditBill, BankAccount] = payment_method_in

    @property
    def raw_copy_ledger(self) -> list[RecurringLedgerRow]:
        """list: A deep copy of the ledger to prevent accidental modification."""
        return cast(list[RecurringLedgerRow], self._ledger.raw_copy_ledger)

    @property
    def ledger_col_count(self) -> int:
        """int: The number of columns in the ledger."""
        return self._ledger.col_count

    @property
    def ledger_header(self) -> list[str]:
        return self._ledger.header

    @property
    def account_name(self) -> str:
        """str: The name of the bill."""
        return self._accountInfo.account_name

    @property
    def account_type(self) -> AccountType:
        """AccountType: The type of the bill's account."""
        return self._accountInfo.account_type

    def make_payment(self, date_in: date) -> None:
        """
        Apply the minimum payment to the bill and record it in the ledger.

        Parameters
        ----------
            date_in : date
                The date on which the payment is applied.
        """
        self._accountInfo.update_balance(credit=self._minimum_payment)
        self._payment_method.make_a_transaction(
            date_in=date_in,
            action=f"{self.account_name}-Payment",
            credit=MinorUnit(0),
            debit=self._minimum_payment,
        )
        self._ledger.add_entry_to_ledger(
            RecurringLedgerRow(
                row_number=self._ledger.row_number,
                date=date_in,
                description="Minimum Payment",
                credit=self._minimum_payment.to_major(),
                debit=MajorUnit(0),
                paid_to_date=self._accountInfo.balance.to_major(),
            )
        )

    def process_day(self, date_in: date) -> None:
        """
        Process a single day, applying a payment if it matches a trigger date.

        Parameters
        ----------
            date_in : date
                The date being processed.
        """
        if self._trigger_days.date_triggered(date_in):
            self.make_payment(date_in=date_in)

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
