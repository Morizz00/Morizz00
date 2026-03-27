#!/usr/bin/env python3
"""
update_readme.py
Fetches LeetCode stats, generates SVG cards, updates README markers.
"""

import re, sys, requests
import generate_cards as cards

ACCOUNTS = {
    "MAIN":     "Mozzy_11",
    "CONTESTS": "TheSmurfAndor",
}
README_PATH  = "README.md"
LEETCODE_GQL = "https://leetcode.com/graphql"
RAW_BASE = "assets/cards"

HEADERS = {
    "Content-Type": "application/json",
    "Referer":      "https://leetcode.com",
    "User-Agent":   "Mozilla/5.0",
}

PROFILE_QUERY = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    username
    submitStats { acSubmissionNum { difficulty count } }
  }
}
"""

CONTEST_QUERY = """
query getUserContestRanking($username: String!) {
  userContestRanking(username: $username) {
    attendedContestsCount
    rating
    globalRanking
    topPercentage
  }
}
"""

def gql(query, variables):
    r = requests.post(LEETCODE_GQL, json={"query": query, "variables": variables},
                      headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()

def fetch_main(username):
    data  = gql(PROFILE_QUERY, {"username": username})
    user  = data["data"]["matchedUser"]
    stats = {s["difficulty"]: s for s in user["submitStats"]["acSubmissionNum"]}
    return {
        "username": user["username"],
        "total":    stats.get("All",    {}).get("count", 0),
        "easy":     stats.get("Easy",   {}).get("count", 0),
        "medium":   stats.get("Medium", {}).get("count", 0),
        "hard":     stats.get("Hard",   {}).get("count", 0),
    }

def fetch_contests(username):
    p  = gql(PROFILE_QUERY,  {"username": username})
    c  = gql(CONTEST_QUERY,  {"username": username})
    user  = p["data"]["matchedUser"]
    stats = {s["difficulty"]: s for s in user["submitStats"]["acSubmissionNum"]}
    cr    = c["data"].get("userContestRanking") or {}
    return {
        "username":       user["username"],
        "total":          stats.get("All",    {}).get("count", 0),
        "easy":           stats.get("Easy",   {}).get("count", 0),
        "medium":         stats.get("Medium", {}).get("count", 0),
        "hard":           stats.get("Hard",   {}).get("count", 0),
        "rating":         int(cr.get("rating") or 0),
        "global_rank":    cr.get("globalRanking") or 0,
        "top_pct":        round(float(cr.get("topPercentage") or 0), 1),
        "contests_count": cr.get("attendedContestsCount") or 0,
    }

def img_block(svg_file, link, alt):
    return (
        f'<div align="center">\n'
        f'  <a href="{link}">\n'
        f'    <img src="{RAW_BASE}/{svg_file}" alt="{alt}" />\n'
        f'  </a>\n'
        f'</div>\n'
    )

def replace_section(content, marker, body):
    pat = rf"(<!-- {marker}:START -->).*?(<!-- {marker}:END -->)"
    return re.sub(pat, rf"\1\n{body}\n\2", content, flags=re.DOTALL)

def main():
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    errors = []

    # LeetCode Main
    try:
        d = fetch_main(ACCOUNTS["MAIN"])
        cards.write_main(d)
        content = replace_section(content, "LEETCODE-MAIN",
            img_block("lc_main.svg", f"https://leetcode.com/{d['username']}/", "LeetCode Main"))
        print(f"✅ Main ({d['username']}): {d['total']} solved")
    except Exception as e:
        errors.append(str(e))
        print(f"❌ Main failed: {e}", file=sys.stderr)

    # LeetCode Contests
    try:
        d = fetch_contests(ACCOUNTS["CONTESTS"])
        cards.write_contests(d)
        content = replace_section(content, "LEETCODE-CONTESTS",
            img_block("lc_contests.svg", f"https://leetcode.com/{d['username']}/", "LeetCode Contests"))
        print(f"✅ Contests ({d['username']}): {d['total']} solved, rating {d['rating']}")
    except Exception as e:
        errors.append(str(e))
        print(f"❌ Contests failed: {e}", file=sys.stderr)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("📝 README.md written")

    if errors:
        print(f"\n⚠️  {len(errors)} error(s)")
        sys.exit(1)

if __name__ == "__main__":
    main()
