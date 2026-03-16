# Themes

snip ships with two built-in themes and a JSON-based system for importing your own.

---

## Built-in themes

| Name | Description |
|------|-------------|
| `tokyo-night` | Dark blue palette — default |
| `dracula` | Purple-tinted dark theme |

Switch between them with:

```bash
snip theme set dracula
snip theme set tokyo-night
```

The active theme is remembered across sessions and stored in `~/.config/snip/config.json`.

---

## Commands

```bash
snip theme list               # list all available themes (built-in + custom)
snip theme set <name>         # set the active theme
snip theme import <file>      # import a theme JSON and activate it
```

To try a theme for one session without changing your saved preference:

```bash
snip --theme dracula
```

---

## Writing a custom theme

A theme is a JSON file with a `name` and a `colors` object. You only need to include the colors you want to override — any key you omit falls back to the Tokyo Night default.

```json
{
  "name": "my-theme",
  "colors": {
    "bg":             "#1a1b26",
    "surface":        "#16161e",
    "panel":          "#1f2335",
    "border":         "#3b4261",
    "border_dim":     "#292e42",
    "select_bg":      "#283457",
    "hover_bg":       "#1e2030",
    "accent":         "#7dcfff",
    "accent_hover":   "#5db0df",
    "teal":           "#73daca",
    "purple":         "#bb9af7",
    "pill_bg":        "#3b4261",
    "pill_bg_hover":  "#414868",
    "text":           "#c0caf5",
    "text_hi":        "#e0e7ff",
    "text_mid":       "#a9b1d6",
    "text_muted":     "#565f89",
    "text_dim":       "#3b4261",
    "text_ghost":     "#2a2c42",
    "syntax_string":  "#9ece6a",
    "syntax_number":  "#ff9e64",
    "syntax_operator":"#89ddff",
    "syntax_error":   "#f7768e"
  }
}
```

### Color reference

| Key | Where it's used |
|-----|----------------|
| `bg` | Main screen and panel backgrounds |
| `surface` | Search bar, status bar, code block background |
| `panel` | Edit modal background, footer |
| `border` | Most borders and dividers |
| `border_dim` | Subtle borders between list items |
| `select_bg` | Background of the selected snippet in the list |
| `hover_bg` | Hover state for list items |
| `accent` | Logo diamond, highlighted borders, links, button fills |
| `accent_hover` | Save button hover state |
| `teal` | Tags in list and preview |
| `purple` | Pin star icon, decorators in syntax highlighting |
| `pill_bg` | Footer key badge background, cancel button |
| `pill_bg_hover` | Cancel button hover state |
| `text` | Main body text |
| `text_hi` | Selected item title, snippet title in preview |
| `text_mid` | Unselected item titles |
| `text_muted` | Footer text, form labels, description text |
| `text_dim` | Placeholder text, metadata (language, dates) |
| `text_ghost` | Empty-state hint, modal dividers |
| `syntax_string` | String literals in code preview |
| `syntax_number` | Numbers and constants in code preview |
| `syntax_operator` | Operators in code preview |
| `syntax_error` | Errors and exceptions in code preview |

### Importing

```bash
snip theme import ~/dotfiles/themes/my-theme.json
```

This copies the file to `~/.config/snip/themes/my-theme.json` and immediately activates it. The theme name is taken from the `name` field in the JSON, not the filename.

---

## Where themes are stored

| Location | Contents |
|----------|----------|
| `~/.config/snip/themes/` | Custom imported theme files |
| `~/.config/snip/config.json` | Active theme name |

Built-in themes (`tokyo-night`, `dracula`) are compiled into the package and do not appear on disk.

---

## Sharing themes

Because themes are just JSON files, they're easy to share:

- Drop them in your dotfiles repo and import on each machine
- Share as a GitHub Gist
- Pass via stdin: `curl -s <url> > my-theme.json && snip theme import my-theme.json`

---

## Example: Gruvbox

```json
{
  "name": "gruvbox",
  "colors": {
    "bg":             "#282828",
    "surface":        "#1d2021",
    "panel":          "#3c3836",
    "border":         "#504945",
    "border_dim":     "#3c3836",
    "select_bg":      "#32302f",
    "hover_bg":       "#2d2926",
    "accent":         "#b8bb26",
    "accent_hover":   "#98971a",
    "teal":           "#8ec07c",
    "purple":         "#d3869b",
    "pill_bg":        "#504945",
    "pill_bg_hover":  "#665c54",
    "text":           "#ebdbb2",
    "text_hi":        "#fbf1c7",
    "text_mid":       "#d5c4a1",
    "text_muted":     "#928374",
    "text_dim":       "#665c54",
    "text_ghost":     "#504945",
    "syntax_string":  "#b8bb26",
    "syntax_number":  "#d79921",
    "syntax_operator":"#83a598",
    "syntax_error":   "#fb4934"
  }
}
```
