# TODO

## Tooling

| Priority | Item                                                                                                                                                                                      |
|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| High     | Investigate what [tool.ty.environment] `python =` is needed to work cross platform.                                                                                                       |
| Medium   | Enable ruff `D` (pydocstyle) rules — audit all docstrings for presence and format compliance first; add `ignore = ["D203", "D212"]` and `"tests/*.py" = ["D"]` per-file ignore when ready |

## Bugs

| Priority | Item |
|---|---|
|---| NO BUGS TO ADDRESS

## Design

### Serialization — `to_dict` / `from_dict`

| Priority | Item |
|----------|------|
| Low      | `RevolvingCreditBill` — `payment_method_in` should ideally only accept `BankAccount`; two-pass design may have resolved the original constraint; revisit when implementing payment method deletion or narrowing |
