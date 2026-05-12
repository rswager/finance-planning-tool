# TODO

## Bugs

| Priority | Item |
|---|---|
| 🔴 High | `TriggerDays` does not advance past initial pay dates — if `initial_pay_date_in` is before the simulation start date, the trigger never fires; `TriggerDays` should fast-forward to the next occurrence on or after the first processed day |

## Design

| Priority | Item |
|---|---|
| 🟡 Medium | `FinancedBill` and `RevolvingCreditBill` are ~80% identical — `make_payment`, `apply_daily_interest`, `process_day`, and all display properties are duplicated verbatim; extract a shared base class |
| 🟢 Low | `round_up_down = False` is a confusing name for a single bool that controls two inverse parameters (`round_up` / `round_down`) |
| 🟢 Low | `add_chart()` in `main.py` has no type annotations |
