#!/usr/bin/env python3
"""Fetch GitHub achievement badges for a profile and write them to a JSON file.

Run by .github/workflows/update-github-achievements.yml on a schedule so the
portfolio site can read badges from a same-origin static file instead of
scraping github.com from the browser at page-load time (which is blocked by
CORS and previously relied on an unreliable third-party proxy).
"""
import json
import re
import sys
import urllib.request
from collections import OrderedDict
from pathlib import Path

USERNAME = "AbhijeetYadav09"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "assets" / "data" / "github-achievements.json"

BADGE_IMG_RE = re.compile(r"achievements/([a-z0-9-]+)-default\.png")
TIER_RE = re.compile(
    r'achievements/([a-z0-9-]+)-default\.png[^>]*>.*?(?:x(\d+)|×\s*(\d+))',
    re.IGNORECASE | re.DOTALL,
)


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; achievements-fetcher/1.0)"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_badges(html: str):
    slugs = list(OrderedDict.fromkeys(BADGE_IMG_RE.findall(html)))
    tiers = {}
    for m in TIER_RE.finditer(html):
        slug = m.group(1)
        count = m.group(2) or m.group(3)
        if count:
            tiers[slug] = int(count)
    badges = [{"slug": slug, "tier": tiers.get(slug)} for slug in slugs]
    return badges


def main():
    url = f"https://github.com/{USERNAME}?tab=achievements"
    try:
        html = fetch_html(url)
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to fetch {url}: {exc}", file=sys.stderr)
        sys.exit(1)

    badges = parse_badges(html)
    if not badges:
        print("No badges parsed from profile page; leaving existing file untouched.", file=sys.stderr)
        sys.exit(1)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump({"username": USERNAME, "badges": badges}, f, indent=2)
        f.write("\n")

    print(f"Wrote {len(badges)} badges to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
