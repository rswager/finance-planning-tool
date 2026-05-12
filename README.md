# finance-planning-tool

A financial modeling tool that lets users enter account and payment details, then simulates daily activity, compounding interest, and recurring payments to generate multi-year projections and a detailed transaction ledger for personal financial analysis.

---

## Getting Started

This project uses [Pixi](https://pixi.sh) to manage the Python environment and development tools. Pixi handles all dependencies — you do not need to create a virtual environment manually.

### Prerequisites

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
pixi run python main.py
```

The start date, end date, account balances, and all bill/income parameters are configured directly in `main.py`.

---

## Development tasks

```bash
pixi run test          # run the test suite
pixi run ruff          # lint the codebase
pixi run ruff-fix      # lint and auto-fix what ruff can
pixi run ruff-format   # format all files
pixi run typecheck     # run ty type checking
pixi run check         # run all pre-commit hooks against every file
```

---

## Development Tools

### Pixi

[Pixi](https://pixi.sh) is a cross-platform package manager built on the conda ecosystem. It reads `pyproject.toml` to resolve a fully locked environment and pins all dependencies in `pixi.lock`. Every developer gets an identical environment regardless of what is already installed on their machine.

Key files:
- `pyproject.toml` — declares dependencies and pixi tasks under `[tool.pixi.*]`
- `pixi.lock` — the resolved lockfile (committed to source control for reproducibility)
- `.pixi/` — the local environment directory (git-ignored)

### Ruff

[Ruff](https://docs.astral.sh/ruff/) is a fast Python linter and formatter written in Rust. It replaces flake8, isort, and black in a single tool.

- `pixi run ruff` — checks for lint errors
- `pixi run ruff-fix` — auto-fixes lint errors where possible
- `pixi run ruff-format` — formats code (like black)

Configuration lives under `[tool.ruff]` in `pyproject.toml`.

### ty

[ty](https://github.com/astral-sh/ty) is a fast Python type checker from Astral (the same team behind Ruff and uv). It checks type annotations without requiring a fully annotated codebase.

- `pixi run typecheck` — runs `ty check` against the project

### pytest

[pytest](https://docs.pytest.org) is the test framework used for all unit tests. Tests live in the `tests/` directory.

- `pixi run test` — runs the full test suite

### pre-commit

[pre-commit](https://pre-commit.com) runs a set of checks automatically before each `git commit`. It prevents bad code from entering the repository without requiring manual tool runs.

Hooks configured in `.pre-commit-config.yaml`:

| Hook | What it does |
|---|---|
| `end-of-file-fixer` | Ensures every file ends with a newline |
| `trailing-whitespace` | Strips trailing whitespace |
| `check-toml` | Validates `pyproject.toml` syntax |
| `check-merge-conflict` | Blocks commits that contain unresolved merge conflict markers |
| `debug-statements` | Catches leftover `breakpoint()` / `pdb` calls |
| `check-added-large-files` | Blocks files over 500 KB from being committed |
| `ruff` | Lints and auto-fixes Python files |
| `ruff-format` | Formats Python files |
| `ty` | Runs type checking |
| `pytest` | Runs the test suite |

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
├── models/                  # core domain models (no GUI dependencies)
│   ├── accountInformation.py
│   ├── bankAccount.py
│   ├── enumType.py
│   ├── financed_bill.py
│   ├── income.py
│   ├── interest.py
│   ├── ledger.py
│   ├── recurring_bill.py
│   ├── revolving_credit_bill.py
│   ├── triggerDays.py
│   └── utils.py
├── tests/                   # pytest unit tests
├── main.py                  # simulation entry point (outputs Excel workbook)
├── pyproject.toml           # project metadata, dependencies, tool config
├── pixi.lock                # fully resolved dependency lockfile
├── .pre-commit-config.yaml  # pre-commit hook definitions
└── TODO.md                  # known issues and design improvements
```

> **AI assistants:** See `CLAUDE.md` for project conventions and guidelines.
