# TODO

## Tooling

| Priority  | Item |
|-----------|------|
| A/trivial | Add `detect-secrets` as first pre-commit hook; create `.secrets.baseline` |
| B/trivial | Add `.gitattributes` with `* text=auto` for consistent line endings across platforms |
| B/trivial | Add `from __future__ import annotations` to all modules (currently missing everywhere except `utils.py`) |
| B/small   | Add `pytest-cov` dev dependency; configure 80% coverage floor in `pyproject.toml` under `[tool.pytest.ini_options]` |
| High      | Investigate what [tool.ty.environment] `python =` is needed to work cross platform.                                                                                                       |
| Medium    | Enable ruff `D` (pydocstyle) rules — audit all docstrings for presence and format compliance first; add `ignore = ["D203", "D212"]` and `"tests/*.py" = ["D"]` per-file ignore when ready |

## Bugs

| Priority | Item |
|----------|------|
| A/trivial | `utils.py:MinorUnit.from_major` — uses `int()` which truncates on some float inputs (e.g. `int(2.7 * 100) = 269` not 270); use `round()` instead |
| A/trivial | `main.py:53` — `assert chart is not None` is stripped by `python -O`; replace with `if chart is None: raise RuntimeError(...)` |
| B/trivial | `bill_base.py:payment_method` raises `ValueError("Payment method not set.")`; design doc specifies `RuntimeError` — fix to match |

## Design

### Serialization — `to_dict` / `from_dict`

| Priority | Item |
|----------|------|
| Low      | `RevolvingCreditBill` — `payment_method_in` should ideally only accept `BankAccount`; two-pass design may have resolved the original constraint; revisit when implementing payment method deletion or narrowing |
| Done     | Consider reorganizing `models/` into subfolders (e.g. `accounts/`, `bills/`) — directory is growing and grouping would improve navigation                                          |

### Architecture / Code Quality

| Priority | Item |
|----------|------|
| A/small   | `main.py` — wrap all simulation and Excel-output code in a function; call it from `if __name__ == "__main__":`; the current `pass` guard is dead code and importing the module runs a full 10-year simulation |
| A/small   | `to_dict` reaches into private attributes of sibling objects — add public properties: `AccountInformation.initial_balance`, `Interest.apr_rate`, `TriggerDays.frequency` |
| A/trivial | `main.py:272-273` — replace `os.path.join` / `os.path.expanduser` with `pathlib.Path`; remove the `os` import |
| B/small   | `bill_base.py:BillBase.to_dict` / `from_dict` — convert from `NotImplementedError` to `@abstractmethod` so the type system catches incomplete subclasses |
| B/trivial | All `from_dict` methods — annotate the untyped `dict_in` parameter as `dict[str, Any]` |
| C/trivial | `main.py` simulation loops — replace `for key in dict: dict[key].method()` with `for item in dict.values(): item.method()` |
| C/small   | `_accountInfo` — rename to `_account_info` throughout (`bill_base.py`, `bank_account.py`, and all usages) to match snake_case convention |
| C/medium  | All `__init__.py` files — add one-line module docstrings and define `__all__` as sorted tuples |
| C/medium  | `AccountInformation` — convert to `@dataclass(frozen=False)` to remove boilerplate `__init__` and property definitions |
| C/small   | `_dirs.py` — move from project root into an appropriate package |
| C/large   | Adopt `src/` layout to prevent accidental source-tree imports |

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

---

## Tests

| Priority | Item |
|----------|------|
| A/trivial | Remove `tests/__init__.py` — the test directory must not be a package (causes import shadowing) |
| B/small   | `test_bill_financed.py:81` — replace direct `_accountInfo._balance` mutation with a small-balance loan constructed via the public constructor |
| B/small   | `test_income.py:38-44` — add public `name` and `contributions` properties to `Income`; update tests to use them instead of `_income_name` / `_account_contributions` |
| B/small   | Add integration test for the credit-card charging path: `RecurringBill` with a `RevolvingCreditBill` as its payment method (the `CrunchyRoll`/`Spotify` pattern) |
| C/trivial | `test_utils.py` — remove direct tests of private `_calculate_rounded_value`; behavior is already covered by `test_round_value` |

---

## Docs

| Priority | Item |
|----------|------|
| B/medium | README — add "What this is not" section, explicit Goals as validatable commitments, and platform intent statement |
| B/small  | Add `CHANGELOG.md` following the format in DMP standards (heading per release, bold section labels) |
