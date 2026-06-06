from datetime import date
from typing import Self, cast

from models.bills.bill_base import BillBase
from models.core.enum_type import AccountType, FrequencyType
from models.core.ledger import RecurringLedgerRow
from models.core.protocols import Chargeable
from models.core.utils import MajorUnit, MinorUnit


class RecurringBill(BillBase):
    """
    Represents a recurring bill with a fixed minimum payment that is applied at
    a specified frequency to a designated payment method (Chargeable).
    """

    def __init__(
        self,
        name_in: str,
        minimum_payment_in: MinorUnit,
        account_type_in: AccountType,
        initial_pay_date_in: date,
        frequency_type_in: FrequencyType,
        payment_method_in: Chargeable | None,
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
            payment_method_in : Chargeable | None
                The account or credit bill that receives the payment.
            round_up : bool, optional
                If True, rounds the minimum payment up for conservative budgeting.
        """
        super().__init__(
            name_in=name_in,
            minimum_payment_in=minimum_payment_in,
            account_type_in=account_type_in,
            balance_in=MinorUnit(0),
            initial_pay_date_in=initial_pay_date_in,
            frequency_type_in=frequency_type_in,
            payment_method_in=payment_method_in,
            ledger_row_type=RecurringLedgerRow,
            round_up=round_up,
        )

    @classmethod
    def from_dict(cls, dict_in, chargeable_registry: dict[str, Chargeable]) -> Self:
        """Given a dictionary, create a RecurringBill object from it."""
        try:
            return cls(
                name_in=dict_in["name_in"],
                minimum_payment_in=MinorUnit(dict_in["minimum_payment_in"]),
                account_type_in=AccountType(dict_in["account_type_in"]),
                initial_pay_date_in=date.fromisoformat(dict_in["initial_pay_date_in"]),
                frequency_type_in=FrequencyType(dict_in["frequency_type_in"]),
                payment_method_in=chargeable_registry[dict_in["payment_method_in"]],
                round_up=dict_in["round_up"],
            )
        except KeyError as e:
            raise KeyError(f"Missing required field: {e.args[0]}") from e

    def to_dict(self) -> dict:
        """Return the Dictionary representation of the RecurringBill object."""
        return {
            "name_in": self.account_name,
            "minimum_payment_in": int(self._minimum_payment),
            "account_type_in": self.account_type.value,
            "initial_pay_date_in": self._initial_pay_date.isoformat(),
            "frequency_type_in": self._trigger_days._frequency.value,
            "payment_method_in": self.payment_method.account_name,  # ty: ignore[unresolved-attribute]
            "round_up": self._round_up,
        }

    @property
    def raw_copy_ledger(self) -> list[RecurringLedgerRow]:
        """list: A deep copy of the ledger to prevent accidental modification."""
        return cast(list[RecurringLedgerRow], self._ledger.raw_copy_ledger)  # noqa

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

    def make_payment(self, date_in: date) -> None:
        """
        Apply the minimum payment to the bill and record it in the ledger.

        Parameters
        ----------
            date_in : date
                The date on which the payment is applied.
        """
        self._accountInfo.update_balance(credit=self._minimum_payment)
        self.payment_method.make_a_transaction(
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
