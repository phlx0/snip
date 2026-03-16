# CLI reference

## Synopsis

```
snip [OPTIONS] [QUERY]
```

## Commands

| Command | Description |
|---------|-------------|
| `snip` | Open the TUI |
| `snip <query>` | Find a snippet by title, print content, copy to clipboard |
| `snip run <query>` | Run a snippet as a shell command |
| `snip init zsh\|bash` | Print shell completion script |
| `snip theme list` | List all available themes |
| `snip theme set <name>` | Set the active theme |
| `snip theme import <file>` | Import a custom theme JSON and activate it |

## Options

| Option | Description |
|--------|-------------|
| `--list [tag]` | Print all snippet titles, one per line. Optionally filter by tag |
| `--add <file>` | Save a file as a snippet. Language is auto-detected from the file extension |
| `--delete <query>` | Delete a snippet by title without opening the TUI |
| `--json <query>` | Output a snippet's full metadata as JSON |
| `--export` | Dump all snippets as JSON to stdout |
| `--import <file\|->` | Import snippets from a JSON file. Use `-` to read from stdin |
| `--from-history` | Pick a command from shell history and save it as a snippet |
| `--theme <name>` | Launch the TUI with a specific theme for this session only |
| `--db <path>` | Use a custom database file instead of `~/.config/snip/snip.db` |
| `-q`, `--quiet` | Suppress informational stderr output |
| `--version`, `-v` | Print version string |
| `--help`, `-h` | Show help |

## Query matching

When a query is provided, snip searches snippet titles:

1. **Exact match** — if a title matches the query exactly (case-insensitive), it wins
2. **Substring match** — if no exact match, all titles containing the query are returned
3. **Multiple matches** — lists candidates and exits; be more specific
4. **No match** — exits with code 1

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | No snippet found, multiple matches, or invalid input |

When using `snip run`, the exit code of the snippet's shell command is passed through.

## Examples

```bash
# Copy a snippet
snip ports

# Run a snippet
snip run docker-clean

# Save a script as a snippet
snip --add ~/.local/bin/myscript.sh

# Export for backup
snip --export > ~/dotfiles/snippets.json

# Restore on a new machine
snip --import ~/dotfiles/snippets.json

# Filter by tag and fuzzy-pick
snip --list devops | fzf | xargs snip

# Use in a script without noise
TOKEN=$(snip -q my-token)

# Try the Dracula theme for one session
snip --theme dracula

# Permanently switch to Dracula
snip theme set dracula

# Import a custom theme
snip theme import ~/dotfiles/themes/gruvbox.json
```
