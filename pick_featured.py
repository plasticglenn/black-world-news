# ============================================================
# BLACK WORLD NEWS — Featured Story Picker
#
# Two modes:
#   python pick_featured.py            -> AUTO: scores recent stories and
#                                         rotates a fresh, interesting featured
#                                         story each day (used by the scheduler).
#   python pick_featured.py --choose   -> interactive: pick by hand.
#
# "Most interesting" = strongly prefers big, reputable publications, then
# narrative interest + having a real image. Never features Wikipedia, LinkedIn,
# YouTube, stat databases or think-tank PDFs.
# ============================================================

import json
import os
import sys
from datetime import date
from urllib.parse import urlparse

ARCHIVE_FILE  = "stories.json"
FEATURED_FILE = "featured.json"

# Reputable news publications — a story from one of these is strongly preferred.
BIG_PUBS = {
    "bbc.com", "bbc.co.uk", "reuters.com", "apnews.com", "theguardian.com",
    "nytimes.com", "washingtonpost.com", "aljazeera.com", "cnn.com", "npr.org",
    "ft.com", "economist.com", "bloomberg.com", "africanews.com", "news.sky.com",
    "independent.co.uk", "time.com", "theconversation.com", "abcnews.go.com",
    "cbsnews.com", "nbcnews.com", "pbs.org", "scmp.com", "theafricareport.com",
    "premiumtimesng.com", "punchng.com", "thecable.ng", "mg.co.za", "nation.africa",
}

# Never feature these on the homepage hero (not news articles / look bad as a lead).
EXCLUDE = {
    "en.wikipedia.org", "wikipedia.org", "linkedin.com", "youtube.com",
    "statista.com", "worldpopulationreview.com", "pmc.ncbi.nlm.nih.gov",
    "ncbi.nlm.nih.gov", "worldbank.org", "imf.org", "who.int", "cfr.org",
    "brookings.edu", "epi.org", "finance.yahoo.com", "antiracismnewsletter.com",
}

FRAMING_INTEREST = {
    "Resistant": 18, "Human": 15, "Exploited": 12,
    "Victim": 6, "Criminal": 6, "Statistic": 3,
}


def domain(url):
    try:
        d = urlparse(url).netloc.lower()
        return d[4:] if d.startswith("www.") else d
    except Exception:
        return ""


def score(s):
    sc = 0
    d = domain(s.get("url", ""))
    if d in BIG_PUBS:
        sc += 100
    if s.get("image"):
        sc += 12
    sc += FRAMING_INTEREST.get(s.get("narrative_framing", ""), 5)
    if s.get("structural_factors"):
        sc += 5
    if len((s.get("title_en") or s.get("title") or "")) > 25:
        sc += 3
    if (s.get("summary_en") or s.get("summary")):
        sc += 3
    return sc


def load_stories():
    with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_featured(story):
    with open(FEATURED_FILE, "w", encoding="utf-8") as f:
        json.dump({"url": story["url"], "title": story.get("title", "")},
                  f, indent=2, ensure_ascii=False)


def eligible(s):
    d = domain(s.get("url", ""))
    if not s.get("url") or d in EXCLUDE:
        return False
    title = (s.get("title_en") or s.get("title") or "")
    if len(title) < 20 or "�" in title:   # too short, or mojibake (looks broken)
        return False
    return True


def auto_pick(stories):
    # Draw from a wide-ish recent window so the deck is varied and high quality,
    # not whatever a single run happened to cluster on.
    recent = sorted(stories, key=lambda s: s.get("saved_at", ""), reverse=True)[:200]
    pool = [s for s in recent if eligible(s)]
    ranked = sorted(pool, key=lambda s: (score(s), s.get("saved_at", "")), reverse=True)
    # Build a varied "deck": big pubs float to the top (score), but cap each
    # domain at 2 so one source/topic can't dominate the rotation.
    deck, per_domain = [], {}
    for s in ranked:
        d = domain(s["url"])
        if per_domain.get(d, 0) >= 2:
            continue
        per_domain[d] = per_domain.get(d, 0) + 1
        deck.append(s)
        if len(deck) >= 12:
            break
    if not deck:
        deck = ranked[:1] or stories[:1]
    # Rotate through the deck by calendar day: fresh hero daily, always strong.
    pick = deck[date.today().toordinal() % len(deck)]
    save_featured(pick)
    print("Featured ->", (pick.get("title_en") or pick.get("title", ""))[:70])
    print("  source :", domain(pick["url"]), "| score", score(pick),
          "| deck size", len(deck))


def choose(stories):
    recent = sorted(stories, key=lambda s: s.get("saved_at", ""), reverse=True)[:20]
    print("\n" + "=" * 60)
    print("  Pick Your Featured Story (20 most recent)")
    print("=" * 60 + "\n")
    for i, s in enumerate(recent):
        print(f"  [{i+1:2}]  {(s.get('title_en') or s.get('title','Untitled'))[:65]}")
        print(f"         {s.get('country','')} | {s.get('category','')} | {domain(s.get('url',''))}\n")
    try:
        c = input("Number to feature (Enter to keep current): ").strip()
    except EOFError:
        return
    if c.isdigit() and 0 <= int(c) - 1 < len(recent):
        save_featured(recent[int(c) - 1])
        print("Featured set. Now run: python generate_site.py")


def main():
    stories = load_stories()
    if "--choose" in sys.argv:
        choose(stories)
    else:
        auto_pick(stories)


if __name__ == "__main__":
    main()
