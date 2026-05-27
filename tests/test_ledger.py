import datetime

import pytest

from models.ledger import BankAccountLedgerRow, Ledger, StandardLedgerRow
from models.utils import MajorUnit

# --- Fixtures ---


@pytest.fixture
def ledger():
    """Ledger instance initialized with default columns."""
    return Ledger(ledger_row_type=StandardLedgerRow)


# --- Tests ---


def test_ledger_initialization(ledger):
    """Ensure ledger initializes with given columns."""
    assert ledger.header == StandardLedgerRow.COLUMNS


def test_col_count(ledger):
    """Ensure column count is correct."""
    assert ledger.col_count == len(StandardLedgerRow.COLUMNS)


def test_add_valid_entry(ledger):
    """Adding a valid entry should append it to the ledger."""
    entry = StandardLedgerRow(
        row_number=1,
        date=datetime.date(2025, 11, 8),
        description="Deposit",
        credit=MajorUnit(100.00),
    )
    ledger.add_entry_to_ledger(entry)
    assert ledger.raw_copy_ledger[-1] == entry


def test_add_invalid_entry_length(ledger):
    """Entries with wrong number of fields should raise ValueError."""
    bad_entry = BankAccountLedgerRow(
        row_number=2,
        date=datetime.date(2025, 11, 8),
        description="Deposit",
        credit=MajorUnit(100),
        debit=MajorUnit(0),
        balance=MajorUnit(100),
    )
    with pytest.raises(ValueError):
        ledger.add_entry_to_ledger(bad_entry)


def test_ledger_returns_copy(ledger):
    """Ensure ledger property returns a copy, not direct reference."""
    copy = ledger.raw_copy_ledger
    copy.append(
        StandardLedgerRow(
            row_number=2,
            date=datetime.date(2025, 11, 8),
            description="Deposit",
            credit=MajorUnit(100.00),
        )
    )
    assert len(ledger.raw_copy_ledger) == 0  # Ledger should remain unchanged


if __name__ == "__main__":
    pytest.main([__file__])
