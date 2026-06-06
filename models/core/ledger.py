import dataclasses
from collections.abc import Iterator
from copy import deepcopy
from dataclasses import astuple, dataclass
from datetime import date
from typing import Any, ClassVar

from models.core.utils import MajorUnit


@dataclass(frozen=True)
class StandardLedgerRow:
    row_number: int
    date: date
    description: str
    credit: MajorUnit
    COLUMNS: ClassVar[list[str]] = ["No.", "Date", "Description", "Credit"]

    def __iter__(self) -> Iterator[Any]:
        return iter(astuple(self))

    def __len__(self) -> int:
        return len(dataclasses.fields(self))


@dataclass(frozen=True)
class BankAccountLedgerRow(StandardLedgerRow):
    debit: MajorUnit
    balance: MajorUnit
    COLUMNS: ClassVar[list[str]] = StandardLedgerRow.COLUMNS + ["Debit", "Balance"]


@dataclass(frozen=True)
class InterestLedgerRow(BankAccountLedgerRow):
    interest_to_date: MajorUnit
    COLUMNS: ClassVar[list[str]] = BankAccountLedgerRow.COLUMNS + ["Interest To Date"]


@dataclass(frozen=True)
class RecurringLedgerRow(StandardLedgerRow):
    debit: MajorUnit
    paid_to_date: MajorUnit
    COLUMNS: ClassVar[list[str]] = StandardLedgerRow.COLUMNS + ["Debit", "Total Paid To Date"]


class Ledger:
    """
    Represents a simple ledger for tracking financial transactions.

    Attributes
    ----------
        _header : list[str]
            A list of columns for the ledger.
        _ledger : list[StandardLedgerRow]
            The internal ledger data including transaction entries,
            as StandardLedgerRow (including inherited Dataclasses)
        _col_count : int
            The number of columns in the ledger.
    """

    def __init__(self, ledger_row_type: type[StandardLedgerRow]) -> None:
        """
        Initialize a Ledger with column headers.

        Parameters
        ----------
        ledger_row_type : type[StandardLedgerRow]
                The ledger row class to use for this bill (e.g. RecurringLedgerRow, InterestLedgerRow).
        """
        self._ledger_row_type = ledger_row_type
        self._header: list[str] = ledger_row_type.COLUMNS  # type: ignore[attr-defined]
        self._ledger: list[StandardLedgerRow] = []
        self._col_count = len(self._header)

    @property
    def raw_copy_ledger(self) -> list[StandardLedgerRow]:
        """
        list: Returns a deep copy of the ledger to prevent modifications to the original.
        """
        # return a copy
        return deepcopy(self._ledger)

    @property
    def header(self) -> list[str]:
        return self._header

    @property
    def col_count(self) -> int:
        """
        int: Returns the number of columns in the ledger.
        """
        return self._col_count

    def add_entry_to_ledger(self, entry: StandardLedgerRow) -> None:
        """
        Append a new entry to the ledger.

        Parameters
        ----------
        entry : StandardLedgerRow
            A StandardLedgerRow (and Inherited Dataclasses) of values corresponding to each column in the ledger.

        Raises
        ------
        ValueError
            If the entry does not match the number of columns in the ledger.
        """
        # Append a new entry to the ledger
        if len(entry) != self._col_count:
            raise ValueError(f"Entry must have {self._col_count} elements. {len(entry)} elements in entry")
        self._ledger.append(entry)

    @property
    def row_number(self) -> int:
        """
        int: Returns the next row number for a new entry.
        Starts at 1 because row 0 contains column headers.
        """
        return len(self._ledger)


if __name__ == "__main__":
    my_ledge = StandardLedgerRow(row_number=1, date=date(2021, 1, 1), description="My Ledger", credit=MajorUnit(100))
    my_bank = BankAccountLedgerRow(
        row_number=1,
        date=date(2021, 1, 1),
        description="My Ledger",
        credit=MajorUnit(100),
        debit=MajorUnit(100),
        balance=MajorUnit(0),
    )
    print(my_bank.row_number)
