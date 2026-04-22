# CLAUDE.md

Guidelines for AI assistants working in this repository.

## Before writing files

Enter plan mode before making any file changes. Present the plan and get approval before proceeding.

## Task tracking

When planning work with 3 or more steps, record tasks in a git-ignored `TODO.local.md` at the project root rather than relying on in-context tracking. This file survives context compaction and provides continuity across long sessions. Keep it up-to-date as tasks are completed, added, or decided against.

## Philosophy

Solve the actual problem at hand, not a more general one — this guards against over-engineering and scope creep.

Use names, types, and signatures to give callers correct expectations. Code's job is to satisfy those expectations without surprises.

Code must be correct, reliable, performant, and well-tested.

First drafts are drafts. Refactoring toward simplicity is part of the work, not gold-plating.

## Commit messages

Use imperative mood: "Add feature" not "Added feature". Do not add `Co-Authored-By` trailers. Explain the "why" in the commit body for non-trivial changes.

## Running tasks

Always use `pixi run` for development tasks — do not call `python`, `pytest`, `ruff`, or `ty` directly.

```bash
pixi run test        # run tests
pixi run typecheck   # type check
pixi run ruff        # lint
pixi run check       # all pre-commit hooks
```

Pre-commit runs pytest on every commit. Tests must pass before a commit will land.

## Type annotations

Annotate all function signatures, including return types. Functions with no return value use `-> None`.

- **Parameters**: accept the broadest reasonable type that accomplishes what the function needs
- **Return types**: return the narrowest useful type

## Monetary values

All monetary amounts are stored and calculated in `MinorUnit` (integer minor units, e.g. cents for USD). Never use raw `int` or `float` for money.

- Use `MinorUnit.from_major(x)` to convert user-facing dollar amounts into `MinorUnit`
- Use `.to_major()` for display or ledger output only
- The active currency defaults to USD and can be changed via `MinorUnit.set_currency(CurrencyType.X)`

## Intentional design decisions

Do not flag these as issues — they are deliberate:

- **`round_up_down`** — a single bool that applies conservative rounding throughout: expenses round up, income rounds down. This is intentional budgeting behavior.
- **`Mortgage` / `Mortgage_Escrow` split** — these are two separate entries by design. `Mortgage` covers principal and interest (a `FinancedBill` with a diminishing balance), and `Mortgage_Escrow` covers insurance and taxes (a `RecurringBill` that never pays off). They are not duplicates.

## Communication

When an alternative approach is offered, treat it as discussion — weigh pros and cons together rather than treating it as a directive.
