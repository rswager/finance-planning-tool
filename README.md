# finance-planning-tool

A financial modeling tool that lets users enter account and payment details, then simulates daily activity, compounding interest, and recurring payments to generate multi-year projections and a detailed transaction ledger for personal financial analysis.

---

## Goals

- Model daily financial activity (income deposits, interest accrual, bill payments) over a multi-year period for a configurable set of accounts and bills
- Support bank accounts, recurring bills, financed loans, and revolving credit lines
- Output a multi-sheet Excel workbook: one sheet per account or bill, each with a transaction ledger table and a projected balance chart
- Serve as the domain-model foundation for a future GUI

## What this is not

- Not a live budgeting app — no bank integrations, no real-time data
- Not multi-user
- Not financial advice — projections are only as accurate as the inputs
- Not a distributed or production system — personal tool, runs locally

---

## Getting Started

This project uses [Pixi](https://pixi.sh) to manage the Python environment and development tools. Pixi handles all dependencies — you do not need to create a virtual environment manually.

### Prerequisites

This project supports Windows, macOS (Intel and Apple Silicon), and Linux.

Install Pixi using the method that matches your OS:

**Windows**

```powershell
# winget
winget install prefix-dev.pixi

# Scoop
scoop install pixi

# Official installer script
iwr -useb https://pixi.sh/install.ps1 | iex
```

**macOS**

```bash
# Homebrew
brew install pixi

# Official installer script
curl -fsSL https://pixi.sh/install.sh | bash
```

**Linux**

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

After installing, verify with:

```bash
pixi --version
```

### Install the environment

From the project root:

```bash
pixi install
```

This resolves and installs all dependencies (including dev tools) into an isolated environment under `.pixi/`. Running it again is a no-op if nothing has changed.

---

## Running the application

`main.py` is the simulation entry point. It walks through every day between a start and end date, processing income deposits, interest accrual, and bill payments for each configured account. When the simulation finishes it writes a multi-sheet Excel workbook to `~/Downloads/Output_Analysis.xlsx` — one sheet per account or bill, each with a transaction ledger table and a projected balance line chart.

```bash
pixi run python src/finance_planning_tool/main.py
```

The start date, end date, account balances, and all bill/income parameters are configured directly in `main.py`.

---

## Development tasks

```bash
pixi run check          # run all pre-commit hooks against every file
pixi run test           # run the test suite
pixi run ruff           # lint the codebase
pixi run ruff-fix       # lint and auto-fix what ruff can
pixi run ruff-format    # format all files
pixi run typecheck      # run ty type checking
pixi run codespell      # run codespell to highlight common typos
pixi run codespell-fix  # run codespell in interactive mode to fix common typos
pixi run secrets-scan   # run detects secret to scan and update baseline
pixi run secrets-audit  # run detects secrets in interactive mode to address secrets found, if any
pixi run version-bump   # increment the patch version in pyproject.toml (e.g. 0.1.0 → 0.1.1)
```

---

## Development Tools

### Pixi

[Pixi](https://pixi.sh) is a cross-platform package manager built on the conda ecosystem. It reads `pyproject.toml` to resolve a fully locked environment and pins all dependencies in `pixi.lock`. Every developer gets an identical environment regardless of what is already installed on their machine.

Key files:
- `pyproject.toml` — declares dependencies and pixi tasks under `[tool.pixi.*]`
- `pixi.lock` — the resolved lockfile (committed to source control for reproducibility)
- `.pixi/` — the local environment directory (git-ignored)

### Hatchling

[Hatchling](https://hatch.pypa.io/latest/build/) is the build backend that packages `finance_planning_tool` for installation. It is declared in the `[build-system]` table of `pyproject.toml` and used by pixi to install the package into the local environment in editable mode — `pixi install` handles this automatically.

The package version is stored in `pyproject.toml` under `[project] version`. To bump it:

- `pixi run version-bump` — increments the patch number (e.g. `0.1.0` → `0.1.1`)
- `pixi run hatch version minor` — increments the minor number (e.g. `0.1.0` → `0.2.0`)
- `pixi run hatch version major` — increments the major number (e.g. `0.1.0` → `1.0.0`)

After bumping, update `CHANGELOG.md`, commit, and create an annotated tag so the version is reachable by number later:

```bash
git add pyproject.toml src/finance_planning_tool/__init__.py CHANGELOG.md
git commit -m "Release v0.1.1"
git tag -a v0.1.1 -m "v0.1.1"
git push origin v0.1.1
```

Annotated tags (`-a`) carry a message and are stored as full objects in git, which makes them more useful than lightweight tags for marking releases.

### Ruff

[Ruff](https://docs.astral.sh/ruff/) is a fast Python linter and formatter written in Rust. It replaces flake8, isort, and black in a single tool.

- `pixi run ruff` — checks for lint errors
- `pixi run ruff-fix` — auto-fixes lint errors where possible
- `pixi run ruff-format` — formats code (like black)

Configuration lives under `[tool.ruff]` in `pyproject.toml`.

### codespell

[codespell](https://github.com/codespell-project/codespell) is a spell checker designed for source code. It finds common misspellings in comments, documentation, strings, variable names, and other text files without flagging valid code syntax.

- `pixi run codespell` — checks the project for spelling mistakes
- `pixi run codespell-fix` — interactively fixes common misspellings with user

### Detect Secrets

[Detect Secrets](https://github.com/Yelp/detect-secrets) is a module designed for detecting secrets inside of code bases. It gives a convenient way for identifying exisisting secrets and for identifying and preventing new secrets from entering the code base.

- `pixi run secrets-scan` — Scan the code base and commit it to the baseline
- `pixi run secrets-audit` — Walk through the results and classify them as TP/FP

### ty

[ty](https://github.com/astral-sh/ty) is a fast Python type checker from Astral (the same team behind Ruff and uv). It checks type annotations without requiring a fully annotated codebase.

- `pixi run typecheck` — runs `ty check` against the project

### pytest

[pytest](https://docs.pytest.org) is the test framework used for all unit tests. Tests live in the `tests/` directory.

- `pixi run test` — runs the full test suite
- `pixi run pytest tests/test_income.py` — runs a single test file
- `pixi run pytest tests/test_income.py::test_to_dict` — runs a single test function


### pre-commit

[pre-commit](https://pre-commit.com) runs a set of checks automatically before each `git commit`. It prevents bad code from entering the repository without requiring manual tool runs.

Hooks configured in `.pre-commit-config.yaml`:

| Hook                      | What it does                                                  |
|---------------------------|---------------------------------------------------------------|
| `end-of-file-fixer`       | Ensures every file ends with a newline                        |
| `trailing-whitespace`     | Strips trailing whitespace                                    |
| `check-toml`              | Validates `pyproject.toml` syntax                             |
| `check-merge-conflict`    | Blocks commits that contain unresolved merge conflict markers |
| `debug-statements`        | Catches leftover `breakpoint()` / `pdb` calls                 |
| `check-added-large-files` | Blocks files over 500 KB from being committed                 |
| `ruff`                    | Lints and auto-fixes Python files                             |
| `ruff-format`             | Formats Python files                                          |
| `codespell`               | Identify common typos                                         |
| `Detect Secrets`          | Detect passwords and ... secrets                              |
| `ty`                      | Runs type checking                                            |
| `pytest`                  | Runs the test suite                                           |

#### First-time setup

After `pixi install`, initialize the pre-commit hooks once:

```bash
pixi run setup
```

This installs the hooks into `.git/hooks/` so they fire automatically on every `git commit`. To run all hooks manually against every file at any time:

```bash
pixi run check
```

To update all hooks to their latest versions:

```bash
pixi run pre-commit autoupdate
```

---

## Contributing

### Branch naming

Branches follow the pattern `{action}/{username}/{description}`:

| Action | When to use |
|---|---|
| `feature` | New functionality |
| `bugfix` | Bug fix |
| `debt` | Tech debt / refactoring |
| `docs` | Documentation only |
| `chore` | Tooling, config, housekeeping |

Examples:
- `feature/rswager/add-gui`
- `bugfix/rswager/fix-add-table-crash`
- `debt/rswager/base-class-financed-bills`
- `docs/rswager/add-project-conventions`

---

## Project Structure

```
finance-planning-tool/
├── src/finance_planning_tool
│   ├── _dirs.py                        # app data directory constants (cross-platform)
│   ├── main.py                         # simulation entry point (outputs Excel workbook)
│   └── models/                         # core domain models (no GUI dependencies)
│       ├── accounts/                   # bank accounts and account information
│       │   ├── account_information.py
│       │   └── bank_account.py
│       ├── bills/                      # bill types (recurring, financed, revolving credit)
│       │   ├── bill_base.py
│       │   ├── bill_financed.py
│       │   ├── bill_recurring.py
│       │   └── bill_revolving_credit.py
│       ├── core/                       # shared infrastructure (enums, utils, ledger)
│       │   ├── chargeable.py
│       │   ├── enum_type.py
│       │   ├── interest.py
│       │   ├── ledger.py
│       │   ├── trigger_days.py
│       │   └── utils.py
│       ├── income/                     # income sources
│       │   └── income.py
│       └── persistence/                # file I/O and serialization
│           ├── json_reader_writer.py
│           ├── serial_lookup.py
│           └── serializer.py
├── tests/                              # pytest unit tests
│   ├── conftest.py                     # reusable fixtures
│   └── test_*.py                       # test files
├── pyproject.toml                      # project metadata, dependencies, tool config
├── pixi.lock                           # fully resolved dependency lockfile
├── .pre-commit-config.yaml             # pre-commit hook definitions
└── TODO.md                             # known issues and design improvements
```

> **AI assistants:** See `CLAUDE.md` for project conventions and guidelines.
