from copy import deepcopy


class Ledger:
    """
    Represents a simple ledger for tracking financial transactions.

    Attributes
    ----------
        _ledger : list
            The internal ledger data including column headers and transaction entries.
        _col_count : int
            The number of columns in the ledger.
    """

    def __init__(self, columns: list) -> None:
        """
        Initialize a Ledger with column headers.

        Parameters
        ----------
        columns : list
            A list of column names for the ledger.
        """
        self._ledger = [columns]
        self._col_count = len(columns)

    @property
    def raw_copy_ledger(self) -> list:
        """
        list: Returns a deep copy of the ledger to prevent modifications to the original.
        """
        # return a copy
        return deepcopy(self._ledger)

    @property
    def col_count(self) -> int:
        """
        int: Returns the number of columns in the ledger.
        """
        return self._col_count

    def add_entry_to_ledger(self, entry: list) -> None:
        """
        Append a new entry to the ledger.

        Parameters
        ----------
        entry : list
            A list of values corresponding to each column in the ledger.

        Raises
        ------
        ValueError
            If the entry does not match the number of columns in the ledger.
        """
        # Append a new entry to the ledger
        expected_length = len(self._ledger[0])
        if len(entry) != expected_length:
            raise ValueError(f"Entry must have {expected_length} elements. {len(entry)} elements in entry")
        self._ledger.append(entry)

    @property
    def row_number(self) -> int:
        """
        int: Returns the next row number for a new entry.
        Starts at 1 because row 0 contains column headers.
        """
        return len(self._ledger)
