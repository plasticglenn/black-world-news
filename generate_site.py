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
    if not framing:
        return ""
    color = FRAMING_COLORS.get(framing, "#555")
    return f'<span class="badge" style="background:{color}">{framing}</span>'


def factor_tags(factors):
    if not factors:
        return ""
    tags = "".join(f'<span class="factor">{f}</span>' for f in factors if f != "None identified")
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

        .badge {{
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            padding: 0.2rem 0.5rem;
            color: #fff;
            border-radius: 2px;
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
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            background: #eef4f0;
            border: 1px solid #c5daca;
            color: #2a5a3a;
            padding: 0.15rem 0.5rem;
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
    <h1>BLACK WORLD NEWS</h1>
    <p class="masthead-tagline">Documenting anti-Black racism globally — updated daily</p>
    <p class="masthead-meta">Last updated: {now} &nbsp;|&nbsp; {total} stories in archive</p>
</header>

<nav>
    <a href="#latest">Latest</a>
    <a href="#kids">🌍 Kids Corner</a>
    <a href="#archive">Archive</a>
    {''.join(f'<a href="#{c.lower().replace(" ", "-").replace("/", "-")}">{c}</a>' for c in REGION_ORDER if c in by_country)}
</nav>

<div class="breaking-bar"><span>LIVE</span> Monitoring {total} stories across {len(by_country)} regions — updated {now}</div>

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
            <p>Big stories, easy to understand — just for you!</p>
        </div>
        <div class="kids-grid">{kids_html}</div>
    </div>

    <!-- BREAK -->
    <div class="page-break-alt">
        <h2>News From Around The World</h2>
        <p>Browse by region — {total} stories and counting</p>
    </div>

    <!-- ARCHIVE BY REGION -->
    <div class="container" id="archive">
        {archive_sections}
    </div>

</main>

<footer>
    <p><strong>BLACK WORLD NEWS</strong> — A Pan-African media monitoring project.</p>
    <p style="margin-top:0.5rem">Stories sourced from open web. Analysis by AI through a Pan-African lens. Links go to original sources.</p>
</footer>

</body>
</html>"""


def main():
    stories = load_stories()
    if not stories:
        print("No stories to display.")
        return

    cache = load_image_cache()
    html  = build_html(stories, cache)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    save_image_cache(cache)
    print(f"Site generated: {OUTPUT_FILE}")
    print(f"Total stories: {len(stories)}")
    print(f"Images cached: {len(cache)}")


if __name__ == "__main__":
    main()
