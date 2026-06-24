from __future__ import annotations

from datetime import date
from typing import Any, Self, cast

from models.accounts.account_information import AccountInformation
from models.core.chargeable import Chargeable
from models.core.enum_type import AccountType
from models.core.ledger import BankAccountLedgerRow, Ledger
from models.core.utils import MajorUnit, MinorUnit


class BankAccount(Chargeable):
    """
    Represents a financial account with a running ledger of all transactions.

    This class manages account metadata (name, type, balance) and logs all
    deposits, withdrawals, and adjustments to a structured ledger. It provides
    read-only access to the account details and exposes methods for recording
    transaction activity.
    """

    TYPE_KEY = "bank_account"

    def __init__(self, name_in: str, balance_in: MinorUnit, account_type_in: AccountType) -> None:
        """
        Initialize a new BankAccount.

        Parameters
        ----------
            name_in : str
                The name of the account.
            balance_in : MinorUnit
                The starting balance of the account in minor units (e.g. cents).
            account_type_in : AccountType
                The type of account (e.g., SAVINGS, CHECKING, CREDIT).
        """
        self._account_info = AccountInformation(name_in, balance_in, account_type_in)
        self._ledger = Ledger(ledger_row_type=BankAccountLedgerRow)

    @classmethod
    def from_dict(cls, dict_in: dict[str, Any]) -> Self:
        """Given a dictionary, create a BankAccount object from it."""
        try:
            return cls(
                name_in=dict_in["name_in"],
                balance_in=MinorUnit(dict_in["balance_in"]),
                account_type_in=AccountType(dict_in["account_type_in"]),
            )
        except KeyError as e:
            raise KeyError(f"Missing required field: {e.args[0]}") from e

    def to_dict(self) -> dict:
        """Return the Dictionary representation of the BankAccount object."""
        return {
            "name_in": self.account_name,
            "balance_in": int(self.balance_minor),
            "account_type_in": self.account_type.value,
            "serial_type_in": self.TYPE_KEY,
        }

    @property
    def balance_minor(self) -> MinorUnit:
        """MinorUnit: The current balance in minor units (e.g. cents)."""
        return self._account_info.balance

    @property
    def balance_major(self) -> MajorUnit:
        """MajorUnit: The current balance in major units (e.g. dollars)."""
        return self._account_info.balance.to_major()

    @property
    def raw_copy_ledger(self) -> list[BankAccountLedgerRow]:
        """list: A deep copy of the ledger, safe to modify without affecting the original."""
        return cast(list[BankAccountLedgerRow], self._ledger.raw_copy_ledger)  # noqa

    @property
    def ledger_col_count(self) -> int:
        """int: The number of columns defined in the ledger."""
        return self._ledger.col_count

    @property
    def ledger_header(self) -> list[str]:
        return self._ledger.header

    @property
    def account_name(self) -> str:
        """str: The name assigned to this account."""
        return self._account_info.account_name

    @property
    def account_type(self) -> AccountType:
        """AccountType: The type/category of this account."""
        return self._account_info.account_type

    def make_a_transaction(self, date_in: date, action: str, credit: MinorUnit, debit: MinorUnit) -> None:
        """
        Record a financial transaction and update the account balance and ledger.

        Parameters
        ----------
            date_in : date
                The date of the transaction.
            action : str
                A short description of the transaction (e.g., "Deposit", "Payment").
            credit : MinorUnit
                Amount added to the account balance.
            debit : MinorUnit
                Amount subtracted from the account balance.
        """
        self._account_info.update_balance(credit=credit, debit=debit)
        self._ledger.add_entry_to_ledger(
            BankAccountLedgerRow(
                row_number=self._ledger.row_number,
                date=date_in,
                description=action,
                credit=credit.to_major(),
                debit=debit.to_major(),
                balance=self._account_info.balance.to_major(),
            )
        )
