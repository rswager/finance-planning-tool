from datetime import date
from typing import Self

from models.accounts.account_information import AccountInformation
from models.core.enum_type import AccountType, FrequencyType
from models.core.ledger import Ledger, StandardLedgerRow
from models.core.protocols import Chargeable
from models.core.trigger_days import TriggerDays
from models.core.utils import MinorUnit, round_value


class BillBase:
    def __init__(
        self,
        name_in: str,
        balance_in: MinorUnit,
        minimum_payment_in: MinorUnit,
        account_type_in: AccountType,
        initial_pay_date_in: date,
        frequency_type_in: FrequencyType,
        payment_method_in: Chargeable | None,
        ledger_row_type: type[StandardLedgerRow],
        round_up: bool = False,
    ) -> None:
        """
        Initialize a Base Bill instance.

        Parameters
        ----------
            name_in : str
                The name of the bill.
            balance_in : MinorUnit
                The initial balance owed. Positive balances are treated as debt.
            minimum_payment_in : MinorUnit
                The minimum payment amount per period in minor units (e.g. cents).
            account_type_in : AccountType
                Type of account associated with the bill.
            initial_pay_date_in : date
                The first date the payment should be applied.
            frequency_type_in : FrequencyType
                How often the payment is made (e.g., MONTHLY, BI_WEEKLY).
            payment_method_in : Chargeable | None
                The account or credit bill that receives the payment.
            ledger_row_type : type[StandardLedgerRow]
                The ledger row class to use for this bill (e.g. RecurringLedgerRow, InterestLedgerRow).
            round_up : bool, optional
                If True, rounds the minimum payment up for conservative budgeting.
        """
        self._accountInfo = AccountInformation(name_in=name_in, balance_in=balance_in, account_type_in=account_type_in)
        self._ledger = Ledger(ledger_row_type=ledger_row_type)
        self._minimum_payment = (
            minimum_payment_in if not round_up else round_value(minimum_payment_in, round_up=round_up)
        )
        self._round_up = round_up
        self._trigger_days = TriggerDays(frequency_in=frequency_type_in)
        self._trigger_days.trigger_date = initial_pay_date_in
        self._initial_pay_date = initial_pay_date_in
        self._payment_method: Chargeable | None = payment_method_in

    @classmethod
    def from_dict(cls, dict_in, chargeable_registry: dict[str, Chargeable]) -> Self:
        raise NotImplementedError(
            "Use a concrete subclass's from_dict instead. (RecurringBill, FinancedBill, RevolvingCreditBill)"
        )

    def to_dict(self) -> dict:
        raise NotImplementedError(
            "Use a concrete subclass's to_dict instead. (RecurringBill, FinancedBill, RevolvingCreditBill)"
        )

    @property
    def account_name(self) -> str:
        """str: The name of this bill."""
        return self._accountInfo.account_name

    @property
    def account_type(self) -> AccountType:
        """AccountType: The type of this account (e.g., LOAN, REVOLVING)."""
        return self._accountInfo.account_type

    @property
    def raw_copy_ledger(self) -> list[StandardLedgerRow]:
        """list: A deep copy of the ledger to prevent accidental modification."""
        return self._ledger.raw_copy_ledger

    @property
    def ledger_col_count(self) -> int:
        """int: The number of columns in the ledger."""
        return self._ledger.col_count

    @property
    def ledger_header(self) -> list[str]:
        return self._ledger.header

    @property
    def payment_method(self) -> Chargeable | None:
        if self._payment_method is None:
            raise ValueError("Payment method not set.")
        return self._payment_method

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

    def update_payment_method(self, payment_method_in: Chargeable | None) -> None:
        """Update the payment method of the bill."""
        self._payment_method = payment_method_in
