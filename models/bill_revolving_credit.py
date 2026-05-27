from datetime import date

from models.bill_financed import FinancedBill
from models.enum_type import AccountType, FrequencyType
from models.protocols import Chargeable
from models.utils import MinorUnit


class RevolvingCreditBill(FinancedBill):
    """
    Represents a revolving credit bill, such as a credit card, that accrues daily interest
    and requires minimum payments at specified intervals. Payments are applied to a linked chargeable account.
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
        payment_method_in : Chargeable
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

    @property
    def exceeded_credit_limit(self) -> bool:
        """bool: True if the current balance exceeds the credit limit."""
        return abs(self._accountInfo.balance) > self._credit_limit
