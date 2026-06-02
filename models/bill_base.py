from datetime import date
from typing import Self

from models.account_information import AccountInformation
from models.enum_type import AccountType, FrequencyType
from models.ledger import Ledger, StandardLedgerRow
from models.protocols import Chargeable
from models.trigger_days import TriggerDays
from models.utils import MinorUnit, round_value


class BillBase:
    def __init__(
        self,
        name_in: str,
        balance_in: MinorUnit,
        minimum_payment_in: MinorUnit,
        account_type_in: AccountType,
        initial_pay_date_in: date,
        frequency_type_in: FrequencyType,
        payment_method_in: Chargeable,
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
            payment_method_in : Chargeable
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
        self._trigger_days = TriggerDays(frequency_in=frequency_type_in)
        self._trigger_days.trigger_date = initial_pay_date_in
        self._payment_method: Chargeable = payment_method_in

    @classmethod
    def from_dict(cls, dict_in,chargeable_registry: dict[str, Chargeable]) -> Self:
        """Given a dictionary, create a BillBase object from it."""
        try:
            return cls(
                name_in=dict_in['name_in'],
                balance_in=MinorUnit(dict_in['balance_in']),
                minimum_payment_in=MinorUnit(dict_in['minimum_payment_in']),
                account_type_in=AccountType(dict_in['account_type_in']),
                initial_pay_date_in=date.fromisoformat(dict_in['initial_pay_date_in']), # Do we need to cast this to Date()?
                frequency_type_in=dict_in['frequency_type_in'],
                payment_method_in=chargeable_registry[dict_in['payment_method_in']] , # pass key return object need to account for NONE/Invalid?
                ledger_row_type=dict_in['ledger_row_type'],
                round_up=dict_in['round_up'],
            )
        except KeyError as e:
            raise KeyError(f"Missing required field: {e.args[0]}")


    def to_dict(self) -> dict:
        """Return the Dictionary representation of the BillBase object."""
        return {
            "name_in": self.account_name,
            "balance_in": self.balance_minor,
            "minimum_payment_in": self._minimum_payment,
            "account_type_in": self.account_type.value,
            "initial_pay_date_in": self._trigger_dates.trigger_date.isoformat(), # I think we can just use this? Otherwise we will need to make a new cls variable
            "frequency_type_in": self._trigger_dates.frequency_type_in.value,
            "payment_method_in": self.payment_method.account_name, # We save the account name and load by the key via the chargeable_registry
            "ledger_row_type": None, # We don't currenlty have access to this. May need to add it to the class method of Ledger
            "round_up": None # We don't store this, most likely will need to do that

        }

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
