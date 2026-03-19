# Scripting with snip

snip is designed to compose with other tools. Here are patterns for using it in scripts and automation.

## Capture content silently

Use `-q` to suppress the "Copied to clipboard" message so stdout is clean:

```bash
TOKEN=$(snip -q my-api-token)
curl -H "Authorization: Bearer $TOKEN" https://api.example.com
```

## Run a snippet and check exit code

```bash
snip run deploy-prod
if [[ $? -ne 0 ]]; then
  echo "deploy failed"
  exit 1
fi
```

## Pipe snippet content into a command

```bash
snip -q my-sql-query | psql -U myuser mydb
snip -q nginx-config | ssh user@server "cat > /etc/nginx/nginx.conf"
```

## Use JSON output for structured data

```bash
# Get the content field only
snip --json ports | jq -r '.content'

# Get tags
snip --json deploy | jq -r '.tags[]'

# Check language
snip --json myscript | jq -r '.language'
```

## Iterate over all snippets

```bash
snip --list | while read -r title; do
  echo "=== $title ==="
  snip -q "$title"
  echo
done
```

## Filter by tag and run each

```bash
snip --list startup | while read -r title; do
  snip run "$title"
done
```

## Automated backup in cron

```bash
# Add to crontab: crontab -e
0 9 * * * snip --export > ~/dotfiles/snippets-$(date +%F).json
```

If you're tracking `~/.config/snip/snippets/` with git (v0.7.0+), a cron export is less necessary — every snippet edit is already a committable change.

## Check if a snippet exists

```bash
if snip -q mysnippet > /dev/null 2>&1; then
  echo "found"
else
  echo "not found"
fi
```
