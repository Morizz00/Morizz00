#!/usr/bin/env python3
"""
update_readme.py
Scrapes LeetCode stats for two accounts and updates README.md markers.
Run by GitHub Actions on a schedule.
"""

import re
import sys
import json
import requests

# ── Config ────────────────────────────────────────────────────────────────────
ACCOUNTS = {
    "MAIN":     "Mozzy_11",
    "CONTESTS": "TheSmurfAndor",
}
TENSORTONIC_URL  = "https://tensortonic.com/profile/feapoflaith"
README_PATH      = "README.md"
LEETCODE_GQL     = "https://leetcode.com/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "Referer":       "https://leetcode.com",
    "User-Agent":    "Mozilla/5.0",
}

# ── GraphQL query ─────────────────────────────────────────────────────────────
QUERY = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    username
    profile {
      ranking
    }
    submitStats {
      acSubmissionNum {
        difficulty
        count
        submissions
      }
    }
    badges {
      name
    }
  }
}
"""

# ── Helpers ───────────────────────────────────────────────────────────────────
def fetch_leetcode(username: str) -> dict:
    resp = requests.post(
        LEETCODE_GQL,
        json={"query": QUERY, "variables": {"username": username}},
        headers=HEADERS,
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    user = data["data"]["matchedUser"]
    stats = {s["difficulty"]: s for s in user["submitStats"]["acSubmissionNum"]}
    return {
        "username": user["username"],
        "ranking":  user["profile"]["ranking"],
        "total":    stats.get("All",  {}).get("count", 0),
        "easy":     stats.get("Easy", {}).get("count", 0),
        "medium":   stats.get("Medium", {}).get("count", 0),
        "hard":     stats.get("Hard", {}).get("count", 0),
        "badges":   len(user.get("badges", [])),
    }

def badge(label: str, message: str, color: str, logo: str = "") -> str:
    label_enc   = label.replace("-", "--").replace("_", "__").replace(" ", "_")
    message_enc = str(message).replace("-", "--").replace("_", "__").replace(" ", "_")
    logo_part   = f"&logo={logo}" if logo else ""
    return (
        f"![{label}](https://img.shields.io/badge/"
        f"{label_enc}-{message_enc}-{color}?style=flat-square{logo_part})"
    )

def leet_block(data: dict, label: str, color: str) -> str:
    profile_url = f"https://leetcode.com/{data['username']}/"
    lines = [
        f"### 🧩 LeetCode — {label} [`{data['username']}`]({profile_url})",
        "",
        f"{badge('Solved', data['total'], color, 'leetcode')} "
        f"{badge('Easy', data['easy'], '00b8a3')} "
        f"{badge('Medium', data['medium'], 'ffa116')} "
        f"{badge('Hard', data['hard'], 'ef4743')} "
        f"{badge('Rank', f\"#{data['ranking']:,}\", '6c757d')}",
        "",
    ]
    return "\n".join(lines)

def tensortonic_block() -> str:
    return (
        "### 🤖 TensorTonic\n\n"
        f"[![TensorTonic](https://img.shields.io/badge/TensorTonic-feapoflaith-FF6B35?"
        f"style=flat-square&logo=pytorch&logoColor=white)]({TENSORTONIC_URL})\n"
    )

def replace_section(content: str, marker: str, new_body: str) -> str:
    pattern = rf"(<!-- {marker}:START -->).*?(<!-- {marker}:END -->)"
    replacement = rf"\1\n{new_body}\n\2"
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    errors = []

    # LeetCode — Main
    try:
        main_data = fetch_leetcode(ACCOUNTS["MAIN"])
        block = leet_block(main_data, "Main", "FFA116")
        content = replace_section(content, "LEETCODE-MAIN", block)
        print(f"✅ Fetched Main ({ACCOUNTS['MAIN']}): {main_data['total']} solved")
    except Exception as e:
        errors.append(f"Main LeetCode: {e}")
        print(f"❌ Main LeetCode failed: {e}", file=sys.stderr)

    # LeetCode — Contests
    try:
        contest_data = fetch_leetcode(ACCOUNTS["CONTESTS"])
        block = leet_block(contest_data, "Contests", "EF4743")
        content = replace_section(content, "LEETCODE-CONTESTS", block)
        print(f"✅ Fetched Contests ({ACCOUNTS['CONTESTS']}): {contest_data['total']} solved")
    except Exception as e:
        errors.append(f"Contests LeetCode: {e}")
        print(f"❌ Contests LeetCode failed: {e}", file=sys.stderr)

    # TensorTonic (static badge — no public API)
    content = replace_section(content, "TENSORTONIC", tensortonic_block())
    print("✅ TensorTonic block updated")

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("📝 README.md written successfully")

    if errors:
        print(f"\n⚠️  {len(errors)} error(s) occurred — partial update written")
        sys.exit(1)

if __name__ == "__main__":
    main()
