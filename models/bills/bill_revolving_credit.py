from datetime import date
from typing import Self

from models.bills.bill_financed import FinancedBill
from models.core.chargeable import Chargeable
from models.core.enum_type import AccountType, FrequencyType
from models.core.utils import MinorUnit


class RevolvingCreditBill(FinancedBill, Chargeable):
    """
    Represents a revolving credit bill, such as a credit card, that accrues daily interest
    and requires minimum payments at specified intervals. Payments are applied to a linked chargeable account.
    """

    TYPE_KEY = "bill_revolving_credit"

    def __init__(
        self,
        name_in: str,
        balance_in: MinorUnit,
        account_type_in: AccountType,
        initial_pay_date_in: date,
        frequency_type_in: FrequencyType,
        minimum_payment_in: MinorUnit,
        payment_method_in: Chargeable | None,
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
        payment_method_in : Chargeable | None
            The account used to make the payment.
        apr_rate_in : float
            The annual percentage rate as a decimal (e.g., 0.05 for 5% APR).
        credit_limit_in : MinorUnit
            Maximum credit allowed on this account in minor units.
        round_up : bool, optional
            Whether to round the minimum payment up for conservative budgeting.
        """
        super().__init__(
            name_in=name_in,
            balance_in=balance_in,
            account_type_in=account_type_in,
            initial_pay_date_in=initial_pay_date_in,
            frequency_type_in=frequency_type_in,
            minimum_payment_in=minimum_payment_in,
            payment_method_in=payment_method_in,
            apr_rate_in=apr_rate_in,
            round_up=round_up,
        )
        self._credit_limit = credit_limit_in

    @classmethod
    def from_dict(cls, dict_in, chargeable_registry: dict[str, Chargeable]) -> Self:
        """Given a dictionary, create a RevolvingCreditBill object from it.

        Note: chargeable_registry should only contain BankAccount entries.
        RevolvingCreditBill.__init__ enforces this — passing any other Chargeable
        will raise a type error at construction.
        """
        try:
            return cls(
                name_in=dict_in["name_in"],
                balance_in=MinorUnit(dict_in["balance_in"]),
                account_type_in=AccountType(dict_in["account_type_in"]),
                initial_pay_date_in=date.fromisoformat(dict_in["initial_pay_date_in"]),
                frequency_type_in=FrequencyType(dict_in["frequency_type_in"]),
                minimum_payment_in=MinorUnit(dict_in["minimum_payment_in"]),
                payment_method_in=chargeable_registry[dict_in["payment_method_in"]],
                apr_rate_in=dict_in["apr_rate_in"],
                credit_limit_in=MinorUnit(dict_in["credit_limit_in"]),
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
            "payment_method_in": self.payment_method.account_name,
            "apr_rate_in": self._interest._apr_rate,
            "credit_limit_in": int(self._credit_limit),
            "round_up": self._round_up,
            "serial_type_in": self.TYPE_KEY,
        }

    @property
    def exceeded_credit_limit(self) -> bool:
        """bool: True if the current balance exceeds the credit limit."""
        return abs(self._accountInfo.balance) > self._credit_limit
