# Code Boilerplate Vault (`cb`)

Code Boilerplate Vault is a Python command-line snippet vault for students and data scientists. It is designed to save reusable code snippets, terminal commands, and assignment templates so they are easy to find and reuse from the terminal.

This repository is being built as a DSC 190 final project. The first commit focuses on the package frame; the next commits will fill in the full MVP behavior.

## Usage

Planned commands:

```bash
cb init
cb add plot-hist --tag python --tag seaborn --description "Histogram template"
cb list
cb get plot-hist
cb copy plot-hist
cb search pandas
cb delete plot-hist
```

## Installation

During local development:

```bash
uv sync
uv run cb --help
```

After the package is pushed to GitHub, it should be installable with:

```bash
uv add "git+https://github.com/<your-username>/<your-repo>.git"
```

## Development

Run tests with:

```bash
uv run pytest
```

## Future Improvements

- categories
- import/export markdown
- fuzzy search
- project-specific snippet collections
- optional sync
