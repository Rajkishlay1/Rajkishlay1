#!/usr/bin/env python3
"""
Auto-updates assets/live_builder_snapshot.svg every 6 hours via GitHub Actions.
Fetches live GitHub stats for Rajkishlay1 and renders a dark-mode Bento Builder Card.
"""
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

USERNAME = os.getenv("GITHUB_USERNAME", "Rajkishlay1")
OUT_SVG = Path(__file__).resolve().parent.parent / "assets" / "live_builder_snapshot.svg"


def gh_get(url: str) -> dict | list:
    headers = {"User-Agent": "Rajkishlay1-Profile-Updater", "Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    user = gh_get(f"https://api.github.com/users/{USERNAME}")
    repos = gh_get(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner")

    public_repos = user.get("public_repos", 0)
    followers = user.get("followers", 0)
    total_stars = sum(r.get("stargazers_count", 0) for r in repos if not r.get("fork"))

    top_repos = sorted(
        [r for r in repos if not r.get("fork")],
        key=lambda r: (r.get("stargazers_count", 0), r.get("pushed_at", "")),
        reverse=True,
    )[:4]

    max_score = max([r.get("stargazers_count", 0) for r in top_repos] + [1])

    ist = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist).strftime("%d %b %Y · %I:%M %p IST").upper()

    repo_bars_svg = ""
    y_start = 152
    for idx, r in enumerate(top_repos):
        name = escape(r.get("name", "")[:32])
        stars = r.get("stargazers_count", 0)
        lang = escape(r.get("language") or "Python")
        pct = max(14, int((stars / max_score) * 100)) if stars > 0 else max(18, 85 - idx * 18)
        bar_w = int(380 * (pct / 100.0))
        y = y_start + idx * 46
        repo_bars_svg += f"""
  <text x="360" y="{y}" fill="#E2E8F0" font-family="Segoe UI, Arial, sans-serif" font-size="13" font-weight="600">{name}</text>
  <text x="740" y="{y}" fill="#94A3B8" font-family="Consolas, monospace" font-size="11" text-anchor="end">{lang} · ★ {stars}</text>
  <rect x="360" y="{y+8}" width="380" height="7" rx="3.5" fill="#1E293B"/>
  <rect x="360" y="{y+8}" width="{bar_w}" height="7" rx="3.5" fill="url(#barGrad)"/>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="410" viewBox="0 0 800 410" fill="none">
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="800" y2="410" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="#070B14"/>
      <stop offset="100%" stop-color="#0F172A"/>
    </linearGradient>
    <linearGradient id="cardGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#111827"/>
      <stop offset="100%" stop-color="#0B1120"/>
    </linearGradient>
    <linearGradient id="barGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#00D4FF"/>
      <stop offset="100%" stop-color="#3B82F6"/>
    </linearGradient>
  </defs>

  <rect width="800" height="410" rx="16" fill="url(#bgGrad)" stroke="#1E293B" stroke-width="1.5"/>

  <!-- LEFT: BUILDER PASS ID CARD -->
  <rect x="26" y="26" width="300" height="358" rx="14" fill="url(#cardGrad)" stroke="#334155" stroke-width="1.2"/>
  <rect x="136" y="14" width="80" height="18" rx="4" fill="#1D4ED8"/>
  <text x="176" y="27" fill="#FFFFFF" font-family="Consolas, monospace" font-size="9" font-weight="700" text-anchor="middle">KR / BUILDER PASS</text>

  <text x="44" y="60" fill="#00D4FF" font-family="Consolas, monospace" font-size="11" font-weight="700">INVOLTICS · SOLARHUB</text>
  <text x="308" y="60" fill="#64748B" font-family="Consolas, monospace" font-size="11" text-anchor="end">#0158</text>

  <rect x="44" y="76" width="264" height="140" rx="10" fill="#0A101F" stroke="#1E3A8A" stroke-width="1"/>
  <text x="176" y="120" fill="#FFFFFF" font-family="Segoe UI, Arial, sans-serif" font-size="22" font-weight="800" text-anchor="middle">KISHLAY RAJ</text>
  <text x="176" y="144" fill="#00D4FF" font-family="Consolas, monospace" font-size="11" font-weight="700" text-anchor="middle">LEAD BACKEND &amp; IOT ARCHITECT</text>
  <rect x="92" y="162" width="168" height="24" rx="12" fill="#0F2942" stroke="#00D4FF" stroke-width="0.8"/>
  <text x="176" y="178" fill="#E0F2FE" font-family="Consolas, monospace" font-size="10" text-anchor="middle">179 PLANTS · 150K+ PKTS/DAY</text>

  <text x="44" y="248" fill="#94A3B8" font-family="Consolas, monospace" font-size="10">LOCATION: GREATER NOIDA, INDIA</text>
  <text x="44" y="268" fill="#94A3B8" font-family="Consolas, monospace" font-size="10">STACK: PYTHON · DJANGO · MQTT · AWS</text>

  <rect x="44" y="286" width="264" height="44" rx="8" fill="#070B14" stroke="#1E293B"/>
  <text x="58" y="304" fill="#EF4444" font-family="Consolas, monospace" font-size="9" font-weight="700">● LIVE AUTO-SYNC (EVERY 6H)</text>
  <text x="58" y="320" fill="#CBD5E1" font-family="Consolas, monospace" font-size="10">{escape(now_ist)}</text>

  <text x="176" y="362" fill="#475569" font-family="Consolas, monospace" font-size="10" text-anchor="middle">|||| ||| || |||| ||| |||| ||| ||||</text>

  <!-- RIGHT: REAL WORK. REAL IMPACT. -->
  <text x="360" y="42" fill="#00D4FF" font-family="Consolas, monospace" font-size="10" font-weight="700">04 / BUILDER CREDENTIALS</text>
  <text x="360" y="68" fill="#FFFFFF" font-family="Segoe UI, Arial, sans-serif" font-size="22" font-weight="800">REAL WORK. REAL IMPACT.</text>

  <!-- 3 KPI BOXES -->
  <rect x="360" y="82" width="118" height="52" rx="8" fill="#0F172A" stroke="#1E293B"/>
  <text x="374" y="109" fill="#EF4444" font-family="Segoe UI, Arial, sans-serif" font-size="22" font-weight="800">{public_repos}</text>
  <text x="374" y="125" fill="#94A3B8" font-family="Consolas, monospace" font-size="9">PUBLIC REPOS</text>

  <rect x="491" y="82" width="118" height="52" rx="8" fill="#0F172A" stroke="#1E293B"/>
  <text x="505" y="109" fill="#00D4FF" font-family="Segoe UI, Arial, sans-serif" font-size="22" font-weight="800">{total_stars}</text>
  <text x="505" y="125" fill="#94A3B8" font-family="Consolas, monospace" font-size="9">TOTAL STARS</text>

  <rect x="622" y="82" width="118" height="52" rx="8" fill="#0F172A" stroke="#1E293B"/>
  <text x="636" y="109" fill="#38BDF8" font-family="Segoe UI, Arial, sans-serif" font-size="22" font-weight="800">{followers}</text>
  <text x="636" y="125" fill="#94A3B8" font-family="Consolas, monospace" font-size="9">FOLLOWERS</text>

  {repo_bars_svg}

  <!-- FOOTER STATUS PILL -->
  <rect x="360" y="340" width="380" height="44" rx="8" fill="#0F172A" stroke="#1E293B"/>
  <rect x="374" y="350" width="46" height="16" rx="4" fill="#EF4444"/>
  <text x="397" y="362" fill="#FFFFFF" font-family="Consolas, monospace" font-size="9" font-weight="700" text-anchor="middle">NOW</text>
  <text x="428" y="362" fill="#FFFFFF" font-family="Segoe UI, Arial, sans-serif" font-size="12" font-weight="700">Architecting SolarHub &amp; CHAMP AI OS</text>
  <text x="374" y="377" fill="#64748B" font-family="Consolas, monospace" font-size="9">Auto-refreshed every 6 hours via GitHub Actions</text>
</svg>
"""
    OUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    OUT_SVG.write_text(svg, encoding="utf-8")
    print(f"Updated {OUT_SVG} | repos={public_repos} stars={total_stars} followers={followers}")


if __name__ == "__main__":
    main()
