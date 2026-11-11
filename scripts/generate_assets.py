"""Generates the static visual assets for the profile README (stdlib only).

    python scripts/generate_assets.py

Outputs into assets/: hero.svg, ticker.svg and cards/<slug>.svg.
Everything is pure SVG + SMIL/CSS so it animates inside a GitHub <img> tag.
"""
import math
import os
import random
from html import escape

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
SANS = "-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','SF Mono',Consolas,'DejaVu Sans Mono',monospace"


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("wrote", os.path.normpath(path))


# --------------------------------------------------------------------------- hero
def hero():
    W, H, HZ = 1200, 440, 262
    rnd = random.Random(7)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" '
         f'aria-label="Arunan Kavirajan">']
    s.append(f'''<defs>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="70"/></filter>
<filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<linearGradient id="name" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="#e0f2fe"/><stop offset="1" stop-color="#ede9fe"/></linearGradient>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05060d" stop-opacity="1"/><stop offset=".35" stop-color="#05060d" stop-opacity="0"/><stop offset="1" stop-color="#05060d" stop-opacity=".85"/></linearGradient>
<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#38bdf8" stop-opacity="0"/><stop offset=".5" stop-color="#a78bfa"/><stop offset="1" stop-color="#f472b6" stop-opacity="0"/></linearGradient>
<clipPath id="floor"><rect x="0" y="{HZ}" width="{W}" height="{H-HZ}"/></clipPath>
<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<style>
.mono{{font-family:{MONO}}}
.name{{font-family:{SANS};font-weight:900;font-size:84px}}
.blink{{animation:bl 1.1s steps(1) infinite}}@keyframes bl{{50%{{opacity:0}}}}
</style>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="#05060d"/>''')

    # aurora blobs
    for cx, cy, r, col, dx, dy, dur in [(230, 120, 190, "#38bdf8", 90, 30, 14), (980, 90, 210, "#a78bfa", -80, 40, 17),
                                         (620, 330, 170, "#f472b6", 60, -40, 20)]:
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}" opacity=".30" filter="url(#blur)">'
                 f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" '
                 f'dur="{dur}s" repeatCount="indefinite"/></circle>')

    # perspective floor: vertical rays + moving horizontal lines
    s.append('<g clip-path="url(#floor)" stroke="#8b5cf6">')
    for i in range(-14, 15):
        x2 = W / 2 + i * 150
        s.append(f'<line x1="{W/2}" y1="{HZ}" x2="{x2}" y2="{H+10}" stroke-opacity="{0.34 - abs(i)*0.012:.3f}"/>')
    n, dur = 9, 4.5
    for k in range(n):
        ys = ";".join(f"{HZ + (H-HZ+20)*(j/24)**2.2:.1f}" for j in range(25))
        ops = ";".join(f"{min(1, j/24*2.2)*.55:.2f}" for j in range(25))
        s.append(f'<line x1="0" x2="{W}" stroke="#38bdf8" y1="{HZ}" y2="{HZ}">'
                 f'<animate attributeName="y1" values="{ys}" dur="{dur}s" begin="-{k*dur/n:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="y2" values="{ys}" dur="{dur}s" begin="-{k*dur/n:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="stroke-opacity" values="{ops}" dur="{dur}s" begin="-{k*dur/n:.2f}s" repeatCount="indefinite"/></line>')
    s.append('</g>')
    s.append(f'<rect y="{HZ-40}" width="{W}" height="{H-HZ+40}" fill="url(#fade)"/>')
    s.append(f'<rect x="100" y="{HZ}" width="1000" height="2" fill="url(#beam)" filter="url(#glow)"/>')

    # rising code particles
    glyphs = ["{ }", "</>", "=>", "01", "()", "[]", "#", ";", "&&", "fn", "::", "0x"]
    for _ in range(26):
        x, d, sz = rnd.randint(20, W - 20), rnd.uniform(7, 15), rnd.choice([12, 14, 16, 20])
        col = rnd.choice(["#38bdf8", "#a78bfa", "#f472b6", "#94a3b8"])
        s.append(f'<text class="mono" x="{x}" y="{H+30}" font-size="{sz}" fill="{col}" opacity="0">{escape(rnd.choice(glyphs))}'
                 f'<animate attributeName="y" values="{H+30};-30" dur="{d:.1f}s" begin="-{rnd.uniform(0,d):.1f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values="0;.5;.5;0" keyTimes="0;.2;.8;1" dur="{d:.1f}s" begin="-{rnd.uniform(0,d):.1f}s" repeatCount="indefinite"/></text>')

    # name with RGB-split glitch
    cx = W / 2
    glitch = "0 0;0 0;-7 1;6 -2;0 0;0 0;4 0;-5 1;0 0;0 0"
    kt = "0;.60;.61;.63;.64;.80;.81;.83;.84;1"
    for col, dx in (("#22d3ee", -4), ("#f472b6", 4)):
        s.append(f'<text class="name" x="{cx+dx}" y="168" text-anchor="middle" textLength="1020" lengthAdjust="spacingAndGlyphs" '
                 f'fill="{col}" opacity=".75" style="mix-blend-mode:screen">ARUNAN KAVIRAJAN'
                 f'<animateTransform attributeName="transform" type="translate" calcMode="discrete" values="{glitch}" keyTimes="{kt}" dur="5s" repeatCount="indefinite"/></text>')
    s.append(f'<text class="name" x="{cx}" y="168" text-anchor="middle" textLength="1020" lengthAdjust="spacingAndGlyphs" '
             f'fill="url(#name)" filter="url(#glow)">ARUNAN KAVIRAJAN</text>')

    # rotating role line
    lines = ["I BUILD THINGS THAT SHIP", "FULL-STACK  ·  MOBILE  ·  AI TOOLING", "DETERMINISTIC CORE. INTELLIGENT EDGE.",
             "FROM ZERO TO DEPLOYED"]
    dur = 3.5 * len(lines)
    for i, t in enumerate(lines):
        a, b, c, d = i / len(lines), (i + .07) / len(lines), (i + .93) / len(lines), (i + 1) / len(lines)
        pts = [(0, 0), (a, 0), (b, 1), (c, 1), (d, 0), (1, 0)] if i else [(0, 1), (c, 1), (d, 0), (1, 0)]
        pts = sorted(set(pts))
        s.append(f'<text class="mono" x="{cx}" y="222" text-anchor="middle" font-size="22" letter-spacing="6" fill="#cbd5e1" opacity="{pts[0][1]}">{escape(t)}'
                 f'<animate attributeName="opacity" keyTimes="{";".join(f"{p:.4f}" for p, _ in pts)}" '
                 f'values="{";".join(str(v) for _, v in pts)}" dur="{dur}s" repeatCount="indefinite"/></text>')

    # HUD + frame + scanline
    s.append(f'<g class="mono" font-size="12" fill="#64748b" letter-spacing="2"><text x="36" y="42">SYS://PROFILE</text>'
             f'<text x="{W-36}" y="42" text-anchor="end"><tspan class="blink" fill="#22c55e">●</tspan> ONLINE</text>'
             f'<text x="36" y="{H-30}">BUILD 2026</text><text x="{W-36}" y="{H-30}" text-anchor="end">SHIPPING</text></g>')
    s.append('<g fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" opacity=".8">'
             f'<path d="M18 52V18H52"/><path d="M{W-52} 18H{W-18}V52"/><path d="M18 {H-52}V{H-18}H52"/><path d="M{W-52} {H-18}H{W-18}V{H-52}"/></g>')
    s.append(f'<rect width="{W}" height="3" fill="#fff" opacity=".07"><animate attributeName="y" values="-4;{H}" dur="6s" repeatCount="indefinite"/></rect>')
    s.append('</g>')
    s.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="#fff" stroke-opacity=".1"/>')
    s.append('</svg>')
    write("hero.svg", "\n".join(s))


# ------------------------------------------------------------------------- ticker
def ticker():
    items = ["TYPESCRIPT", "PYTHON", "FLUTTER", "REACT", "NEXT.JS", "FASTAPI", "DART", "TAILWIND", "SQLITE", "NODE.JS",
             "VITE", "OPENCV", "AI AGENTS", "GITHUB ACTIONS", "VERCEL"]
    W, H, cw, gap = 1200, 56, 11.2, 56
    x, parts = 0.0, []
    for t in items:
        parts.append((x, t))
        x += len(t) * cw + gap
    total = x
    body = []
    for rep in range(2):
        for px, t in parts:
            body.append(f'<text x="{px+rep*total:.1f}" y="35" class="m">{escape(t)}</text>'
                        f'<text x="{px+rep*total+len(t)*cw+gap/2-5:.1f}" y="35" class="d">◆</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Technologies: {escape(", ".join(items))}">
<defs><linearGradient id="e" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".08" stop-color="#fff"/><stop offset=".92" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="mk"><rect width="{W}" height="{H}" fill="url(#e)"/></mask>
<linearGradient id="t" x1="0" x2="1"><stop offset="0" stop-color="#38bdf8"/><stop offset="1" stop-color="#a78bfa"/></linearGradient></defs>
<style>.m{{font:700 18px {MONO};fill:#cbd5e1;letter-spacing:2px}}.d{{font:14px {MONO};fill:#a78bfa}}</style>
<rect width="{W}" height="{H}" rx="10" fill="#080b16"/>
<rect x="0" y="0" width="{W}" height="1.5" fill="url(#t)" opacity=".8"/><rect x="0" y="{H-1.5}" width="{W}" height="1.5" fill="url(#t)" opacity=".8"/>
<g mask="url(#mk)"><g><animateTransform attributeName="transform" type="translate" from="0 0" to="-{total:.1f} 0" dur="38s" repeatCount="indefinite"/>
{"".join(body)}</g></g></svg>'''
    write("ticker.svg", svg)


# -------------------------------------------------------------------------- cards
CARDS = [
    ("koda", "01", "KODA", "Codebase intelligence that\ndoesn't hallucinate.", "Deterministic graph first, AI reasoning second.",
     ["Next.js", "TypeScript", "AI Agents"], "#38bdf8", "#6366f1", "LIVE"),
    ("algorithm-laboratory", "02", "ALGORITHM LAB", "Watch algorithms run.\nThen race them.", "Line-by-line traces and head-to-head benchmarks.",
     ["React", "FastAPI", "Python"], "#34d399", "#38bdf8", "LIVE"),
    ("certiva", "03", "CERTIVA", "Certificates,\nwithout the chaos.", "Bulk generation for events, entirely in the browser.",
     ["React", "TypeScript"], "#fbbf24", "#f43f5e", "LIVE"),
    ("d-brownies-billing", "04", "D BROWNIES BILLING", "A point of sale for\na real food stall.", "Offline orders, Bluetooth receipts, live analytics.",
     ["Flutter", "SQLite", "Bluetooth"], "#e0a47a", "#f472b6", "ANDROID"),
    ("ascend", "05", "ASCEND", "Deep work with\naccountability.", "Focus timers, progression and live peer presence.",
     ["React", "TypeScript"], "#a78bfa", "#38bdf8", "LIVE"),
    ("echoes", "06", "ECHOES", "An anonymous\ntime capsule.", "Messages drift across a starfield. No accounts, no feed.",
     ["React", "Vite"], "#f472b6", "#818cf8", "LIVE"),
]


def card(slug, num, title, tag1, tag2, tags, c1, c2, status):
    W, H = 580, 240
    l1, l2 = tag1.split("\n")
    live = status == "LIVE"
    pill_col = "#22c55e" if live else "#fbbf24"
    pw = 78 if live else 104
    chips, x = [], 28
    for t in tags:
        w = len(t) * 7.6 + 24
        chips.append(f'<rect x="{x}" y="{H-58}" width="{w:.0f}" height="26" rx="13" fill="{c1}" fill-opacity=".10" stroke="{c1}" stroke-opacity=".45"/>'
                     f'<text x="{x+w/2:.0f}" y="{H-41}" text-anchor="middle" class="chip">{escape(t)}</text>')
        x += w + 8
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="{escape(title)}: {escape(l1)} {escape(l2)}">
<defs>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>
<radialGradient id="r" cx="1" cy="0" r="1"><stop offset="0" stop-color="{c1}" stop-opacity=".30"/><stop offset="1" stop-color="{c1}" stop-opacity="0"/></radialGradient>
<clipPath id="c"><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18"/></clipPath>
</defs>
<style>
.t{{font:800 30px {SANS};fill:#fff;letter-spacing:.5px}}
.h{{font:700 19px {SANS};fill:#e2e8f0}}
.s{{font:14px {SANS};fill:#94a3b8}}
.chip{{font:600 12px {MONO};fill:#e2e8f0}}
.n{{font:900 96px {SANS};fill:url(#g);opacity:.16}}
.p{{font:700 11px {MONO};letter-spacing:2px;fill:{pill_col}}}
.go{{font:700 13px {MONO};letter-spacing:2px;fill:url(#g)}}
</style>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="#0a0d1a"/>
<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="url(#r)"/>
<text class="n" x="{W-22}" y="104" text-anchor="end">{num}</text></g>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="none" stroke="#fff" stroke-opacity=".09"/>
<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="18" fill="none" stroke="url(#g)" stroke-width="2.5" stroke-linecap="round" pathLength="1000" stroke-dasharray="170 830">
<animate attributeName="stroke-dashoffset" from="0" to="-1000" dur="6s" repeatCount="indefinite"/></rect>
<rect x="28" y="26" width="{pw}" height="24" rx="12" fill="{pill_col}" fill-opacity=".12" stroke="{pill_col}" stroke-opacity=".5"/>
<circle cx="43" cy="38" r="4" fill="{pill_col}"><animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></circle>
<text class="p" x="54" y="42">{status}</text>
<text class="t" x="28" y="92">{escape(title)}</text>
<text class="h" x="28" y="124">{escape(l1)}</text><text class="h" x="28" y="148">{escape(l2)}</text>
<text class="s" x="28" y="{H-68}">{escape(tag2)}</text>
{"".join(chips)}
<text class="go" x="{W-28}" y="{H-41}" text-anchor="end">{"OPEN" if live else "SOURCE"} ↗</text>
</svg>'''
    write(f"cards/{slug}.svg", svg)


if __name__ == "__main__":
    hero()
    ticker()
    for c in CARDS:
        card(*c)
