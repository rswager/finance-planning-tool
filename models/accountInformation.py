from models.enumType import AccountType

class AccountInformation:
    """
    Represents a financial account with a name, balance, and account type.

    This class provides balance tracking, overdraft detection, and supports
    credit/debit updates. The balance, name, and type are stored internally,
    with the name and type treated as immutable after initialization.
    """


    def __init__(self, name_in: str, balance_in: float, account_type_in: AccountType) -> None:
        """
        Initialize a new AccountInformation instance.

        Parameters
        ----------
            name_in : str
                The display/name of the account.
            balance_in : float
                The starting balance.
            account_type_in : AccountType
                The type of account (checking, savings, investment, etc.).

        Returns
        -------
            None
        """
        self._balance: float = balance_in
        self._account_name: str = name_in
        self._account_type: AccountType = account_type_in

    @property
    def balance(self) -> float:
        """
        Return
        -------
            float
                The current account balance.

         Notes
        -------
            The balance is considered immutable through this property.
            Use `update_balance()` to apply credits/debits, or the setter
            only when explicitly replacing the value.
        """
        # immutable type
        return self._balance

    @property
    def is_overdrafted(self) -> bool:
        """
        Returns
        -------
            bool
                Indicates whether the account is overdrafted.

        Notes
        -------
            Returns True only for CHECKING or SAVINGS accounts
            with a balance below zero.
        """
        # We only want to show over draft on checking and savings accounts
        if self._account_type in(AccountType.SAVINGS,AccountType.CHECKING):
            return self._balance<0
        return False

    def update_balance(self,credit:float=0, debit:float=0) -> None:
        """
        Apply a credit or debit to the account balance.

        Parameters
        ----------
            credit : (float, optional)
                Amount to add to the balance. Defaults to 0.
            debit : (float, optional)
                Amount to subtract from the balance. Defaults to 0.

        Return
        -------
            None

        Notes
        -------
            The function calculates: new_balance = old_balance + credit - debit
        """
        self._balance = self._balance + credit - debit

    @property
    def account_name(self) -> str:
        """
        Returns
        -------
            str:
                The name of the account (immutable).
        """
        # immutable type
        return self._account_name

    @property
    def account_type(self) -> AccountType:
        """
        Returns
        -------
            AccountType:
                The type/category of the account (immutable).
        """
        # immutable type
        return self._account_type
