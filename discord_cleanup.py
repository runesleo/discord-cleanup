#!/usr/bin/env python3
"""
Discord Server Cleanup Tool

Batch leave Discord servers you no longer need.
Works with your browser's Discord session — no bot required.

Usage:
    python discord_cleanup.py list                    # List all servers
    python discord_cleanup.py list --category         # List with auto-categorization
    python discord_cleanup.py cleanup                 # Interactive cleanup (dry-run first)
    python discord_cleanup.py cleanup --execute       # Actually leave servers
    python discord_cleanup.py leave <server_id>       # Leave a specific server
    python discord_cleanup.py leave <id1> <id2> ...   # Leave multiple servers

Token:
    Set DISCORD_TOKEN env var, or pass --token <token>

    To get your token from Chrome DevTools:
    1. Open Discord in browser, press F12
    2. Go to Network tab, click any request to discord.com
    3. Find "Authorization" header, copy the value
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

API_BASE = "https://discord.com/api/v10"
RATE_LIMIT_PAUSE = 1.0  # seconds between leave requests


def api_request(method, endpoint, token, data=None):
    """Make a Discord API request."""
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "X-Discord-Locale": "en-US",
        "X-Discord-Timezone": "Asia/Shanghai",
    }

    req = urllib.request.Request(url, method=method, headers=headers)
    if data:
        req.data = json.dumps(data).encode()

    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 204:
                return None
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            retry_after = json.loads(e.read()).get("retry_after", 5)
            print(f"  Rate limited, waiting {retry_after}s...")
            time.sleep(retry_after)
            return api_request(method, endpoint, token, data)
        elif e.code == 401:
            print("Error: Invalid token. Please check your Discord token.")
            sys.exit(1)
        else:
            body = e.read().decode()
            print(f"Error {e.code}: {body}")
            return None


def get_guilds(token):
    """Fetch all guilds the user is in."""
    guilds = []
    after = None

    while True:
        endpoint = "/users/@me/guilds?limit=200"
        if after:
            endpoint += f"&after={after}"

        batch = api_request("GET", endpoint, token)
        if not batch:
            break

        guilds.extend(batch)
        if len(batch) < 200:
            break
        after = batch[-1]["id"]

    return guilds


def get_user_info(token):
    """Get current user info to verify token."""
    return api_request("GET", "/users/@me", token)


def categorize_guild(guild):
    """Auto-categorize a guild based on name patterns."""
    name = guild["name"].lower()

    categories = {
        "Airdrop/DeFi": ["airdrop", "defi", "swap", "bridge", "zk", "layer", "l2",
                         "arb", "op ", "starknet", "scroll", "linea", "blast", "zora",
                         "eigen", "ethena", "pendle"],
        "NFT": ["nft", "ape", "punk", "azuki", "doodle", "art", "mint", "opensea"],
        "GameFi": ["game", "guild", "play", "quest", "axie"],
        "Node/Infra": ["node", "validator", "rpc", "infra", "oracle"],
        "Trading": ["trade", "signal", "alpha", "whale", "dex", "perp", "futures"],
        "DAO": ["dao", "governance", "vote", "treasury"],
        "Dev/Tools": ["dev", "hack", "build", "github", "code", "sdk", "api"],
    }

    for category, keywords in categories.items():
        if any(kw in name for kw in keywords):
            return category

    return "Other"


def cmd_list(args, token):
    """List all servers."""
    guilds = get_guilds(token)

    if not guilds:
        print("No servers found.")
        return

    if args.category:
        # Group by category
        categorized = {}
        for g in guilds:
            cat = categorize_guild(g)
            categorized.setdefault(cat, []).append(g)

        print(f"\n{'='*60}")
        print(f" {len(guilds)} servers, auto-categorized")
        print(f"{'='*60}")

        for cat in sorted(categorized.keys()):
            servers = categorized[cat]
            print(f"\n[{cat}] ({len(servers)})")
            for g in servers:
                owner = " 👑" if g.get("owner") else ""
                print(f"  {g['id']}  {g['name']}{owner}")
    else:
        print(f"\n{'='*60}")
        print(f" {len(guilds)} servers")
        print(f"{'='*60}\n")

        for g in guilds:
            owner = " 👑" if g.get("owner") else ""
            print(f"  {g['id']}  {g['name']}{owner}")

    print(f"\n👑 = you own this server (cannot leave, only delete)")
    print(f"Total: {len(guilds)} servers\n")


def cmd_cleanup(args, token):
    """Interactive cleanup flow."""
    guilds = get_guilds(token)

    if not guilds:
        print("No servers found.")
        return

    # Show categorized list
    categorized = {}
    for g in guilds:
        cat = categorize_guild(g)
        categorized.setdefault(cat, []).append(g)

    print(f"\n{'='*60}")
    print(f" Found {len(guilds)} servers")
    print(f"{'='*60}")

    for cat in sorted(categorized.keys()):
        servers = categorized[cat]
        print(f"\n[{cat}] ({len(servers)})")
        for g in servers:
            owner = " 👑" if g.get("owner") else ""
            print(f"  {g['id']}  {g['name']}{owner}")

    # Load or create whitelist
    whitelist_file = os.path.join(os.path.dirname(__file__) or ".", "whitelist.json")
    whitelist = set()

    if os.path.exists(whitelist_file):
        with open(whitelist_file) as f:
            whitelist = set(json.load(f))
        print(f"\nLoaded whitelist: {len(whitelist)} servers to keep")

    # Owned servers auto-whitelisted
    owned = {g["id"] for g in guilds if g.get("owner")}
    whitelist |= owned

    to_leave = [g for g in guilds if g["id"] not in whitelist]
    to_keep = [g for g in guilds if g["id"] in whitelist]

    print(f"\n--- Plan ---")
    print(f"  Keep:  {len(to_keep)} servers (whitelisted + owned)")
    print(f"  Leave: {len(to_leave)} servers")

    if to_leave:
        print(f"\nServers to leave:")
        for g in to_leave:
            print(f"  ❌ {g['name']}")

    if not args.execute:
        print(f"\n⚠️  DRY RUN — no servers were left.")
        print(f"To execute: python {sys.argv[0]} cleanup --execute")
        print(f"\nTo customize, edit {whitelist_file} (list of server IDs to keep)")

        # Save default whitelist if none exists
        if not os.path.exists(whitelist_file):
            with open(whitelist_file, "w") as f:
                json.dump(list(owned), f, indent=2)
            print(f"Created {whitelist_file} with {len(owned)} owned servers.")
            print(f"Add server IDs you want to keep, then re-run with --execute.")
        return

    # Execute
    confirm = input(f"\nLeave {len(to_leave)} servers? Type 'yes' to confirm: ")
    if confirm.strip().lower() != "yes":
        print("Cancelled.")
        return

    success = 0
    failed = 0

    for g in to_leave:
        print(f"  Leaving {g['name']}...", end=" ", flush=True)
        result = api_request("DELETE", f"/users/@me/guilds/{g['id']}", token)
        if result is None:  # 204 No Content = success
            print("✅")
            success += 1
        else:
            print(f"❌ {result}")
            failed += 1
        time.sleep(RATE_LIMIT_PAUSE)

    print(f"\nDone: {success} left, {failed} failed")
    print(f"Remaining: {len(guilds) - success} servers")


def cmd_leave(args, token):
    """Leave specific servers by ID."""
    if not args.server_ids:
        print("Error: provide at least one server ID")
        sys.exit(1)

    # Verify servers exist
    guilds = {g["id"]: g for g in get_guilds(token)}

    for sid in args.server_ids:
        if sid not in guilds:
            print(f"  ⚠️  {sid} — not in your server list, skipping")
            continue

        g = guilds[sid]
        if g.get("owner"):
            print(f"  ⚠️  {g['name']} — you own this server, cannot leave")
            continue

        print(f"  Leaving {g['name']}...", end=" ", flush=True)
        result = api_request("DELETE", f"/users/@me/guilds/{sid}", token)
        if result is None:
            print("✅")
        else:
            print(f"❌ {result}")
        time.sleep(RATE_LIMIT_PAUSE)


def main():
    parser = argparse.ArgumentParser(
        description="Discord Server Cleanup Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--token", help="Discord user token (or set DISCORD_TOKEN env)")

    sub = parser.add_subparsers(dest="command")

    # list
    p_list = sub.add_parser("list", help="List all servers")
    p_list.add_argument("--category", "-c", action="store_true", help="Auto-categorize servers")

    # cleanup
    p_cleanup = sub.add_parser("cleanup", help="Interactive cleanup")
    p_cleanup.add_argument("--execute", action="store_true", help="Actually leave (default: dry-run)")

    # leave
    p_leave = sub.add_parser("leave", help="Leave specific servers")
    p_leave.add_argument("server_ids", nargs="+", help="Server IDs to leave")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Get token
    token = args.token or os.environ.get("DISCORD_TOKEN")
    if not token:
        print("Error: Discord token required.")
        print("  Set DISCORD_TOKEN env var, or pass --token <token>")
        print("\n  To get your token:")
        print("  1. Open Discord in browser, press F12")
        print("  2. Network tab → click any request to discord.com")
        print("  3. Copy the 'Authorization' header value")
        sys.exit(1)

    # Verify token
    user = get_user_info(token)
    if not user:
        sys.exit(1)
    print(f"Logged in as: {user['username']} ({user['id']})")

    # Route command
    if args.command == "list":
        cmd_list(args, token)
    elif args.command == "cleanup":
        cmd_cleanup(args, token)
    elif args.command == "leave":
        cmd_leave(args, token)


if __name__ == "__main__":
    main()
