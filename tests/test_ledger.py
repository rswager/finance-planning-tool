from datetime import date

import pytest

from finance_planning_tool.models.core import (
    BankAccountLedgerRow,
    InterestLedgerRow,
    MajorUnit,
    RecurringLedgerRow,
    StandardLedgerRow,
)


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
        date=date(2025, 11, 8),
        description="Deposit",
        credit=MajorUnit(100.00),
    )
    ledger.add_entry_to_ledger(entry)
    assert ledger.raw_copy_ledger[-1] == entry


def test_add_invalid_entry_length(ledger):
    """Entries with wrong number of fields should raise ValueError."""
    bad_entry = BankAccountLedgerRow(
        row_number=2,
        date=date(2025, 11, 8),
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
            date=date(2025, 11, 8),
            description="Deposit",
            credit=MajorUnit(100.00),
        )
    )
    assert len(ledger.raw_copy_ledger) == 0  # Ledger should remain unchanged


def test_standard_ledger_row_iter():
    row = StandardLedgerRow(row_number=1, date=date(2025, 1, 1), description="Test", credit=MajorUnit(100))
    assert list(row) == [1, date(2025, 1, 1), "Test", MajorUnit(100)]


@pytest.mark.parametrize(
    "ledger_type",
    [
        (StandardLedgerRow),
        (BankAccountLedgerRow),
        (InterestLedgerRow),
        (RecurringLedgerRow),
    ],
)
def test_COLUMNS_immutable_index_assignment(ledger_type):
    with pytest.raises(TypeError):
        ledger_type.COLUMNS[0] = "Not Allowed"


@pytest.mark.parametrize(
    "ledger_type",
    [
        (StandardLedgerRow),
        (BankAccountLedgerRow),
        (InterestLedgerRow),
        (RecurringLedgerRow),
    ],
)
def test_COLUMNS_immutable_del(ledger_type):
    with pytest.raises(TypeError):
        del ledger_type.COLUMNS[0]


@pytest.mark.parametrize(
    "ledger_type",
    [
        (StandardLedgerRow),
        (BankAccountLedgerRow),
        (InterestLedgerRow),
        (RecurringLedgerRow),
    ],
)
def test_COLUMNS_immutable_slice_assignment(ledger_type):
    with pytest.raises(TypeError):
        ledger_type.COLUMNS[0:2] = ("A", "B")
