from datetime import date

from PyQt5.uic.properties import int_list

from models.accountInformation import AccountInformation
from models.enumType import AccountType
from models.ledger import Ledger
from models.utils import cents_to_dollars, money_cents, money_dollars
from typing import Self


class BankAccount:
    """
    Represents a financial account with a running ledger of all transactions.

    This class manages account metadata (name, type, balance) and logs all
    deposits, withdrawals, and adjustments to a structured ledger. It provides
    read-only access to the account details and exposes methods for recording
    transaction activity.
    """

    @classmethod
    def from_dict(cls,dict_in) -> Self :
        try:
            return cls(
                name_in = dict_in['name_in'],
                balance_in = money_cents(dict_in['balance_in']),
                account_type_in = AccountType(dict_in['account_type_in'])
            )
        except KeyError as e:
            raise KeyError(f"Missing required field: {e.args[0]}")


    def __init__(self, name_in: str, balance_in: money_cents, account_type_in: AccountType) -> None:
        """
        Initialize a new BankAccount.

        Parameters
        ----------
            name_in : str
                The name of the account.
            balance_in : money_cents(int)
                The starting balance of the account in cents
            account_type_in : AccountType
                The type of account (e.g., SAVINGS, CHECKING, CREDIT).
        """
        self._accountInfo = AccountInformation(name_in, balance_in, account_type_in)
        self._ledger = Ledger(columns=['No.', 'Date', 'Description', 'Credit', 'Debit', 'Balance'])

    @property
    def balance_cents(self) -> money_cents:
        """
        Returns
        -------
            money_cents
                Returns the current balance in terms of cents
        """
        return self._accountInfo.balance

    @property
    def balance_dollars(self) -> money_dollars:
        """
        Returns
        -------
            money_cents
                Returns the current balance in terms of dollars
        """
        return cents_to_dollars(self._accountInfo.balance)

    @property
    def raw_copy_ledger(self) -> list:
        """
        Returns
        -------
            list
                A deep copy of the ledger. Safe to modify without affecting
                the original ledger data.
        """
        # returns a deepcopy of the ledger
        return self._ledger.raw_copy_ledger

    @property
    def ledger_col_count(self) -> int:
        """
        Returns
        -------
            int
                The number of columns defined in the ledger.
        """
        return self._ledger.col_count

    @property
    def account_name(self) -> str:
        """
        Returns
        -------
            str
                The name assigned to this account.
        """
        return self._accountInfo.account_name

    @property
    def account_type(self) -> AccountType:
        """
        Returns
        -------
            AccountType
                The type/category of this account.
        """
        return self._accountInfo.account_type

    def make_a_transaction(self, date_in: date, action: str, credit: money_cents, debit: money_cents) -> None:
        """
        Record a financial transaction and update the account balance and ledger.

        Parameters
        ----------
            date_in : date
                The date of the transaction.
            action : str
                A short description of the transaction (e.g., "Deposit", "Payment").
            credit : money_cents
                Amount added to the account balance.
            debit : money_cents
                Amount subtracted from the account balance.

        Notes
        -----
        - The account balance is updated before writing the ledger entry.
        - Ledger entries include a row number, date, description, credit, debit, and resulting balance.
        """
        self._accountInfo.update_balance(credit=credit,debit=debit)
        self._ledger.add_entry_to_ledger([self._ledger.row_number, date_in, action,
                                          cents_to_dollars(credit),
                                          cents_to_dollars(debit),
                                          self.balance_dollars])
