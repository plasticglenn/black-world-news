# ============================================================
# BACKFILL TRANSLATIONS — adds EN/ES/PT/FR titles + summaries
# to existing stories that don't have them yet.
#
# Run after upgrading the AI prompt:
#   python backfill_translations.py
#
# Smart behaviour:
#   - Processes newest stories first
#   - Skips stories whose title looks already in English (saves tokens)
#   - Exits cleanly when Groq's daily limit hits
#   - Safe to re-run — skips stories that already have title_en set
# ============================================================

import sys
import json
import os
import time
import re
from json_repair import repair_json

# Make sure emojis print on Windows
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from groq import Groq

ARCHIVE_FILE = "stories.json"
MODEL        = "llama-3.3-70b-versatile"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def looks_english(text):
    """Cheap heuristic: title is likely already in English if it's pure ASCII
    and doesn't contain telltale Spanish/Portuguese/French accents or words."""
    if not text:
        return True
    # If any non-ASCII char appears, treat as non-English
    if re.search(r"[^\x00-\x7f]", text):
        return False
    # If it contains common non-English connector words, treat as non-English
    foreign_markers = (
        " de ", " del ", " la ", " el ", " los ", " las ", " une ", " une ",
        " du ", " des ", " une ", " que ", " avec ", " sin ", " com ",
        " para ", " que ", " ao ", " na "
    )
    low = " " + text.lower() + " "
    if any(m in low for m in foreign_markers):
        return False
    return True


def translate_story(story):
    """Ask Groq for EN/ES/PT/FR title + summary for one story.
    Returns dict or None on failure. Raises RuntimeError on rate-limit."""
    title   = story.get("title", "")
    summary = story.get("summary", "")

    prompt = f"""You are a professional translator. Translate the following news story
title and summary into English, Spanish, Portuguese, and French. Keep translations
natural and concise. Do not add commentary.

Title: {title}
Summary: {summary}

Respond ONLY in JSON with these fields:
- "title_en": title in English (if already English, repeat verbatim)
- "title_es": title in Spanish
- "title_pt": title in Portuguese
- "title_fr": title in French
- "summary_es": summary in Spanish
- "summary_pt": summary in Portuguese
- "summary_fr": summary in French
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.choices[0].message.content

        if "```" in raw:
            raw = raw.split("```")[-2] if raw.count("```") >= 2 else raw
            if raw.startswith("json"):
                raw = raw[4:]

        raw = raw[raw.find("{"):raw.rfind("}")+1].strip()
        return json.loads(repair_json(raw))

    except Exception as e:
        msg = str(e)
        if "rate_limit_exceeded" in msg or "429" in msg:
            # Surface this so the caller can stop cleanly
            raise RuntimeError("RATE_LIMIT")
        print(f"  ⚠️  Translation failed: {e}")
        return None


def save(stories):
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(stories, f, indent=2, ensure_ascii=False)


def main():
    if not os.path.exists(ARCHIVE_FILE):
        print(f"No archive at {ARCHIVE_FILE}")
        return

    with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
        stories = json.load(f)

    total = len(stories)

    # Newest-first so any non-English stories from recent runs get priority
    indexed = sorted(
        enumerate(stories),
        key=lambda pair: pair[1].get("saved_at", ""),
        reverse=True
    )

    # Pick stories that need translation, skip ones that already look English
    needs = []
    skipped_english = 0
    for i, s in indexed:
        if s.get("title_en"):
            continue
        if looks_english(s.get("title", "")):
            # Mark title_en = title so we don't keep visiting it
            s["title_en"] = s["title"]
            skipped_english += 1
            continue
        needs.append(i)

    print(f"📚  Loaded {total} stories.")
    print(f"⚡  Auto-marked {skipped_english} as already-English (saved tokens).")
    print(f"🌍  {len(needs)} stories need real translation.\n")

    if skipped_english:
        save(stories)

    if not needs:
        print("Nothing more to do.")
        return

    translated_count = 0
    for n, story_idx in enumerate(needs):
        story = stories[story_idx]
        title_short = story.get("title", "")[:60]
        print(f"[{n+1}/{len(needs)}] {title_short}...")

        try:
            translations = translate_story(story)
        except RuntimeError as e:
            if str(e) == "RATE_LIMIT":
                print("\n🛑  Groq daily token limit reached. Stopping cleanly.")
                print(f"    Translated {translated_count} new stories this run.")
                print("    Run this script again tomorrow to continue, or upgrade Groq tier.")
                save(stories)
                return
            raise

        if not translations:
            continue

        for key in ("title_en", "title_es", "title_pt", "title_fr",
                    "summary_es", "summary_pt", "summary_fr"):
            if translations.get(key):
                story[key] = translations[key]

        translated_count += 1

        # Save every 5 stories
        if translated_count % 5 == 0:
            save(stories)
            print(f"  💾  Checkpoint saved ({translated_count} new translations)")

        time.sleep(0.5)

    save(stories)
    done = sum(1 for s in stories if s.get("title_en"))
    print(f"\n✅  Done. {done}/{total} stories now have English titles.")


if __name__ == "__main__":
    main()
