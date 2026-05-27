# ============================================================
# SOCIAL POST GENERATOR — Drafts per-platform posts from recent
# stories. You review and post manually (auto-posting requires
# API tokens; we can add that later).
#
# Usage:
#   python social_post.py            # draft posts for the 5 newest unposted stories
#   python social_post.py 10         # same but for 10 newest
#   python social_post.py reset      # clear the queue and start fresh
# ============================================================

import sys
import json
import os
import re
from json_repair import repair_json

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from groq import Groq

ARCHIVE_FILE  = "stories.json"
QUEUE_FILE    = "social_queue.json"
MARKDOWN_FILE = "social_queue.md"
MODEL         = "llama-3.3-70b-versatile"
SITE_URL      = "https://www.blackworldnews.world"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def already_posted_urls(queue):
    return {item.get("url") for item in queue if item.get("url")}


def country_hashtag(country):
    # Map our standard country names to clean hashtag-safe forms
    return {
        "United States":  "#BlackAmerica",
        "United Kingdom": "#BlackBritain",
        "Canada":         "#BlackCanada",
        "Brazil":         "#Brazil",
        "Colombia":       "#Colombia",
        "Ghana":          "#Ghana",
        "Nigeria":        "#Nigeria",
        "South Africa":   "#SouthAfrica",
        "France":         "#France",
        "Germany":        "#Germany",
        "Australia":      "#Australia",
        "Other/Global":   "#Global",
    }.get(country, "")


def draft_for(story):
    """Ask Groq to draft posts for one story across 4 platforms."""
    title    = story.get("title_en") or story.get("title", "")
    summary  = story.get("summary_en") or story.get("summary", "")
    country  = story.get("country", "")
    category = story.get("category", "")
    framing  = story.get("narrative_framing", "")
    url      = story.get("url", "")

    country_tag = country_hashtag(country)

    prompt = f"""You are a social media editor for Black World News — a Pan-African news outlet.
Draft posts in a neutral, serious tone (think BBC, not buzzword Twitter).
The site links readers to the original article, not to BWN itself, so always cite the source story.

Story title: {title}
Summary: {summary}
Country: {country}
Topic: {category}
Framing: {framing}

Respond in JSON only with these exact fields:
- "instagram": a 2-3 sentence caption ending with 5-8 relevant hashtags. Hook reader with the most striking fact. Include {country_tag} if applicable.
- "x": a single post under 270 characters. Lead with the story's hook. Use plain English.
- "threads": a 2-3 sentence post under 480 characters. Slightly more reflective than the X post. Includes 2-3 hashtags.
- "tiktok": a one-sentence concept for a 30-second vertical video that would explain this story to a younger audience.

Rules:
- No emojis in any post.
- No hyphens anywhere.
- Never use the words "Pan-African", "systemic", or "narrative framing" in posts.
- Plain, direct, wire-service tone."""

    raw = ""
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.choices[0].message.content

        if "```" in raw:
            raw = raw.split("```")[-2] if raw.count("```") >= 2 else raw
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw[raw.find("{"):raw.rfind("}") + 1].strip()
        return json.loads(repair_json(raw))

    except Exception as e:
        print(f"    AI draft failed: {e}")
        print(f"    Raw (first 200): {raw[:200]}")
        return None


def write_markdown(queue):
    """Write a copy-paste-friendly version of every draft post."""
    lines = ["# Social Media Queue\n",
             "Copy and paste each block into the matching platform.\n",
             "Edit the queue or rerun social_post.py to regenerate.\n"]
    for i, item in enumerate(queue, 1):
        title  = item.get("title", "")
        url    = item.get("url", "")
        posts  = item.get("posts", {})

        lines.append(f"\n---\n\n## {i}. {title}\n")
        lines.append(f"**Source:** {url}\n")

        for platform in ["instagram", "x", "threads", "tiktok"]:
            text = posts.get(platform, "")
            if not text:
                continue
            lines.append(f"\n### {platform.upper()}\n")
            lines.append(f"```\n{text}\n```\n")

    with open(MARKDOWN_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    args = sys.argv[1:]

    # Reset mode — clear the queue
    if args and args[0] == "reset":
        save_json(QUEUE_FILE, [])
        print(f"Queue cleared. {QUEUE_FILE} is now empty.")
        return

    limit = int(args[0]) if args else 5

    stories = load_json(ARCHIVE_FILE, [])
    if not stories:
        print("No stories found.")
        return

    queue = load_json(QUEUE_FILE, [])
    posted = already_posted_urls(queue)

    # Newest first, skip ones already in the queue
    stories = sorted(stories, key=lambda s: s.get("saved_at", ""), reverse=True)
    candidates = [s for s in stories if s.get("url") not in posted][:limit]

    print(f"Drafting posts for {len(candidates)} stories...\n")

    for i, story in enumerate(candidates, 1):
        title = story.get("title_en") or story.get("title", "")
        print(f"[{i}/{len(candidates)}] {title[:70]}")
        posts = draft_for(story)
        if not posts:
            continue

        queue.append({
            "url":       story.get("url", ""),
            "title":     title,
            "country":   story.get("country", ""),
            "category":  story.get("category", ""),
            "image":     story.get("image", ""),
            "posts":     posts,
            "drafted_at": story.get("saved_at", ""),
        })
        save_json(QUEUE_FILE, queue)
        print(f"    Drafted: IG / X / Threads / TikTok\n")

    write_markdown(queue)
    print(f"Done. {len(queue)} stories in queue.")
    print(f"Markdown for copy-paste: {MARKDOWN_FILE}")


if __name__ == "__main__":
    main()
