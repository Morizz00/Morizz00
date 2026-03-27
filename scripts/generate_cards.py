#!/usr/bin/env python3
"""
generate_cards.py
Generates SVG stat cards for LeetCode Main + Contests.
LeetCode orange/dark theme.
"""

import math, os

OUT_DIR = "assets/cards"
os.makedirs(OUT_DIR, exist_ok=True)

T = {
    "bg":     "#0d1117",
    "bg2":    "#161b22",
    "border": "#2d2d2d",
    "text":   "#ffffff",
    "muted":  "#808080",
    "orange": "#ffa116",
    "teal":   "#00b8a3",
    "red":    "#ef4743",
    "yellow": "#ffb800",
}

def donut(cx, cy, r, sw, pct, color):
    circ = 2 * math.pi * r
    dash = pct * circ
    gap  = circ - dash
    bg  = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#2d2d2d" stroke-width="{sw}"/>'
    val = (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
        f'stroke="{color}" stroke-width="{sw}" '
        f'stroke-dasharray="{dash:.2f} {gap:.2f}" '
        f'stroke-linecap="round" '
        f'transform="rotate(-90 {cx} {cy})"/>'
    )
    return bg + val

def bar(x, y, w, h, pct, color, label, count):
    filled = max(pct * w, 0)
    r = h // 2
    out  = f'<text x="{x}" y="{y-5}" font-size="10" fill="{T["muted"]}" font-family="JetBrains Mono,monospace">{label}</text>'
    out += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="#2d2d2d"/>'
    out += f'<rect x="{x}" y="{y}" width="{filled:.1f}" height="{h}" rx="{r}" fill="{color}"/>'
    out += f'<text x="{x+w+8}" y="{y+h}" font-size="10" fill="{T["text"]}" font-family="JetBrains Mono,monospace" font-weight="600">{count}</text>'
    return out

def wrap(w, h, body):
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'xmlns="http://www.w3.org/2000/svg">\n'
        f'<defs><style>'
        f'@import url("https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&display=swap");'
        f'</style></defs>\n'
        f'{body}\n</svg>'
    )

# ── LeetCode Main ─────────────────────────────────────────────────────────────
def card_main(d):
    W, H   = 495, 195
    total  = d["total"]
    easy, medium, hard = d["easy"], d["medium"], d["hard"]
    pe = easy   / max(total, 1)
    pm = medium / max(total, 1)
    ph = hard   / max(total, 1)
    pct = min(total / 3500, 1.0)
    cx, cy, r = 82, 103, 54

    e = []
    e.append(f'<rect width="{W}" height="{H}" rx="10" fill="{T["bg"]}"/>')
    e.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="9.5" fill="none" stroke="{T["border"]}"/>')

    # header strip
    e.append(f'<rect width="{W}" height="38" rx="10" fill="#161b22"/>')
    e.append(f'<rect y="28" width="{W}" height="10" fill="#161b22"/>')
    e.append(f'<text x="18" y="24" font-size="11" fill="{T["muted"]}" font-family="JetBrains Mono,monospace" font-weight="600" letter-spacing="1.5">LEETCODE  ›  MAIN</text>')
    e.append(f'<text x="{W-18}" y="24" font-size="11" fill="{T["orange"]}" font-family="JetBrains Mono,monospace" font-weight="600" text-anchor="end">@{d["username"]}</text>')
    e.append(f'<line x1="0" y1="38" x2="{W}" y2="38" stroke="{T["border"]}"/>')

    # donut
    e.append(donut(cx, cy, r, 10, pct, T["orange"]))
    # inner ring accent
    e.append(donut(cx, cy, r-14, 4, pe, T["teal"]))
    e.append(f'<text x="{cx}" y="{cy-6}" text-anchor="middle" font-size="21" font-weight="700" fill="{T["text"]}" font-family="JetBrains Mono,monospace">{total}</text>')
    e.append(f'<text x="{cx}" y="{cy+12}" text-anchor="middle" font-size="9" fill="{T["muted"]}" font-family="JetBrains Mono,monospace" letter-spacing="1">SOLVED</text>')

    # bars
    bx, bw, bh = 168, 268, 8
    e.append(bar(bx, 60,  bw, bh, pe, T["teal"],   "Easy",   easy))
    e.append(bar(bx, 98,  bw, bh, pm, T["orange"], "Medium", medium))
    e.append(bar(bx, 136, bw, bh, ph, T["red"],    "Hard",   hard))

    # footer
    e.append(f'<line x1="0" y1="{H-30}" x2="{W}" y2="{H-30}" stroke="{T["border"]}"/>')
    e.append(f'<text x="18" y="{H-12}" font-size="10" fill="{T["muted"]}" font-family="JetBrains Mono,monospace">leetcode.com/{d["username"]}</text>')

    return wrap(W, H, "\n".join(e))


# ── LeetCode Contests ─────────────────────────────────────────────────────────
def card_contests(d):
    W, H = 495, 220
    total  = d["total"]
    easy, medium, hard = d["easy"], d["medium"], d["hard"]
    rating = d["rating"]
    g_rank = d["global_rank"]
    top_p  = d["top_pct"]
    n_cont = d["contests_count"]

    pe = easy   / max(total, 1)
    pm = medium / max(total, 1)
    ph = hard   / max(total, 1)
    rp = min(rating / 4000, 1.0)
    cx, cy, r = 82, 112, 54

    # rating colour thresholds (LeetCode style)
    if rating >= 2400:   rcol = "#ff0000"
    elif rating >= 2100: rcol = "#ff8c00"
    elif rating >= 1900: rcol = T["yellow"]
    elif rating >= 1600: rcol = "#8b5cf6"
    else:                rcol = T["teal"]

    e = []
    e.append(f'<rect width="{W}" height="{H}" rx="10" fill="{T["bg"]}"/>')
    e.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="9.5" fill="none" stroke="{T["border"]}"/>')

    # header
    e.append(f'<rect width="{W}" height="38" rx="10" fill="#161b22"/>')
    e.append(f'<rect y="28" width="{W}" height="10" fill="#161b22"/>')
    e.append(f'<text x="18" y="24" font-size="11" fill="{T["muted"]}" font-family="JetBrains Mono,monospace" font-weight="600" letter-spacing="1.5">LEETCODE  ›  CONTESTS</text>')
    e.append(f'<text x="{W-18}" y="24" font-size="11" fill="{T["orange"]}" font-family="JetBrains Mono,monospace" font-weight="600" text-anchor="end">@{d["username"]}</text>')
    e.append(f'<line x1="0" y1="38" x2="{W}" y2="38" stroke="{T["border"]}"/>')

    # rating donut
    e.append(donut(cx, cy, r, 10, rp, rcol))
    e.append(donut(cx, cy, r-14, 4, ph, T["red"]))
    e.append(f'<text x="{cx}" y="{cy-7}" text-anchor="middle" font-size="19" font-weight="700" fill="{T["text"]}" font-family="JetBrains Mono,monospace">{rating if rating else "—"}</text>')
    e.append(f'<text x="{cx}" y="{cy+12}" text-anchor="middle" font-size="9" fill="{T["muted"]}" font-family="JetBrains Mono,monospace" letter-spacing="1">RATING</text>')

    # bars
    bx, bw, bh = 168, 230, 8
    e.append(bar(bx, 56,  bw, bh, pe, T["teal"],   "Easy",   easy))
    e.append(bar(bx, 94,  bw, bh, pm, T["orange"], "Medium", medium))
    e.append(bar(bx, 132, bw, bh, ph, T["red"],    "Hard",   hard))

    # stat pill row
    py = 163
    e.append(f'<rect x="12" y="{py}" width="{W-24}" height="26" rx="6" fill="#161b22"/>')
    rank_str = f"#{g_rank:,}" if g_rank else "—"
    top_str  = f"Top {top_p}%" if top_p else "—"
    cols = [
        (rank_str,       "Global Rank", W*0.17),
        (top_str,        "Percentile",  W*0.40),
        (str(n_cont) if n_cont else "—", "Contests", W*0.63),
        (str(total),     "Solved",      W*0.84),
    ]
    for val, lbl, px in cols:
        e.append(f'<text x="{px:.0f}" y="{py+11}" text-anchor="middle" font-size="11" font-weight="700" fill="{T["orange"]}" font-family="JetBrains Mono,monospace">{val}</text>')
        e.append(f'<text x="{px:.0f}" y="{py+23}" text-anchor="middle" font-size="9" fill="{T["muted"]}" font-family="JetBrains Mono,monospace">{lbl}</text>')

    # footer
    e.append(f'<line x1="0" y1="{H-30}" x2="{W}" y2="{H-30}" stroke="{T["border"]}"/>')
    e.append(f'<text x="18" y="{H-12}" font-size="10" fill="{T["muted"]}" font-family="JetBrains Mono,monospace">leetcode.com/{d["username"]}</text>')

    return wrap(W, H, "\n".join(e))


def write_main(data):
    p = os.path.join(OUT_DIR, "lc_main.svg")
    with open(p, "w") as f: f.write(card_main(data))
    print(f"✅ Written {p}")

def write_contests(data):
    p = os.path.join(OUT_DIR, "lc_contests.svg")
    with open(p, "w") as f: f.write(card_contests(data))
    print(f"✅ Written {p}")
