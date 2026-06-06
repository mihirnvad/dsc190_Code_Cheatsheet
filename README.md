# Code Boilerplate (`cb`)

`cb` is a local command line tool for reusable code snippets, terminal commands, and assignment templates. It solves the problem of wasting time searching for multiple, seperate code snippets that needs to be used often. It keeps code and commands stored locally with quick and easy access with clipboard support.

## What `cb` Can Do

- Save snippets using your default terminal editor.
- Organize snippets with descriptions and multiple tags.
- Search names, descriptions, tags, and snippet bodies.
- Print snippets with syntax highlighting when possible.
- Copy snippet bodies directly to the clipboard.
- List the entire library in a table.
- Safely overwrite or delete snippets with confirmation prompts.
- Store everything locally in an inspectable JSON file.

Save a reusable plotting snippet:

```bash
cb add plot-hist \
  --tag python \
  --tag seaborn \
  --description "Histogram template"
```

Your default editor opens so you can enter the snippet body. After saving and closing the editor:

```bash
cb list
cb get plot-hist
cb copy plot-hist
```

Find it later by name, description, tag, or code:

```bash
cb search seaborn
```

Remove it when it is no longer needed:

```bash
cb delete plot-hist
```

## Commands

| Command | Ability |
| --- | --- |
| `cb init` | Create the local library directory and JSON file. |
| `cb add NAME` | Open an editor and save a new snippet. |
| `cb get NAME` | Show snippet metadata and highlighted code. |
| `cb copy NAME` | Copy only the snippet body to the clipboard. |
| `cb list` | Display all snippets in a table. |
| `cb search QUERY` | Search every stored snippet field. |
| `cb delete NAME` | Confirm and delete a snippet. |
| `cb --version` | Show the installed version. |

### Add

```bash
cb add NAME [--tag TAG]... [--description TEXT]
```

`--tag` may be repeated:

```bash
cb add pandas-groupby \
  --tag python \
  --tag pandas \
  --description "Group and aggregate a DataFrame"
```

If `NAME` already exists, `cb` asks before overwriting it. Existing tags and descriptions are preserved when their options are omitted.

### Get

```bash
cb get pandas-groupby
```

Displays the snippet name, description, tags, timestamps, and body. Python and shell-like snippets receive syntax highlighting when detected.

### Copy

```bash
cb copy pandas-groupby
```

Copies the stored body exactly as saved and prints a success message.

### List

```bash
cb list
```

Shows name, description, tags, creation time, and update time for every snippet.

### Search

```bash
cb search groupby
cb search pandas
cb search "DataFrame"
```

Search is case-insensitive and checks:

- snippet names
- descriptions
- tags
- snippet bodies

### Delete

```bash
cb delete pandas-groupby
```

## Stored Data

Each snippet is saved locally with this structure:

```json
{
  "name": "plot-hist",
  "description": "Seaborn histogram template",
  "tags": ["python", "plot", "seaborn"],
  "body": "import seaborn as sns\nsns.histplot(df[\"age\"])\n",
  "created_at": "2026-06-05T18:30:00+00:00",
  "updated_at": "2026-06-05T18:30:00+00:00"
}
```


## Installation

Run the project locally:

```bash
uv sync
uv run cb --help
```

Add to terminal with:
```bash
uv add "git+https://github.com/mihirnvad/dsc190_Code_Cheatsheet.git"
```

## Development

Run the tests:

```bash
uv run pytest
```

Use a temporary library during manual testing:

```bash
export CB_STORAGE_PATH="$PWD/scratch-snippets.json"
```