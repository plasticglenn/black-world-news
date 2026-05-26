# ============================================================
# BLACK WORLD NEWS — Featured Story Picker
# Run this after the agent collects new stories.
# It shows you the newest stories and lets you choose
# which one goes in the featured spot on the homepage.
# ============================================================

import json
import os
import sys

ARCHIVE_FILE  = "stories.json"
FEATURED_FILE = "featured.json"   # stores your choice

def load_stories():
    with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_featured(story):
    with open(FEATURED_FILE, "w", encoding="utf-8") as f:
        json.dump({"url": story["url"], "title": story["title"]}, f, indent=2)

def main():
    stories = load_stories()

    # Sort newest first and take the top 20
    recent = sorted(stories, key=lambda s: s.get("saved_at", ""), reverse=True)[:20]

    print("\n" + "="*60)
    print("  BLACK WORLD NEWS — Pick Your Featured Story")
    print("="*60)
    print(f"\nShowing the 20 most recent stories.\n")

    for i, s in enumerate(recent):
        title   = s.get("title", "Untitled")[:65]
        country = s.get("country", "")
        cat     = s.get("category", "")
        framing = s.get("narrative_framing", "")
        print(f"  [{i+1:2}]  {title}")
        print(f"         {country} | {cat} | {framing}\n")

    print("-"*60)
    try:
        choice = input("Enter the number of the story to feature (or press Enter to keep current): ").strip()
    except EOFError:
        print("No choice made. Keeping current featured story.")
        return

    if not choice:
        print("No change made.")
        return

    try:
        index = int(choice) - 1
        if 0 <= index < len(recent):
            selected = recent[index]
            save_featured(selected)
            print(f"\nFeatured story set to:\n  {selected['title']}\n")
            print("Now run:  python generate_site.py")
            print("Then:     git add . && git commit -m 'Update featured story' && git push origin main\n")
        else:
            print("Number out of range. No change made.")
    except ValueError:
        print("Invalid input. No change made.")

if __name__ == "__main__":
    main()
