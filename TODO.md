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

| Priority | Item |
|----------|------|
| Low      | `RevolvingCreditBill` — `payment_method_in` should ideally only accept `BankAccount`; two-pass design may have resolved the original constraint; revisit when implementing payment method deletion or narrowing |
| Done     | Consider reorganizing `models/` into subfolders (e.g. `accounts/`, `bills/`) — directory is growing and grouping would improve navigation                                          |

**Registry pattern:** `from_dict` methods accept a `registry: dict[str, Chargeable]`. The caller builds this dict and passes it in; `from_dict` looks up references by name. Circular `Chargeable` references (A's payment method is B, B's is A) are unsupported by design.

**Two-pass deserialization:** Rather than enforcing strict load order, the top-level loader uses two passes:

- **Pass 1 (Build):** Deserialize all objects. Bills are created with `payment_method=None`; Income is created with empty `account_contributions`. Record `(bill, account_name)` and `(income, [account_names])` pairs for later linking. Add every completed object to the registry as it's built.
- **Pass 2 (Link):** For each recorded bill pair, look up the real account in the now-complete registry and call `bill.update_payment_method(real_account)`. For each Income, call `set_account_contribution` with resolved accounts. Any unresolved name at this point is a data error and should raise.

The `payment_method` property raises a clear `RuntimeError` if accessed before `update_payment_method` is called, providing a loud guard without a placeholder class.

### File Save / Load

A top-level persistence module (separate from the models) owns load/save orchestration.

| Priority    | Item                                                                                                                                                                  |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Done        | Add `TYPE_KEY` class-level constant to each serializable class (accounts, bills, etc.)                                                                                |
| Done        | Update `to_dict()` on each serializable class to include `"type": self.TYPE_KEY`                                                                                      |
| Done        | Create dispatch table in the persistence layer mapping `TYPE_KEY` strings to classes                                                                                  |
| Done        | Build JSON writer — writes list of dicts to a JSON file                                                                                                               |
| Done        | Build JSON reader — reads JSON file, returns list of dicts                                                                                                            |
| High        | Build serializer — takes model objects, calls `to_dict()` on each, passes results to JSON writer                                                                      |
| High        | Build deserializer — reads dicts from JSON reader, uses dispatch table + `from_dict()` for two-phase reconstruction into model objects                                |
| Done        | Write a test verifying every serializable class's `TYPE_KEY` is present in the dispatch table                                                                         |
| Done        | Use `pathlib.Path` for all file paths in the persistence layer to ensure OS-agnostic behavior                                                                         |

**TYPE_KEY / dispatch table:** Each serializable class defines a stable `TYPE_KEY = "some_string"` constant. `to_dict()` emits this as `"type"`. The persistence layer holds a dispatch table `{TYPE_KEY: Class}` — the only place that imports model classes, avoiding circular imports. A class rename does not silently break saved files because `TYPE_KEY` is an explicit constant, not derived from the class name.
