#!/usr/bin/env bash
set -euo pipefail

# ── colours ──────────────────────────────────────────────────────────
RED='\033[0;31m'
GRN='\033[0;32m'
BLU='\033[0;34m'
DIM='\033[2m'
BOLD='\033[1m'
RST='\033[0m'

ok()   { echo -e "  ${GRN}✓${RST}  $*"; }
info() { echo -e "  ${BLU}·${RST}  $*"; }
die()  { echo -e "  ${RED}✗${RST}  $*" >&2; exit 1; }

# ── paths ─────────────────────────────────────────────────────────────
VENV_DIR="$HOME/.local/share/snip"
BIN_DIR="$HOME/.local/bin"
BIN="$BIN_DIR/snip"

# Detect whether we're running from a local clone or piped via curl
if [[ -n "${BASH_SOURCE[0]:-}" && "${BASH_SOURCE[0]}" != "bash" && -f "${BASH_SOURCE[0]}" ]]; then
  REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
  REPO_DIR=""
fi

# ── header ────────────────────────────────────────────────────────────
echo
echo -e "  ${BOLD}◆ snip${RST}  ${DIM}terminal snippet vault — installer${RST}"
echo -e "  ${DIM}────────────────────────────────────${RST}"
echo

# ── python check ──────────────────────────────────────────────────────
PYTHON=$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)
[[ -z "$PYTHON" ]] && die "python3 not found — install it first"

PY_VER=$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$("$PYTHON" -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$("$PYTHON" -c 'import sys; print(sys.version_info.minor)')

[[ "$PY_MAJOR" -lt 3 || ( "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 10 ) ]] \
  && die "python $PY_VER found — need 3.10+"

ok "python $PY_VER"

# ── create venv ───────────────────────────────────────────────────────
if [[ -d "$VENV_DIR" ]]; then
  info "updating existing install at $VENV_DIR"
  rm -rf "$VENV_DIR"
fi

info "creating virtual environment"
"$PYTHON" -m venv "$VENV_DIR" --clear --prompt snip
ok "venv ready"

# ── install package ───────────────────────────────────────────────────
info "installing snip"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
if [[ -n "$REPO_DIR" ]]; then
  "$VENV_DIR/bin/pip" install --quiet -e "$REPO_DIR"
else
  "$VENV_DIR/bin/pip" install --quiet snip-tui
fi
ok "package installed"

# ── create launcher ───────────────────────────────────────────────────
mkdir -p "$BIN_DIR"
cat > "$BIN" <<EOF
#!/usr/bin/env bash
exec "$VENV_DIR/bin/python" -m snip "\$@"
EOF
chmod +x "$BIN"
ok "launcher created at $BIN"

# ── PATH check ───────────────────────────────────────────────────────
if ! echo "$PATH" | tr ':' '\n' | grep -qx "$BIN_DIR"; then
  echo
  echo -e "  ${RED}!${RST}  ${BOLD}$BIN_DIR${RST} is not in your PATH"

  SHELL_RC=""
  case "${SHELL:-}" in
    */zsh)  SHELL_RC="$HOME/.zshrc" ;;
    */bash) SHELL_RC="$HOME/.bashrc" ;;
  esac

  if [[ -n "$SHELL_RC" ]]; then
    echo -e "  ${DIM}adding to $SHELL_RC …${RST}"
    echo '' >> "$SHELL_RC"
    echo '# snip' >> "$SHELL_RC"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
    ok "added — restart your shell or run:  source $SHELL_RC"
  else
    info "add this to your shell config:"
    echo -e "      ${BOLD}export PATH=\"\$HOME/.local/bin:\$PATH\"${RST}"
  fi
fi

# ── done ──────────────────────────────────────────────────────────────
echo
echo -e "  ${BOLD}all done.${RST}  run ${BOLD}snip${RST} to start"
echo
