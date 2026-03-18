import json
import os
import subprocess
import sys
from pathlib import Path

VERSION = "0.6.1"

# Set to True by -q / --quiet to suppress informational stderr messages
_quiet = False


def _info(msg: str) -> None:
    if not _quiet:
        print(msg, file=sys.stderr)


def _run_tui(db_path: Path, theme_name: str | None = None) -> None:
    from snip.app import SnipApp
    SnipApp(db_path=db_path, theme_name=theme_name).run()


def _run_list(db_path: Path, tag: str = "") -> None:
    from snip.storage.database import Database

    db = Database(db_path)
    snippets = db.get_all()
    if tag:
        snippets = [s for s in snippets if tag.lower() in [t.lower() for t in s.tags]]
    for s in snippets:
        print(s.title)


def _resolve(query: str, db_path: Path):
    from snip.storage.database import Database

    db = Database(db_path)
    snippets = db.get_all()
    q = query.lower()
    exact = [s for s in snippets if s.title.lower() == q]
    matches = exact or [s for s in snippets if q in s.title.lower()]

    if not matches:
        print(f"snip: no snippet matching '{query}'", file=sys.stderr)
        sys.exit(1)

    if len(matches) > 1:
        print(f"snip: {len(matches)} snippets match '{query}' — be more specific:", file=sys.stderr)
        for s in matches:
            print(f"  • {s.title}", file=sys.stderr)
        sys.exit(1)

    return matches[0]


def _run_copy(query: str, db_path: Path) -> None:
    from snip.utils.clipboard import copy_to_clipboard

    snippet = _resolve(query, db_path)
    print(snippet.content)
    if copy_to_clipboard(snippet.content):
        _info(f"Copied '{snippet.title}' to clipboard.")


def _run_exec(query: str, db_path: Path) -> None:
    snippet = _resolve(query, db_path)
    result = subprocess.run(snippet.content, shell=True)
    sys.exit(result.returncode)


def _run_json(query: str, db_path: Path) -> None:
    snippet = _resolve(query, db_path)
    print(json.dumps({
        "id": snippet.id,
        "title": snippet.title,
        "content": snippet.content,
        "language": snippet.language,
        "description": snippet.description,
        "tags": snippet.tags,
        "pinned": snippet.pinned,
    }, indent=2))


def _run_delete(query: str, db_path: Path) -> None:
    from snip.storage.database import Database

    snippet = _resolve(query, db_path)
    db = Database(db_path)
    db.delete(snippet.id)
    _info(f"Deleted '{snippet.title}'.")


def _lang_from_ext(path: Path) -> str:
    mapping = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".sh": "bash", ".bash": "bash", ".zsh": "bash",
        ".go": "go", ".rs": "rust", ".c": "c", ".cpp": "cpp",
        ".java": "java", ".json": "json", ".yaml": "yaml", ".yml": "yaml",
        ".toml": "toml", ".sql": "sql", ".html": "html", ".css": "css",
        ".md": "markdown", ".rb": "ruby", ".php": "php",
        ".dockerfile": "dockerfile", ".ps1": "powershell",
    }
    name = path.name.lower()
    if name in ("dockerfile", ".dockerfile"):
        return "dockerfile"
    return mapping.get(path.suffix.lower(), "text")


def _run_add(file_path: str, db_path: Path) -> None:
    from snip.models.snippet import Snippet
    from snip.storage.database import Database

    path = Path(file_path)
    if not path.exists():
        print(f"snip: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    content = path.read_text()
    title = path.stem
    language = _lang_from_ext(path)

    db = Database(db_path)
    snippet = db.create(Snippet(title=title, content=content, language=language))
    _info(f"Saved '{snippet.title}' (id {snippet.id}, language: {language})")


def _run_export(db_path: Path) -> None:
    from snip.storage.database import Database

    db = Database(db_path)
    data = [
        {
            "title": s.title,
            "content": s.content,
            "language": s.language,
            "description": s.description,
            "tags": s.tags,
            "pinned": s.pinned,
        }
        for s in db.get_all()
    ]
    print(json.dumps(data, indent=2))


def _run_import(file_path: str, db_path: Path) -> None:
    from snip.models.snippet import Snippet
    from snip.storage.database import Database

    if file_path == "-":
        raw = sys.stdin.read()
    else:
        p = Path(file_path)
        if not p.exists():
            print(f"snip: file not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        raw = p.read_text()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"snip: invalid JSON — {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print("snip: JSON must be an array of snippet objects", file=sys.stderr)
        sys.exit(1)

    db = Database(db_path)
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            print(f"snip: skipping entry {i} — expected an object", file=sys.stderr)
            continue
        if "title" not in item or "content" not in item:
            print(f"snip: skipping entry {i} — missing title or content", file=sys.stderr)
            continue
        db.create(Snippet(
            title=item["title"],
            content=item["content"],
            language=item.get("language", "text"),
            description=item.get("description", ""),
            tags=item.get("tags", []),
            pinned=item.get("pinned", False),
        ))
        _info(f"  imported '{item['title']}'")

    _info(f"\nDone. {len(data)} snippet(s) imported.")


def _read_history() -> list[str]:
    shell = os.environ.get("SHELL", "")
    candidates = []
    if "zsh" in shell:
        candidates.append(Path.home() / ".zsh_history")
    candidates.append(Path.home() / ".bash_history")

    for hist_file in candidates:
        if not hist_file.exists():
            continue
        lines = hist_file.read_text(errors="replace").splitlines()
        cmds = []
        for line in lines:
            if line.startswith(":") and ";" in line:
                line = line.split(";", 1)[1]
            line = line.strip()
            if line and not line.startswith("#"):
                cmds.append(line)
        seen: set[str] = set()
        deduped = []
        for cmd in reversed(cmds):
            if cmd not in seen:
                seen.add(cmd)
                deduped.append(cmd)
        return deduped

    return []


def _run_from_history(db_path: Path) -> None:
    from snip.models.snippet import Snippet
    from snip.storage.database import Database

    history = _read_history()
    if not history:
        print("snip: no shell history found", file=sys.stderr)
        sys.exit(1)

    if subprocess.run(["which", "fzf"], capture_output=True).returncode == 0:
        result = subprocess.run(
            ["fzf", "--prompt=pick a command > ", "--height=40%", "--reverse"],
            input="\n".join(history),
            text=True,
            capture_output=True,
        )
        if result.returncode != 0 or not result.stdout.strip():
            print("snip: nothing selected", file=sys.stderr)
            sys.exit(0)
        command = result.stdout.strip()
    else:
        preview = history[:50]
        for i, cmd in enumerate(preview, 1):
            print(f"  {i:>3}.  {cmd}")
        print()
        try:
            choice = input("Pick a number (or q to quit): ").strip()
        except (EOFError, KeyboardInterrupt):
            sys.exit(0)
        if choice.lower() == "q":
            sys.exit(0)
        try:
            command = preview[int(choice) - 1]
        except (ValueError, IndexError):
            print("snip: invalid selection", file=sys.stderr)
            sys.exit(1)

    print(f"\n  command: {command}")
    try:
        title = input("  title (leave blank to use command): ").strip()
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)
    if not title:
        title = command[:60]

    db = Database(db_path)
    snippet = db.create(Snippet(title=title, content=command, language="bash"))
    _info(f"\nSaved '{snippet.title}' (id {snippet.id})")


_BASH_COMPLETION = """\
_snip_complete() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local flags="--list --add --export --import --from-history --delete --json --version --quiet --db run"
    if [[ COMP_CWORD -eq 1 ]]; then
        local titles
        titles=$(snip --list 2>/dev/null)
        COMPREPLY=($(compgen -W "$flags $titles" -- "$cur"))
    fi
}
complete -F _snip_complete snip
"""

_ZSH_COMPLETION = """\
#compdef snip
_snip() {
    local -a titles
    titles=(${(f)"$(snip --list 2>/dev/null)"})
    local -a flags
    flags=(
        '--list:print all snippet titles'
        '--add:save a file as a snippet'
        '--export:export all snippets to JSON'
        '--import:import snippets from JSON'
        '--from-history:save a command from shell history'
        '--delete:delete a snippet by title'
        '--json:output snippet as JSON'
        '--version:show version'
        '--quiet:suppress informational output'
        '--db:use a custom database path'
        'run:run a snippet as a shell command'
    )
    _arguments '1: :(${flags[@]} ${titles[@]})'
}
_snip
"""


def _run_theme_list() -> None:
    from snip import themes

    active = themes.get_active_name()
    for name in themes.list_themes():
        marker = "  (active)" if name == active else ""
        print(f"  {name}{marker}")


def _run_theme_import(file_path: str) -> None:
    from snip import themes

    src = Path(file_path)
    if not src.exists():
        print(f"snip: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    try:
        name = themes.import_theme(src)
    except Exception as e:
        print(f"snip: invalid theme file — {e}", file=sys.stderr)
        sys.exit(1)
    themes.set_active(name)
    _info(f"Imported and activated theme '{name}'.")


def _run_theme_set(name: str) -> None:
    from snip import themes

    try:
        themes.load(name)
    except FileNotFoundError as e:
        print(f"snip: {e}", file=sys.stderr)
        sys.exit(1)
    themes.set_active(name)
    _info(f"Active theme set to '{name}'.")


def _run_init(shell: str) -> None:
    if shell == "bash":
        print(_BASH_COMPLETION)
        _info("# Add to ~/.bashrc:  eval \"$(snip init bash)\"")
    elif shell == "zsh":
        print(_ZSH_COMPLETION)
        _info("# Add to ~/.zshrc:   eval \"$(snip init zsh)\"")
    else:
        print(f"snip: unknown shell '{shell}' — supported: bash, zsh", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    global _quiet
    from snip.app import _DEFAULT_DB

    db_path: Path = _DEFAULT_DB
    theme_name: str | None = None
    args = sys.argv[1:]

    # Strip --db <path>
    if len(args) >= 2 and args[0] == "--db":
        db_path = Path(args[1])
        args = args[2:]

    # Strip --theme <name>
    if len(args) >= 2 and args[0] == "--theme":
        theme_name = args[1]
        args = args[2:]

    # Strip -q / --quiet
    if "-q" in args or "--quiet" in args:
        _quiet = True
        args = [a for a in args if a not in ("-q", "--quiet")]

    try:
        if not args:
            _run_tui(db_path, theme_name)
        elif args[0] in ("--help", "-h"):
            print(f"""\
snip {VERSION} — terminal snippet vault

USAGE
  snip                          open the TUI
  snip <query>                  copy a snippet to clipboard
  snip run <query>              run a snippet as a shell command

OPTIONS
  --list [tag]                  print all titles (optionally filter by tag)
  --add <file>                  save a file as a snippet
  --delete <query>              delete a snippet
  --json <query>                output snippet as JSON
  --export                      dump all snippets to JSON (stdout)
  --import <file|->>            import snippets from JSON
  --from-history                pick a shell history command and save it
  --theme <name>                launch TUI with a specific theme
  --db <path>                   use a custom database file
  -q, --quiet                   suppress informational output
  --version                     show version
  --help                        show this help

THEMES
  snip theme list               list available themes
  snip theme import <file>      import a custom theme JSON and activate it
  snip theme set <name>         set the active theme

SHELL COMPLETION
  eval "$(snip init zsh)"       add to ~/.zshrc
  eval "$(snip init bash)"      add to ~/.bashrc

EXAMPLES
  snip ports                    copy 'ports' snippet to clipboard
  snip run deploy               run 'deploy' snippet in shell
  snip --list docker            list snippets tagged #docker
  snip --theme dracula          open TUI with the Dracula theme
  snip --list | fzf | xargs snip
  snip --export > backup.json
""")
        elif args[0] in ("--version", "-v"):
            print(f"snip {VERSION}")
        elif args[0] == "--list":
            tag = args[1] if len(args) >= 2 else ""
            _run_list(db_path, tag)
        elif args[0] in ("--exec", "run") and len(args) >= 2:
            _run_exec(" ".join(args[1:]), db_path)
        elif args[0] == "--add" and len(args) >= 2:
            _run_add(args[1], db_path)
        elif args[0] == "--export":
            _run_export(db_path)
        elif args[0] == "--import" and len(args) >= 2:
            _run_import(args[1], db_path)
        elif args[0] == "--from-history":
            _run_from_history(db_path)
        elif args[0] == "--delete" and len(args) >= 2:
            _run_delete(" ".join(args[1:]), db_path)
        elif args[0] == "--json" and len(args) >= 2:
            _run_json(" ".join(args[1:]), db_path)
        elif args[0] == "theme":
            if len(args) < 2 or args[1] == "list":
                _run_theme_list()
            elif args[1] == "import" and len(args) >= 3:
                _run_theme_import(args[2])
            elif args[1] == "set" and len(args) >= 3:
                _run_theme_set(args[2])
            else:
                print("snip: usage: snip theme <list|import <file>|set <name>>", file=sys.stderr)
                sys.exit(1)
        elif args[0] == "init" and len(args) >= 2:
            _run_init(args[1])
        else:
            _run_copy(" ".join(args), db_path)
    except ImportError as e:
        print(f"snip: missing dependency — {e}", file=sys.stderr)
        print("Run: pip install textual pyperclip", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"snip: failed to start — {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
