# ============================================================
# ADD ONE URL — fetches a single article, sends to AI, saves it.
# Use when you spot a story you want in the archive right now.
#
# Usage:
#   python add_url.py https://www.brasildefato.com.br/2026/05/26/some-article/
#
# Optional second arg overrides the country (otherwise AI decides):
#   python add_url.py <url> Brazil
# ============================================================

import sys
import json
import os
import requests
from bs4 import BeautifulSoup

# Reuse dispatch.py's functions and settings
from dispatch import (
    analyze_story,
    get_article_image,
    is_duplicate,
    load_archive,
    save_archive,
)

def fetch_and_add(url, country_override=None):
    archive = load_archive()

    # Skip if we already have this story
    fake_story = {"url": url}
    if is_duplicate(fake_story, archive):
        print(f"⏭️  Already in archive: {url}")
        return

    print(f"🌐 Fetching: {url}")
    try:
        r = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        soup = BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"❌  Could not fetch URL: {e}")
        return

    # Pull title from <title>, <h1>, or og:title
    title = ""
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"]
    elif soup.title and soup.title.string:
        title = soup.title.string.strip()
    elif soup.h1:
        title = soup.h1.get_text(strip=True)

    if not title:
        print("❌  Could not find a title on the page.")
        return

    # Pull article body
    article_text = " ".join(p.get_text() for p in soup.find_all("p"))[:3000]
    image_url    = get_article_image(url, soup)

    print(f"📰  Title: {title[:80]}")
    print(f"🖼️   Image: {image_url[:80] if image_url else '(none)'}")
    print(f"🤖  Sending to AI for analysis...")

    snippet = article_text[:300]
    analyzed = analyze_story(title, url, snippet, article_text)

    if not analyzed:
        print("❌  AI analysis failed. Nothing saved.")
        return

    if country_override:
        analyzed["country"] = country_override
    analyzed["image"] = image_url

    archive.append(analyzed)
    save_archive(archive)

    print(f"✅  Saved!")
    print(f"    Country:  {analyzed.get('country')}")
    print(f"    Category: {analyzed.get('category')}")
    print(f"    Framing:  {analyzed.get('narrative_framing')}")
    print(f"    Archive now has {len(archive)} stories.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_url.py <url> [country]")
        sys.exit(1)

    url      = sys.argv[1]
    country  = sys.argv[2] if len(sys.argv) >= 3 else None
    fetch_and_add(url, country_override=country)
