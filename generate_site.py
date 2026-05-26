import json
import os
import urllib.parse
import requests as req
from datetime import datetime
from collections import defaultdict

ARCHIVE_FILE  = "stories.json"
OUTPUT_FILE   = "index.html"
IMAGE_CACHE   = "image_cache.json"
PEXELS_KEY    = os.environ.get("PEXELS_API_KEY", "")

# --- Change this to set the featured story ---
FEATURED_KEYWORD = "Youth Unemployment"

FRAMING_COLORS = {
    "Criminal":  "#e74c3c",
    "Victim":    "#e67e22",
    "Statistic": "#7f8c8d",
    "Human":     "#27ae60",
    "Resistant": "#2980b9",
    "Exploited": "#f39c12",
}

CATEGORY_COLORS = {
    "Policing":    "#1a2a4a",
    "Housing":     "#7a3a0a",
    "Employment":  "#0a4a3a",
    "Education":   "#3a1a5a",
    "Healthcare":  "#5a0a1a",
    "Politics":    "#1a3a2a",
    "Culture":     "#4a1a3a",
    "Hate Crime":  "#5a1a0a",
    "Immigration": "#0a3a4a",
    "Other":       "#2a2a2a",
}

COUNTRY_FLAGS = {
    "Canada":         "🇨🇦",
    "United States":  "🇺🇸",
    "United Kingdom": "🇬🇧",
    "France":         "🇫🇷",
    "Germany":        "🇩🇪",
    "Brazil":         "🇧🇷",
    "South Africa":   "🇿🇦",
    "Nigeria":        "🇳🇬",
    "Ghana":          "🇬🇭",
    "Australia":      "🇦🇺",
    "Other/Global":   "🌍",
}

REGION_ORDER = [
    "United States",
    "United Kingdom",
    "Canada",
    "France",
    "Germany",
    "Brazil",
    "Nigeria",
    "Ghana",
    "South Africa",
    "Australia",
    "Other/Global",
]


def load_image_cache():
    if os.path.exists(IMAGE_CACHE):
        with open(IMAGE_CACHE, "r") as f:
            return json.load(f)
    return {}

def save_image_cache(cache):
    with open(IMAGE_CACHE, "w") as f:
        json.dump(cache, f, indent=2)

def pexels_image(query, cache):
    if query in cache:
        return cache[query]
    if not PEXELS_KEY:
        return ""
    try:
        r = req.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": query, "per_page": 1, "orientation": "landscape"},
            timeout=10
        )
        photos = r.json().get("photos", [])
        url = photos[0]["src"]["large"] if photos else ""
        cache[query] = url
        return url
    except:
        cache[query] = ""
        return ""

def story_image(story, cache, featured=False):
    og = story.get("image", "")
    if og:
        return og
    if featured:
        country  = story.get("country", "")
        cat      = story.get("category", "").lower()
        title    = story.get("title", "")[:60]
        query    = f"Black people {cat} {country} {title}"
    else:
        cat     = story.get("category", "").lower()
        country = story.get("country", "")
        query   = f"{cat} {country} community people"
    return pexels_image(query, cache)

def ai_image_url(story):
    title   = story.get("title", "")[:80]
    summary = story.get("summary", "")[:150]
    country = story.get("country", "world")
    cat     = story.get("category", "news").lower()
    prompt  = f"editorial photojournalism, {title}, {summary}, {country}, {cat}, real people, powerful, documentary photography, no text, no watermark"
    encoded = urllib.parse.quote(prompt)
    seed    = abs(hash(story.get("url", ""))) % 99999
    return f"https://image.pollinations.ai/prompt/{encoded}?width=900&height=500&nologo=true&seed={seed}"


def load_stories():
    if not os.path.exists(ARCHIVE_FILE):
        print(f"No archive found at {ARCHIVE_FILE}")
        return []
    with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def framing_badge(framing):
    # A small coloured dot — hints at the framing without announcing it
    if not framing:
        return ""
    color = FRAMING_COLORS.get(framing, "#aaa")
    return f'<span class="framing-dot" style="background:{color}" title="{framing}"></span>'


def factor_tags(factors):
    # Small quiet tags at the bottom of each card
    if not factors:
        return ""
    tags = "".join(f'<span class="factor">{f.lower()}</span>' for f in factors if f != "None identified")
    return f'<div class="factors">{tags}</div>' if tags else ""


def story_card(story, featured=False, archive=False, cache=None):
    title   = story.get("title", "Untitled")
    url     = story.get("url", "#")
    country = story.get("country", "Other/Global")
    cat     = story.get("category", "")
    summary = story.get("summary", "")
    framing = story.get("narrative_framing", "")
    analysis= story.get("narrative_analysis", "")
    factors = story.get("structural_factors", [])
    saved   = story.get("saved_at", "")
    flag    = COUNTRY_FLAGS.get(country, "🌍")
    explicit= story.get("explicit_racism", False)
    explicit_tag = '<span class="explicit-tag">EXPLICIT RACISM</span>' if explicit else ""
    og_image = story.get("image", "")

    if archive:
        return f"""
    <div class="card archive-card">
        <div class="card-meta">
            <span class="flag-country">{flag} {country}</span>
            <span class="category">{cat}</span>
            {framing_badge(framing)}
        </div>
        <h2 class="card-title"><a href="{url}" target="_blank" rel="noopener">{title}</a></h2>
        <p class="card-summary">{summary}</p>
        <div class="card-footer">
            <span class="saved-at">{saved}</span>
            <a href="{url}" class="read-more" target="_blank" rel="noopener">Read →</a>
        </div>
    </div>"""

    img_src = story_image(story, cache or {}, featured=featured)
    img_html = f'<img class="card-img{"  featured-img" if featured else ""}" src="{img_src}" alt="" loading="lazy">' if img_src else ""

    card_class = "card featured" if featured else "card"

    return f"""
    <div class="{card_class}">
        {img_html}
        <div class="card-meta">
            <span class="flag-country">{flag} {country}</span>
            <span class="category">{cat}</span>
            {framing_badge(framing)}
            {explicit_tag}
        </div>
        <h2 class="card-title"><a href="{url}" target="_blank" rel="noopener">{title}</a></h2>
        <p class="card-summary">{summary}</p>
        {'<p class="narrative-analysis">' + analysis + '</p>' if analysis else ''}
        {factor_tags(factors)}
        <div class="card-footer">
            <span class="saved-at">Collected: {saved}</span>
            <a href="{url}" class="read-more" target="_blank" rel="noopener">Read original →</a>
        </div>
    </div>"""


def kids_card(story):
    title = story.get("title", "Untitled")
    url   = story.get("url", "#")
    summary = story.get("summary", "")
    country = story.get("country", "")
    flag  = COUNTRY_FLAGS.get(country, "🌍")
    image = story.get("image", "")
    colors = ["#ff6b6b","#ffd93d","#6bcb77","#4d96ff","#ff9ff3","#f9844a"]
    import hashlib
    color = colors[int(hashlib.md5(url.encode()).hexdigest(), 16) % len(colors)]

    img_html = f'<img class="kids-img" src="{image}" alt="" loading="lazy">' if image else f'<div class="kids-img-placeholder" style="background:{color}"><span style="font-size:2.5rem">🌍</span></div>'

    return f"""
    <div class="kids-card">
        {img_html}
        <div class="kids-card-body">
            <span class="kids-flag">{flag}</span>
            <h3 class="kids-title"><a href="{url}" target="_blank" rel="noopener">{title}</a></h3>
            <p class="kids-summary">{summary}</p>
            <a href="{url}" class="kids-btn" target="_blank" rel="noopener">Read the story →</a>
        </div>
    </div>"""


def build_html(stories, cache):
    now   = datetime.now().strftime("%B %d, %Y — %H:%M")
    total = len(stories)

    # Sort newest first
    stories = sorted(stories, key=lambda s: s.get("saved_at", ""), reverse=True)

    # Find featured story by keyword, fall back to most recent
    keyword = FEATURED_KEYWORD.lower()
    featured = next(
        (s for s in stories if keyword in s.get("title", "").lower() or keyword in s.get("summary", "").lower()),
        stories[0] if stories else None
    )
    remaining = [s for s in stories if s is not featured]
    latest = remaining[:6]

    # Group by country
    by_country = defaultdict(list)
    for s in stories:
        by_country[s.get("country", "Other/Global")].append(s)

    # Kids section — Education & Culture stories with Human/Resistant framing
    kids_stories = [s for s in stories if
        s.get("category") in ("Education", "Culture") and
        s.get("narrative_framing") in ("Human", "Resistant")][:6]
    kids_html = "".join(kids_card(s) for s in kids_stories) if kids_stories else "<p style='color:#555;padding:1rem;font-family:Fredoka One,cursive'>More kids stories coming soon!</p>"

    # Build featured block
    featured_html = story_card(featured, featured=True, cache=cache) if featured else ""

    # Build latest grid
    latest_html = "".join(story_card(s, cache=cache) for s in latest)

    # Build country sections
    archive_sections = ""
    seen_countries = set(REGION_ORDER)
    ordered = REGION_ORDER + [c for c in by_country if c not in seen_countries]

    for country in ordered:
        if country not in by_country:
            continue
        flag = COUNTRY_FLAGS.get(country, "🌍")
        cards = "".join(story_card(s, archive=True, cache=cache) for s in by_country[country])
        archive_sections += f"""
        <section class="country-section">
            <h3 class="country-heading">{flag} {country} <span class="count">({len(by_country[country])})</span></h3>
            <div class="card-grid">{cards}</div>
        </section>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Black World News</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@400;600&family=Fredoka+One&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            background: #f2f2f2;
            color: #111;
            font-family: 'Source Sans 3', sans-serif;
            font-size: 16px;
            line-height: 1.6;
        }}

        a {{ color: inherit; text-decoration: none; }}

        /* MASTHEAD */
        .masthead {{
            background: #1a3a2a;
            padding: 1.75rem 1.5rem 1.5rem;
            text-align: center;
        }}

        .logo-wrap {{
            display: flex;
            justify-content: center;
            margin-bottom: 1rem;
            filter: drop-shadow(0 2px 8px rgba(0,0,0,0.4));
        }}

        .masthead-eyebrow {{
            font-size: 0.7rem;
            letter-spacing: 0.3em;
            text-transform: uppercase;
            color: #8ab89a;
            margin-bottom: 0.6rem;
            font-weight: 600;
        }}

        .masthead h1 {{
            font-family: 'Playfair Display', serif;
            font-size: clamp(1.8rem, 5vw, 3.2rem);
            font-weight: 900;
            color: #ffffff;
            letter-spacing: 0.05em;
            line-height: 1;
        }}

        .masthead-tagline {{
            margin-top: 0.6rem;
            font-size: 0.8rem;
            color: #8ab89a;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }}

        .masthead-meta {{
            margin-top: 1rem;
            font-size: 0.78rem;
            color: #6a9a7a;
            border-top: 1px solid #2a5a3a;
            padding-top: 0.75rem;
        }}

        /* NAVIGATION */
        nav {{
            background: #111;
            padding: 0 1.5rem;
            display: flex;
            gap: 0;
            overflow-x: auto;
            border-bottom: 3px solid #1a3a2a;
        }}

        nav a {{
            font-size: 0.78rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #ccc;
            white-space: nowrap;
            font-weight: 600;
            padding: 0.75rem 1rem;
            border-bottom: 3px solid transparent;
            margin-bottom: -3px;
            transition: color 0.15s, border-color 0.15s;
        }}

        nav a:hover {{
            color: #fff;
            border-bottom-color: #1a3a2a;
        }}

        /* BREAKING BAR */
        .breaking-bar {{
            background: #1a3a2a;
            color: #fff;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 0.4rem 1.5rem;
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .breaking-bar span {{
            background: #fff;
            color: #1a3a2a;
            padding: 0.1rem 0.5rem;
            font-size: 0.7rem;
        }}

        /* LAYOUT */
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1.5rem;
        }}

        .section-label {{
            font-family: 'Playfair Display', serif;
            font-size: 1rem;
            font-weight: 700;
            color: #1a3a2a;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            border-bottom: 3px solid #1a3a2a;
            padding-bottom: 0.4rem;
            margin-bottom: 1.5rem;
        }}

        /* ARCHIVE CARDS — minimal, no images */
        .archive-card {{
            border-left: 3px solid #ddd;
            border-top: none;
            padding: 0.9rem 1.2rem;
        }}

        .archive-card:hover {{
            border-left-color: #1a3a2a;
            box-shadow: none;
        }}

        .archive-card .card-title {{
            font-size: 1rem;
        }}

        .archive-card .card-summary {{
            font-size: 0.82rem;
            color: #666;
        }}

        /* LABEL ONLY — replaces placeholder on non-featured cards */
        .card-label-only {{
            padding: 0.35rem 0;
            margin-bottom: 0.5rem;
        }}

        .card-label-only span {{
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: #1a3a2a;
            border-left: 3px solid #1a3a2a;
            padding-left: 0.5rem;
        }}

        /* CARD IMAGES */
        .card-img {{
            width: 100%;
            height: 180px;
            object-fit: cover;
            display: block;
            margin-bottom: 1rem;
        }}

        .card-img-placeholder {{
            width: 100%;
            height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
        }}

        .card-img-placeholder span {{
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            color: rgba(255,255,255,0.5);
        }}

        .featured .card-img,
        .featured .card-img-placeholder {{
            height: 260px;
        }}

        /* CARDS */
        .card {{
            background: #fff;
            border: 1px solid #ddd;
            border-top: 3px solid transparent;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1.25rem;
            transition: border-top-color 0.2s, box-shadow 0.2s;
        }}

        .card:hover {{
            border-top-color: #1a3a2a;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }}

        .card.featured {{
            background: #fff;
            border: 1px solid #bbb;
            border-top: 5px solid #1a3a2a;
            padding: 2rem;
            margin-bottom: 2rem;
        }}

        .card-meta {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
        }}

        .flag-country {{
            font-size: 0.8rem;
            color: #1a3a2a;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .category {{
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            background: #eef4f0;
            border: 1px solid #c5daca;
            padding: 0.15rem 0.5rem;
            color: #1a3a2a;
            font-weight: 600;
        }}

        /* Framing shown as a small coloured dot — subtle, not a label */
        .framing-dot {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            vertical-align: middle;
            cursor: default;
            flex-shrink: 0;
        }}

        .explicit-tag {{
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            padding: 0.2rem 0.5rem;
            background: transparent;
            border: 1px solid #1a3a2a;
            color: #1a3a2a;
        }}

        .card-title {{
            font-family: 'Playfair Display', serif;
            font-size: 1.2rem;
            font-weight: 700;
            color: #111;
            margin-bottom: 0.6rem;
            line-height: 1.3;
        }}

        .featured .card-title {{
            font-size: 1.4rem;
        }}

        .card-title a:hover {{ color: #1a3a2a; }}

        .card-summary {{
            font-size: 0.9rem;
            color: #444;
            margin-bottom: 0.6rem;
        }}

        .narrative-analysis {{
            font-size: 0.85rem;
            color: #666;
            font-style: italic;
            border-left: 3px solid #c5daca;
            padding-left: 0.75rem;
            margin-bottom: 0.6rem;
        }}

        .factors {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            margin-bottom: 0.75rem;
        }}

        .factor {{
            font-size: 0.62rem;
            text-transform: lowercase;
            letter-spacing: 0.02em;
            background: none;
            border: none;
            color: #bbb;
            padding: 0;
            font-weight: 600;
        }}

        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px solid #eee;
        }}

        .saved-at {{ font-size: 0.75rem; color: #aaa; }}

        .read-more {{
            font-size: 0.8rem;
            color: #1a3a2a;
            font-weight: 700;
            letter-spacing: 0.04em;
        }}

        .read-more:hover {{ text-decoration: underline; }}

        /* GRID */
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 1rem;
        }}

        .card-grid .card {{ margin-bottom: 0; }}

        /* COUNTRY SECTIONS */
        .country-section {{ margin-bottom: 3rem; }}

        .country-heading {{
            font-family: 'Playfair Display', serif;
            font-size: 1.3rem;
            font-weight: 700;
            color: #111;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #111;
        }}

        .country-heading .count {{
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.85rem;
            font-weight: 400;
            color: #999;
        }}

        /* PAGE BREAKS */
        .page-break {{
            background: #1a3a2a;
            color: #fff;
            text-align: center;
            padding: 2.5rem 1.5rem;
            margin: 0;
        }}

        .page-break h2 {{
            font-family: 'Playfair Display', serif;
            font-size: clamp(1rem, 3vw, 1.5rem);
            font-weight: 900;
            letter-spacing: 0.05em;
            margin-bottom: 0.4rem;
        }}

        .page-break p {{
            font-size: 0.9rem;
            color: #8ab89a;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        .page-break-alt {{
            background: #111;
            color: #fff;
            text-align: center;
            padding: 2.5rem 1.5rem;
            margin: 0;
        }}

        .page-break-alt h2 {{
            font-family: 'Playfair Display', serif;
            font-size: clamp(1rem, 3vw, 1.5rem);
            font-weight: 900;
            letter-spacing: 0.05em;
            margin-bottom: 0.4rem;
        }}

        .page-break-alt p {{
            font-size: 0.9rem;
            color: #666;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}

        /* KIDS SECTION */
        .kids-section {{
            background: #ffffff;
            padding: 3rem 1.5rem;
            border-top: 8px solid #ffd93d;
            border-bottom: 8px solid #ffd93d;
            position: relative;
        }}

        .kids-header {{
            text-align: center;
            margin-bottom: 2rem;
            position: relative;
        }}

        .kids-header h2 {{
            font-family: 'Fredoka One', cursive;
            font-size: clamp(1.6rem, 4vw, 2.4rem);
            color: #ff6b6b;
            text-shadow: 2px 2px 0 #ffd93d;
            line-height: 1.1;
        }}

        .kids-header p {{
            font-family: 'Fredoka One', cursive;
            font-size: 1.1rem;
            color: #4d96ff;
            margin-top: 0.5rem;
        }}

        .kids-header::after {{
            content: '⭐ 🌍 ⭐';
            display: block;
            font-size: 1.2rem;
            margin-top: 0.5rem;
            letter-spacing: 0.5rem;
        }}

        .kids-grid {{
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
        }}

        .kids-card {{
            background: #fff;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(0,0,0,0.08);
            border: 4px solid #ffd93d;
            transition: transform 0.25s, box-shadow 0.25s;
        }}

        .kids-card:nth-child(2) {{ border-color: #6bcb77; }}
        .kids-card:nth-child(3) {{ border-color: #4d96ff; }}
        .kids-card:nth-child(4) {{ border-color: #ff6b6b; }}
        .kids-card:nth-child(5) {{ border-color: #f9844a; }}
        .kids-card:nth-child(6) {{ border-color: #a855f7; }}

        .kids-card:hover {{
            transform: translateY(-6px) rotate(0.5deg);
            box-shadow: 0 12px 32px rgba(0,0,0,0.12);
        }}

        .kids-img {{
            width: 100%;
            height: 160px;
            object-fit: cover;
            display: block;
        }}

        .kids-img-placeholder {{
            width: 100%;
            height: 160px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .kids-card-body {{
            padding: 1.25rem;
        }}

        .kids-flag {{
            font-size: 1.5rem;
            display: block;
            margin-bottom: 0.4rem;
        }}

        .kids-title {{
            font-family: 'Fredoka One', cursive;
            font-size: 1.2rem;
            color: #222;
            line-height: 1.3;
            margin-bottom: 0.6rem;
        }}

        .kids-title a:hover {{ color: #ff6b6b; }}

        .kids-summary {{
            font-size: 0.88rem;
            color: #555;
            line-height: 1.5;
            margin-bottom: 1rem;
        }}

        .kids-flag {{
            font-size: 1.8rem;
            display: block;
            margin-bottom: 0.4rem;
        }}

        .kids-btn {{
            display: inline-block;
            background: #ffd93d;
            color: #111;
            font-family: 'Fredoka One', cursive;
            font-size: 0.95rem;
            padding: 0.45rem 1.2rem;
            border-radius: 30px;
            border: 2px solid #111;
            box-shadow: 3px 3px 0 #111;
            transition: transform 0.15s, box-shadow 0.15s;
        }}

        .kids-btn:hover {{
            transform: translate(2px, 2px);
            box-shadow: 1px 1px 0 #111;
        }}

        /* FOOTER */
        footer {{
            background: #111;
            border-top: 4px solid #1a3a2a;
            text-align: center;
            padding: 2rem;
            font-size: 0.8rem;
            color: #666;
        }}

        footer strong {{ color: #8ab89a; }}

        /* ========== MOBILE APP EXPERIENCE ========== */
        @media (max-width: 768px) {{

            /* APP HEADER — compact, sticky */
            .masthead {{
                position: sticky;
                top: 0;
                z-index: 100;
                padding: 0.75rem 1rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
                text-align: left;
                border-top: none;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            }}

            .logo-wrap {{ margin-bottom: 0; }}
            .logo-wrap svg {{ width: 36px; height: 36px; }}

            .masthead-eyebrow {{ display: none; }}
            .masthead-tagline {{ display: block; font-size: 0.6rem; letter-spacing: 0.06em; margin-top: 0.2rem; color: #8ab89a; }}
            .masthead-meta {{ display: none; }}

            .masthead-text {{
                flex: 1;
                padding-left: 0.75rem;
            }}

            .masthead h1 {{
                font-size: 1.3rem;
                letter-spacing: 0.02em;
                text-align: left;
            }}

            /* HIDE desktop nav, show bottom app nav */
            nav {{ display: none; }}
            .breaking-bar {{ font-size: 0.68rem; padding: 0.35rem 0.75rem; }}

            /* BOTTOM TAB BAR */
            body {{ padding-bottom: 60px; }}

            body::after {{
                content: '';
                display: block;
            }}

            .mobile-tabs {{
                display: flex !important;
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: #111;
                border-top: 2px solid #1a3a2a;
                z-index: 200;
                height: 60px;
            }}

            .mobile-tabs a {{
                flex: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: #888;
                font-size: 0.6rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                gap: 0.2rem;
                text-decoration: none;
                transition: color 0.15s;
            }}

            .mobile-tabs a:first-child {{ color: #8ab89a; }}
            .mobile-tabs a .tab-icon {{ font-size: 1.1rem; }}

            /* FEATURED — full bleed hero card */
            .card.featured {{
                border-radius: 0;
                border: none;
                border-top: none;
                padding: 0;
                margin-bottom: 0;
                position: relative;
                overflow: hidden;
            }}

            .featured-img {{
                height: 280px;
                width: 100%;
                object-fit: cover;
                display: block;
            }}

            .card.featured .card-meta,
            .card.featured .card-title,
            .card.featured .card-summary,
            .card.featured .narrative-analysis,
            .card.featured .factors,
            .card.featured .card-footer {{
                padding: 0 1rem;
            }}

            .card.featured .card-meta {{ padding-top: 1rem; }}
            .card.featured .card-footer {{ padding-bottom: 1rem; }}
            .card.featured .card-title {{ font-size: 1.25rem; }}

            /* LATEST — horizontal scroll strip */
            .card-grid {{
                display: flex;
                overflow-x: auto;
                scroll-snap-type: x mandatory;
                gap: 0.75rem;
                padding: 0 1rem 1rem;
                -webkit-overflow-scrolling: touch;
                scrollbar-width: none;
            }}

            .card-grid::-webkit-scrollbar {{ display: none; }}

            .card-grid .card {{
                min-width: 260px;
                max-width: 260px;
                scroll-snap-align: start;
                margin-bottom: 0;
                border-radius: 12px;
                flex-shrink: 0;
            }}

            .card-grid .card-img {{ height: 150px; border-radius: 12px 12px 0 0; }}

            /* SECTION LABELS */
            .section-label {{
                padding: 0 1rem;
                font-size: 0.75rem;
            }}

            .container {{ padding: 1rem 0; }}

            /* PAGE BREAKS — slimmer on mobile */
            .page-break, .page-break-alt {{
                padding: 1.25rem 1rem;
                text-align: left;
            }}

            /* KIDS — single column, app card style */
            .kids-section {{ padding: 1.5rem 1rem; }}
            .kids-grid {{
                grid-template-columns: 1fr;
                gap: 1rem;
            }}
            .kids-card {{ border-radius: 16px; }}
            .kids-header h2 {{ font-size: 1.5rem; }}

            /* ARCHIVE — slim list rows */
            .archive-card {{
                border-radius: 0;
                border-left: none;
                border-bottom: 1px solid #eee;
                padding: 0.85rem 1rem;
                margin-bottom: 0;
            }}

            .archive-card .card-title {{ font-size: 0.95rem; }}
            .archive-card .card-summary {{ display: none; }}
            .archive-card .factors {{ display: none; }}
            .archive-card .narrative-analysis {{ display: none; }}
            .archive-card .card-footer {{
                padding-top: 0.4rem;
                margin-top: 0.4rem;
            }}

            .country-section {{ margin-bottom: 1.5rem; }}
            .country-heading {{
                font-size: 1rem;
                padding: 0.5rem 1rem;
                margin-bottom: 0;
                border-bottom: 2px solid #111;
                background: #f8f8f8;
            }}

            footer {{ padding: 1.25rem 1rem; font-size: 0.75rem; margin-bottom: 60px; }}
        }}
    </style>
</head>
<body>

<header class="masthead">
    <div class="logo-wrap">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="72" height="72" aria-hidden="true">
            <!-- Outer ring -->
            <circle cx="50" cy="50" r="47" fill="#1a3a2a" stroke="rgba(255,255,255,0.15)" stroke-width="1.5"/>
            <!-- Globe latitude lines -->
            <ellipse cx="50" cy="50" rx="47" ry="22" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="1"/>
            <ellipse cx="50" cy="50" rx="47" ry="40" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
            <!-- Globe longitude lines -->
            <ellipse cx="50" cy="50" rx="22" ry="47" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="1"/>
            <!-- Equator -->
            <line x1="3" y1="50" x2="97" y2="50" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>
            <!-- Africa shape — simplified -->
            <path d="M46 28 Q52 26 55 32 Q60 36 58 44 Q62 50 60 57 Q58 65 54 70 Q50 74 47 70 Q42 64 41 57 Q38 50 40 44 Q39 36 43 30 Z"
                  fill="rgba(255,255,255,0.22)" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/>
            <!-- BWN monogram -->
            <text x="50" y="56" text-anchor="middle"
                  font-family="Georgia, 'Times New Roman', serif"
                  font-size="17" font-weight="bold" fill="white" opacity="0.9">BWN</text>
        </svg>
    </div>
    <p class="masthead-eyebrow">Your World Today</p>
    <div class="masthead-text">
        <h1>BLACK WORLD NEWS</h1>
        <p class="masthead-tagline">"Let my people go, that they may serve me." – Exodus 8:1</p>
    </div>
    <p class="masthead-meta admin-only" style="display:none">Last updated: {now} &nbsp;|&nbsp; {total} stories in archive</p>
</header>

<nav>
    <a href="#latest">Latest</a>
    <a href="#kids">🌍 Kids Corner</a>
    <a href="#archive">Archive</a>
    {''.join(f'<a href="#{c.lower().replace(" ", "-").replace("/", "-")}">{c}</a>' for c in REGION_ORDER if c in by_country)}
</nav>

<div class="breaking-bar"><span>LIVE</span> Monitoring {total} stories across {len(by_country)} regions. Updated {now}</div>

<main>

    <!-- FEATURED + LATEST -->
    <div class="container" id="latest">
        <p class="section-label">Featured Story</p>
        {featured_html}
        <p class="section-label">Latest</p>
        <div class="card-grid">{latest_html}</div>
    </div>

    <!-- BREAK -->
    <div class="page-break">
        <h2>Stories That Matter. Every Day.</h2>

        <p>Tracking the Black experience across {len(by_country)} regions worldwide</p>
    </div>

    <!-- KIDS SECTION -->
    <div class="kids-section" id="kids">
        <div class="kids-header">
            <h2>🌍 Kids Corner!</h2>
            <p>Big stories, easy to understand. Just for you!</p>
        </div>
        <div class="kids-grid">{kids_html}</div>
    </div>

    <!-- BREAK -->
    <div class="page-break-alt">
        <h2>News From Around The World</h2>
        <p>Browse by region. {total} stories and counting</p>
    </div>

    <!-- ARCHIVE BY REGION -->
    <div class="container" id="archive">
        {archive_sections}
    </div>

</main>

<div class="mobile-tabs" style="display:none">
    <a href="#latest"><span class="tab-icon">🏠</span>Latest</a>
    <a href="#kids"><span class="tab-icon">🌍</span>Kids</a>
    <a href="#archive"><span class="tab-icon">📰</span>Archive</a>
    <a href="#latest"><span class="tab-icon">🔍</span>Search</a>
</div>

<footer>
    <p><strong>BLACK WORLD NEWS</strong></p>
    <p style="margin-top:0.5rem">Stories sourced from the open web. AI summaries. Links always go to the original source.</p>
</footer>

<script>
  // If the URL contains ?admin — show the hidden stats
  // Example: https://www.blackworldnews.world?admin
  if (window.location.search.includes('admin')) {{
    document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'block');
  }}
</script>

</body>
</html>"""


def page_shell(title, content, active=""):
    # Shared header, nav and footer used by every page
    nav_links = [
        ("Latest", "/black-world-news/index.html", "latest"),
        ("About", "/black-world-news/about.html", "about"),
        ("Resources", "/black-world-news/resources.html", "resources"),
        ("Trends", "/black-world-news/trends.html", "trends"),
        ("Community", "/black-world-news/community.html", "community"),
        ("🌍 Kids", "/black-world-news/index.html#kids", "kids"),
    ]
    nav_html = "".join(
        f'<a href="{url}" class="{"active" if key == active else ""}">{label}</a>'
        for label, url, key in nav_links
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Black World News</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ background: #f2f2f2; color: #111; font-family: 'Source Sans 3', sans-serif; font-size: 16px; line-height: 1.7; }}
        a {{ color: inherit; text-decoration: none; }}

        .masthead {{ background: #1a3a2a; border-bottom: 3px solid #111; padding: 1.25rem 1.5rem; display: flex; align-items: center; gap: 1rem; }}
        .masthead h1 {{ font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 900; color: #fff; letter-spacing: 0.04em; }}
        .masthead h1 a:hover {{ color: #c8d8c0; }}
        .masthead-tagline {{ font-size: 0.65rem; color: #8ab89a; letter-spacing: 0.1em; text-transform: uppercase; margin-top: 0.2rem; }}

        nav {{ background: #111; padding: 0.6rem 1.5rem; display: flex; gap: 1.5rem; overflow-x: auto; }}
        nav a {{ font-size: 0.78rem; letter-spacing: 0.08em; text-transform: uppercase; color: #888; white-space: nowrap; font-weight: 600; transition: color 0.2s; }}
        nav a:hover, nav a.active {{ color: #8ab89a; }}

        .page-container {{ max-width: 860px; margin: 0 auto; padding: 3rem 1.5rem; }}
        .page-title {{ font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 900; color: #111; margin-bottom: 0.5rem; }}
        .page-subtitle {{ font-size: 1rem; color: #666; margin-bottom: 2.5rem; padding-bottom: 1.5rem; border-bottom: 2px solid #111; }}

        .section-title {{ font-family: 'Playfair Display', serif; font-size: 1.2rem; font-weight: 700; color: #1a3a2a; margin: 2rem 0 1rem; }}
        .placeholder-block {{ background: #fff; border: 1px dashed #ccc; border-left: 4px solid #1a3a2a; padding: 2rem; color: #999; font-style: italic; margin-bottom: 1rem; }}

        footer {{ background: #111; border-top: 4px solid #1a3a2a; text-align: center; padding: 2rem; font-size: 0.8rem; color: #555; margin-top: 4rem; }}
        footer strong {{ color: #8ab89a; }}

        @media (max-width: 768px) {{
            .masthead {{ padding: 0.75rem 1rem; }}
            .masthead h1 {{ font-size: 1.2rem; }}
            .page-container {{ padding: 2rem 1rem; }}
            .page-title {{ font-size: 1.5rem; }}
        }}
    </style>
</head>
<body>
<header class="masthead">
    <div>
        <h1><a href="/black-world-news/index.html">BLACK WORLD NEWS</a></h1>
        <p class="masthead-tagline">"Let my people go, that they may serve me." – Exodus 8:1</p>
    </div>
</header>
<nav>{nav_html}</nav>

<div class="page-container">
    {content}
</div>

<footer>
    <p><strong>BLACK WORLD NEWS</strong> Your World Today</p>
    <p style="margin-top:0.5rem">Stories sourced from the open web. Links go to original sources.</p>
</footer>
</body>
</html>"""


def build_about():
    content = """
    <h1 class="page-title">About</h1>
    <p class="page-subtitle">Who we are, what we do, and why it matters.</p>

    <h2 class="section-title">What is Black World News?</h2>
    <p>Black World News is a news aggregation service covering stories involving Black communities around the world. We monitor sources across Africa, North and South America, the Caribbean, and Europe and publish summaries daily.</p>

    <h2 class="section-title">How it works</h2>
    <p>We use automated tools to search, collect, and summarize news articles from across the web. Each story is tagged by country and topic. Links always go back to the original source.</p>

    <h2 class="section-title">Who it is for</h2>
    <p>Anyone who wants to stay informed. Families, students, researchers, professionals. The site is free and open to everyone.</p>

    <h2 class="section-title">Who built this?</h2>
    <p>Black World News was founded by Glenn Asare in 2026.</p>

    <h2 class="section-title">Why it exists</h2>
    <p>News about Black communities around the world is scattered across hundreds of sources. We put it in one place. We are connected through shared experiences and this is where you come to see them.</p>
    """
    return page_shell("About", content, active="about")


def build_resources():
    books = [
        ("The New Jim Crow", "Michelle Alexander", "How mass incarceration has become a system of racial control in the United States."),
        ("Black Reconstruction in America", "W.E.B. Du Bois", "The definitive account of what Black people built after slavery, and how it was dismantled."),
        ("How Europe Underdeveloped Africa", "Walter Rodney", "A clear-eyed account of how colonial extraction shaped the economic gap between Africa and the West."),
        ("The Warmth of Other Suns", "Isabel Wilkerson", "The story of the Great Migration told through three families who left the American South."),
        ("Homegoing", "Yaa Gyasi", "A novel tracing one family across eight generations from Ghana to the United States."),
        ("Small Axe", "Linton Kwesi Johnson", "Poetry from the front lines of Black Britain."),
    ]
    orgs = [
        ("African Union", "https://au.int", "The continental body coordinating political and economic cooperation across 55 African nations."),
        ("Black Lives Matter Global Network", "https://blacklivesmatter.com", "A decentralised movement with chapters across the US, UK, and Canada."),
        ("NAACP", "https://naacp.org", "The oldest civil rights organisation in the United States, focused on legal advocacy and policy."),
        ("Runnymede Trust", "https://www.runnymedetrust.org", "The UK's leading race equality think tank."),
        ("Institute of the Black World 21st Century", "https://ibw21.org", "Research and advocacy grounded in the Pan-African tradition."),
    ]
    films = [
        ("13th", "Ava DuVernay, 2016", "Traces the history of racial inequality in the United States through the prison system."),
        ("I Am Not Your Negro", "Raoul Peck, 2016", "James Baldwin's unfinished manuscript brought to life. Essential viewing."),
        ("When They See Us", "Ava DuVernay, 2019", "The true story of the Central Park Five, wrongly convicted as teenagers."),
        ("Concerning Violence", "Göran Hugo Olsson, 2014", "Frantz Fanon's writing on colonialism set against archival footage of African liberation movements."),
        ("Black Panther: Wakanda Forever", "Ryan Coogler, 2022", "Not just a superhero film. A meditation on grief, sovereignty, and what we owe each other."),
    ]

    books_html = "".join(f"""
        <div class="resource-item">
            <strong>{title}</strong> <span class="resource-author">by {author}</span>
            <p>{desc}</p>
        </div>""" for title, author, desc in books)

    orgs_html = "".join(f"""
        <div class="resource-item">
            <strong><a href="{url}" target="_blank" rel="noopener">{name}</a></strong>
            <p>{desc}</p>
        </div>""" for name, url, desc in orgs)

    films_html = "".join(f"""
        <div class="resource-item">
            <strong>{title}</strong> <span class="resource-author">{year}</span>
            <p>{desc}</p>
        </div>""" for title, year, desc in films)

    content = f"""
    <h1 class="page-title">Resources</h1>
    <p class="page-subtitle">Books, organisations, and films worth your time.</p>

    <style>
        .resource-item {{ background:#fff; border-left:4px solid #1a3a2a; padding:1rem 1.25rem; margin-bottom:1rem; }}
        .resource-item strong {{ font-size:1rem; color:#111; }}
        .resource-item strong a:hover {{ color:#1a3a2a; text-decoration:underline; }}
        .resource-author {{ font-size:0.85rem; color:#888; margin-left:0.5rem; }}
        .resource-item p {{ font-size:0.9rem; color:#555; margin-top:0.4rem; line-height:1.5; }}
    </style>

    <h2 class="section-title">Books</h2>
    {books_html}

    <h2 class="section-title">Organisations</h2>
    {orgs_html}

    <h2 class="section-title">Films and Documentaries</h2>
    {films_html}
    """
    return page_shell("Resources", content, active="resources")


def build_trends():
    # Load live data from the archive
    stories = load_stories()
    total = len(stories)
    if not stories:
        return page_shell("Trends", "<p>No data yet.</p>", active="trends")

    from collections import Counter

    framing_counts  = Counter(s.get("narrative_framing", "") for s in stories if s.get("narrative_framing") and s.get("narrative_framing") != "None")
    category_counts = Counter(s.get("category", "") for s in stories if s.get("category"))
    country_counts  = Counter(s.get("country", "") for s in stories if s.get("country"))
    factor_counts   = Counter()
    for s in stories:
        for f in s.get("structural_factors", []):
            if f and f != "None identified":
                factor_counts[f] += 1
    explicit_count = sum(1 for s in stories if s.get("explicit_racism"))

    def bar_chart(counts, colors=None, total_override=None):
        top = counts.most_common(8)
        max_val = top[0][1] if top else 1
        denom = total_override or sum(v for _, v in top)
        rows = ""
        for label, count in top:
            pct = round(count / denom * 100)
            bar_pct = round(count / max_val * 100)
            color = (colors or {}).get(label, "#1a3a2a")
            rows += f"""
            <div class="trend-row">
                <div class="trend-label">{label}</div>
                <div class="trend-bar-wrap">
                    <div class="trend-bar" style="width:{bar_pct}%;background:{color}"></div>
                </div>
                <div class="trend-count">{count} <span class="trend-pct">({pct}%)</span></div>
            </div>"""
        return f'<div class="trend-chart">{rows}</div>'

    framing_html   = bar_chart(framing_counts, FRAMING_COLORS, total_override=total)
    category_html  = bar_chart(category_counts)
    country_html   = bar_chart(country_counts)
    factor_html    = bar_chart(factor_counts)

    content = f"""
    <h1 class="page-title">Trends</h1>
    <p class="page-subtitle">Patterns across {total} stories collected so far. Updated each time the site rebuilds.</p>

    <style>
        .trend-stat {{ display:inline-block; background:#1a3a2a; color:#fff; padding:1rem 2rem; margin-bottom:2rem; text-align:center; margin-right:1rem; }}
        .trend-stat strong {{ display:block; font-size:2rem; font-family:'Playfair Display',serif; }}
        .trend-stat span {{ font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; color:#8ab89a; }}
        .trend-chart {{ margin-bottom:1rem; }}
        .trend-row {{ display:flex; align-items:center; gap:0.75rem; margin-bottom:0.6rem; }}
        .trend-label {{ width:160px; font-size:0.82rem; font-weight:600; color:#333; flex-shrink:0; }}
        .trend-bar-wrap {{ flex:1; background:#eee; height:18px; }}
        .trend-bar {{ height:18px; transition:width 0.4s; }}
        .trend-count {{ font-size:0.82rem; color:#666; width:80px; text-align:right; flex-shrink:0; }}
        .trend-pct {{ color:#aaa; font-size:0.75rem; }}
        @media(max-width:600px) {{ .trend-label {{ width:100px; font-size:0.75rem; }} .trend-count {{ width:60px; }} }}
    </style>

    <div>
        <div class="trend-stat"><strong>{total}</strong><span>Stories collected</span></div>
        <div class="trend-stat"><strong>{explicit_count}</strong><span>Explicit racism flagged</span></div>
        <div class="trend-stat"><strong>{len(country_counts)}</strong><span>Countries covered</span></div>
    </div>

    <h2 class="section-title">How stories frame Black people</h2>
    {framing_html}

    <h2 class="section-title">Topics covered</h2>
    {category_html}

    <h2 class="section-title">Stories by country</h2>
    {country_html}

    <h2 class="section-title">Forces appearing in the stories</h2>
    {factor_html}
    """
    return page_shell("Trends", content, active="trends")


def build_community():
    content = """
    <h1 class="page-title">Community</h1>
    <p class="page-subtitle">This space belongs to you. Share a story. Share a thought.</p>

    <h2 class="section-title">Submit a story tip</h2>
    <div class="placeholder-block">Coming soon.</div>

    <h2 class="section-title">Reader voices</h2>
    <div class="placeholder-block">Coming soon.</div>
    """
    return page_shell("Community", content, active="community")


def main():
    stories = load_stories()
    if not stories:
        print("No stories to display.")
        return

    cache = load_image_cache()
    html  = build_html(stories, cache)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    # Build the four extra pages
    for filename, builder in [
        ("about.html",     build_about),
        ("resources.html", build_resources),
        ("trends.html",    build_trends),
        ("community.html", build_community),
    ]:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(builder())
        print(f"Page generated: {filename}")

    save_image_cache(cache)
    print(f"Site generated: {OUTPUT_FILE}")
    print(f"Total stories: {len(stories)}")
    print(f"Images cached: {len(cache)}")


if __name__ == "__main__":
    main()
