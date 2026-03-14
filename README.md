# snip 📎

> A terminal snippet manager. Store, search, and copy code without leaving your shell.

```
┌─ snip ──────────────────────────────────────────────────────── 14:32 ─┐
│ / Search snippets…                                                      │
├───────────────────────────┬─────────────────────────────────────────── │
│ 📌 List all listening...  │  List all listening ports                   │
│    bash  #networking      │  Show every port your machine is listening  │
│ ─────────────────────     │  #networking #ports #devops                 │
│  Pretty-print JSON        │                                             │
│    bash  #json #cli       │  ┌─────────────────────────────────────┐   │
│ ─────────────────────     │  │  1  ss -tlnp                        │   │
│  Reverse a list (Python)  │  │  2  # or on macOS:                  │   │
│    python  #list          │  │  3  lsof -iTCP -sTCP:LISTEN -nP     │   │
│ ─────────────────────     │  └─────────────────────────────────────┘   │
│  Git: undo last commit    │                                             │
│    bash  #git             │  lang: bash · created: 2024-01-15 09:00    │
│                           │                                             │
├───────────────────────────┴─────────────────────────────────────────── │
│  n New  e Edit  d Delete  y Copy  p Pin  / Search  q Quit               │
└─────────────────────────────────────────────────────────────────────── ┘
```

## The problem

You write a clever one-liner. You close the terminal. Three weeks later you're Googling
the same thing again. `snip` is your personal snippet vault that lives where you work.

## Features

- **Syntax highlighting** — powered by Rich/Pygments, 20+ languages
- **Fuzzy search** — live filter across title, content, tags, and language
- **Clipboard copy** — press `y` to yank a snippet's content instantly
- **Pin snippets** — keep your most-used snippets at the top
- **Tags** — organise freely with space-separated tags
- **Vim-style navigation** — `j`/`k` to move, `/` to search, `q` to quit
- **SQLite storage** — lives in `~/.config/snip/snip.db`, portable and fast
- **No server, no account** — fully offline, your data stays local

## Install

```bash
pip install snip-tui
```

Or from source:

```bash
git clone https://github.com/yourusername/snip
cd snip
pip install -e .
```

## Usage

```bash
snip          # open the TUI
```

### Keyboard shortcuts

| Key     | Action                        |
|---------|-------------------------------|
| `n`     | New snippet                   |
| `e`     | Edit selected snippet         |
| `d`     | Delete selected snippet       |
| `y`     | Copy content to clipboard     |
| `p`     | Toggle pin on selected snippet|
| `/`     | Focus search bar              |
| `Esc`   | Clear search / close modal    |
| `j`/`k` | Move down / up                |
| `q`     | Quit                          |

### Custom database path

```bash
snip --db ~/Dropbox/snippets.db   # sync via Dropbox, iCloud, etc.
```

## Project structure

```
snip/
├── snip/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── app.py               # Textual App class + demo seeding
│   ├── models/
│   │   └── snippet.py       # Snippet dataclass
│   ├── storage/
│   │   └── database.py      # SQLite CRUD layer
│   ├── ui/
│   │   ├── screens/
│   │   │   ├── main_screen.py   # Primary TUI screen
│   │   │   └── edit_screen.py   # New/edit modal
│   │   └── widgets/
│   │       ├── snippet_list.py  # Left panel
│   │       └── snippet_preview.py # Right panel (syntax highlight)
│   └── utils/
│       └── clipboard.py     # Cross-platform clipboard
└── tests/
    ├── conftest.py
    ├── test_snippet.py
    ├── test_database.py
    └── test_clipboard.py
```

## Development

```bash
pip install -e ".[dev]"
make test          # run tests
make test-cov      # run tests with coverage
```

## License

MIT
