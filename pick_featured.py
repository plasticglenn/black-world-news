# ============================================================
# BLACK WORLD NEWS — Featured Story Picker
#
# Two modes:
#   python pick_featured.py            -> AUTO: scores recent stories and
#                                         rotates a fresh, interesting featured
#                                         story each day (used by the scheduler).
#   python pick_featured.py --choose   -> interactive: pick by hand.
#
# "Most interesting" = ONLY vetted, reputable news organisations are eligible
# for the hero (hard gate), then ranked by narrative interest + a real image.
# Never features Wikipedia, LinkedIn, YouTube, stat databases or think-tank PDFs.
# ============================================================

import json
import os
import sys
from datetime import date
from urllib.parse import urlparse

ARCHIVE_FILE  = "stories.json"
FEATURED_FILE = "featured.json"

# Reputable news organisations. Membership here is a HARD GATE: a story is only
# eligible for the hero if its source is on this list. It blends established
# diaspora / African / Caribbean / Latin American press (the heart of this site)
# with major international wire and quality outlets. Add a source only after a
# quick credibility check; keep commentary/advocacy blogs and aggregators off it.
REPUTABLE = {
    # International wire / quality press
    "bbc.com", "bbc.co.uk", "reuters.com", "apnews.com", "theguardian.com",
    "nytimes.com", "washingtonpost.com", "aljazeera.com", "cnn.com", "npr.org",
    "ft.com", "economist.com", "bloomberg.com", "news.sky.com", "independent.co.uk",
    "time.com", "theconversation.com", "abcnews.go.com", "cbsnews.com",
    "nbcnews.com", "pbs.org", "scmp.com", "dw.com",
    # Pan-African / African national press
    "africanews.com", "theafricareport.com", "allafrica.com", "premiumtimesng.com",
    "punchng.com", "thecable.ng", "mg.co.za", "nation.africa", "gna.org.gh",
    "standardmedia.co.ke",
    # Caribbean press
    "jamaicaobserver.com", "nationnews.com", "newsday.co.tt",
    "caribbeannationalweekly.com",
    # Black diaspora press (UK / Brazil / Colombia)
    "voice-online.co.uk", "almapreta.com.br", "brasildefato.com.br", "elheraldo.co",
}

# A subset of REPUTABLE that floats to the top of the rotation (extra scoring
# weight) so the strongest outlets lead when several reputable stories compete.
TOP_TIER = {
    "bbc.com", "bbc.co.uk", "reuters.com", "apnews.com", "theguardian.com",
    "nytimes.com", "washingtonpost.com", "aljazeera.com", "ft.com", "economist.com",
    "bloomberg.com", "africanews.com", "theafricareport.com", "premiumtimesng.com",
    "scmp.com", "dw.com",
}

# Belt-and-suspenders: never feature these even if one sneaks onto a list above
# (not news articles / look bad as a lead / source documents, not reporting).
EXCLUDE = {
    "en.wikipedia.org", "wikipedia.org", "linkedin.com", "youtube.com", "tiktok.com",
    "vk.com", "statista.com", "worldpopulationreview.com", "pmc.ncbi.nlm.nih.gov",
    "ncbi.nlm.nih.gov", "worldbank.org", "imf.org", "who.int", "cfr.org",
    "brookings.edu", "epi.org", "finance.yahoo.com", "antiracismnewsletter.com",
    "impactinvesting.online",
}

# Editorial weighting (selection only — published copy stays neutral).
# Prefer stories with structural depth, a sense of people's agency, and a clear
# account of who benefits, over passive or numbers-only coverage.
FRAMING_WEIGHT = {
    "Resistant": 30, "Exploited": 26, "Human": 14,
    "Victim": 8, "Criminal": 6, "Statistic": 2,
}
# Structural signals that mark a story as substantive rather than surface.
FACTOR_WEIGHT = {
    "Colonial legacy": 12, "Corporate extraction": 12, "Land theft": 12,
    "Foreign debt": 12, "Engineered unemployment": 12,
    "Mass incarceration": 8, "Drug war": 8, "Alcohol industry targeting": 8,
    "Voter suppression": 8, "Police violence": 8, "Media bias": 6,
}


def domain(url):
    try:
        d = urlparse(url).netloc.lower()
        return d[4:] if d.startswith("www.") else d
    except Exception:
        return ""


def score(s):
    sc = 0
    # All eligible stories are already reputable (see eligible()); give the major
    # wire/quality outlets an extra nudge so they lead the rotation.
    if domain(s.get("url", "")) in TOP_TIER:
        sc += 30
    if s.get("image"):
        sc += 8
    # Depth of the story: framing, structural factors, and whether it names who benefits.
    sc += FRAMING_WEIGHT.get(s.get("narrative_framing", ""), 5)
    for f in (s.get("structural_factors") or [])[:3]:
        sc += FACTOR_WEIGHT.get(f, 0)
    cb = (s.get("cui_bono") or "").strip().lower()
    if cb and cb not in ("unclear", "unclear.", "none", "none."):
        sc += 15
    if len((s.get("title_en") or s.get("title") or "")) > 25:
        sc += 2
    if (s.get("summary_en") or s.get("summary")):
        sc += 2
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
    if not s.get("url"):
        return False
    # HARD GATE: only vetted, reputable news organisations reach the hero.
    if d not in REPUTABLE or d in EXCLUDE:
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
        # No reputable story in the recent window — keep the current hero rather
        # than promote an unvetted source. (Should be rare; the archive is dense
        # with reputable diaspora/African/wire sources.)
        print("No reputable story in recent window — keeping current featured.")
        return
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
