from datetime import date
from typing import Self, cast

from models.bills.bill_base import BillBase
from models.core.enum_type import AccountType, FrequencyType
from models.core.interest import Interest
from models.core.ledger import InterestLedgerRow
from models.core.protocols import Chargeable
from models.core.utils import MajorUnit, MinorUnit


class FinancedBill(BillBase):
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
        payment_method_in: Chargeable,
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
            payment_method_in : Chargeable
                The account or credit source used to make payments.
            apr_rate_in : float
                The annual percentage rate as a fraction (e.g., 0.05 for 5% APR).
            round_up : bool, optional
                Whether to round up the minimum payment for conservative budgeting.
        """
        # This is a debt!
        balance_in = -balance_in if balance_in > 0 else balance_in
        super().__init__(
            name_in=name_in,
            minimum_payment_in=minimum_payment_in,
            account_type_in=account_type_in,
            balance_in=balance_in,
            initial_pay_date_in=initial_pay_date_in,
            frequency_type_in=frequency_type_in,
            payment_method_in=payment_method_in,
            ledger_row_type=InterestLedgerRow,
            round_up=round_up,
        )
        self._interest = Interest(apr_rate_in)

    @classmethod
    def from_dict(cls, dict_in, chargeable_registry: dict[str, Chargeable]) -> Self:
        """Given a dictionary, create a FinancedBill object from it."""
        try:
            return cls(
                name_in=dict_in["name_in"],
                balance_in=MinorUnit(dict_in["balance_in"]),
                account_type_in=AccountType(dict_in["account_type_in"]),
                initial_pay_date_in=date.fromisoformat(dict_in["initial_pay_date_in"]),
                frequency_type_in=FrequencyType(dict_in["frequency_type_in"]),
                minimum_payment_in=MinorUnit(dict_in["minimum_payment_in"]),
                payment_method_in=chargeable_registry[
                    dict_in["payment_method_in"]
                ],  # pass key return object need to account for NONE/Invalid?
                apr_rate_in=dict_in["apr_rate_in"],
                round_up=dict_in["round_up"],
            )
        except KeyError as e:
            raise KeyError(f"Missing required field: {e.args[0]}") from e

    def to_dict(self) -> dict:
        """Return the Dictionary representation of the FinancedBill object."""
        return {
            "name_in": self.account_name,
            "balance_in": int(self._accountInfo._initial_balance),
            "account_type_in": self.account_type.value,
            "initial_pay_date_in": self._initial_pay_date.isoformat(),
            "frequency_type_in": self._trigger_days._frequency.value,
            "minimum_payment_in": int(self._minimum_payment),
            "payment_method_in": self._payment_method.account_name,  # ty: ignore[unresolved-attribute]
            "apr_rate_in": self._interest._apr_rate,
            "round_up": self._round_up,
        }

    @property
    def raw_copy_ledger(self) -> list[InterestLedgerRow]:
        """list: A deep copy of the ledger for safe inspection or external use."""
        return cast(list[InterestLedgerRow], self._ledger.raw_copy_ledger)  # noqa

    @property
    def loan_balance_minor(self) -> MinorUnit:
        """MinorUnit: The current outstanding balance in minor units (e.g. cents)."""
        return self._accountInfo.balance

    @property
    def loan_balance_major(self) -> MajorUnit:
        """MajorUnit: The current outstanding balance in major units (e.g. dollars)."""
        return self._accountInfo.balance.to_major()

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
