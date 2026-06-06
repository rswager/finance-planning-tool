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
| Done     | `Income` — `to_dict` / `from_dict` implemented; pass 1 creates with empty `account_contributions`; pass 2 calls `set_account_contribution` with resolved accounts                |
| Done     | `BillBase` — make `payment_method_in` optional (default `None`); add `payment_method` property that raises clearly if accessed before linking; add `update_payment_method(account: Chargeable)` method for pass 2 |
| Done     | `Chargeable` protocol — add `account_name` to narrow accidental implementors (e.g. `FinancedBill` satisfies it via `make_a_transaction` but is not intended to be chargeable); also investigate whether the protocol approach is the right long-term pattern vs. an alternative (e.g. explicit base class or registry) for tracking what is chargeable as the codebase grows |
| Low      | `RevolvingCreditBill` — `payment_method_in` should ideally only accept `BankAccount`; two-pass design may have resolved the original constraint; revisit when implementing payment method deletion or narrowing |
| Done     | Consider reorganizing `models/` into subfolders (e.g. `accounts/`, `bills/`) — directory is growing and grouping would improve navigation                                          |

**Registry pattern:** `from_dict` methods accept a `registry: dict[str, Chargeable]`. The caller builds this dict and passes it in; `from_dict` looks up references by name. Circular `Chargeable` references (A's payment method is B, B's is A) are unsupported by design.

**Two-pass deserialization:** Rather than enforcing strict load order, the top-level loader uses two passes:

- **Pass 1 (Build):** Deserialize all objects. Bills are created with `payment_method=None`; Income is created with empty `account_contributions`. Record `(bill, account_name)` and `(income, [account_names])` pairs for later linking. Add every completed object to the registry as it's built.
- **Pass 2 (Link):** For each recorded bill pair, look up the real account in the now-complete registry and call `bill.update_payment_method(real_account)`. For each Income, call `set_account_contribution` with resolved accounts. Any unresolved name at this point is a data error and should raise.

The `payment_method` property raises a clear `RuntimeError` if accessed before `update_payment_method` is called, providing a loud guard without a placeholder class.

### File Save / Load

A top-level module (separate from the models) owns load/save orchestration.

| Priority | Item |
|----------|------|
| High | Write all models to a single JSON file via a top-level serializer |
| High | On load: deserialize in order (BankAccounts → RevolvingCreditBills → Income → Bills), building the registry incrementally so each step can resolve references from the previous step |
