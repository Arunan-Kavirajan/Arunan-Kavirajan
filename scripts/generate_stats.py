"""Builds assets/stats.svg: a self-hosted, theme-aware GitHub activity dashboard.

Standard library only. Uses the GraphQL API when GITHUB_TOKEN is set (contribution
calendar, commits, PRs, streaks) and falls back to the public REST API otherwise.
"""
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timezone
from html import escape

USER = os.environ.get("GH_USER", "Arunan-Kavirajan")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "stats.svg")

FALLBACK_COLORS = {
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Python": "#3572A5",
    "Dart": "#00B4AB", "CSS": "#563d7c", "HTML": "#e34c26", "C++": "#f34b7d",
    "Kotlin": "#A97BFF", "Swift": "#F05138", "C": "#555555", "Java": "#b07219",
}

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(ownerAffiliation: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def http(url, data=None):
    headers = {"User-Agent": "profile-stats", "Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_graphql():
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    res = http("https://api.github.com/graphql", body)
    if "errors" in res or not (res.get("data") or {}).get("user"):
        raise RuntimeError(res.get("errors"))
    u = res["data"]["user"]
    cc = u["contributionsCollection"]
    langs, stars = {}, 0
    for repo in u["repositories"]["nodes"]:
        stars += repo["stargazerCount"]
        for e in repo["languages"]["edges"]:
            n = e["node"]
            color = n["color"] or FALLBACK_COLORS.get(n["name"], "#8b949e")
            langs.setdefault(n["name"], [0, color])[0] += e["size"]
    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    return {
        "repos": u["repositories"]["totalCount"], "stars": stars,
        "followers": u["followers"]["totalCount"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "total": cc["contributionCalendar"]["totalContributions"],
        "days": [(d["date"], d["contributionCount"]) for d in days],
        "langs": langs,
    }


def fetch_rest():
    user = http("https://api.github.com/users/" + USER)
    repos = http("https://api.github.com/users/%s/repos?per_page=100&type=owner" % USER)
    langs, stars = {}, 0
    for r in repos:
        if r["fork"]:
            continue
        stars += r["stargazers_count"]
        for name, size in http(r["languages_url"]).items():
            langs.setdefault(name, [0, FALLBACK_COLORS.get(name, "#8b949e")])[0] += size
    return {"repos": user["public_repos"], "stars": stars, "followers": user["followers"],
            "commits": None, "prs": None, "total": None, "days": [], "langs": langs}


def streaks(days):
    counts = [c for _, c in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    seq = counts[:-1] if counts and counts[-1] == 0 else counts  # today may still be empty
    cur = 0
    for c in reversed(seq):
        if not c:
            break
        cur += 1
    return cur, longest


def level(c, mx):
    if c == 0:
        return 0
    q = c / mx
    return 1 if q <= .25 else 2 if q <= .5 else 3 if q <= .75 else 4


def fmt(n):
    return "-" if n is None else "{:,}".format(n)


STYLE = """<style>
:root{--bg:#080b16;--card:#0d1226;--bd:#1e2a4a;--fg:#e2e8f0;--mut:#8b9bb8;
--l0:#121a33;--l1:#1e3a8a;--l2:#2563eb;--l3:#38bdf8;--l4:#c4b5fd}
text{font-family:-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;fill:var(--fg)}
.m{fill:var(--mut);font-size:11px}.h{font-size:15px;font-weight:700;letter-spacing:.5px}.v{font-size:28px;font-weight:800;fill:url(#ac)}
.l0{fill:var(--l0)}.l1{fill:var(--l1)}.l2{fill:var(--l2)}.l3{fill:var(--l3)}.l4{fill:var(--l4)}
.c,.t{animation:f .5s ease backwards}
@keyframes f{from{opacity:0}}
</style>
<defs><linearGradient id="ac" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#38bdf8"/><stop offset="1" stop-color="#a78bfa"/></linearGradient></defs>"""


def build(d):
    W, H, PAD = 800, 380, 24
    cur, longest = streaks(d["days"]) if d["days"] else (None, None)
    tiles = [("Contributions", d["total"], "last 12 months"), ("Commits", d["commits"], "last 12 months"),
             ("Pull requests", d["prs"], "last 12 months"),
             ("Current streak", cur, "days"), ("Longest streak", longest, "days")]
    gap = 12
    tw = (W - 2 * PAD - gap * (len(tiles) - 1)) / len(tiles)

    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" role="img" '
           'aria-label="GitHub activity for %s">' % (W, H, W, escape(USER)), STYLE,
           '<rect width="%d" height="%d" rx="12" fill="var(--bg)" stroke="var(--bd)"/>' % (W, H),
           '<text x="%d" y="36" class="h">GitHub activity</text>' % PAD,
           '<text x="%d" y="36" class="m" text-anchor="end">@%s</text>' % (W - PAD, escape(USER))]

    for i, (label, val, sub) in enumerate(tiles):
        x = PAD + i * (tw + gap)
        out.append(
            '<g class="t" style="animation-delay:%.2fs">'
            '<rect x="%.1f" y="52" width="%.1f" height="74" rx="8" fill="var(--card)" stroke="var(--bd)"/>'
            '<text x="%.1f" y="74" class="m">%s</text>'
            '<text x="%.1f" y="104" class="v">%s</text>'
            '<text x="%.1f" y="118" class="m" style="font-size:10px">%s</text></g>'
            % (i * .08, x, tw, x + 14, label, x + 14, fmt(val), x + 14, sub))

    hy = 158
    out.append('<text x="%d" y="%d" class="h" style="font-size:13px">Contribution calendar</text>' % (PAD, hy))
    days = d["days"]
    if days:
        mx = max(c for _, c in days) or 1
        first = date.fromisoformat(days[0][0])
        cells = [None] * ((first.weekday() + 1) % 7) + days  # Sunday-first columns
        size, g, gx = 11, 3, PAD + 26
        for idx, cell in enumerate(cells):
            if cell is None:
                continue
            col, row = divmod(idx, 7)
            ds, cnt = cell
            out.append(
                '<rect class="c l%d" x="%d" y="%d" width="%d" height="%d" rx="2" style="animation-delay:%.3fs">'
                '<title>%d contributions on %s</title></rect>'
                % (level(cnt, mx), gx + col * (size + g), hy + 16 + row * (size + g), size, size, col * .012, cnt, ds))
        for r, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
            out.append('<text x="%d" y="%d" class="m" style="font-size:9px">%s</text>'
                       % (PAD, hy + 16 + r * (size + g) + 9, name))
        last_m = None
        for col in range((len(cells) + 6) // 7):
            week = [c for c in cells[col * 7:col * 7 + 7] if c]
            if not week:
                continue
            dt = date.fromisoformat(week[0][0])
            m = dt.strftime("%b")
            if m != last_m and (col == 0 or dt.day <= 7):
                out.append('<text x="%d" y="%d" class="m" style="font-size:9px">%s</text>'
                           % (gx + col * (size + g), hy + 12, m))
                last_m = m
    else:
        out.append('<text x="%d" y="%d" class="m">Contribution data unavailable (no API token).</text>'
                   % (PAD, hy + 40))

    ly = 300
    langs = sorted(d["langs"].items(), key=lambda kv: -kv[1][0])
    total = sum(v[0] for _, v in langs) or 1
    top, rest = langs[:6], sum(v[0] for _, v in langs[6:])
    out.append('<text x="%d" y="%d" class="h" style="font-size:13px">Languages by code volume</text>' % (PAD, ly))
    bw, x = W - 2 * PAD, float(PAD)
    out.append('<clipPath id="bar"><rect x="%d" y="%d" width="%d" height="10" rx="5"/></clipPath>'
               '<g clip-path="url(#bar)">' % (PAD, ly + 10, bw))
    for name, (sz, color) in top:
        w = bw * sz / total
        out.append('<rect x="%.1f" y="%d" width="%.1f" height="10" fill="%s"><title>%s</title></rect>'
                   % (x, ly + 10, w, color, escape(name)))
        x += w
    if rest:
        out.append('<rect x="%.1f" y="%d" width="%.1f" height="10" fill="#8b949e"/>' % (x, ly + 10, PAD + bw - x))
    out.append('</g>')
    lx = PAD
    for name, (sz, color) in top:
        label = "%s %.1f%%" % (name, sz / total * 100)
        out.append('<circle cx="%d" cy="%d" r="5" fill="%s"/><text x="%d" y="%d" class="m" style="font-size:12px">%s</text>'
                   % (lx + 5, ly + 36, color, lx + 16, ly + 40, escape(label)))
        lx += 16 + len(label) * 6.6 + 14

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out.append('<text x="%d" y="%d" class="m" text-anchor="end">%d public repos  ·  %d stars  ·  %d followers  ·  updated %s UTC</text>'
               % (W - PAD, H - 14, d["repos"], d["stars"], d["followers"], now))
    out.append('</svg>')
    return "\n".join(out)


def main():
    try:
        data = fetch_graphql() if TOKEN else fetch_rest()
    except Exception as e:  # keep the previous SVG if the API is unavailable
        print("Stats fetch failed (%s); leaving existing file untouched." % e, file=sys.stderr)
        sys.exit(0 if os.path.exists(OUT) else 1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(build(data))
    print("Wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
