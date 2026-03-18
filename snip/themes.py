from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_CONFIG_DIR = Path.home() / ".config" / "snip"


@dataclass
class Theme:
    name: str = "tokyo-night"
    # Backgrounds
    bg: str = "#0d0f18"
    surface: str = "#0a0b14"
    panel: str = "#13141f"
    # Borders
    border: str = "#2a2c42"
    border_dim: str = "#1a1c2e"
    # Interactive states
    select_bg: str = "#131729"
    hover_bg: str = "#12131e"
    # Accent / brand colors
    accent: str = "#7aa2f7"
    accent_hover: str = "#5a82d7"
    teal: str = "#73daca"
    purple: str = "#bb9af7"
    pill_bg: str = "#252640"
    pill_bg_hover: str = "#2a2c50"
    # Text
    text: str = "#c0caf5"
    text_hi: str = "#e0e7ff"
    text_mid: str = "#a0aabf"
    text_muted: str = "#565f89"
    text_dim: str = "#3b3f5c"
    text_ghost: str = "#2a2c42"
    # Syntax highlighting
    syntax_string: str = "#9ece6a"
    syntax_number: str = "#ff9e64"
    syntax_operator: str = "#89ddff"
    syntax_error: str = "#f7768e"


TOKYO_NIGHT = Theme(name="tokyo-night")

DRACULA = Theme(
    name="dracula",
    bg="#282a36",
    surface="#21222c",
    panel="#1e1f29",
    border="#44475a",
    border_dim="#373844",
    select_bg="#383a4c",
    hover_bg="#2d2f3e",
    accent="#bd93f9",
    accent_hover="#9d73d9",
    teal="#8be9fd",
    purple="#ff79c6",
    pill_bg="#44475a",
    pill_bg_hover="#4a4d65",
    text="#f8f8f2",
    text_hi="#ffffff",
    text_mid="#d6d8e0",
    text_muted="#6272a4",
    text_dim="#44475a",
    text_ghost="#44475a",
    syntax_string="#f1fa8c",
    syntax_number="#bd93f9",
    syntax_operator="#ff79c6",
    syntax_error="#ff5555",
)

_BUILTIN: dict[str, Theme] = {
    "tokyo-night": TOKYO_NIGHT,
    "dracula": DRACULA,
}

# Set at startup before TUI launches; widgets read this at render time.
current: Theme = TOKYO_NIGHT


def _themes_dir() -> Path:
    return _CONFIG_DIR / "themes"


def list_themes() -> list[str]:
    names = list(_BUILTIN.keys())
    td = _themes_dir()
    if td.exists():
        names += [f.stem for f in sorted(td.glob("*.json"))]
    return sorted(set(names))


def load(name: str) -> Theme:
    """Return a Theme by name (built-in or from ~/.config/snip/themes/)."""
    if name in _BUILTIN:
        return _BUILTIN[name]
    path = _themes_dir() / f"{name}.json"
    if not path.exists():
        available = ", ".join(list_themes())
        raise FileNotFoundError(f"Theme '{name}' not found. Available: {available}")
    return _load_file(path)


def _load_file(path: Path) -> Theme:
    data = json.loads(path.read_text())
    colors = data.get("colors", {})
    theme = Theme(name=data.get("name", path.stem))
    for key, value in colors.items():
        if key != "name" and hasattr(theme, key):
            setattr(theme, key, value)
    return theme


def import_theme(src: Path) -> str:
    """Validate + copy a theme JSON file to ~/.config/snip/themes/. Returns theme name."""
    try:
        data = json.loads(src.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}") from e
    if "colors" not in data:
        raise ValueError("Theme file must contain a 'colors' object")
    name = data.get("name", src.stem)
    dest = _themes_dir()
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"{name}.json").write_text(src.read_text())
    return name


def get_active_name() -> str:
    config = _CONFIG_DIR / "config.json"
    if config.exists():
        try:
            return json.loads(config.read_text()).get("theme", "tokyo-night")
        except Exception as e:
            import sys
            print(f"snip: warning — could not read theme config: {e}", file=sys.stderr)
    return "tokyo-night"


def set_active(name: str) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = _CONFIG_DIR / "config.json"
    cfg: dict = {}
    if config.exists():
        try:
            cfg = json.loads(config.read_text())
        except Exception as e:
            import sys
            print(f"snip: warning — could not read theme config, resetting: {e}", file=sys.stderr)
    cfg["theme"] = name
    config.write_text(json.dumps(cfg, indent=2))


def build_css(theme: Theme) -> str:
    """Return the full app CSS with theme variable values injected at the top."""
    vars_block = (
        f"$snip-bg: {theme.bg};\n"
        f"$snip-surface: {theme.surface};\n"
        f"$snip-panel: {theme.panel};\n"
        f"$snip-border: {theme.border};\n"
        f"$snip-border-dim: {theme.border_dim};\n"
        f"$snip-select-bg: {theme.select_bg};\n"
        f"$snip-hover-bg: {theme.hover_bg};\n"
        f"$snip-accent: {theme.accent};\n"
        f"$snip-accent-hover: {theme.accent_hover};\n"
        f"$snip-teal: {theme.teal};\n"
        f"$snip-purple: {theme.purple};\n"
        f"$snip-pill-bg: {theme.pill_bg};\n"
        f"$snip-pill-bg-hover: {theme.pill_bg_hover};\n"
        f"$snip-text: {theme.text};\n"
        f"$snip-text-hi: {theme.text_hi};\n"
        f"$snip-text-mid: {theme.text_mid};\n"
        f"$snip-text-muted: {theme.text_muted};\n"
        f"$snip-text-dim: {theme.text_dim};\n"
        f"$snip-text-ghost: {theme.text_ghost};\n"
        "\n"
    )
    tcss = (Path(__file__).parent / "snip.tcss").read_text(encoding="utf-8")
    return vars_block + tcss
