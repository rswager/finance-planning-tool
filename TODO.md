# TODO

## Bugs

*No open bugs.*


## Design

| Priority | Item |
|---|---|
| 🟡 Medium | `main.py` has no `if __name__ == '__main__':` guard — the entire simulation runs on import, which will conflict with future GUI work |
| 🟡 Medium | `FinancedBill` and `RevolvingCreditBill` are ~80% identical — `make_payment`, `apply_daily_interest`, `process_day`, and all display properties are duplicated verbatim; extract a shared base class |
| 🟢 Low | `round_up_down = False` is a confusing name for a single bool that controls two inverse parameters (`round_up` / `round_down`) |
| 🟢 Low | `ledger.py` type annotations are too generic — `columns: list` and `entry: list` should be `list[str]` and `list[Any]` |
| 🟢 Low | `add_table()`, `add_chart()` in `main.py` have no type annotations |
