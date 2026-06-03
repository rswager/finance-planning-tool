# TODO

## Tooling

| Priority | Item |
|----------|------|
| Medium | Enable ruff `D` (pydocstyle) rules — audit all docstrings for presence and format compliance first; add `ignore = ["D203", "D212"]` and `"tests/*.py" = ["D"]` per-file ignore when ready |

## Bugs

| Priority | Item |
|---|---|
|---| NO BUGS TO ADDRESS

## Design

### Serialization — `to_dict` / `from_dict`

Add `to_dict` and `from_dict` class methods to each model. Order matters — objects with no dependencies come first so the registry can be built up before objects that reference others.

| Priority | Item                                                                                                                                                                               |
|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Done     | `BankAccount` — no object references; serialize standalone                                                                                                                         |
| Done     | `BillBase` — raises `NotImplementedError` on both methods; concrete subclasses must implement                                                                                      |
| Done     | `RecurringBill` — extends `BillBase`; no extra fields beyond base                                                                                                                  |
| Done     | `FinancedBill` — extends `BillBase`; adds `apr_rate`                                                                                                                               |
| Done     | `RevolvingCreditBill` — extends `FinancedBill`; adds `credit_limit`                                                                                                                |
| Done     | `bill_*` — tests added for to_dict, from_dict round-trip, and missing-key errors                                                                                                   |
| High     | `Income` — `account_contributions` is `list[tuple[BankAccount, float]]`; serialize as `[{account_name, contribution}]`; `from_dict` needs a registry to resolve account references |
| Medium   | `bill_*` — `payment_method_in` uses `# ty: ignore[unresolved-attribute]` because `account_name` is not on `Chargeable`; fix by adding `account_name` to the protocol              |
| Medium   | `RevolvingCreditBill` — `payment_method_in` should only accept `BankAccount` but kept as `Chargeable` for LSP compliance; investigate `cast()` or protocol narrowing approach      |
| Medium   | Consider reorganizing `models/` into subfolders (e.g. `accounts/`, `bills/`) — directory is growing and grouping would improve navigation                                          |

**Registry pattern:** `from_dict` methods accept a `registry: dict[str, Chargeable]`. The caller builds this dict in order before calling `from_dict`. Circular `Chargeable` references (A's payment method is B, B's is A) are unsupported by design.

**Deserialization order:** `BankAccounts → RevolvingCreditBills → Income → Bills (RecurringBill, FinancedBill)`

### File Save / Load

A top-level module (separate from the models) owns load/save orchestration.

| Priority | Item |
|----------|------|
| High | Write all models to a single JSON file via a top-level serializer |
| High | On load: deserialize in order (BankAccounts → RevolvingCreditBills → Income → Bills), building the registry incrementally so each step can resolve references from the previous step |
