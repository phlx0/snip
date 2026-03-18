# Changelog

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) —
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.6.2] — 2026-03-19

### Fixed
- `_run_add` (`snip --add`) now opens files with `errors="replace"` so non-UTF-8 files no longer raise `UnicodeDecodeError`
- JSON import: `tags` field is validated to be a list; non-list values are coerced to `[]` and each element is cast to `str` to prevent DB type corruption; `pinned` is explicitly cast to `bool`
- Theme config parse errors in `get_active_name` and `set_active` are now printed to stderr instead of being swallowed silently
- `database.py`: replaced `Optional[Snippet]` with `Snippet | None`, removed unused `from typing import Optional`
- `_resolve` in `__main__.py` now declares `-> Snippet` return type

### Tests
- Added `tests/test_main.py` covering `_lang_from_ext`, `_resolve`, `_run_add`, `_run_export`, and `_run_import` (including all edge cases added in 0.6.1 and 0.6.2)
- Added `tests/test_themes.py` covering `load`, `list_themes`, `get_active_name`, `set_active`, and `import_theme`

---

## [0.6.1] — 2026-03-18

### Fixed
- `__init__.py` version was stale (`0.1.0`); now kept in sync with `pyproject.toml` and `__main__.py`
- JSON import (`snip --import`) now validates that the root value is an array and that each entry is an object; previously a non-array root or a non-dict entry would cause a `TypeError` at runtime
- `.dockerfile` filenames (no extension, dot-prefixed) are now correctly detected as the `dockerfile` language when using `snip --add`
- Redundant `except (ValueError, Exception)` in theme import narrowed to `except Exception` (`ValueError` is a subclass and was dead code)
- Clipboard fallback no longer silently swallows errors; `ImportError` from missing `pyperclip` is handled separately, other failures are printed to stderr
- Removed unnecessary `shell=True` from the Windows `clip` subprocess call
- `models/snippet.py`: replaced `Optional[int]` / `Optional[datetime]` with `int | None` / `datetime | None` (consistent with the rest of the codebase); removed unused `from typing import Optional`

---

## [0.6.0] — 2026-03-16

### Added
- Theme system: all UI colors are now driven by a `Theme` dataclass; `snip.tcss` uses CSS variables throughout
- Built-in themes: `tokyo-night` (default) and `dracula`
- `snip theme list` — list all available themes (built-in and custom)
- `snip theme set <name>` — persist the active theme to `~/.config/snip/config.json`
- `snip theme import <file>` — validate and install a custom theme JSON, then activate it
- `--theme <name>` flag — launch the TUI with a specific theme for one session without changing the saved preference
- Custom themes are stored in `~/.config/snip/themes/` as plain JSON files and can be committed to dotfiles or shared as Gists
- Syntax highlighting colors (Pygments) and all Rich inline markup adapt to the active theme

---

## [0.5.1] — 2026-03-16

### Fixed
- Demo snippets no longer reappear after deleting all snippets; seeding now only runs on a genuine first install (when the database file does not yet exist)
- Arrow-key navigation in the new/edit snippet form no longer gets stuck in the language selector
- Navigating down from the title field opens the language dropdown automatically; navigating up from description also opens it
- At the top of the language list, pressing up closes the dropdown and moves focus to the title field; at the bottom, pressing down closes it and moves to description
- Arrow keys in the code field navigate lines normally; at the first line pressing up moves to tags, at the last line pressing down moves to the cancel/save buttons
- `up`/`down` navigation no longer wraps around (no more carousel behaviour)
- Pressing `Enter` in any text input (title, description, tags) advances focus to the next field

### Added
- `ctrl+s` saves the snippet from anywhere in the form, including from inside the code editor

---

## [0.5.0] — 2026-03-15

### Added
- `snip --help` / `-h` — print full usage reference directly in the terminal
- `CONTRIBUTING.md` — contributor guide covering setup, workflow, and conventions

---

## [0.4.0] — 2026-03-15

### Added
- `snip --delete <query>` — delete a snippet by title without opening the TUI
- `snip --json <query>` — output full snippet metadata as JSON for scripting
- `snip --list <tag>` — filter listed titles by tag
- `snip --version` / `-v` — print version string
- `snip -q` / `--quiet` — suppress informational stderr output for clean scripting
- `snip init zsh` / `snip init bash` — print shell completion scripts; activate with `eval "$(snip init zsh)"`; tab-completes snippet titles and all flags

---

## [0.3.0] — 2026-03-15

### Added
- `snip run <query>` — cleaner alias for running a snippet as a shell command
- `snip --add <file>` — save any file as a snippet; language auto-detected from extension
- `snip --export` — dump all snippets to JSON on stdout (pipe to a file for dotfile backups)
- `snip --import <file>` — bulk-import snippets from a JSON file (`-` to read from stdin)
- `snip --from-history` — interactively pick a command from shell history (bash/zsh) and save it as a snippet; uses `fzf` if available, falls back to a numbered list

---

## [0.2.0] — 2026-03-15

### Added
- `snip <query>` — non-interactive snippet lookup: finds a snippet by title, prints content to stdout, and copies it to the clipboard. Exact title match is preferred; falls back to substring match. Multiple matches list candidates.
- `snip --list` — prints all snippet titles one per line, designed for piping into `fzf` or other tools
- `snip --exec <query>` — runs a matched snippet directly as a shell command; exits with the command's return code
- fzf one-liner in README: `snip --list | fzf | xargs snip`

---

## [0.1.0] — 2026-03-14

### Added
- Full TUI built with [Textual](https://github.com/Textualize/textual)
- Snippet list with live search (title, description, tags, language)
- Syntax-highlighted code preview using a custom Tokyo Night Pygments style
- Create / edit / delete snippets via a modal form
- Pin snippets to keep them at the top of the list
- Clipboard copy with `y` (via pyperclip)
- Vim-style navigation (`j`/`k`) and `/` search
- SQLite storage at `~/.config/snip/snip.db`
- Demo snippets seeded on first run
- `install.sh` one-liner installer for Linux / macOS
- `--db` flag for a custom database path (easy Dropbox / iCloud sync)

[Unreleased]: https://github.com/phlx0/snip/compare/v0.6.2...HEAD
[0.6.2]: https://github.com/phlx0/snip/compare/v0.6.1...v0.6.2
[0.6.1]: https://github.com/phlx0/snip/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/phlx0/snip/compare/v0.5.1...v0.6.0
[0.5.1]: https://github.com/phlx0/snip/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/phlx0/snip/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/phlx0/snip/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/phlx0/snip/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/phlx0/snip/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/phlx0/snip/releases/tag/v0.1.0
