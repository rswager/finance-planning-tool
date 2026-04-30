# TODO

## Bugs

*No open bugs.*


## In Progress

### Typed ledger row dataclasses

Replace untyped `list` rows with frozen dataclasses that support inheritance and iteration.

- [x] Add `StandardLedgerRow`, `BankAccountLedgerRow`, `InterestLedgerRow`, `RecurringLedgerRow` to `ledger.py` — frozen dataclasses with `__iter__` via `dataclasses.astuple`
- [x] Update `Ledger.add_entry_to_ledger` to accept `StandardLedgerRow` instead of `list`
- [x] `BankAccount` — construct `BankAccountLedgerRow` in `make_a_transaction`, type `raw_copy_ledger` as `list[BankAccountLedgerRow]`
- [x] `FinancedBill` — construct `InterestLedgerRow` in `make_a_transaction`, type `raw_copy_ledger` as `list[InterestLedgerRow]`
- [x] `RevolvingCreditBill` — same as `FinancedBill`
- [x] `RecurringBill` — construct `RecurringLedgerRow` in `make_a_transaction`, type `raw_copy_ledger` as `list[RecurringLedgerRow]`
- [x] Update `main.py` consumers to use named field access on rows


## Design

| Priority | Item |
|---|---|
| 🟡 Medium | `FinancedBill` and `RevolvingCreditBill` are ~80% identical — `make_payment`, `apply_daily_interest`, `process_day`, and all display properties are duplicated verbatim; extract a shared base class |
| 🟢 Low | `round_up_down = False` is a confusing name for a single bool that controls two inverse parameters (`round_up` / `round_down`) |
| 🟢 Low | `ledger.py` type annotations are too generic — `columns: list` and `entry: list` should be `list[str]` and `list[Any]` |
| 🟢 Low | `add_table()`, `add_chart()` in `main.py` have no type annotations |
