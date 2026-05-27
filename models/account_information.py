from models.enum_type import AccountType
from models.utils import MinorUnit


class AccountInformation:
    """
    Represents a financial account with a name, balance, and account type.

    This class provides balance tracking, overdraft detection, and supports
    credit/debit updates. The balance, name, and type are stored internally,
    with the name and type treated as immutable after initialization.
    """

    def __init__(self, name_in: str, balance_in: MinorUnit, account_type_in: AccountType) -> None:
        """
        Initialize a new AccountInformation instance.

        Parameters
        ----------
            name_in : str
                The display/name of the account.
            balance_in : MinorUnit
                The starting balance in minor units (e.g. cents).
            account_type_in : AccountType
                The type of account (checking, savings, investment, etc.).
        """
        self._balance: MinorUnit = balance_in
        self._account_name: str = name_in
        self._account_type: AccountType = account_type_in

    @property
    def balance(self) -> MinorUnit:
        """MinorUnit: The current account balance in minor units."""
        return self._balance

    @property
    def is_overdrafted(self) -> bool:
        """
        bool: True if this is a CHECKING or SAVINGS account with a negative balance.
        """
        if self._account_type in (AccountType.SAVINGS, AccountType.CHECKING):
            return self._balance < 0
        return False

    def update_balance(self, credit: MinorUnit = MinorUnit(0), debit: MinorUnit = MinorUnit(0)) -> None:
        """
        Apply a credit or debit to the account balance.

        Parameters
        ----------
            credit : MinorUnit, optional
                Amount to add to the balance. Defaults to 0.
            debit : MinorUnit, optional
                Amount to subtract from the balance. Defaults to 0.
        """
        self._balance = self._balance + credit - debit

    @property
    def account_name(self) -> str:
        """str: The name of the account (immutable)."""
        return self._account_name

    @property
    def account_type(self) -> AccountType:
        """AccountType: The type/category of the account (immutable)."""
        return self._account_type
