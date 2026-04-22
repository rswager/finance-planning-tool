# TODO

## Bugs

| Priority | Item |
|---|---|
| 🔴 High | `add_table()` crashes with `IndexError` on an empty ledger — `data[0]` is accessed after `data.pop(0)` with no length check |
| 🟡 Medium | `Income.deposit()` silently loses cents — `floor()` on each contribution drops fractional cents (~$26 lost over a 10-year projection on a biweekly $2,557.31 paycheck) |

## Design

| Priority | Item |
|---|---|
| 🟡 Medium | `main.py` has no `if __name__ == '__main__':` guard — the entire simulation runs on import, which will conflict with future GUI work |
| 🟡 Medium | `FinancedBill` and `RevolvingCreditBill` are ~80% identical — `make_payment`, `apply_daily_interest`, `process_day`, and all display properties are duplicated verbatim; extract a shared base class |
| 🟡 Medium | `add_table()` mutates its input via `data.pop(0)` — works today because `raw_copy_ledger` returns a deep copy, but the hidden side effect is fragile; replace with `data = data_in[1:]` |
| 🟢 Low | `get_col()` reimplements `xlsxwriter.utility.xl_col_to_name()` which already exists in the dependency |
| 🟢 Low | `round_up_down = False` is a confusing name for a single bool that controls two inverse parameters (`round_up` / `round_down`) |
