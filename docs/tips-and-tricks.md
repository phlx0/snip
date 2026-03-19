# Tips & tricks

## Name snippets like commands

Use short, memorable names that feel like commands — `ports`, `disk`, `docker-clean`, `who`. Then `snip ports` reads naturally.

## Use tags as categories

Tags let you group snippets without rigid folders:

```
#docker #devops     → infrastructure stuff
#git                → git one-liners
#debug              → debugging helpers
#startup            → things to run when setting up a machine
```

Filter them from the CLI: `snip --list docker`

## Pin your most-used snippets

Press `p` in the TUI to pin a snippet — it stays at the top of the list permanently. Great for snippets you reach for every day.

## Save entire scripts, not just one-liners

snip handles multi-line content fine. Save that 20-line deploy script and run it with `snip run deploy`.

## Keep a "startup" tag

Tag snippets you run on a new machine with `#startup`, then:

```bash
snip --list startup | while read -r t; do snip run "$t"; done
```

One command to bootstrap a new environment.

## Use descriptions

When editing a snippet, fill in the description field. It shows up in the TUI preview and is searchable — so `snip` finds it even if you forget the exact title.

## Quick add from terminal output

```bash
# Save the output of a command as a snippet
some-command | snip --import -
```

Or just copy it and create a new snippet with `n` in the TUI.

## Chain with pbcopy / xclip manually

```bash
snip -q ports | xclip -selection clipboard
```

Useful if you want to copy without the built-in clipboard logic.

## Sync across machines with git

Since v0.7.0, snippets are plain files in `~/.config/snip/snippets/`. Track them with git for free sync, history, and diffs:

```bash
cd ~/.config/snip
git init
git add snippets/
git commit -m "initial snippets"
git remote add origin git@github.com:you/snippets.git
git push -u origin main
```

On another machine: `git clone` the repo into `~/.config/snip/` and snip picks it up automatically.

## Back up before big changes

```bash
snip --export > ~/snip-backup-$(date +%F).json
```

Or if you're already using git for your snippets, just check the log — every change is already tracked.
