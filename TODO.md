# TODO

## Tooling

| Priority  | Item |
|-----------|------|
| Done      | Add `detect-secrets` as first pre-commit hook; create `.secrets.baseline` |
| Done      | Add `.gitattributes` with `* text=auto` for consistent line endings across platforms |
| Done      | Add `from __future__ import annotations` to all modules |
| Done      | Add `pytest-cov` dev dependency; configure 80% coverage floor in `pyproject.toml` |
| B/small   | `[tool.ty.environment] python = ".pixi/envs/default"` — confirmed needed for pixi envs; open question is whether the path resolves correctly on Linux/Mac where the Python binary is at `bin/python` vs `python.exe` on Windows |
| Medium    | Enable ruff `D` (pydocstyle) rules — audit all docstrings for presence and format compliance first; add `ignore = ["D203", "D212"]` and `"tests/*.py" = ["D"]` per-file ignore when ready |

## Bugs

| Priority | Item |
|----------|------|
| Done      | `utils.py:MinorUnit.from_major` — uses `int()` which truncates on some float inputs; use `round()` instead |
| A/trivial | `main.py:73` — `assert chart is not None` is stripped by `python -O`; replace with `if chart is None: raise RuntimeError(...)` |
| B/trivial | `bill_base.py:payment_method` raises `ValueError("Payment method not set.")`; design doc specifies `RuntimeError` — fix to match; `test_serializer.py:74` and `test_bill_base.py` also need updating |

## Design

### Serialization — `to_dict` / `from_dict`

| Priority | Item |
|----------|------|
| Low      | `RevolvingCreditBill` — `payment_method_in` should ideally only accept `BankAccount`; two-pass design may have resolved the original constraint; revisit when implementing payment method deletion or narrowing |
| Done     | Consider reorganizing `models/` into subfolders (e.g. `accounts/`, `bills/`) — directory is growing and grouping would improve navigation                                          |

### Architecture / Code Quality

| Priority | Item |
|----------|------|
| Done      | `main.py` — wrap all simulation and Excel-output code in a function; call it from `if __name__ == "__main__":` |
| A/small   | `to_dict` reaches into private attributes of sibling objects — add public properties: `AccountInformation.initial_balance`, `Interest.apr_rate`, `TriggerDays.frequency` |
| A/trivial | `main.py:297-298` — replace `os.path.join` / `os.path.expanduser` with `pathlib.Path`; remove the `os` import |
| B/small   | `serializer.py:66,79,92,96` — Replace `print()` with loguru; tag `logger.bind(library="finance_planning_tool")`; silent drops of financial records are a data-loss risk — log at WARNING minimum |
| B/trivial | `serializer.py:82` — `assert isinstance(chargeable_account, Chargeable)` is stripped by `python -O`; replace with `if/raise` |
| B/question | `serializer.py:71-83` — Payment-method linker looks up accounts by `payment_method_in` (account_name string) but the outer dict is keyed by collection key, which may differ (e.g. `"Car_Payment_Ford"` vs `"Car Payment - Ford"`); document the key==name invariant or fix the lookup |
| Done      | `bill_base.py:BillBase.to_dict` / `from_dict` — convert from `NotImplementedError` to `@abstractmethod` |
| Done      | All `from_dict` methods — annotate the untyped `dict_in` parameter as `dict[str, Any]` |
| C/trivial | `main.py` simulation loops — replace `for key in dict: dict[key].method()` with `for item in dict.values(): item.method()` |
| Done      | `_accountInfo` — rename to `_account_info` throughout |
| C/medium  | All `__init__.py` files — add one-line module docstrings and define `__all__` as sorted tuples |
| C/medium  | `AccountInformation` — convert to `@dataclass(frozen=False)` to remove boilerplate `__init__` and property definitions |
| C/small   | `_dirs.py` — move from project root into an appropriate package |
| Done      | Adopt `src/` layout to prevent accidental source-tree imports |
| C/trivial | `ledger.py:row_number` docstring says "starts at 1 (row 0 is headers)" but returns `len(self._ledger)`, which is 0 on empty — fix the docstring |
| C/trivial | Missing class docstrings: `bill_base.py:BillBase`, `chargeable.py:Chargeable`; missing module docstring: `main.py` |
| C/trivial | `ledger.py:126-136` — `if __name__ == "__main__":` scratch block; remove it |
| C/trivial | `income.py:116` — `sum()` over all prior contributions on every loop iteration is O(n²); replace with a running-total accumulator |
| C/trivial | `income.py:55` — `round_up=not round_down` in the else branch always evaluates to `False`; replace with the literal `False` |
| C/question | `income.py:63-66` — `Income.account_name` exists only to satisfy the registry-by-name pattern; consider renaming to `name` or documenting the intent |

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
| Done        | Build serializer — takes model objects, calls `to_dict()` on each, passes results to JSON writer                                                                      |
| Done        | Build deserializer — reads dicts from JSON reader, uses dispatch table + `from_dict()` for two-phase reconstruction into model objects                                |
| Done        | Write a test verifying every serializable class's `TYPE_KEY` is present in the dispatch table                                                                         |
| Done        | Use `pathlib.Path` for all file paths in the persistence layer to ensure OS-agnostic behavior                                                                         |

**TYPE_KEY / dispatch table:** Each serializable class defines a stable `TYPE_KEY = "some_string"` constant. `to_dict()` emits this as `"type"`. The persistence layer holds a dispatch table `{TYPE_KEY: Class}` — the only place that imports model classes, avoiding circular imports. A class rename does not silently break saved files because `TYPE_KEY` is an explicit constant, not derived from the class name.

---

## Tests

| Priority | Item |
|----------|------|
| Done      | Remove `tests/__init__.py` |
| B/small   | `test_bill_financed.py:61` — replace direct `_account_info._balance` mutation with a small-balance loan constructed via the public constructor |
| B/small   | `test_bill_revolving_credit.py:25` — replace direct `_account_info._balance` mutation with a loan constructed at the right initial balance |
| B/small   | `test_income.py:18-21,131` — accesses `_income_name`, `_account_contributions`, `_trigger_days` directly; add public `name` and `contributions` properties to `Income` |
| B/small   | `test_bill_base.py:30,34` — reads `_payment_method` and mutates it to trigger the error path; expose via a fixture constructed without a payment method instead |
| B/small   | `test_interest.py:41` — accesses `_interest_to_date` directly; `Interest` already has a public `interest_to_date` property — use it |
| B/small   | `test_bill_recurring.py:28` — accesses `_minimum_payment` directly; add a public `minimum_payment` property to `BillBase` |
| B/small   | Add integration test for the credit-card charging path: `RecurringBill` with a `RevolvingCreditBill` as its payment method (the `CrunchyRoll`/`Spotify` pattern) |
| C/trivial | `test_utils.py` — remove direct tests of private `_calculate_rounded_value`; behavior is already covered by `test_round_value` |

---

## Docs

| Priority | Item |
|----------|------|
| Done     | README — add "What this is not" section, explicit Goals as validatable commitments, and platform intent statement |
| Done     | Add `CHANGELOG.md` following the format in DMP standards (heading per release, bold section labels) |
