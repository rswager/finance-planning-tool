# CHANGELOG

## Unreleased

Ongoing domain model improvements and code quality fixes identified in the June 2026 audit.

**Internal:**
- Planned: replace `print()` in serializer with loguru, fix `assert` on file-loaded data,
  add public properties to remove `to_dict` private cross-access, fix test private-attribute
  access, `main.py` scaffolding cleanup

---

## v0.1.0 (2026-06-28)

Initial release establishing the core domain model, simulation engine, persistence layer,
and developer tooling pipeline.

**Features:**
- Domain models: `BankAccount`, `RecurringBill`, `FinancedBill`, `RevolvingCreditBill`,
  `Income` — each with `to_dict` / `from_dict` serialization
- Two-pass JSON persistence: serialize all objects to a file; reconstruct with
  payment-method linking on load
- 10-year daily simulation in `main.py`; outputs a multi-sheet Excel workbook with
  per-account ledgers and balance charts
- `MinorUnit` / `MajorUnit` monetary value types with currency support and
  conservative rounding
- `Ledger` with typed row dataclasses (`BankAccountLedgerRow`, `InterestLedgerRow`,
  `RecurringLedgerRow`)
- `TriggerDays` for flexible payment scheduling (monthly, bi-weekly, etc.)

**Internal:**
- Pixi-managed environment with fully-pinned `pixi.lock`
- Pre-commit pipeline: detect-secrets, ruff (lint + format), codespell, ty, pytest
- `src/` layout with hatchling build backend and editable pixi path dependency
- 219 tests, 100% domain-model coverage; 80% floor enforced
- Cross-platform: win-64, linux-64, osx-64, osx-arm64
