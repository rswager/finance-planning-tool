import datetime

import pytest

from models.ledger import BankAccountLedgerRow, Ledger, StandardLedgerRow
from models.utils import MajorUnit

# --- Fixtures ---


@pytest.fixture
def columns():
    """Default ledger column headers."""
    return StandardLedgerRow.COLUMNS


@pytest.fixture
def ledger(columns):
    """Ledger instance initialized with default columns."""
    return Ledger(columns)


@pytest.fixture
def empty_ledger():
    """Ledger with no columns."""
    return Ledger([])


# --- Tests ---


def test_ledger_initialization(columns, ledger):
    """Ensure ledger initializes with given columns."""
    assert ledger.header == columns


def test_col_count(columns, ledger):
    """Ensure column count is correct."""
    assert ledger.col_count == len(columns)


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


def test_empty_columns(empty_ledger):
    """Empty column list should initialize with empty schema."""
    assert empty_ledger.raw_copy_ledger == []


def test_add_entry_to_empty_columns(empty_ledger):
    """Cannot add entry when there are no defined columns."""
    with pytest.raises(ValueError):
        empty_ledger.add_entry_to_ledger(
            StandardLedgerRow(
                row_number=1,
                date=datetime.date(2025, 11, 8),
                description="Deposit",
                credit=MajorUnit(100.00),
            )
        )


if __name__ == "__main__":
    pytest.main([__file__])
