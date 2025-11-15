from copy import deepcopy

class Ledger:
    def __init__(self, columns:list) -> None:
        self._ledger = [columns]
        self._col_count = len(columns)

    @property
    def ledger(self) -> list:
        # return a reference
        return self._ledger

    @property
    def raw_copy_ledger(self) -> list:
        # return a copy
        return deepcopy(self._ledger)

    @property
    def col_count(self) -> int:
        return self._col_count

    def add_entry_to_ledger(self, entry: list) -> None:
        # Append a new entry to the ledger
        expected_length = len(self.ledger[0])
        if len(entry) != expected_length:
            raise ValueError(f"Entry must have {expected_length} elements. {len(entry)} elements in entry")
        self._ledger.append(entry)

    @property
    def row_number(self) -> int:
        return len(self._ledger)