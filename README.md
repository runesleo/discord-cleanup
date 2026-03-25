# discord-cleanup

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()

Batch leave Discord servers you no longer need. Zero dependencies, single file, dry-run by default.

I had 166 Discord servers from the airdrop era — ZK, Arb, OP, Starknet, NFT, node, GameFi — with 30,000+ unread mentions. This script cleaned it down to 16 in under 2 minutes.

## Quick Start

```bash
git clone https://github.com/runesleo/discord-cleanup.git
cd discord-cleanup

# Set your Discord token (see "Get Your Token" below)
export DISCORD_TOKEN="your_token_here"

# See what you have
python discord_cleanup.py list --category

# Preview cleanup (dry-run, nothing happens)
python discord_cleanup.py cleanup

# Edit whitelist.json → add server IDs you want to keep

# Execute cleanup
python discord_cleanup.py cleanup --execute
```

No `pip install`, no `requirements.txt`, no virtual env. Just Python.

## Commands

```bash
# List all servers
python discord_cleanup.py list

# List with auto-categorization (Airdrop/DeFi, NFT, GameFi, Trading, etc.)
python discord_cleanup.py list --category

# Interactive cleanup — dry-run first, shows what would be removed
python discord_cleanup.py cleanup

# Actually leave servers (requires typing "yes" to confirm)
python discord_cleanup.py cleanup --execute

# Leave specific servers by ID
python discord_cleanup.py leave <server_id> [<server_id> ...]
```

## How Cleanup Works

```
Fetch all servers → Auto-categorize → Generate whitelist.json
                                            ↓
                              Edit whitelist (add IDs to keep)
                                            ↓
                              Run --execute → Confirm "yes" → Done
```

1. Fetches all your servers and groups them by category
2. Creates `whitelist.json` — servers you own are auto-whitelisted
3. **Dry-run by default**: shows the plan, touches nothing
4. You edit `whitelist.json` to add servers worth keeping
5. `--execute` leaves the rest, with a confirmation prompt

## Get Your Token

1. Open [Discord](https://discord.com/app) in your browser
2. Press `F12` → **Network** tab
3. Click anything in Discord, find a request to `discord.com`
4. Copy the `Authorization` header value

```bash
export DISCORD_TOKEN="your_token_here"
# or
python discord_cleanup.py list --token "your_token_here"
```

> **Security note:** Your token grants full account access. Never commit it, never share it. If compromised, change your Discord password immediately (invalidates all tokens).

## Safety

- **Dry-run by default** — nothing happens unless you pass `--execute`
- **Confirmation required** — must type `yes` to proceed
- **Owned servers protected** — auto-whitelisted, can't accidentally leave
- **Rate limit handling** — waits automatically when Discord throttles
- **Whitelist persistence** — saved to file, survives re-runs

## Other Tools

- [x-reader](https://github.com/runesleo/x-reader) — Universal content reader for 7+ platforms
- [claude-code-workflow](https://github.com/runesleo/claude-code-workflow) — Battle-tested Claude Code workflow template

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=runesleo/discord-cleanup,runesleo/x-reader,runesleo/claude-code-workflow,runesleo/systematic-debugging-skill&type=Date)](https://star-history.com/#runesleo/discord-cleanup&runesleo/x-reader&runesleo/claude-code-workflow&runesleo/systematic-debugging-skill&Date)

## License

MIT

---

Built by [@runes_leo](https://x.com/runes_leo) · [leolabs.me](https://leolabs.me)
