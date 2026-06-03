# TODO

## Bugs

| Priority | Item |
|---|---|
|---| NO BUGS TO ADDRESS

## Design

### Serialization — `to_dict` / `from_dict`

Add `to_dict` and `from_dict` class methods to each model. Order matters — objects with no dependencies come first so the registry can be built up before objects that reference others.

| Priority | Item                                                                                                                                                                              |
|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| High     | `BankAccount` — no object references; serialize standalone                                                                                                                        |
| High     | `BillBase` — shared fields (name, balance, minimum payment, frequency, date); `from_dict` needs a `registry` parameter to resolve `payment_method` by name                        |
| High     | `RecurringBill` — extends `BillBase`; no extra fields beyond base                                                                                                                 |
| High     | `FinancedBill` — extends `BillBase`; adds `apr_rate`                                                                                                                              |
| High     | `RevolvingCreditBill` — extends `FinancedBill`; adds `credit_limit`                                                                                                               |
| High     | `Income` — `account_contributions` is `list[tuple[BankAccount, float]]`; serialize as `[{account_name, contribution}]`; `from_dict` needs a registry to resolve account references |
| Medium   | `bill_*` — need to investigate how to handle the payment_method_in ty error in to_dict                                                                                             |

**Registry pattern:** `from_dict` methods that need live objects accept a `registry: dict[str, Chargeable]` (or `dict[str, BankAccount]` for `Income`). The caller builds this dict before calling `from_dict`. `RevolvingCreditBill` satisfies `Chargeable` and must also be added to the registry if used as a payment method.

### File Save / Load

A top-level module (separate from the models) owns load/save orchestration.

| Priority | Item |
|----------|------|
| High | Write all models to a single JSON file via a top-level serializer |
| High | On load: deserialize in order (accounts → bills → income), building the registry incrementally so each step can resolve references from the previous step |
