"""Generates the visuals for the profile README (stdlib only):

    python scripts/generate_assets.py

Concept: the profile is a record sleeve. A Joy Division-style signal ridgeline for the
cover, a stats strip, a tracklist (one animated row per project) and liner notes that
embed the ASCII portrait. Pure SVG + SMIL, so it animates inside a GitHub <img>.
Line counts are measured from git-tracked source (ts/tsx/js/py/dart/css) of each repo.
"""
import math
import os
import random
import re
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "assets")
INK, PAPER, ACC, MUTE = "#0b0b0c", "#f4f4f2", "#ff4d2e", "#85858c"
SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','SF Mono',Consolas,'DejaVu Sans Mono',monospace"

TRACKS = [
    # n, title, blurb, stack, lines of code, link label
    ("01", "KODA", "Codebase intelligence that doesn't hallucinate.", "NEXT.JS · TYPESCRIPT · AI AGENTS", 6114, "LIVE"),
    ("02", "ALGORITHM LAB", "Watch algorithms run. Then race them.", "REACT · FASTAPI · PYTHON", 6613, "LIVE"),
    ("03", "CERTIVA", "Certificates, without the chaos.", "REACT · TYPESCRIPT", 3555, "LIVE"),
    ("04", "D BROWNIES BILLING", "A point of sale for a real food stall.", "FLUTTER · SQLITE · BLUETOOTH", 4737, "SOURCE"),
    ("05", "ASCEND", "Deep work, with accountability.", "REACT · TYPESCRIPT", 6590, "LIVE"),
    ("06", "ECHOES", "An anonymous time capsule.", "REACT · VITE", 3072, "LIVE"),
    ("07", "CHAT CLUB", "A home on the web for a cybersecurity club.", "NEXT.JS · TYPESCRIPT", 9707, "LIVE"),
]


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("wrote", os.path.normpath(path))


# ---------------------------------------------------------------------------- hero
def hero():
    W, H = 1200, 640
    N, K, STEP = 34, 5, 8
    X0, X1 = 150, 1050
    rnd = random.Random(11)
    xs = list(range(X0, X1 + 1, STEP))
    base0, dy = 150, 10.5

    # smooth envelope with a few "events" (peaks) so the silhouette reads like a signal
    peaks = [(600, 1.0, 120), (455, .55, 70), (735, .7, 80), (330, .3, 60), (880, .35, 60)]

    def env(x):
        return min(1.0, sum(a * math.exp(-((x - c) / s) ** 2) for c, a, s in peaks))

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" '
         f'aria-label="Arunan Kavirajan. Selected works, volume 01.">',
         f'''<defs>
<linearGradient id="fx" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".15" stop-color="#fff" stop-opacity="0"/><stop offset=".27" stop-color="#fff"/><stop offset=".73" stop-color="#fff"/><stop offset=".85" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="mx"><rect width="{W}" height="{H}" fill="url(#fx)"/></mask>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .55 0"/></filter>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
</defs>
<style>.mono{{font-family:{MONO}}}.sans{{font-family:{SANS}}}</style>
<rect width="{W}" height="{H}" rx="6" fill="{INK}"/>''']

    hot = 24
    s.append('<g mask="url(#mx)">')
    for j in range(N):
        base = base0 + j * dy
        amp = 46 + 40 * (j / N)  # nearer lines swing harder
        a = [rnd.uniform(.03, .06), rnd.uniform(.09, .14), rnd.uniform(.18, .27)]
        p = [rnd.uniform(0, 6.28) for _ in range(3)]
        m = [rnd.choice([1, 1, 2]), rnd.choice([1, 2, 3]), rnd.choice([2, 3, 4])]
        frames = []
        for k in range(K):
            th = 2 * math.pi * k / (K - 1)
            pts = []
            for x in xs:
                v = (.5 * math.sin(a[0] * x + p[0] + m[0] * th) + .32 * math.sin(a[1] * x + p[1] - m[1] * th)
                     + .26 * math.sin(a[2] * x + p[2] + m[2] * th))
                v = abs(v) * 1.25 - .12 + .15 * math.sin(.9 * x + j + th)
                pts.append((x, base - amp * env(x) * max(0, v)))
            frames.append("M" + " L".join(f"{x},{y:.1f}" for x, y in pts) + f" L{X1},{H+30} L{X0},{H+30} Z")
        stroke, sw, op = (ACC, 1.8, 1) if j == hot else (PAPER, 1.15, .55 + .45 * j / N)
        s.append(f'<path d="{frames[0]}" fill="{INK}" stroke="{stroke}" stroke-width="{sw}" stroke-opacity="{op:.2f}" stroke-linejoin="round">'
                 f'<animate attributeName="d" dur="18s" repeatCount="indefinite" values="{";".join(frames)}"/></path>')
    s.append('</g>')

    # playhead sweeping across the cover
    s.append(f'<g><rect x="0" y="86" width="1.6" height="430" fill="{ACC}"><animate attributeName="x" values="{X0};{X1}" dur="18s" repeatCount="indefinite"/></rect>'
             f'<path d="M-6 80H6L0 90Z" fill="{ACC}"><animateTransform attributeName="transform" type="translate" values="{X0} 0;{X1} 0" dur="18s" repeatCount="indefinite"/></path></g>')

    # type
    s.append(f'<text class="mono" x="40" y="48" font-size="15" letter-spacing="6" fill="{PAPER}" style="fill:{PAPER}">ARUNAN KAVIRAJAN</text>')
    s.append(f'<text class="mono" x="{W-40}" y="48" font-size="15" letter-spacing="6" text-anchor="end" style="fill:{MUTE}">SELECTED WORKS  /  VOL. 01</text>')
    s.append(f'<text class="sans" x="38" y="598" font-size="104" font-weight="900" textLength="1124" lengthAdjust="spacing" '
             f'style="fill:{PAPER}">ARUNAN KAVIRAJAN</text>')
    s.append(f'<rect x="40" y="610" width="1120" height="1" fill="{PAPER}" opacity=".25"/>')
    s.append(f'<circle cx="{W-40}" cy="617" r="4" fill="{ACC}"><animate attributeName="opacity" values="1;.15;1" dur="1.4s" repeatCount="indefinite"/></circle>')
    s.append(f'<text class="mono" x="{W-52}" y="621" font-size="11" letter-spacing="3" text-anchor="end" style="fill:{MUTE}">NOW PLAYING</text>')
    s.append(f'<rect width="{W}" height="{H}" rx="6" filter="url(#grain)" opacity=".10"/>')
    s.append('</svg>')
    write("hero.svg", "\n".join(s))


# --------------------------------------------------------------------------- facts
def facts():
    total = sum(t[4] for t in TRACKS)
    items = [(str(len(TRACKS)), "PROJECTS SHIPPED"), (str(sum(1 for t in TRACKS if t[5] == "LIVE")), "LIVE ON THE WEB"),
             (f"{total // 1000}K+", "LINES OF CODE"), ("4", "LANGUAGES")]
    W, H = 1000, 150
    cw = W / len(items)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="'
         f'{escape(", ".join(a + " " + b.lower() for a, b in items))}">',
         f'<style>.n{{font:900 62px {SANS};fill:{PAPER};letter-spacing:-2px}}.l{{font:12px {MONO};letter-spacing:3px;fill:{MUTE}}}</style>',
         f'<rect width="{W}" height="{H}" rx="6" fill="{INK}"/>']
    for i, (n, label) in enumerate(items):
        x = i * cw + 36
        s.append(f'<rect x="{x}" y="26" width="{cw-72:.0f}" height="2" fill="{PAPER}" opacity=".18"/>'
                 f'<rect x="{x}" y="26" width="0" height="2" fill="{ACC}"><animate attributeName="width" values="0;{cw-72:.0f};{cw-72:.0f};0" keyTimes="0;.3;.8;1" dur="7s" begin="{i*.5}s" repeatCount="indefinite"/></rect>'
                 f'<text class="n" x="{x-3}" y="100">{n}</text><text class="l" x="{x}" y="128">{label}</text>')
    s.append('</svg>')
    write("facts.svg", "\n".join(s))


# -------------------------------------------------------------------------- tracks
def track(i, t):
    n, title, blurb, stack, loc, kind = t
    W, H = 1000, 108
    rnd = random.Random(100 + i)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" '
         f'aria-label="Track {n}: {escape(title)}. {escape(blurb)}">',
         f'<style>.n{{font:700 15px {MONO};fill:{ACC}}}.t{{font:900 32px {SANS};fill:{PAPER};letter-spacing:-.5px}}'
         f'.b{{font:15px {SANS};fill:#d4d4d8}}.s{{font:11px {MONO};letter-spacing:2px;fill:{MUTE}}}'
         f'.v{{font:700 24px {MONO};fill:{PAPER}}}.k{{font:10px {MONO};letter-spacing:3px;fill:{MUTE}}}.g{{font:700 13px {MONO};letter-spacing:3px;fill:{ACC}}}</style>',
         f'<rect width="{W}" height="{H}" rx="6" fill="{INK}"/>',
         f'<rect x="0" y="0" width="4" height="{H}" rx="2" fill="{ACC}" opacity=".9"/>',
         f'<text class="n" x="32" y="46">{n}</text>',
         f'<text class="t" x="76" y="48">{escape(title)}</text>',
         f'<text class="b" x="76" y="72">{escape(blurb)}</text>',
         f'<text class="s" x="76" y="92">{escape(stack)}</text>']
    # equalizer
    bx, bw, gap, base = 470, 5, 4, 70
    for b in range(24):
        hs = [rnd.randint(8, 52) for _ in range(5)]
        hs[-1] = hs[0]
        dur = rnd.uniform(1.1, 2.4)
        col = ACC if b % 8 == 3 else PAPER
        s.append(f'<rect x="{bx + b*(bw+gap)}" y="{base-hs[0]}" width="{bw}" height="{hs[0]}" fill="{col}" opacity=".85">'
                 f'<animate attributeName="height" values="{";".join(map(str, hs))}" dur="{dur:.2f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="y" values="{";".join(str(base-h) for h in hs)}" dur="{dur:.2f}s" repeatCount="indefinite"/></rect>')
    s.append(f'<text class="v" x="{W-170}" y="52" text-anchor="end">{loc:,}</text><text class="k" x="{W-170}" y="74" text-anchor="end">LINES</text>')
    dot = f'<circle cx="{W-132}" cy="{H/2-3:.0f}" r="4" fill="{ACC}"><animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></circle>' if kind == "LIVE" else ""
    s.append(dot + f'<text class="g" x="{W-28}" y="{H/2+2:.0f}" text-anchor="end">{"    " if kind=="LIVE" else ""}{kind} ↗</text>')
    s.append('</svg>')
    write(f"tracks/{n}.svg", "\n".join(s))


# -------------------------------------------------------------------------- credits
def credits():
    W, H = 1000, 470
    src = open(os.path.join(HERE, "..", "portrait.svg"), encoding="utf-8").read()
    inner = src[src.index(">") + 1: src.rindex("</svg>")]
    inner = re.sub(r"<style>.*?</style>", "", inner, flags=re.S)
    inner = re.sub(r'<rect width="[\d.]+" height="[\d.]+" fill="transparent"/>', "", inner)
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', src)
    pw, ph = float(vb.group(1)), float(vb.group(2))
    sc = 400 / pw
    return_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Liner notes: all tracks written, designed and deployed by Arunan Kavirajan. Cover portrait is ASCII art rendered by a Python pipeline.">
<style>
.p{{font-family:{MONO};font-size:12.9px;fill:#b9b9bf}}
.h{{font:700 12px {MONO};letter-spacing:4px;fill:{ACC}}}
.a{{font:15px {SANS};fill:#d4d4d8}}
.big{{font:900 44px {SANS};fill:{PAPER};letter-spacing:-1px}}
.m{{font:11px {MONO};letter-spacing:2px;fill:{MUTE}}}
</style>
<rect width="{W}" height="{H}" rx="6" fill="{INK}"/>
<svg x="36" y="{(H - ph*sc)/2:.0f}" width="400" height="{ph*sc:.0f}" viewBox="0 0 {pw} {ph}"><g class="p">{inner}</g></svg>
<rect x="476" y="40" width="1" height="{H-80}" fill="{PAPER}" opacity=".15"/>
<text class="h" x="516" y="80">LINER NOTES</text>
<text class="a" x="516" y="128">Every track on this record was written,</text>
<text class="a" x="516" y="152">designed, mixed and deployed by</text>
<text class="big" x="514" y="208">Arunan</text><text class="big" x="514" y="254">Kavirajan</text>
<rect x="516" y="282" width="60" height="3" fill="{ACC}"/>
<text class="m" x="516" y="326">RECORDED  ON  GITHUB</text>
<text class="m" x="516" y="348">MASTERED  ON  VERCEL</text>
<text class="m" x="516" y="370">COVER ART  BY  PYTHON + OPENCV</text>
<text class="m" x="516" y="414">PRESSED IN LIMITED QUANTITY OF ONE.</text>
</svg>'''
    write("credits.svg", return_svg)


if __name__ == "__main__":
    hero()
    facts()
    for i, t in enumerate(TRACKS):
        track(i, t)
    credits()
