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

For another `uv` project, install this package from GitHub with:

```bash
uv add "git+https://github.com/mihirnvad/dsc190_Code_Cheatsheet.git"
```

To install `cb` as a standalone command-line tool, use:

```bash
uv tool install "git+https://github.com/mihirnvad/dsc190_Code_Cheatsheet.git"
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

If a snippet with the same name already exists, `cb` asks before overwriting it. When overwriting, omitted tags or descriptions keep their existing values.

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

## Troubleshooting

`cb copy` uses `pyperclip`, which depends on the operating system clipboard. It should work out of the box on macOS, Windows, and most desktop Linux environments. On minimal Linux environments, install a clipboard backend such as `xclip` or `xsel` if copying fails.

## Future Improvements

- categories
- import/export markdown
- fuzzy search
- project-specific snippet collections
- optional sync
