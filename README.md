<div align="center">

<br/>

# ◆ snip

**A terminal snippet manager that lives where you work.**

Store, search, and yank code without leaving your shell.

<br/>

![snip terminal interface](assets/hero.svg)

<br/>

</div>

---

## The problem

You write a clever one-liner. You close the terminal. Three weeks later you're Googling the same thing again.

**snip** is your personal snippet vault — local, offline, instantly searchable from your terminal. No browser tabs, no account, no sync drama.

---

## Install

```bash
pip install snip-tui
```

**From source:**

```bash
git clone https://github.com/yourusername/snip
cd snip
pip install -e .
```

---

## Usage

```bash
snip                              # open the TUI
snip --db ~/Dropbox/snippets.db   # use a custom db path (sync via Dropbox, iCloud, etc.)
```

---

## Features

| | |
|---|---|
| **Syntax highlighting** | Powered by Rich + Pygments across 20+ languages |
| **Live search** | Filters across title, description, tags, and language as you type |
| **Clipboard copy** | Press `y` to yank a snippet's content instantly |
| **Pin snippets** | Keep your most-used snippets at the top of the list |
| **Tags** | Organise freely with space-separated tags |
| **Vim-style navigation** | `j`/`k` or arrow keys to move, `/` to search, `q` to quit |
| **SQLite storage** | Lives in `~/.config/snip/snip.db` — portable and fast |
| **Fully offline** | No server, no account, your data stays local |

---

## Keyboard shortcuts

| Key | Action |
|-----|--------|
| `n` | New snippet |
| `e` | Edit selected snippet |
| `d` | Delete selected snippet |
| `y` | Copy content to clipboard |
| `p` | Toggle pin on selected snippet |
| `/` | Focus search bar |
| `Esc` | Clear search / unfocus |
| `↑` `↓` or `j` `k` | Navigate list |
| `Tab` / `↑` `↓` | Navigate form fields (in new/edit modal) |
| `q` | Quit |

---

## Project structure

```
snip/
├── snip/
│   ├── __main__.py
│   ├── app.py               # Textual app + theme + demo seeding
│   ├── models/
│   │   └── snippet.py       # Snippet dataclass
│   ├── storage/
│   │   └── database.py      # SQLite CRUD layer
│   ├── ui/
│   │   ├── screens/
│   │   │   ├── main_screen.py   # Primary TUI screen
│   │   │   └── edit_screen.py   # New/edit modal
│   │   └── widgets/
│   │       ├── snippet_list.py      # Left panel
│   │       └── snippet_preview.py   # Right panel (syntax highlight)
│   └── utils/
│       └── clipboard.py
└── tests/
```

---

## Development

```bash
pip install -e ".[dev]"
make test        # run tests
make test-cov    # run with coverage
```

---

## License

MIT
