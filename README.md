# Code Boilerplate Vault (`cb`)

Code Boilerplate Vault is a Python command-line snippet vault for students and data scientists. It saves reusable code snippets, terminal commands, and assignment templates so they can be searched, printed, deleted, and copied from the terminal.

The default storage path is:

```text
~/.cb/snippets.json
```

Snippets are stored locally as JSON, so the MVP stays lightweight and easy to inspect.

## Why This Is Useful

Coursework and data science projects often reuse the same small pieces of code: plotting templates, pandas patterns, setup commands, Git commands, and assignment starter files. `cb` keeps those examples in one searchable local vault instead of scattering them across old notebooks, notes, and browser tabs.

## Installation

Install dependencies for local development with `uv`:

```bash
uv sync
```

Run the CLI from the repository:

```bash
uv run cb --help
```

After pushing the project to GitHub, install it as a command-line tool with:

```bash
uv tool install "git+https://github.com/<your-username>/<your-repo>.git"
```

## Usage

Create the local storage folder and JSON file:

```bash
cb init
```

Add a snippet. This opens your default terminal editor:

```bash
cb add plot-hist --tag python --tag seaborn --description "Histogram template"
```

List all snippets:

```bash
cb list
```

Print a snippet:

```bash
cb get plot-hist
```

Copy a snippet body to the clipboard:

```bash
cb copy plot-hist
```

Search names, descriptions, tags, and snippet bodies:

```bash
cb search pandas
```

Delete a snippet:

```bash
cb delete plot-hist
```

Show the installed version:

```bash
cb --version
```

## Development

Run tests:

```bash
uv run pytest
```

Use a temporary storage file while testing commands manually:

```bash
export CB_STORAGE_PATH="$PWD/scratch-snippets.json"
```

On PowerShell:

```powershell
$env:CB_STORAGE_PATH = "$PWD\scratch-snippets.json"
```

## Future Improvements

- categories
- import/export markdown
- fuzzy search
- project-specific snippet collections
- optional sync
