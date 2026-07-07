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

# The single brand colour used across every section (region and issue pages).
# Change it here once and the whole site stays uniform. The kids page is the
# only place that intentionally uses bright, playful colour.
BRAND = "#1a3a2a"

# ---------------------------------------------------------------------------
# CONTENT CHANNELS — single source of truth for where the BWN Kids portal sends
# people. This is the distribution "machine": fill a URL in when the channel
# goes live and the site wires it up everywhere. Leave "" for a calm
# "Coming soon" door (still shown, just not clickable yet). No other file
# needs editing.
# ---------------------------------------------------------------------------
YOUTUBE_URL   = "https://www.youtube.com/channel/UCddUUCREEHYOLoEzmCfobKQ"   # live (Channel ID; swap to @handle once it activates)
TIKTOK_URL    = "https://www.tiktok.com/@blackworldnews"   # live
INSTAGRAM_URL = ""   # e.g. "https://www.instagram.com/blackworldnews"
FACEBOOK_URL  = "https://www.facebook.com/profile.php?id=61590158803177"   # live (numeric ID until a username is claimed)
X_URL         = ""   # e.g. "https://x.com/blackworldnews"
WHATSAPP_URL  = ""   # e.g. a WhatsApp channel invite link
COMICS_URL    = "comics.html"   # on-site comics page (placeholder until first strip ships)


def social_bar_html():
    # Footer social row. Shows ONLY channels with a URL set, so the adult site
    # stays clean until accounts exist. Self-contained inline styles (no CSS
    # edits). The kids page never gets this bar — safety rule.
    live = [(n, u) for n, u in (
        ("YouTube", YOUTUBE_URL), ("TikTok", TIKTOK_URL),
        ("Instagram", INSTAGRAM_URL), ("Facebook", FACEBOOK_URL),
        ("X", X_URL), ("WhatsApp", WHATSAPP_URL),
    ) if u]
    if not live:
        return ""
    links = "".join(
        f'<a href="{u}" target="_blank" rel="noopener" '
        f'style="color:#8ab89a;font-weight:600;text-decoration:none;">{n}</a>'
        for n, u in live
    )
    return ('<nav aria-label="Our channels" style="margin-top:0.9rem;display:flex;'
            'gap:0.5rem 1.1rem;justify-content:center;flex-wrap:wrap;">' + links + '</nav>')


def footer_legal_html():
    # Tiny privacy link for every public footer (kids page excluded — it has no
    # social bar and states its own no-data policy).
    return ('<p style="margin-top:0.6rem;font-size:0.72rem;">'
            '<a href="/privacy.html" style="color:#666;text-decoration:none;">Privacy</a></p>')


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
    "Colombia":       "🇨🇴",
    "Caribbean":      "🌴",
    "Ghana":          "🇬🇭",
    "Nigeria":        "🇳🇬",
    "Kenya":          "🇰🇪",
    "South Africa":   "🇿🇦",
    "Senegal":        "🇸🇳",
    "Mali":           "🇲🇱",
    "Cameroon":       "🇨🇲",
    "Niger":          "🇳🇪",
    "Ivory Coast":    "🇨🇮",
    "Burkina Faso":   "🇧🇫",
    "Zimbabwe":       "🇿🇼",
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
    "Caribbean",
    "Ghana",
    "Nigeria",
    "Kenya",
    "South Africa",
    "Senegal",
    "Mali",
    "Cameroon",
    "Niger",
    "Ivory Coast",
    "Burkina Faso",
    "Zimbabwe",
    "Australia",
    "Other/Global",
]

# Groups countries into nav regions for the archive headings
REGION_GROUPS = {
    "namerica":  {"label": "North America",   "color": BRAND, "countries": ["United States", "Canada"]},
    "caribbean": {"label": "Caribbean",       "color": BRAND, "countries": ["Caribbean"]},
    "samerica":  {"label": "South America",   "color": BRAND, "countries": ["Brazil", "Colombia"]},
    "africa":    {"label": "Africa",          "color": BRAND, "countries": ["Ghana", "Nigeria", "Kenya", "South Africa", "Senegal", "Mali", "Cameroon", "Niger", "Ivory Coast", "Burkina Faso", "Zimbabwe", "Other/Global"]},
    "europe":    {"label": "Europe",          "color": BRAND, "countries": ["United Kingdom", "France", "Germany"]},
    "asia":      {"label": "Asia and Pacific","color": BRAND, "countries": ["Australia", "India", "China", "Japan"]},
}

# Issue groups — map nav topic tabs to story categories
    # Order matters — this is the order shown in the nav after "Home".
    # Policing is deliberately last. One uniform brand colour across all.
ISSUE_GROUPS = {
    "economics":  {"label": "Economics",  "categories": ["Employment", "Housing", "Other"], "color": BRAND},
    "health":     {"label": "Health",     "categories": ["Healthcare"],                     "color": BRAND},
    "education":  {"label": "Education",   "categories": ["Education"],                      "color": BRAND},
    "politics":   {"label": "Politics",   "categories": ["Politics", "Immigration"],        "color": BRAND},
    "culture":    {"label": "Culture",    "categories": ["Culture"],                        "color": BRAND},
    "policing":   {"label": "Policing",   "categories": ["Policing", "Hate Crime"],         "color": BRAND},
}


# Vibrant kid-friendly palette used for "Kids Corner" in the nav.
# Letters cycle through these in order.
KIDS_LETTER_COLORS = ["red", "pink", "blue", "yellow", "green", "orange", "purple"]


# PWA — manifest, theme color, iOS meta tags. Injected into <head> of every page.
PWA_META = """
<!-- PWA -->
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#1a3a2a">
<meta name="application-name" content="Black World News">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="BWN">
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">
<link rel="apple-touch-icon" sizes="152x152" href="/icons/apple-touch-icon-152.png">
<link rel="apple-touch-icon" sizes="167x167" href="/icons/apple-touch-icon-167.png">
<link rel="apple-touch-icon" sizes="180x180" href="/icons/apple-touch-icon.png">
<!-- /PWA -->
<!-- Flag emoji: show real flags on devices that render them (phones, Mac, the app),
     strip the broken two-letter fallback on devices that don't (Windows). The country
     name already sits beside each flag, so nothing meaningful is lost. -->
<script>
(function(){
  function flagsOK(){
    try{
      var x=document.createElement('canvas').getContext('2d');
      x.font='20px sans-serif';
      var pair=x.measureText('\\uD83C\\uDDE8\\uD83C\\uDDE6').width;  // CA flag
      var one =x.measureText('\\uD83C\\uDDE8').width;                // single indicator
      return pair < one*1.5;  // supported: pair forms ~one glyph; unsupported: ~two letters
    }catch(e){return true;}
  }
  if(flagsOK()) return;
  document.documentElement.className+=' no-flags';
  var rx=/\\uD83C[\\uDDE6-\\uDDFF]/g;  // regional-indicator (flag) characters
  function strip(root){
    if(!root) return;
    var w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,null),n,a=[];
    while(n=w.nextNode())a.push(n);
    a.forEach(function(t){
      if(rx.test(t.nodeValue)) t.nodeValue=t.nodeValue.replace(rx,'').replace(/\\s{2,}/g,' ').replace(/^\\s+/,'');
    });
  }
  window.__bwnStripFlags=strip;
  if(document.body) strip(document.body);
  else document.addEventListener('DOMContentLoaded',function(){strip(document.body);});
})();
</script>
"""

# Service worker registration — injected at the bottom of every page.
PWA_SCRIPT = """
<script>
  if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
          navigator.serviceWorker.register('/sw.js').catch(() => {});
      });
  }
</script>
"""

# Cloudflare Web Analytics — injected at the bottom of every page.
# Privacy-respecting, no cookies, no GDPR banner needed.
CLOUDFLARE_ANALYTICS = (
    "<!-- Cloudflare Web Analytics -->"
    "<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
    "data-cf-beacon='{\"token\": \"e3ec5487cf654658b68643a2cb7cfc40\"}'></script>"
    "<!-- End Cloudflare Web Analytics -->"
)


def colorize_kids_text(text):
    """Wrap each character of `text` in a coloured span so the nav link
    becomes glossy multi-color balloon letters. Spaces become visual gaps."""
    out = []
    idx = 0
    for ch in text:
        if ch == " ":
            out.append('<span class="kids-space"></span>')
        else:
            color = KIDS_LETTER_COLORS[idx % len(KIDS_LETTER_COLORS)]
            out.append(f'<span class="kids-letter kc-{color}">{ch}</span>')
            idx += 1
    return "".join(out)


# CSS for the multi-color balloon letters used on every page's "Kids Corner" link.
# Injected into each page's <style> block.
KIDS_LETTER_CSS = """
.kids-letter {
    display: inline-block;
    background: linear-gradient(to bottom, #ffffff -20%, var(--top) 28%, var(--bot) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
    filter:
        drop-shadow(0 1.5px 0 var(--deep))
        drop-shadow(0 2px 2px rgba(0,0,0,0.25));
    padding: 0;
}
.kc-red    { --top: #ff3344; --bot: #b81e30; --deep: #6f1320; }
.kc-pink   { --top: #ff6b9d; --bot: #c2326b; --deep: #6e1b3c; }
.kc-blue   { --top: #4d96ff; --bot: #1e5fb3; --deep: #103b73; }
.kc-yellow { --top: #ffd83d; --bot: #c89914; --deep: #7a5d08; }
.kc-green  { --top: #2ec167; --bot: #15803d; --deep: #0a4d24; }
.kc-orange { --top: #ff9f43; --bot: #c46d10; --deep: #6e3d05; }
.kc-purple { --top: #b366ff; --bot: #7a23c0; --deep: #3f0c6e; }
.kids-space { display: inline-block; width: 0.25em; }
"""


def make_two_tier_nav(active_region="", active_issue=""):
    """Single-row nav: issues | regions, separated by a pipe divider."""
    # Home first, Policing last (per editorial direction).
    issues = [
        ("Home",       "index.html",     "home"),
        ("Economics",  "economics.html", "economics"),
        ("Health",     "health.html",    "health"),
        ("Education",  "education.html", "education"),
        ("Politics",   "politics.html",  "politics"),
        ("Culture",    "culture.html",   "culture"),
        ("Sports",     "sports.html",    "sports"),
        ("Policing",   "policing.html",  "policing"),
    ]
    regions = [
        ("N. America",     "namerica.html",  "namerica"),
        ("Caribbean",      "caribbean.html", "caribbean"),
        ("S. America",     "samerica.html",  "samerica"),
        ("Africa",         "africa.html",    "africa"),
        ("Europe",         "europe.html",    "europe"),
        ("Asia & Pacific", "asia.html",      "asia"),
    ]
    issue_links = "".join(
        f'<a href="{url}" class="nav-issue{" nav-active" if key == active_issue else ""}">{label}</a>'
        for label, url, key in issues
    )
    issue_links += f'<a href="kids.html" class="nav-kids">{colorize_kids_text("Kids Corner")}</a>'
    region_links = "".join(
        f'<a href="{url}" class="nav-region{" nav-active" if key == active_region else ""}">{label}</a>'
        for label, url, key in regions
    )
    search_link = '<a href="search.html" class="nav-search">&#x1F50D; Search</a>'
    return (
        f'<nav class="site-nav">'
        f'{issue_links}'
        f'<span class="nav-divider">|</span>'
        f'{region_links}'
        f'<span class="nav-divider">|</span>'
        f'{search_link}'
        f'</nav>'
    )


def load_image_cache():
    if os.path.exists(IMAGE_CACHE):
        with open(IMAGE_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_image_cache(cache):
    with open(IMAGE_CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

_pexels_blocked = False  # set once we hit the hourly cap, to stop hammering this build


def pexels_image(query, cache, size="large"):
    # Cache key separates sizes so "large" and "large2x" don't collide
    global _pexels_blocked
    cache_key = query if size == "large" else f"{query}::{size}"
    if cache_key in cache:
        return cache[cache_key]
    if not PEXELS_KEY or _pexels_blocked:
        return ""
    try:
        r = req.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": query, "per_page": 1, "orientation": "landscape"},
            timeout=10
        )
        if r.status_code == 429:
            # hit the hourly rate limit — stop calling, and DON'T cache empties
            # (so these queries retry on the next build instead of being stuck).
            _pexels_blocked = True
            return ""
        if r.status_code != 200:
            return ""  # transient error — don't cache, retry next build
        photos = r.json().get("photos", [])
        src = photos[0]["src"] if photos else {}
        url = src.get(size) or src.get("large2x") or src.get("large") or ""
        cache[cache_key] = url  # cache a real URL OR a genuine "no result" for this query
        return url
    except Exception:
        return ""  # network hiccup — don't cache, retry next build


def pexels_pool(query, cache, size="large", n=15):
    # Fetch a POOL of photos for a query (not just the top one), so many cards
    # sharing a generic query each get a DIFFERENT photo instead of all colliding
    # on one and being pushed to the placeholder. Cached under a "pool::" key.
    global _pexels_blocked
    key = f"pool::{query}::{size}"
    if key in cache:
        return cache[key]
    if not PEXELS_KEY or _pexels_blocked:
        return []
    try:
        r = req.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_KEY},
            params={"query": query, "per_page": n, "orientation": "landscape"},
            timeout=10
        )
        if r.status_code == 429:
            _pexels_blocked = True
            return []
        if r.status_code != 200:
            return []
        urls = []
        for p in r.json().get("photos", []):
            s = p.get("src", {})
            u = s.get(size) or s.get("large2x") or s.get("large") or ""
            if u:
                urls.append(u)
        cache[key] = urls
        return urls
    except Exception:
        return []

# Hosts that serve a "no hotlinking" placeholder image when their photo is
# loaded from another site. We never use their og:image — we generate our own
# instead, so a card never shows that ugly red "blocked" graphic.
HOTLINK_BLOCKED_HOSTS = {
    "voice-online.co.uk",
}


def _img_host(url):
    try:
        return urllib.parse.urlparse(url).netloc.replace("www.", "").lower()
    except Exception:
        return ""


def story_image(story, cache, featured=False, used_images=None):
    # used_images is a set we pass around to track what has already appeared on the page.
    # If an image URL has been used before, we skip it and try a different query.
    #
    # For featured: skip the article's og:image (often grainy) and force a clean
    # high-res Pexels photo. For everything else, prefer og:image (article's own).
    og = story.get("image", "")
    # Never trust an og:image from a host that blocks hotlinking — it would show
    # their placeholder. Drop it and fall through to our own image instead.
    if og and _img_host(og) in HOTLINK_BLOCKED_HOSTS:
        og = ""
    if og and not featured:
        if used_images is not None:
            if og in used_images:
                og = ""  # already on the page — fall through to Pexels
            else:
                used_images.add(og)
                return og
        else:
            return og

    country = story.get("country", "")
    cat     = story.get("category", "").lower()
    title   = story.get("title", "")[:60]

    # Try progressively different queries until we get an image not already used
    queries = [
        f"Black people {cat} {country} {title}" if featured else f"{cat} {country} community people",
        f"Black people {country} {cat}",
        f"{cat} Africa community",
        f"Black community {cat}",
    ]

    # Pull a POOL per query and hand this card the first photo not already on the
    # page — so cards sharing a generic query don't all collapse to the placeholder.
    size = "large2x" if featured else "large"
    for query in queries:
        for url in pexels_pool(query, cache, size=size):
            if url and (used_images is None or url not in used_images):
                if used_images is not None:
                    used_images.add(url)
                return url

    # Last resort: a clean branded placeholder so a card is NEVER blank and never
    # shows a blocked-hotlink placeholder.
    gen = ai_image_url(story)
    if used_images is not None:
        used_images.add(gen)
    return gen

# Theme-tinted backgrounds for the branded placeholder, so cards without a photo
# aren't all identical.
_PH_COLORS = {
    "Debt Trap": "#16352a", "Economy": "#1a3a2a", "Land & Resources": "#2c3a18",
    "Politics & Power": "#283340", "Policing": "#262626", "Health": "#0f3b34",
    "Education": "#22314a", "Culture & Arts": "#382440", "Sport": "#3a2a12",
    "Migration": "#163340", "Tech & Media": "#2a2a3a", "Climate": "#16382c", "World": "#1a3a2a",
}


def ai_image_url(story):
    # No real photo available — return a clean, branded SVG placeholder (data URI)
    # so a card NEVER shows a broken image. (Pollinations, the old fallback, is dead.)
    import math
    color = _PH_COLORS.get(derive_theme(story), "#1a3a2a")
    cx, cy, rad = 450, 205, 72
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = rad if i % 2 == 0 else rad * 0.40
        pts.append(f"{cx + r*math.cos(ang):.0f},{cy + r*math.sin(ang):.0f}")
    star = " ".join(pts)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500" viewBox="0 0 900 500">'
        f'<rect width="900" height="500" fill="{color}"/>'
        f'<polygon points="{star}" fill="#ffffff" opacity="0.92"/>'
        '<text x="450" y="350" text-anchor="middle" font-family="Georgia,serif" '
        'font-size="22" fill="#ffffff" opacity="0.6" letter-spacing="5">BLACK WORLD NEWS</text>'
        '</svg>'
    )
    return "data:image/svg+xml," + urllib.parse.quote(svg)


def load_stories():
    if not os.path.exists(ARCHIVE_FILE):
        print(f"No archive found at {ARCHIVE_FILE}")
        return []
    with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def display_title(story, lang="en"):
    """Return the title in the requested language. Falls back to original if missing."""
    if lang == "en":
        return story.get("title_en") or story.get("title", "")
    return story.get(f"title_{lang}") or story.get("title_en") or story.get("title", "")


def display_summary(story, lang="en"):
    """Return the summary in the requested language. Falls back to English."""
    if lang == "en":
        return story.get("summary", "")
    return story.get(f"summary_{lang}") or story.get("summary", "")


def load_highlights():
    # Curated external highlights for the homepage sidebar.
    # Edit highlights.json by hand. Format: [{title, url, image, caption, source}]
    # Guardrail: every highlight must come from a reputable news organisation
    # (same allowlist as the hero) and use a controlled local image, not a
    # hotlink. We don't drop offenders automatically — we warn loudly at build
    # time so a bad entry gets caught before it ships.
    if not os.path.exists("highlights.json"):
        return []
    try:
        with open("highlights.json", "r", encoding="utf-8") as f:
            items = json.load(f)
    except Exception:
        return []
    try:
        from pick_featured import REPUTABLE, domain
        for h in items:
            d = domain(h.get("url", ""))
            if d and d not in REPUTABLE:
                print(f"  [highlights] WARNING: source not on reputable list: {d}")
            img = h.get("image", "")
            if img and not img.startswith("images/"):
                print(f"  [highlights] WARNING: hotlinked image (localise it): {img[:60]}")
    except Exception:
        pass  # never let the guardrail break the build
    return items


def load_servants():
    # "Servants of the Continent" tribute at the foot of the homepage.
    # Edit servants.json by hand. Format: [{name, years, caption, image, url}]
    # Leave url blank for now — we will write our own articles and link them later.
    if not os.path.exists("servants.json"):
        return []
    try:
        with open("servants.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def load_json_file(filename):
    # Simple, safe loader for the hand-curated kids content files.
    # Returns [] if the file is missing or broken, so the page never crashes.
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def kids_portrait_url(prompt, seed=7):
    # Build a Pollinations image URL for a warm, kid-friendly illustrated portrait.
    # Free, no API key, no hotlinking worries. Same prompt + seed = same picture.
    import urllib.parse  # local import keeps this self-contained
    style = ("warm friendly children's book illustration portrait of "
             f"{prompt}, proud and dignified, colourful, soft lighting, "
             "head and shoulders, simple background")
    encoded = urllib.parse.quote(style, safe="")
    return (f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=400&height=400&nologo=true&seed={seed}")


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


def country_label(country):
    # Clean location tag. Hide the ugly "Other/Global" tag entirely, and never fall
    # back to a globe emoji for unknown countries — just omit it.
    if not country or country == "Other/Global":
        return ""
    flag = COUNTRY_FLAGS.get(country, "")
    return f'<span class="flag-country">{(flag + " " + country).strip()}</span>'


# === Theme-first labels ===================================================
# Every story gets ONE meaningful Theme (no "Other", no "Other/Global"). The
# theme is derived at build time from the title/summary keywords, falling back
# to a map of the existing category. The same config is serialised into the
# search page so the client-side cards stay in sync (single source of truth).
import re as _re_themes

_CAT_THEME = {
    "Employment": "Economy", "Housing": "Economy", "Economy": "Economy",
    "Healthcare": "Health", "Education": "Education", "Politics": "Politics & Power",
    "Immigration": "Migration", "Culture": "Culture & Arts", "Policing": "Policing",
    "Hate Crime": "Policing", "Media Bias": "Tech & Media", "Demographics": "Politics & Power",
}

# Ordered most-distinctive first so generic themes (Politics/Economy) act as catch-alls.
_THEME_KEYWORDS = [
    ("Sport", ["football", "soccer", "fifa", "olympic", "olympics", "athletics", "boxing", "cricket",
               "basketball", "nba", "afcon", "world cup", "marathon", "sprinter", "striker",
               "goalkeeper", "tournament", "medal"]),
    ("Land & Resources", ["mining", "mine", "miner", "oil", "gas", "cobalt", "lithium", "gold",
                          "diamond", "diamonds", "farmland", "farmer", "farming", "agriculture",
                          "resource", "resources", "extraction", "drilling", "pipeline", "timber",
                          "deforestation", "fishing", "cocoa", "copper"]),
    ("Policing", ["police", "policing", "officer", "prison", "prisons", "jail", "jailed", "court",
                 "courts", "arrest", "arrested", "trial", "verdict", "sentenced", "detained",
                 "custody", "murder", "murdered", "killed", "killing", "shooting", "crime",
                 "criminal", "brutality", "hate crime", "lynching", "surveillance", "raid"]),
    ("Migration", ["migrant", "migrants", "migration", "immigration", "immigrant", "refugee",
                   "refugees", "asylum", "border", "borders", "windrush", "deport", "deported",
                   "deportation", "visa", "visas"]),
    ("Health", ["health", "hospital", "hospitals", "disease", "virus", "ebola", "malaria", "hiv",
                "cholera", "pandemic", "epidemic", "vaccine", "clinic", "mortality", "outbreak",
                "mental health", "maternal", "medicine"]),
    ("Education", ["school", "schools", "student", "students", "university", "universities",
                   "education", "teacher", "teachers", "college", "pupil", "pupils", "scholarship",
                   "curriculum", "classroom", "literacy"]),
    ("Climate", ["climate", "environment", "environmental", "flood", "flooding", "cyclone",
                 "hurricane", "drought", "emission", "emissions", "carbon", "wildfire",
                 "conservation", "biodiversity", "pollution", "global warming"]),
    ("Culture & Arts", ["music", "musician", "album", "song", "mixtape", "concert", "festival",
                        "reggae", "afrobeat", "afrobeats", "amapiano", "dancehall", "rapper",
                        "singer", "artist", "band", "film", "movie", "cinema", "nollywood", "actor",
                        "actress", "premiere", "grammy", "carnival", "theatre", "comedy", "fashion",
                        "museum", "heritage", "novel", "gospel", "church", "religion"]),
    # Debt Trap — the debt-as-control mechanism (Walter Rodney lens). Checked BEFORE
    # Economy so debt/IMF/World-Bank stories carry this label, not generic "Economy".
    ("Debt Trap", ["imf", "world bank", "debt", "debts", "loan", "loans", "creditor", "creditors",
                   "repayment", "repayments", "default", "bailout", "austerity",
                   "structural adjustment", "debt relief", "debt servicing", "debt distress",
                   "eurobond", "bondholders", "conditionalities", "balance of payments",
                   "development bank", "odious debt", "indebted"]),
    ("Economy", ["gdp", "inflation", "currency", "cfa", "franc", "trade", "tariff", "tariffs",
                 "investment", "investors", "economy", "economic", "jobs", "unemployment",
                 "employment", "wage", "wages", "bank", "banking", "finance", "financial",
                 "budget", "poverty", "recession", "exports", "imports", "business", "market",
                 "growth"]),
    ("Tech & Media", ["technology", "tech", "startup", "startups", "internet", "digital", "software",
                      "smartphone", "artificial intelligence", "social media", "journalist",
                      "journalism", "press freedom", "broadcaster", "podcast", "streaming", "cyber"]),
    ("Politics & Power", ["election", "elections", "president", "government", "minister", "ministers",
                         "parliament", "coup", "war", "conflict", "protest", "protests", "sanction",
                         "sanctions", "diplomat", "diplomatic", "policy", "vote", "voting", "voters",
                         "leader", "leaders", "military", "summit", "democracy", "regime",
                         "governance", "treaty", "ambassador", "opposition", "rebels", "militia",
                         # broader "justice" stories fold in here (not policing)
                         "human rights", "reparations", "civil rights", "racism", "racist",
                         "discrimination", "equality", "segregation", "apartheid", "slavery",
                         "sovereignty", "justice"]),
]

# Precompute patterns once — reused server-side and shipped to the search page.
_THEME_PATTERNS = [
    (theme, r"\b(" + "|".join(_re_themes.escape(k) for k in kws) + r")\b")
    for theme, kws in _THEME_KEYWORDS
]
_THEME_RULES = [(theme, _re_themes.compile(pat)) for theme, pat in _THEME_PATTERNS]


def derive_theme(story):
    text = ((display_title(story, "en") or "") + " " + (display_summary(story, "en") or "")).lower()
    for theme, pat in _THEME_RULES:
        if pat.search(text):
            return theme
    return _CAT_THEME.get(story.get("category", ""), "World")


def theme_tag(story):
    return f'<span class="theme-tag">{derive_theme(story)}</span>'


# Domains/titles that shouldn't headline the homepage (low-signal noise).
_JUNK_DOMAINS = ("youtube.com", "youtu.be", "wikipedia.org", "linkedin.com", "reddit.com", "tiktok.com")
_JUNK_TITLE = ("reaction", "- youtube", "wikipedia", "official trailer", " trailer", "watch online")
# Job boards / recruitment listings — not news. Matched on DOMAIN/PATH (not title,
# so real news about jobs/recruitment from news sites still gets through).
_JOB_DOMAINS = ("jobs", "jobline", "jobalert", "teachjobs", "jobsite", "vacanc", "careers.", "recruitment")
_JOB_PATHS = ("/careers", "/jobs", "/vacanc", "/job-board", "/job/")
# Words too common across this site to be useful for de-duplicating topics.
_TOPIC_STOP = {
    "the","and","for","with","from","that","this","what","could","amid","face","faces","over",
    "into","your","their","about","after","more","than","will","have","has","are","was","were",
    "new","news","say","says","how","why","who","its","but","not","out","off","one","two",
    "africa","african","black","south","north","people","global","country","countries","nation",
    "nations","world","amp",
}


# Piracy / streaming spam — promo pages for pirated films, TV and live sport that
# the scraper occasionally pulls in. Matched on title and domain.
_STREAM_SPAM_TITLE = (
    "streaming community", "free live streaming", "live streaming of", "watch live stream",
    "official link for movies", "movies and tv series", "watch free online", "full movie online",
    "watch full movie", "hd streaming", "streaming links", "free streaming",
)
_STREAM_SPAM_DOMAIN = (
    "streaming-community", "streamingcommunity", "pialadunia", "freestream", "hd-stream",
    "streamvf", "cuevana", "-streaming.", "livestream", "watchseries", "putlocker", "123movies",
)
# Off-mission signal: the summariser's OWN words when a story has nothing to do with
# Black communities (e.g. "no reference to race or Black communities"). If the analysis
# says it isn't about our subject, it doesn't belong in the feed.
_OFFMISSION_SIGNALS = (
    "no reference to race or black", "no reference to black", "not related to black",
    "no relevance to black", "unrelated to black", "ignoring any specific portrayal",
    "no specific reference to black", "no mention of race or black", "no mention of black communit",
    "no direct connection to black", "not relevant to black communit", "no portrayal or impact on black",
    "does not relate to black", "no connection to black communit", "nothing to do with black",
)


def is_off_mission(story):
    # True for piracy/streaming spam or content the analysis itself flags as having
    # no connection to Black communities. Shared by the display filter (below) and
    # the ingestion gate in dispatch.py so both use one definition.
    u = (story.get("url") or "").lower()
    t = (story.get("title_en") or story.get("title") or "").lower()
    s = " ".join((
        story.get("summary_en") or story.get("summary") or "",
        story.get("narrative_analysis") or "",
    )).lower()
    if any(k in t for k in _STREAM_SPAM_TITLE):
        return True
    if any(k in u for k in _STREAM_SPAM_DOMAIN):
        return True
    if any(k in s for k in _OFFMISSION_SIGNALS):
        return True
    return False


def is_low_quality(story):
    from urllib.parse import urlparse
    u = (story.get("url") or "").lower()
    t = (story.get("title_en") or story.get("title") or "").lower()
    if is_off_mission(story):        # piracy/streaming spam + off-mission content
        return True
    if any(d in u for d in _JUNK_DOMAINS):
        return True
    if any(j in t for j in _JUNK_TITLE):
        return True
    # Job boards / recruitment listings (by domain or URL path) — not news.
    try:
        p = urlparse(u)
        net, path = p.netloc.replace("www.", ""), p.path
    except Exception:
        net, path = "", ""
    if any(k in net for k in _JOB_DOMAINS):
        return True
    if any(path.startswith(seg) for seg in _JOB_PATHS):
        return True
    return False


# Organisational / non-journalism sources — primary documents and reports from
# governments, multilaterals, think tanks and academia. These are valuable but
# they are NOT news; they belong in the separate Reports space, not the feed.
_REPORT_DOMAINS = (
    "imf.org", "worldbank.org", "data.worldbank", "un.org", "undp.org", "unctad.org",
    "unicef.org", "who.int", "oecd.org", "oecd-ilibrary", "wto.org", "afdb.org", "au.int",
    "ecowas.int", "unesco.org", "ilo.org", "fao.org", "wfp.org", "iom.int", "weforum.org",
    "brookings.edu", "chathamhouse.org", "cfr.org", "carnegieendowment.org", "csis.org",
    "odi.org", "gga.org", "issafrica.org", "sipri.org", "reliefweb.int", "ssrn.com",
    "researchgate.net", "academia.edu", "jstor.org", "mckinsey.com", "statista.com",
    "tradingeconomics.com", "g20.org", "elysee.fr",
)
_REPORT_TITLE = (
    "working paper", "policy brief", "communiqué", "communique", "white paper",
    "world economic outlook", "outlook database", "recommended resources", "flagship report",
    "annual report", "fact sheet", "background paper", "discussion paper", "press release",
)


def is_report(story):
    # True for organisational reports / primary documents (route to Reports, not the feed).
    from urllib.parse import urlparse
    u = (story.get("url") or "").lower()
    try:
        net = urlparse(u).netloc.replace("www.", "")
    except Exception:
        net = ""
    if net.endswith(".gov") or ".gov." in net or net.endswith(".int") or net.endswith(".edu") or ".gouv." in net:
        return True
    if any(d in net for d in _REPORT_DOMAINS):
        return True
    if u.endswith(".pdf"):
        return True
    t = (story.get("title_en") or story.get("title") or "").lower()
    if any(k in t for k in _REPORT_TITLE):
        return True
    return False


def report_source_type(story):
    # Who issued it — drives the badge on the Reports page (the cui-bono cue).
    from urllib.parse import urlparse
    u = (story.get("url") or "").lower()
    try:
        net = urlparse(u).netloc.replace("www.", "")
    except Exception:
        net = ""
    multi = ("imf.org", "worldbank", "un.org", "undp", "unctad", "unicef", "who.int", "oecd",
             "wto.org", "afdb", "au.int", "ecowas", "unesco", "ilo.org", "fao.org", "wfp.org",
             "iom.int", "weforum", "reliefweb")
    think = ("brookings", "chathamhouse", "cfr.org", "carnegie", "csis.org", "odi.org", "gga.org",
             "issafrica", "sipri", "mckinsey", "statista", "tradingeconomics")
    if any(d in net for d in multi):
        return "Multilateral"
    if any(d in net for d in think):
        return "Think tank"
    if net.endswith(".edu") or any(d in net for d in ("ssrn", "researchgate", "academia.edu", "jstor")):
        return "Academia"
    if net.endswith(".gov") or ".gov." in net or ".gouv." in net or net.endswith(".int") or "elysee" in net:
        return "Government"
    return "Report"


def _topic_sig(story):
    import re
    t = (display_title(story, "en") or "").lower()
    words = [w for w in re.findall(r"[a-z]+", t) if len(w) >= 3 and w not in _TOPIC_STOP]
    return set(words[:6])


def diverse_latest(stories, n=6):
    # Newest stories, kept VARIED (no near-duplicate topics like a run of IMF pieces,
    # cap 2 per category, drop junk) AND rotated daily so the lineup refreshes every
    # day even between the 2-day news runs (the daily shuffle rebuild reads the date).
    pool = [s for s in stories if not is_low_quality(s)]
    window = pool[:60]                      # recent pool to rotate through
    if window:
        doy = datetime.now().timetuple().tm_yday
        off = (doy * n) % len(window)       # shift the start by ~a page each day
        window = window[off:] + window[:off]
    pool = window + pool[60:]

    picked, sigs, cat = [], [], defaultdict(int)
    for s in pool:
        sig = _topic_sig(s)
        if any(len(sig & ps) >= 2 for ps in sigs):   # shares 2+ key words with one already shown
            continue
        c = derive_theme(s)                           # cap by the VISIBLE theme, not raw category
        if cat[c] >= 2:
            continue
        picked.append(s); sigs.append(sig); cat[c] += 1
        if len(picked) >= n:
            return picked
    for s in pool:                          # backfill if variety rules left us short
        if s not in picked:
            picked.append(s)
            if len(picked) >= n:
                break
    return picked


_ENT_KW = ("music", "album", "song", "mixtape", "concert", "festival", "reggae", "dancehall",
           "afrobeat", "amapiano", "singer", "rapper", "artist", "band", "film", "movie", "cinema",
           "nollywood", "actor", "actress", "series", "premiere", "award", "grammy", "carnival",
           "sumfest", "theatre", "comedy", "fashion", "dj ", "soundtrack")


def _is_entertainment(story):
    t = ((story.get("title_en") or story.get("title") or "") + " " + (story.get("summary") or "")).lower()
    return any(k in t for k in _ENT_KW)


def pick_entertainment(stories, n=3):
    # Newest real entertainment (music/film/arts) Culture stories for the homepage:
    # must have an image, not be junk, varied in topic. Falls back to general Culture
    # if there isn't enough true entertainment.
    import re as _re
    def gather(pred):
        out, sigs = [], []
        for s in stories:
            if s.get("category") != "Culture" or not s.get("image") or is_low_quality(s):
                continue
            title = (s.get("title_en") or s.get("title") or "")
            # skip opinion columns / serialised op-eds (", By Author", "(9)")
            if ", by " in title.lower() or _re.search(r"\(\d+\)", title):
                continue
            if not pred(s):
                continue
            sig = _topic_sig(s)
            if any(len(sig & ps) >= 2 for ps in sigs):
                continue
            out.append(s); sigs.append(sig)
            if len(out) >= n:
                break
        return out

    # Only genuine entertainment — better to show fewer real ones than pad with
    # off-topic Culture pieces (history columns, op-eds).
    return gather(_is_entertainment)[:n]


# Black nations to foreground in sport coverage (World Cup angle). Lowercase for matching.
BLACK_NATIONS = [
    "senegal", "morocco", "ghana", "nigeria", "cameroon", "ivory coast", "cote d'ivoire",
    "côte d'ivoire", "egypt", "tunisia", "algeria", "south africa", "mali", "dr congo",
    "congo", "cape verde", "burkina faso", "guinea", "gabon", "zambia", "angola", "mozambique",
    "jamaica", "haiti", "trinidad", "barbados", "ethiopia", "kenya", "uganda", "tanzania",
]


def pick_sport(stories, n=3):
    # Sport stories for the homepage, foregrounding Black nations / the World Cup.
    # First pass requires a World-Cup or Black-nation angle; then backfills with any sport.
    out, sigs = [], []

    def consider(s, focused):
        if derive_theme(s) != "Sport" or not s.get("image") or is_low_quality(s):
            return False
        title = (s.get("title_en") or s.get("title") or "")
        if ", by " in title.lower() or _re_themes.search(r"\(\d+\)", title):  # skip op-ed columns
            return False
        text = (title + " " + (s.get("summary") or "")).lower()
        if focused and "world cup" not in text and not any(b in text for b in BLACK_NATIONS):
            return False
        sig = _topic_sig(s)
        if any(len(sig & ps) >= 2 for ps in sigs):
            return False
        return sig

    for focused in (True, False):
        for s in stories:
            if len(out) >= n:
                break
            if any(s.get("url") == o.get("url") for o in out):
                continue
            sig = consider(s, focused)
            if sig is False:
                continue
            out.append(s); sigs.append(sig)
        if len(out) >= n:
            break
    return out


# World Cup live ticker — client-side fetch from TheSportsDB's free API (factual
# scores, no scraping). Shows recent results + upcoming fixtures, stars Black
# nations, and hides itself entirely when there are no matches in the window
# (so it disappears off-season). __NATIONS__ is replaced with the JSON list.
_WC_TICKER_JS = """
<script>
(function(){
  var track=document.getElementById('wcTrack'), bar=document.getElementById('wcTicker');
  if(!track) return;
  var KEY='3', LEAGUE='4429', BLACK=__NATIONS__;
  function within(ts,lo,hi){ var d=new Date(ts), diff=(d-Date.now())/86400000; return diff>=lo&&diff<=hi; }
  function mark(name){ var n=(name||'').toLowerCase(); for(var i=0;i<BLACK.length;i++){ if(n.indexOf(BLACK[i])>-1) return '★ '; } return ''; }
  function done(e){ return '<span class="wc-item">'+mark(e.strHomeTeam)+e.strHomeTeam+' <b>'+(e.intHomeScore==null?'':e.intHomeScore)+'–'+(e.intAwayScore==null?'':e.intAwayScore)+'</b> '+e.strAwayTeam+mark(e.strAwayTeam)+'</span>'; }
  function up(e){ var d=new Date(e.strTimestamp), w=d.toLocaleDateString('en-GB',{month:'short',day:'numeric'}); return '<span class="wc-item">'+mark(e.strHomeTeam)+e.strHomeTeam+' v '+e.strAwayTeam+mark(e.strAwayTeam)+' <i>'+w+'</i></span>'; }
  function f(u){ return fetch(u).then(function(r){return r.json();}).catch(function(){return {};}); }
  Promise.all([
    f('https://www.thesportsdb.com/api/v1/json/'+KEY+'/eventspastleague.php?id='+LEAGUE),
    f('https://www.thesportsdb.com/api/v1/json/'+KEY+'/eventsnextleague.php?id='+LEAGUE)
  ]).then(function(res){
    var past=((res[0]||{}).events||[]).filter(function(e){return within(e.strTimestamp,-8,0);}).slice(-12).map(done);
    var next=((res[1]||{}).events||[]).filter(function(e){return within(e.strTimestamp,0,18);}).slice(0,12).map(up);
    var items=past.concat(next);
    if(!items.length) return;
    var inner='<span class="wc-label">WORLD CUP</span>'+items.join('<span class="wc-sep">•</span>');
    track.innerHTML=inner+'<span class="wc-sep">•</span>'+inner;
    bar.hidden=false;
  });
})();
</script>
"""


# Full World Cup fixture list (client-side, TheSportsDB season endpoint). Grouped
# by day, stars Black nations, shows scores for played matches. __NATIONS__ injected.
_WC_SCHEDULE_JS = """
<script>
(function(){
  var box=document.getElementById('wcSchedule');
  if(!box) return;
  var KEY='3', LEAGUE='4429', BLACK=__NATIONS__;
  function mark(name){ var n=(name||'').toLowerCase(); for(var i=0;i<BLACK.length;i++){ if(n.indexOf(BLACK[i])>-1) return '★ '; } return ''; }
  function f(u){ return fetch(u).then(function(r){return r.json();}).catch(function(){return {};}); }
  function render(events){
    if(!events||!events.length){ box.innerHTML='<p class="wc-empty">Fixtures will appear here as they are confirmed.</p>'; return; }
    events.sort(function(a,b){ return (a.strTimestamp||'').localeCompare(b.strTimestamp||''); });
    var html='', lastDay='';
    events.forEach(function(e){
      var d=new Date(e.strTimestamp);
      var day=d.toLocaleDateString('en-GB',{weekday:'long',month:'long',day:'numeric'});
      if(day!==lastDay){ html+='<h3 class="wc-day">'+day+'</h3>'; lastDay=day; }
      var h=e.strHomeTeam||'', a=e.strAwayTeam||'';
      var played=(e.intHomeScore!=null && e.intHomeScore!=='');
      var teams, meta;
      if(played){ teams=mark(h)+h+' <b>'+e.intHomeScore+'–'+e.intAwayScore+'</b> '+a+mark(a); meta=e.strVenue||''; }
      else { var t=d.toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit'}); teams=mark(h)+h+' v '+a+mark(a); meta=t+(e.strVenue?' · '+e.strVenue:''); }
      html+='<div class="wc-match"><span class="wc-teams">'+teams+'</span><span class="wc-meta">'+meta+'</span></div>';
    });
    box.innerHTML=html;
  }
  f('https://www.thesportsdb.com/api/v1/json/'+KEY+'/eventsseason.php?id='+LEAGUE+'&s=2026').then(function(d){
    var ev=(d&&d.events)||[];
    if(ev.length){ render(ev); return; }
    f('https://www.thesportsdb.com/api/v1/json/'+KEY+'/eventsnextleague.php?id='+LEAGUE).then(function(d2){ render((d2&&d2.events)||[]); });
  });
})();
</script>
"""


def story_card(story, featured=False, archive=False, cache=None, used_images=None):
    title   = display_title(story, "en")
    url     = story.get("url", "#")
    country = story.get("country", "Other/Global")
    cat     = story.get("category", "")
    summary = display_summary(story, "en")
    framing = story.get("narrative_framing", "")
    analysis   = story.get("narrative_analysis", "")
    cui_bono   = story.get("cui_bono", "")
    factors    = story.get("structural_factors", [])
    saved   = story.get("saved_at", "")
    flag    = COUNTRY_FLAGS.get(country, "🌍")
    explicit= story.get("explicit_racism", False)
    explicit_tag = '<span class="explicit-tag">EXPLICIT RACISM</span>' if explicit else ""
    og_image = story.get("image", "")

    if archive:
        return f"""
    <div class="card archive-card">
        <div class="card-meta">
            {theme_tag(story)}
            {country_label(country)}
            {framing_badge(framing)}
        </div>
        <h2 class="card-title"><a href="{url}" target="_blank" rel="noopener">{title}</a></h2>
        <p class="card-summary">{summary}</p>
        <div class="card-footer">
            <span class="saved-at">{saved}</span>
            <a href="{url}" class="read-more" target="_blank" rel="noopener">Read →</a>
        </div>
    </div>"""

    img_src = story_image(story, cache or {}, featured=featured, used_images=used_images)
    img_html = (
        f'<a href="{url}" target="_blank" rel="noopener" class="card-img-link"><img class="card-img{"  featured-img" if featured else ""}" src="{img_src}" alt="" loading="lazy"></a>'
        if img_src else ""
    )

    card_class = "card featured" if featured else "card"

    return f"""
    <div class="{card_class}">
        {img_html}
        <div class="card-meta">
            {theme_tag(story)}
            {country_label(country)}
            {framing_badge(framing)}
            {explicit_tag}
        </div>
        <h2 class="card-title"><a href="{url}" target="_blank" rel="noopener">{title}</a></h2>
        <p class="card-summary">{summary}</p>
        {'<p class="narrative-analysis">' + analysis + '</p>' if analysis else ''}
        {'<p class="cui-bono">' + cui_bono + '</p>' if cui_bono and cui_bono.lower() != "unclear." and cui_bono.lower() != "unclear" else ''}
        {factor_tags(factors)}
        <div class="card-footer">
            <span class="saved-at">Collected: {saved}</span>
            <a href="{url}" class="read-more" target="_blank" rel="noopener">Read original →</a>
        </div>
    </div>"""


def kids_card(story):
    title   = display_title(story, "en")
    url     = story.get("url", "#")
    summary = display_summary(story, "en")
    country = story.get("country", "")
    flag  = COUNTRY_FLAGS.get(country, "🌍")
    image = story.get("image", "")
    colors = ["#ff6b6b","#ffd93d","#6bcb77","#4d96ff","#ff9ff3","#f9844a"]
    import hashlib
    color = colors[int(hashlib.md5(url.encode()).hexdigest(), 16) % len(colors)]

    img_html = (
        f'<a href="{url}" target="_blank" rel="noopener" class="kids-img-link"><img class="kids-img" src="{image}" alt="" loading="lazy"></a>'
        if image else
        f'<a href="{url}" target="_blank" rel="noopener" class="kids-img-link"><div class="kids-img-placeholder" style="background:{color}"><span style="font-size:2.5rem">🌍</span></div></a>'
    )

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

    # NEWS ONLY on the homepage feed — organisational reports go to the Reports
    # page, junk (wiki/youtube/etc.) is dropped entirely.
    stories = [s for s in stories if not is_report(s) and not is_low_quality(s)]

    # Find featured story — first check featured.json (set by pick_featured.py),
    # then fall back to keyword match, then most recent
    featured = None
    if os.path.exists("featured.json"):
        with open("featured.json", "r", encoding="utf-8") as _f:
            _pick = json.load(_f)
            featured = next((s for s in stories if s.get("url") == _pick.get("url")), None)
    if not featured:
        keyword = FEATURED_KEYWORD.lower()
        featured = next(
            (s for s in stories if keyword in s.get("title", "").lower() or keyword in s.get("summary", "").lower()),
            stories[0] if stories else None
        )
    remaining = [s for s in stories if s is not featured]
    latest = diverse_latest(remaining, 6)

    # Entertainment & Culture pick for the homepage — newest decent Culture story.
    entertainment = pick_entertainment([s for s in remaining if s not in latest]) or pick_entertainment(remaining)

    # Black Sport pick — our nations at the World Cup and beyond.
    sport = pick_sport(remaining)

    # Group by country
    by_country = defaultdict(list)
    for s in stories:
        by_country[s.get("country", "Other/Global")].append(s)

    # Kids section — Education & Culture stories with Human/Resistant framing
    kids_stories = [s for s in stories if
        s.get("category") in ("Education", "Culture") and
        s.get("narrative_framing") in ("Human", "Resistant")][:6]
    kids_html = "".join(kids_card(s) for s in kids_stories) if kids_stories else "<p style='color:#555;padding:1rem;font-family:Fredoka One,cursive'>More kids stories coming soon!</p>"

    # Track which image URLs have already been used — no duplicates on the page
    used_images = set()

    # Build hero block (BBC-style 3-column lead): featured text | featured image | highlights sidebar
    hero_html = ""
    if featured:
        hero_img = story_image(featured, cache, featured=True, used_images=used_images)
        hero_flag = COUNTRY_FLAGS.get(featured.get("country", ""), "🌍")
        hero_url = featured.get("url", "#")
        hero_img_html = (
            f'<a href="{hero_url}" target="_blank" rel="noopener" class="hero-image-link"><img class="hero-img" src="{hero_img}" alt="" loading="lazy"></a>'
            if hero_img else
            '<div class="hero-img" style="background:#1a3a2a"></div>'
        )

        # Curated highlights from highlights.json (external, hand-picked)
        highlights = load_highlights()
        if highlights:
            highlights_html = "".join(
                f'''<div class="highlight">
                    <a href="{h.get("url","#")}" target="_blank" rel="noopener" class="highlight-img-link"><img class="highlight-img" src="{h.get("image","")}" alt="" loading="lazy" onerror="this.style.display='none'"></a>
                    <h3 class="highlight-title"><a href="{h.get("url","#")}" target="_blank" rel="noopener">{h.get("title","")}</a></h3>
                    <p class="highlight-caption">{h.get("caption","")}</p>
                </div>'''
                for h in highlights[:3]
            )
        else:
            highlights_html = '<p style="color:#888;font-size:0.8rem;font-style:italic">Add curated highlights to highlights.json</p>'

        hero_title   = display_title(featured, "en")
        hero_summary = display_summary(featured, "en")
        hero_html = f'''
        <section class="hero">
            <div class="hero-text">
                <div class="card-meta">
                    {theme_tag(featured)}
                    {country_label(featured.get("country",""))}
                    {framing_badge(featured.get("narrative_framing",""))}
                </div>
                <h2 class="hero-title"><a href="{featured.get("url","#")}" target="_blank" rel="noopener">{hero_title}</a></h2>
                <p class="hero-summary">{hero_summary}</p>
                <div class="hero-meta-bottom">
                    <span class="saved-at">{featured.get("saved_at","")}</span>
                    <a href="{featured.get("url","#")}" class="read-more" target="_blank" rel="noopener">Read original &rarr;</a>
                </div>
            </div>
            <div class="hero-image">{hero_img_html}</div>
            <aside class="hero-sidebar">
                <h4 class="sidebar-label">In Focus</h4>
                {highlights_html}
            </aside>
        </section>'''

    # Build latest grid
    latest_html = "".join(story_card(s, cache=cache, used_images=used_images) for s in latest)

    # Entertainment & Culture homepage row
    entertainment_html = ""
    if entertainment:
        ent_cards = "".join(story_card(s, cache=cache, used_images=used_images) for s in entertainment)
        entertainment_html = f'''
    <div class="container">
        <p class="section-label">Entertainment &amp; Culture</p>
        <div class="card-grid">{ent_cards}</div>
    </div>'''

    # Black Sport homepage row — World Cup angle
    sport_html = ""
    if sport:
        sport_cards = "".join(story_card(s, cache=cache, used_images=used_images) for s in sport)
        sport_html = f'''
    <div class="container">
        <p class="section-label">Black Sport &mdash; At the World Cup <a href="sports.html" style="font-weight:700;color:#e8602c;text-transform:none;letter-spacing:0;margin-left:0.5rem;">All sport &rarr;</a></p>
        <div class="card-grid">{sport_cards}</div>
    </div>'''

    # World Cup live ticker script (nations list injected)
    wc_ticker_js = _WC_TICKER_JS.replace("__NATIONS__", json.dumps(BLACK_NATIONS))

    # Regional teasers — one featured story per region, link to region page
    # Homepage stops here. No more long archive.
    regional_teasers = ""
    for region_id, region in REGION_GROUPS.items():
        region_stories = []
        for country in region["countries"]:
            region_stories.extend(by_country.get(country, []))
        if not region_stories:
            continue
        region_sorted = sorted(region_stories, key=lambda s: s.get("saved_at",""), reverse=True)
        teaser = region_sorted[0]
        teaser_card = story_card(teaser, cache=cache, used_images=used_images)
        count = len(region_stories)
        regional_teasers += f"""
        <div class="region-teaser">
            <div class="region-teaser-header">
                <h3 class="region-teaser-title">{region['label']}</h3>
                <a href="{region_id}.html" class="region-more">All {count} stories &rarr;</a>
            </div>
            {teaser_card}
        </div>"""

    # Servants of the Continent — tribute block at the foot of the homepage.
    # Reads servants.json. Cards link out only when a url is provided (our own articles, later).
    servants = load_servants()
    servants_section = ""
    if servants:
        servant_cards = ""
        for p in servants:
            name    = p.get("name", "")
            years   = p.get("years", "")
            caption = p.get("caption", "")
            image   = p.get("image", "")
            url     = p.get("url", "")
            img_html = (
                f'<img class="servant-img" src="{image}" alt="{name}" loading="lazy" onerror="this.style.display=\'none\'">'
                if image else
                '<div class="servant-img servant-img-empty"></div>'
            )
            inner = f"""{img_html}
                <h3 class="servant-name">{name}</h3>
                <p class="servant-years">{years}</p>
                <p class="servant-caption">{caption}</p>"""
            # Whole card is a link only once we have written the article.
            if url:
                servant_cards += f'<a href="{url}" class="servant-card servant-card-link">{inner}</a>'
            else:
                servant_cards += f'<div class="servant-card">{inner}</div>'
        servants_section = f"""
    <!-- SERVANTS OF THE CONTINENT — tribute, below the news -->
    <div class="container servants">
        <p class="section-label">Servants of the Continent</p>
        <p class="servants-intro">The great ones who carried the Black world forward. Their stories live on.</p>
        <div class="servants-grid">
            {servant_cards}
        </div>
    </div>"""

    # Explainers shelf — our own long-form pieces (empty string if none published).
    explainers_section = explainers_shelf_html()

    # Pull featured story image for Open Graph sharing
    og_image = story_image(featured, cache, featured=True) if featured else ""
    og_title = featured.get("title", "Black World News") if featured else "Black World News"
    og_desc  = featured.get("summary", "News about Black communities around the world.")[:160] if featured else "News about Black communities around the world."

    nav_block = make_two_tier_nav()  # homepage = latest, no issue active

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- Page title — shown in browser tab and Google search results -->
    <title>Black World News | Your World Today</title>

    <!-- Meta description — shown under the link in Google search results -->
    <meta name="description" content="News about Black communities across Africa, the Americas, the Caribbean, and Europe. Updated regularly. Free and open to everyone.">

    <!-- Open Graph — controls how the link looks when shared on WhatsApp, Twitter, Facebook -->
    <meta property="og:type"        content="website">
    <meta property="og:site_name"   content="Black World News">
    <meta property="og:url"         content="https://www.blackworldnews.world/">
    <meta property="og:title"       content="{og_title}">
    <meta property="og:description" content="{og_desc}">
    <meta property="og:image"       content="{og_image}">

    <!-- Twitter card — same idea, but for Twitter/X -->
    <meta name="twitter:card"        content="summary_large_image">
    <meta name="twitter:title"       content="{og_title}">
    <meta name="twitter:description" content="{og_desc}">
    <meta name="twitter:image"       content="{og_image}">

    <!-- Tell Google who we are -->
    <meta name="author" content="Black World News">
    <link rel="canonical" href="https://www.blackworldnews.world/">

    <!-- Browser tab icon -->
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="favicon.svg">
    {PWA_META}

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@400;600&family=Fredoka+One&family=Bagel+Fat+One&display=swap" rel="stylesheet">
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
            padding: 1rem 1.5rem 0.9rem;
            text-align: center;
        }}

        .logo-wrap {{
            display: flex;
            justify-content: center;
            margin-bottom: 0.5rem;
            filter: drop-shadow(0 2px 8px rgba(0,0,0,0.4));
        }}

        .masthead-eyebrow {{
            font-size: 0.65rem;
            letter-spacing: 0.3em;
            text-transform: uppercase;
            color: #8ab89a;
            margin-bottom: 0.3rem;
            font-weight: 600;
        }}

        .masthead h1 {{
            font-family: 'Playfair Display', serif;
            font-size: clamp(1.6rem, 5vw, 2.8rem);
            font-weight: 900;
            color: #ffffff;
            letter-spacing: 0.05em;
            line-height: 1;
        }}

        .masthead-tagline {{
            margin-top: 0.35rem;
            font-size: 0.72rem;
            color: #8ab89a;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }}

        .masthead-meta {{
            margin-top: 0.6rem;
            font-size: 0.75rem;
            color: #6a9a7a;
            border-top: 1px solid #2a5a3a;
            padding-top: 0.5rem;
        }}

        /* NAVIGATION — single row, topics | regions, left-aligned to match breaking bar */
        .site-nav {{
            background: #111;
            border-bottom: 3px solid #1a3a2a;
            display: flex;
            justify-content: flex-start;
            align-items: flex-end;
            flex-wrap: nowrap;
            overflow-x: auto;
            scrollbar-width: none;
            padding-left: 0.7rem;
        }}

        .site-nav::-webkit-scrollbar {{ display: none; }}

        .site-nav a {{
            font-size: 0.72rem;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            color: #888;
            white-space: nowrap;
            font-weight: 600;
            padding: 0.65rem 0.8rem;
            border-bottom: 2px solid transparent;
            transition: color 0.15s, border-color 0.15s;
        }}

        .site-nav a:hover {{
            color: #fff;
            border-bottom-color: #1a3a2a;
        }}

        .site-nav a.nav-active {{
            color: #fff;
            border-bottom-color: #1a3a2a;
        }}

        .nav-divider {{
            color: #444;
            padding: 0 0.25rem;
            font-size: 1rem;
            user-select: none;
            flex-shrink: 0;
        }}

        /* Kids Corner — multi-color glossy balloon letters */
        .site-nav a.nav-kids {{
            font-family: 'Bagel Fat One', cursive;
            font-size: 0.95rem;
            letter-spacing: 0.01em;
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
            transform: translateY(-2px);
        }}

        .site-nav a.nav-kids:hover {{
            border-bottom-color: #ffd93d;
        }}

        {KIDS_LETTER_CSS}

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
        /* "Updated" wrapper transparent so it isn't a white box; the date span inside
           keeps the white chip + dark text from the rule above, so it's readable.
           Whole block hidden on mobile via .updated-block in the media query. */
        .breaking-bar .updated-block {{
            background: none; color: #fff; padding: 0; font-size: inherit; letter-spacing: inherit;
        }}

        /* WORLD CUP TICKER — slim scrolling bar, self-hides off-season */
        .wc-ticker {{ background:#0a0a0a; overflow:hidden; white-space:nowrap; border-bottom:2px solid #1a3a2a; }}
        .wc-track {{ display:inline-block; padding:0.4rem 0; animation:wcscroll 60s linear infinite; will-change:transform; }}
        .wc-ticker:hover .wc-track {{ animation-play-state:paused; }}
        .wc-item {{ color:#fff; font-size:0.8rem; font-weight:600; padding:0 0.55rem; letter-spacing:0.02em; }}
        .wc-item b {{ color:#ffd93d; }}
        .wc-item i {{ color:#8ab89a; font-style:normal; font-size:0.72rem; }}
        .wc-sep {{ color:#555; padding:0 0.2rem; }}
        .wc-label {{ background:#e8602c; color:#fff; font-weight:800; font-size:0.7rem; padding:0.15rem 0.6rem; border-radius:3px; margin:0 0.9rem; letter-spacing:0.08em; }}
        @keyframes wcscroll {{ from {{ transform:translateX(0); }} to {{ transform:translateX(-50%); }} }}

        /* LAYOUT */
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem 1.5rem;
        }}

        .section-label {{
            font-family: 'Playfair Display', serif;
            font-size: 0.85rem;
            font-weight: 700;
            color: #1a3a2a;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            border-bottom: 3px solid #1a3a2a;
            padding-bottom: 0.3rem;
            margin-bottom: 0.85rem;
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
        .card-img-link, .hero-image-link, .highlight-img-link, .kids-img-link {{
            display: block;
            overflow: hidden;
            cursor: pointer;
        }}

        .card-img-link img, .hero-image-link img, .highlight-img-link img, .kids-img-link img {{
            transition: transform 0.4s ease, opacity 0.2s ease;
        }}

        .card-img-link:hover img, .hero-image-link:hover img, .highlight-img-link:hover img, .kids-img-link:hover img {{
            transform: scale(1.03);
            opacity: 0.92;
        }}

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

        /* HERO — 3-column lead block: text | image | highlights sidebar */
        .hero {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 1.5rem;
            display: grid;
            grid-template-columns: 1fr 1.6fr 1fr;
            gap: 1.5rem;
            background: #fff;
            border-bottom: 1px solid #ddd;
            align-items: stretch;
        }}

        .hero-text {{
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            padding-right: 0.5rem;
        }}

        .hero-title {{
            font-family: 'Playfair Display', serif;
            font-size: clamp(1.4rem, 2.2vw, 1.85rem);
            font-weight: 900;
            line-height: 1.15;
            color: #111;
            margin: 0.6rem 0 0.85rem;
        }}

        .hero-title a:hover {{ color: #1a3a2a; }}

        .hero-summary {{
            font-size: 0.95rem;
            color: #444;
            line-height: 1.5;
            margin-bottom: 1rem;
        }}

        .hero-meta-bottom {{
            margin-top: auto;
            padding-top: 0.75rem;
            border-top: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .hero-image {{
            overflow: hidden;
            min-height: 380px;
            display: flex;
        }}

        .hero-img {{
            width: 100%;
            height: 100%;
            min-height: 380px;
            object-fit: cover;
            display: block;
        }}

        /* HIGHLIGHTS SIDEBAR */
        .hero-sidebar {{
            border-left: 1px solid #eee;
            padding-left: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}

        .sidebar-label {{
            font-family: 'Playfair Display', serif;
            font-size: 0.8rem;
            font-weight: 700;
            color: #1a3a2a;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            border-bottom: 3px solid #1a3a2a;
            padding-bottom: 0.35rem;
            margin-bottom: 0.5rem;
        }}

        .highlight {{
            padding-bottom: 0.9rem;
            border-bottom: 1px solid #eee;
        }}

        .highlight:last-child {{
            border-bottom: none;
            padding-bottom: 0;
        }}

        .highlight-img {{
            width: 100%;
            height: 110px;
            object-fit: cover;
            display: block;
            margin-bottom: 0.5rem;
        }}

        .highlight-title {{
            font-family: 'Playfair Display', serif;
            font-size: 0.95rem;
            font-weight: 700;
            line-height: 1.3;
            color: #111;
            margin-bottom: 0.3rem;
        }}

        .highlight-title a:hover {{ color: #1a3a2a; }}

        .highlight-caption {{
            font-size: 0.78rem;
            color: #666;
            line-height: 1.4;
        }}

        @media (max-width: 900px) {{
            .hero {{
                grid-template-columns: 1fr;
                padding: 1rem;
                gap: 1rem;
            }}
            .hero-image {{ min-height: 240px; order: -1; }}
            .hero-img {{ min-height: 240px; height: 240px; }}
            .hero-sidebar {{
                border-left: none;
                border-top: 1px solid #ddd;
                padding-left: 0;
                padding-top: 1rem;
            }}
        }}

        /* CARDS */
        .card {{
            background: #fff;
            border: 1px solid #ddd;
            border-top: 3px solid transparent;
            padding: 0.85rem 1rem;
            margin-bottom: 0.75rem;
            transition: border-top-color 0.2s, box-shadow 0.2s;
        }}

        .card:hover {{
            border-top-color: #1a3a2a;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}

        .card.featured {{
            background: #fff;
            border: 1px solid #bbb;
            border-top: 5px solid #1a3a2a;
            padding: 1.25rem;
            margin-bottom: 1rem;
        }}

        .card-meta {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.4rem;
            margin-bottom: 0.4rem;
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

        .theme-tag {{
            font-size: 0.66rem;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            background: #1a3a2a;
            color: #fff;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            font-weight: 700;
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
            font-size: 1rem;
            font-weight: 700;
            color: #111;
            margin-bottom: 0.35rem;
            line-height: 1.3;
        }}

        .featured .card-title {{
            font-size: 1.25rem;
        }}

        .card-title a:hover {{ color: #1a3a2a; }}

        .card-summary {{
            font-size: 0.85rem;
            color: #444;
            margin-bottom: 0.35rem;
            line-height: 1.45;
        }}

        .narrative-analysis {{
            font-size: 0.85rem;
            color: #666;
            font-style: italic;
            border-left: 3px solid #c5daca;
            padding-left: 0.75rem;
            margin-bottom: 0.6rem;
        }}

        .cui-bono {{
            font-size: 0.72rem;
            color: #aaa;
            font-style: italic;
            padding-left: 0.75rem;
            margin-bottom: 0.5rem;
            letter-spacing: 0.01em;
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
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 0.6rem;
        }}

        .card-grid .card {{ margin-bottom: 0; }}

        /* COUNTRY SECTIONS */
        .country-section {{ margin-bottom: 1.5rem; }}

        .country-heading {{
            font-family: 'Playfair Display', serif;
            font-size: 1.1rem;
            font-weight: 700;
            color: #111;
            margin-bottom: 0.6rem;
            padding-bottom: 0.35rem;
            border-bottom: 2px solid #111;
        }}

        .country-heading .count {{
            font-family: 'Source Sans 3', sans-serif;
            font-size: 0.8rem;
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

        /* REGIONAL TEASERS — grid layout, one column per region */
        .teaser-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.25rem;
            margin-top: 0.5rem;
        }}

        .region-teaser {{
            margin-bottom: 0;
            display: flex;
            flex-direction: column;
        }}

        .region-teaser .card {{
            margin-bottom: 0;
            flex: 1;
        }}

        .region-teaser .card-img {{
            height: 150px;
        }}

        .region-teaser-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            border-bottom: 3px solid #1a3a2a;
            padding-bottom: 0.4rem;
            margin-bottom: 0.75rem;
        }}

        .region-teaser-title {{
            font-family: 'Playfair Display', serif;
            font-size: 1.1rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: #1a3a2a;
        }}

        .region-more {{
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #1a3a2a;
            opacity: 0.85;
            transition: opacity 0.15s;
        }}

        .region-more:hover {{ opacity: 1; text-decoration: underline; }}

        /* FOR THE CHILDREN — portal door */
        .kids-portal {{
            display: block;
            background: #0d1f14;
            text-decoration: none;
            overflow: hidden;
            position: relative;
            padding: 4rem 2rem;
            text-align: center;
            border-top: 6px solid #ffd93d;
            border-bottom: 6px solid #ffd93d;
        }}

        .kids-portal:hover .kids-portal-glow {{
            opacity: 1;
            transform: scale(1.2);
        }}

        .kids-portal:hover .kids-portal-btn {{
            background: #ffd93d;
            color: #111;
            letter-spacing: 0.2em;
        }}

        .kids-portal-glow {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0.8);
            width: 600px;
            height: 600px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255,217,61,0.12) 0%, transparent 70%);
            opacity: 0.6;
            transition: opacity 0.5s, transform 0.5s;
            pointer-events: none;
        }}

        .kids-portal-inner {{
            position: relative;
            z-index: 2;
        }}

        .kids-portal-eyebrow {{
            font-size: 0.7rem;
            letter-spacing: 0.3em;
            text-transform: uppercase;
            color: #ffd93d;
            margin-bottom: 1rem;
            font-weight: 600;
        }}

        .kids-portal-title {{
            font-family: 'Bagel Fat One', cursive;
            font-size: clamp(2.8rem, 8vw, 5.5rem);
            font-weight: 400;
            letter-spacing: 0.02em;
            line-height: 1.05;
            margin-bottom: 1.25rem;
        }}

        /* Portal-sized balloon letters — bigger shadow than the nav-sized ones */
        .kids-portal-title .kids-letter {{
            filter:
                drop-shadow(0 4px 0 var(--deep))
                drop-shadow(0 8px 12px rgba(0,0,0,0.4));
        }}

        .kids-portal-title .kids-space {{
            width: 0.3em;
        }}

        .kids-portal-sub {{
            font-size: 0.9rem;
            color: #8ab89a;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 2rem;
        }}

        .kids-portal-btn {{
            display: inline-block;
            border: 2px solid #ffd93d;
            color: #ffd93d;
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            padding: 0.75rem 2.5rem;
            transition: background 0.2s, color 0.2s, letter-spacing 0.2s;
        }}

        @media (max-width: 768px) {{
            .kids-portal {{ padding: 3rem 1.5rem; }}
            .kids-portal-title {{ font-size: 2.8rem; }}
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
            .logo-wrap img {{ width: 36px; height: 36px; }}

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
            .site-nav {{ display: none; }}
            .breaking-bar {{ font-size: 0.68rem; padding: 0.35rem 0.75rem; }}
            /* Mobile: drop the date entirely — cleaner */
            .updated-block {{ display: none; }}

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
            .mobile-tabs a .tab-icon {{ width: 22px; height: 22px; display: block; }}

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
        <!-- One logo for the whole site: edit logo.svg to change it everywhere. -->
        <img src="logo.svg" alt="Black World News" width="48" height="48">
    </div>
    <p class="masthead-eyebrow">Your World Today</p>
    <div class="masthead-text">
        <h1>BLACK WORLD NEWS</h1>
        <p class="masthead-tagline">"Let my people go, that they may serve me." – Exodus 8:1</p>
    </div>
    <p class="masthead-meta admin-only" style="display:none">Last updated: {now} &nbsp;|&nbsp; {total} stories in archive</p>
</header>

{nav_block}

<div class="breaking-bar"><span>LIVE</span> Monitoring stories important to Black people across the world.<span class="updated-block"> Updated <span id="live-date" class="date-full"></span></span></div>
<div class="wc-ticker" id="wcTicker" hidden><div class="wc-track" id="wcTrack"></div></div>

<main>

    <!-- HERO — featured text | image | highlights sidebar -->
    {hero_html}

    <!-- LATEST -->
    <div class="container" id="latest">
        <p class="section-label">Latest</p>
        <div class="card-grid">{latest_html}</div>
    </div>

    <!-- EXPLAINERS — our own long-form pieces -->
    {explainers_section}

    <!-- ENTERTAINMENT & CULTURE -->
    {entertainment_html}

    <!-- BLACK SPORT — World Cup -->
    {sport_html}

    <!-- FOR THE CHILDREN — portal door -->
    <a href="kids.html" class="kids-portal" aria-label="For the Children">
        <div class="kids-portal-inner">
            <div class="kids-portal-glow"></div>
            <p class="kids-portal-eyebrow">A world of their own</p>
            <h2 class="kids-portal-title">{colorize_kids_text("For the Children")}</h2>
            <p class="kids-portal-sub">A place for our children to grow brave, proud, and strong</p>
            <span class="kids-portal-btn">Enter &#8594;</span>
        </div>
    </a>

    <!-- REGIONAL TEASERS — one story per region, click through to full page -->
    <div class="container">
        <p class="section-label">Around the World</p>
        <div class="teaser-grid">
            {regional_teasers}
        </div>
    </div>
{servants_section}

</main>

<div class="mobile-tabs" style="display:none">
    <a href="index.html">
        <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M3 11l9-7 9 7v9a2 2 0 0 1-2 2h-3v-7h-8v7H5a2 2 0 0 1-2-2v-9z"/>
        </svg>
        Home
    </a>
    <a href="policing.html">
        <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M4 6h16M4 12h16M4 18h10"/>
        </svg>
        Topics
    </a>
    <a href="africa.html">
        <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="9"/>
            <path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>
        </svg>
        World
    </a>
    <a href="search.html">
        <svg class="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="11" cy="11" r="7"/>
            <path d="M21 21l-4.3-4.3"/>
        </svg>
        Search
    </a>
</div>

<footer>
    <p><strong>BLACK WORLD NEWS</strong></p>
    <p style="margin-top:0.5rem">Stories sourced from the open web. AI summaries. Links always go to the original source.</p>
    {social_bar_html()}
    {footer_legal_html()}
</footer>

<script>
  // Always show today's date in the breaking bar — runs in the visitor's browser
  const today = new Date();
  const options = {{ month: 'long', day: 'numeric', year: 'numeric' }};
  const dateEl = document.getElementById('live-date');
  if (dateEl) dateEl.textContent = today.toLocaleDateString('en-US', options);

  // If the URL contains ?admin — show the hidden stats
  // Example: https://www.blackworldnews.world?admin
  if (window.location.search.includes('admin')) {{
    document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'block');
  }}
</script>

{wc_ticker_js}
{PWA_SCRIPT}
{CLOUDFLARE_ANALYTICS}
</body>
</html>"""


def page_shell(title, content, active=""):
    # Shared header, nav and footer used by every page
    nav_links = [
        ("Latest", "/black-world-news/index.html", "latest"),
        ("About", "/black-world-news/about.html", "about"),
        ("Resources", "/black-world-news/resources.html", "resources"),
        ("Reports", "/black-world-news/reports.html", "reports"),
        ("Trends", "/black-world-news/trends.html", "trends"),
        ("Community", "/black-world-news/community.html", "community"),
        ("🌍 Kids", "/black-world-news/index.html#kids", "kids"),
    ]
    nav_html = "".join(
        f'<a href="{url}" class="{"active" if key == active else ""}">{label}</a>'
        for label, url, key in nav_links
    )
    page_descriptions = {
        "About":     "Who we are and how Black World News works. Free, open, and updated regularly.",
        "Resources": "Books, organisations, and films about the Black experience around the world.",
        "Trends":    "Patterns in how Black people are covered in global media. Data from our story archive.",
        "Community": "Share a story tip or add your voice to Black World News.",
    }
    page_desc = page_descriptions.get(title, "Black World News covers stories involving Black communities worldwide.")
    page_url  = f"https://www.blackworldnews.world/{title.lower()}.html"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Black World News</title>
    <meta name="description" content="{page_desc}">
    <meta property="og:type"        content="website">
    <meta property="og:site_name"   content="Black World News">
    <meta property="og:url"         content="{page_url}">
    <meta property="og:title"       content="{title} | Black World News">
    <meta property="og:description" content="{page_desc}">
    <meta name="twitter:card"        content="summary">
    <meta name="twitter:title"       content="{title} | Black World News">
    <meta name="twitter:description" content="{page_desc}">
    <meta name="author" content="Black World News">
    <link rel="canonical" href="{page_url}">
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="favicon.svg">
    {PWA_META}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@400;600&family=Fredoka+One&family=Bagel+Fat+One&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ background: #f2f2f2; color: #111; font-family: 'Source Sans 3', sans-serif; font-size: 16px; line-height: 1.7; }}
        a {{ color: inherit; text-decoration: none; }}

        .masthead {{ background: #1a3a2a; border-bottom: 3px solid #111; padding: 1rem 1.5rem; display: flex; align-items: center; gap: 1rem; }}
        .masthead-logo-link, .masthead-spacer {{ flex: 0 0 50px; display: flex; align-items: center; justify-content: center; }}
        .masthead-logo {{ width: 50px; height: 50px; display: block; }}
        .masthead-center {{ flex: 1; text-align: center; }}
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
    <a href="/black-world-news/index.html" class="masthead-logo-link"><img src="logo.svg" alt="BWN" class="masthead-logo"></a>
    <div class="masthead-center">
        <h1><a href="/black-world-news/index.html">BLACK WORLD NEWS</a></h1>
        <p class="masthead-tagline">What matters to you, today</p>
    </div>
    <div class="masthead-spacer"></div>
</header>
<nav>{nav_html}</nav>

<div class="page-container">
    {content}
</div>

<footer>
    <p><strong>BLACK WORLD NEWS</strong> Your World Today</p>
    <p style="margin-top:0.5rem">Stories sourced from the open web. Links go to original sources.</p>
    {social_bar_html()}
    {footer_legal_html()}
</footer>
{PWA_SCRIPT}
{CLOUDFLARE_ANALYTICS}
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


def build_reports():
    # "The Paper Trail" — organisational reports grouped BY THEME, so the documents
    # stack into evidence. Each card names who issued it (the cui-bono cue). Surface
    # copy stays neutral; the structure carries the argument.
    from urllib.parse import urlparse
    stories = load_stories()
    reports = [s for s in stories if is_report(s) and not is_low_quality(s)]
    reports = sorted(reports, key=lambda s: s.get("saved_at", ""), reverse=True)

    # Extraction-relevant themes lead; the rest follow.
    evidence_order = ["Debt Trap", "Land & Resources", "Economy", "Politics & Power", "Policing",
                      "Migration", "Health", "Education", "Tech & Media", "Culture & Arts",
                      "Sport", "Climate", "World"]
    theme_frame = {
        "Debt Trap": "Loans that arrive with conditions &mdash; and a standing claim on what the country earns.",
        "Land & Resources": "Who holds the minerals, the land and the oil &mdash; and where the profit ends up.",
        "Economy": "Trade, currency and work, on terms largely set elsewhere.",
    }
    badge_cls = {"Multilateral": "st-multi", "Government": "st-gov", "Think tank": "st-think",
                 "Academia": "st-acad", "Report": "st-report"}

    groups = defaultdict(list)
    for s in reports:
        groups[derive_theme(s)].append(s)
    ordered = [t for t in evidence_order if groups.get(t)] + [t for t in groups if t not in evidence_order]

    def card(s):
        title = display_title(s, "en")
        url = s.get("url", "#")
        try:
            net = urlparse(url).netloc.replace("www.", "")
        except Exception:
            net = ""
        stype = report_source_type(s)
        saved = s.get("saved_at", "")
        summary = display_summary(s, "en")
        return f"""
        <div class="rep-card" data-stype="{stype}">
            <div class="rep-top">
                <span class="rep-badge {badge_cls.get(stype, 'st-report')}">{stype} &middot; {net}</span>
                <span class="rep-date">{saved}</span>
            </div>
            <a class="rep-title" href="{url}" target="_blank" rel="noopener">{title}</a>
            <p class="rep-sum">{summary}</p>
        </div>"""

    sections = ""
    for t in ordered:
        items = groups[t]
        frame = theme_frame.get(t, "")
        frame_html = f'<p class="rep-frame">{frame}</p>' if frame else ""
        cards = "".join(card(s) for s in items)
        sections += f"""
        <section class="rep-section">
            <h2 class="rep-h2">{t} <span class="rep-count">{len(items)}</span></h2>
            {frame_html}
            <div class="rep-grid">{cards}</div>
        </section>"""
    if not sections:
        sections = "<p>No reports collected yet.</p>"

    content = f"""
    <style>
        .rep-filters {{ display:flex; flex-wrap:wrap; gap:0.5rem; margin:0 0 2rem; }}
        .rep-chip {{ font-size:0.8rem; padding:0.35rem 0.9rem; border-radius:999px; border:1px solid #ddd; background:#fff; color:#555; cursor:pointer; font-weight:600; }}
        .rep-chip.active {{ background:#1a3a2a; color:#fff; border-color:#1a3a2a; }}
        .rep-section {{ margin-bottom:2.5rem; }}
        .rep-h2 {{ font-family:'Playfair Display',serif; font-size:1.4rem; font-weight:900; color:#1a3a2a; display:flex; align-items:center; gap:0.6rem; }}
        .rep-count {{ font-size:0.8rem; font-weight:700; color:#fff; background:#1a3a2a; border-radius:999px; padding:0.1rem 0.6rem; }}
        .rep-frame {{ font-size:0.95rem; color:#666; font-style:italic; margin:0.3rem 0 1rem; }}
        .rep-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:0.9rem; margin-top:0.5rem; }}
        .rep-card {{ background:#fff; border:1px solid #e5e5e5; border-radius:10px; padding:0.9rem 1.1rem; }}
        .rep-top {{ display:flex; justify-content:space-between; align-items:center; gap:0.5rem; margin-bottom:0.4rem; }}
        .rep-badge {{ font-size:0.64rem; font-weight:700; text-transform:uppercase; letter-spacing:0.03em; padding:0.15rem 0.5rem; border-radius:5px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:72%; }}
        .rep-date {{ font-size:0.72rem; color:#aaa; white-space:nowrap; }}
        .rep-title {{ display:block; font-weight:700; font-size:1rem; color:#111; margin-bottom:0.3rem; line-height:1.35; }}
        .rep-title:hover {{ color:#1a3a2a; text-decoration:underline; }}
        .rep-sum {{ font-size:0.85rem; color:#666; line-height:1.5; }}
        .st-multi {{ background:#FAECE7; color:#712B13; }}
        .st-gov {{ background:#E6F1FB; color:#0C447C; }}
        .st-think {{ background:#EEEDFE; color:#3C3489; }}
        .st-acad {{ background:#E1F5EE; color:#085041; }}
        .st-report {{ background:#F1EFE8; color:#444441; }}
        @media(max-width:768px) {{ .rep-grid {{ grid-template-columns:1fr; }} }}
    </style>
    <h1 class="page-title">The Paper Trail</h1>
    <p class="page-subtitle">The documents that decide how wealth moves between Africa and the world &mdash; written by the institutions that move it. Read together, by theme, a pattern shows.</p>
    <div class="rep-filters" id="repFilters">
        <button class="rep-chip active" data-f="all">All</button>
        <button class="rep-chip" data-f="Government">Governments</button>
        <button class="rep-chip" data-f="Multilateral">Multilaterals</button>
        <button class="rep-chip" data-f="Think tank">Think tanks</button>
        <button class="rep-chip" data-f="Academia">Academia</button>
    </div>
    {sections}
    <script>
      (function(){{
        var chips = document.querySelectorAll('.rep-chip');
        chips.forEach(function(c){{
          c.addEventListener('click', function(){{
            chips.forEach(function(x){{ x.classList.remove('active'); }});
            c.classList.add('active');
            var f = c.getAttribute('data-f');
            document.querySelectorAll('.rep-card').forEach(function(card){{
              card.style.display = (f === 'all' || card.getAttribute('data-stype') === f) ? '' : 'none';
            }});
            document.querySelectorAll('.rep-section').forEach(function(sec){{
              var any = false;
              sec.querySelectorAll('.rep-card').forEach(function(card){{ if (card.style.display !== 'none') any = true; }});
              sec.style.display = any ? '' : 'none';
            }});
          }});
        }});
      }})();
    </script>
    """
    return page_shell("Reports", content, active="reports")


def build_privacy():
    # Simple, honest privacy policy. Required for the Google Play listing.
    # CHANGE the contact email below to whatever address you'll actually use.
    content = """
    <h1 class="page-title">Privacy</h1>
    <p class="page-subtitle">Last updated June 2026. Plain and simple: we do not collect your personal information.</p>

    <h2 class="section-title">The short version</h2>
    <p>Black World News does not ask you to sign up, log in, or hand over any personal details. There are no accounts, no comments, no chat, and no advertising. We do not sell or share data about you, because we do not collect it.</p>

    <h2 class="section-title">What we measure</h2>
    <p>We use Cloudflare Web Analytics to count visits so we know which stories people read. It is privacy first: no cookies, no fingerprinting, and no tracking of you across other websites. The numbers we see are anonymous and added together. We cannot identify you from them.</p>

    <h2 class="section-title">No advertising</h2>
    <p>There are no ads on this site and no advertising networks. Nothing on this page is here to follow you around the web.</p>

    <h2 class="section-title">Children</h2>
    <p>Our children's section collects nothing at all. There are no sign-ups, no comments, no chat, and no data of any kind gathered from young readers. Videos and comics we make live on our own channels, and we link to them clearly.</p>

    <h2 class="section-title">Links to other sites</h2>
    <p>News links always go to the original source. Those websites have their own privacy practices, which we do not control.</p>

    <h2 class="section-title">Our app</h2>
    <p>Our Android app simply loads this website. The same practices on this page apply there too. The app itself requests no special permissions and collects no personal data.</p>

    <h2 class="section-title">Changes</h2>
    <p>If this policy changes, we will update the date at the top of this page.</p>

    <h2 class="section-title">Contact</h2>
    <p>Questions? Email <a href="mailto:hello@blackworldnews.world" style="color:#1a3a2a;font-weight:600;">hello@blackworldnews.world</a>.</p>
    """
    return page_shell("Privacy", content, active="")


def comic_slug_page(slug):
    # The on-disk filename for a single strip's reader page.
    return f"comic-{slug}.html"


def published_comics():
    # Strips marked ready to show on the live shelf. Order: newest first
    # (latest entry in comics.json appears first on the shelf).
    strips = load_json_file("comics.json")
    return list(reversed([s for s in strips if s.get("published")]))


def build_comic_reader(strip):
    # One strip rendered as a vertical webtoon: panels stacked top to bottom,
    # speech rendered as real HTML over each panel from comics.json (editable,
    # translatable, accessible). If a panel image isn't there yet, the panel
    # degrades to a friendly "art coming" placeholder so the page never breaks.
    speakers = strip.get("speakers", {})
    panels_html = ""
    for i, panel in enumerate(strip.get("panels", []), start=1):
        bubbles = ""
        for b in panel.get("bubbles", []):
            who = b.get("speaker", "")
            colour = speakers.get(who, "#1a3a2a")
            anchor = b.get("anchor", "top-left")
            bubbles += (
                f'<div class="bubble b-{anchor}">'
                f'<span class="who" style="color:{colour}">{who}</span>'
                f'{b.get("text","")}</div>'
            )
        alt = panel.get("alt", "").replace('"', "&quot;")
        panels_html += f"""
        <div class="panel">
            <img src="{panel.get('img','')}" alt="{alt}" loading="lazy"
                 onerror="this.closest('.panel').classList.add('panel-pending')">
            <div class="pending-note">Panel {i}<br>art coming</div>
            {bubbles}
        </div>"""

    title = strip.get("title", "Comic")
    blurb = strip.get("blurb", "")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Black World News</title>
    <meta name="description" content="{blurb}">
    <link rel="canonical" href="https://www.blackworldnews.world/{comic_slug_page(strip.get('slug',''))}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{blurb}">
    <meta property="og:image" content="https://www.blackworldnews.world/{strip.get('cover','')}">
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="favicon.svg">
    {PWA_META}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@900&family=Fredoka+One&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
        body{{background:#fffdf5;color:#222;font-family:'Source Sans 3',sans-serif;font-size:18px;line-height:1.6;}}
        a{{color:inherit;text-decoration:none;}}
        .masthead{{background:#1a3a2a;padding:1rem 1.5rem;display:flex;align-items:center;gap:1rem;justify-content:center;}}
        .masthead img{{width:50px;height:50px;}}
        .masthead h1{{font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:900;color:#fff;letter-spacing:0.04em;}}
        .reader-hero{{text-align:center;padding:2.2rem 1.5rem 1rem;}}
        .reader-hero h2{{font-family:'Fredoka One',cursive;color:#1a3a2a;font-size:clamp(1.6rem,6vw,2.6rem);line-height:1.15;}}
        .reader-hero p{{color:#666;max-width:600px;margin:0.7rem auto 0;}}
        .strip{{max-width:760px;margin:1.5rem auto;padding:0 1rem;}}
        .panel{{position:relative;max-width:720px;margin:0 auto 1.1rem;border-radius:16px;overflow:hidden;
                background:#fff;box-shadow:0 6px 20px rgba(0,0,0,0.12);}}
        .panel img{{display:block;width:100%;height:auto;}}
        .panel-pending{{min-height:380px;display:flex;align-items:center;justify-content:center;
                background:repeating-linear-gradient(45deg,#fff,#fff 14px,#fdf6e3 14px,#fdf6e3 28px);}}
        .panel-pending img{{display:none;}}
        .pending-note{{display:none;text-align:center;color:#b08900;font-family:'Fredoka One',cursive;
                font-size:1.3rem;line-height:1.4;}}
        .panel-pending .pending-note{{display:block;}}
        .bubble{{position:absolute;max-width:46%;background:rgba(255,255,255,0.96);border-radius:18px;
                padding:0.5rem 0.8rem;box-shadow:0 4px 14px rgba(0,0,0,0.20);
                font-size:clamp(0.82rem,2.7vw,1.05rem);line-height:1.3;}}
        .bubble .who{{display:block;font-family:'Fredoka One',cursive;font-size:0.72em;margin-bottom:0.05rem;}}
        .b-top-left{{top:4%;left:4%;}}
        .b-top-right{{top:4%;right:4%;}}
        .b-bottom-left{{bottom:4%;left:4%;}}
        .b-bottom-right{{bottom:4%;right:4%;}}
        .b-top-center{{top:4%;left:50%;transform:translateX(-50%);max-width:80%;text-align:center;}}
        .b-bottom-center{{bottom:4%;left:50%;transform:translateX(-50%);max-width:80%;text-align:center;}}
        .reader-end{{text-align:center;padding:1.5rem;}}
        .back-home{{display:inline-block;margin:0.4rem;background:#1a3a2a;color:#fff;padding:0.6rem 1.4rem;border-radius:999px;font-weight:700;}}
        .kids-safe-footer{{background:#fff;border-top:3px dashed #ffe9a8;text-align:center;padding:2.5rem 1.5rem;margin-top:1rem;}}
        .kids-safe-footer p{{max-width:600px;margin:0.4rem auto;color:#666;}}
    </style>
</head>
<body>
<header class="masthead">
    <a href="index.html"><img src="logo.svg" alt="Black World News"></a>
    <h1>Black World News</h1>
</header>

<section class="reader-hero">
    <h2>{title}</h2>
    <p>{blurb}</p>
</section>

<section class="strip">{panels_html}
</section>

<section class="reader-end">
    <p>&#11088;</p>
    <a href="comics.html" class="back-home">&larr; More comics</a>
    <a href="kids.html" class="back-home">BWN Kids</a>
</section>

<footer class="kids-safe-footer">
    <p>&#10084;&#65039;</p>
    <p>This page is just for you. No comments, no chats, no sign-ups. We never collect anything about you.</p>
</footer>
{PWA_SCRIPT}
{CLOUDFLARE_ANALYTICS}
</body>
</html>"""


def build_comics():
    # BWN Kids — Comics shelf. Shows published strips as cover cards; if none are
    # published yet, falls back to the warm "coming soon" hero. Same kid-safe world
    # as kids.html (no social bar, no data collection).
    # Cast preview is pulled from kids_figures.json so it stays in sync.
    figures = load_json_file("kids_figures.json")
    cast = ""
    for f in figures:
        cast += f"""
        <div class="cast-card">
            <div class="cast-face" style="background:{f.get('color','#1a3a2a')}">{f.get('initials','')}</div>
            <p class="cast-name">{f.get('name','')}</p>
            <p class="cast-place">{f.get('place','')}</p>
        </div>"""
    # plus one original guide character who walks young readers through the history
    cast += """
        <div class="cast-card">
            <div class="cast-face" style="background:#e8602c">KA</div>
            <p class="cast-name">Kojo &amp; Ama</p>
            <p class="cast-place">Our guides</p>
        </div>"""

    strips = published_comics()
    if strips:
        shelf = ""
        for s in strips:
            shelf += f"""
        <a class="shelf-card" href="{comic_slug_page(s.get('slug',''))}">
            <div class="shelf-cover">
                <img src="{s.get('cover','')}" alt="{s.get('title','').replace('"','&quot;')}" loading="lazy"
                     onerror="this.closest('.shelf-cover').classList.add('cover-pending')">
                <span class="cover-pending-note">&#11088;</span>
            </div>
            <p class="shelf-title">{s.get('title','')}</p>
            <p class="shelf-blurb">{s.get('blurb','')}</p>
        </a>"""
        hero = f"""
<section class="comics-hero">
    <h1 class="comics-title">{colorize_kids_text("Comics")}</h1>
    <p class="comics-sub">Real history and big ideas, told in pictures. Stories of brave people from all around the Black world, made just for our children.</p>
</section>
<section class="shelf">
    <div class="shelf-grid">{shelf}
    </div>
</section>"""
    else:
        hero = f"""
<section class="comics-hero">
    <h1 class="comics-title">{colorize_kids_text("Comics")}</h1>
    <p class="comics-sub">Real history and big ideas, told in pictures. Stories of brave people from all around the Black world, made just for our children. Our first comic is on its way.</p>
    <span class="soon-badge">First strip coming soon</span>
</section>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comics | Black World News</title>
    <meta name="description" content="Comics for our children: real history and big ideas, told in pictures. Coming soon.">
    <link rel="canonical" href="https://www.blackworldnews.world/comics.html">
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="favicon.svg">
    {PWA_META}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@900&family=Bagel+Fat+One&family=Fredoka+One&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
        body{{background:#fffdf5;color:#222;font-family:'Source Sans 3',sans-serif;font-size:18px;line-height:1.6;}}
        a{{color:inherit;text-decoration:none;}}
        {KIDS_LETTER_CSS}
        .masthead{{background:#1a3a2a;padding:1rem 1.5rem;display:flex;align-items:center;gap:1rem;justify-content:center;}}
        .masthead img{{width:50px;height:50px;}}
        .masthead h1{{font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:900;color:#fff;letter-spacing:0.04em;}}
        .comics-hero{{text-align:center;padding:3rem 1.5rem 1.5rem;}}
        .comics-title{{font-family:'Bagel Fat One',cursive;font-size:clamp(2.5rem,9vw,5rem);line-height:1.1;}}
        .comics-title .kids-letter{{filter:drop-shadow(0 3px 0 var(--deep)) drop-shadow(0 6px 8px rgba(0,0,0,0.2));}}
        .comics-title .kids-space{{width:0.3em;}}
        .comics-sub{{font-size:1.15rem;color:#555;max-width:620px;margin:1rem auto 0;}}
        .soon-badge{{display:inline-block;margin-top:1.4rem;background:#e8602c;color:#fff;font-weight:700;padding:0.5rem 1.3rem;border-radius:999px;}}
        .shelf{{max-width:880px;margin:0.5rem auto 1rem;padding:0 1.5rem;}}
        .shelf-grid{{display:flex;gap:1.4rem;justify-content:center;flex-wrap:wrap;}}
        .shelf-card{{display:block;width:240px;background:#fff;border-radius:16px;overflow:hidden;
                box-shadow:0 6px 20px rgba(0,0,0,0.12);transition:transform .15s ease;}}
        .shelf-card:hover{{transform:translateY(-4px);}}
        .shelf-cover{{position:relative;aspect-ratio:4/5;background:repeating-linear-gradient(45deg,#fff,#fff 14px,#fdf6e3 14px,#fdf6e3 28px);
                display:flex;align-items:center;justify-content:center;}}
        .shelf-cover img{{width:100%;height:100%;object-fit:cover;}}
        .cover-pending-note{{display:none;font-size:2.6rem;}}
        .cover-pending img{{display:none;}}
        .cover-pending .cover-pending-note{{display:block;}}
        .shelf-title{{font-family:'Fredoka One',cursive;color:#1a3a2a;padding:0.7rem 0.9rem 0.2rem;font-size:1.05rem;line-height:1.2;}}
        .shelf-blurb{{padding:0 0.9rem 0.9rem;color:#777;font-size:0.85rem;line-height:1.35;}}
        .cast{{max-width:760px;margin:2.5rem auto;padding:0 1.5rem;}}
        .cast h2{{text-align:center;font-family:'Fredoka One',cursive;color:#1a3a2a;margin-bottom:1.2rem;}}
        .cast-grid{{display:flex;gap:1.2rem;justify-content:center;flex-wrap:wrap;}}
        .cast-card{{text-align:center;width:130px;}}
        .cast-face{{width:84px;height:84px;border-radius:50%;margin:0 auto 0.5rem;display:flex;align-items:center;justify-content:center;color:#fff;font-family:'Fredoka One',cursive;font-size:1.5rem;box-shadow:0 4px 12px rgba(0,0,0,0.15);}}
        .cast-name{{font-weight:600;font-size:0.92rem;}}
        .cast-place{{font-size:0.78rem;color:#888;margin-top:0.1rem;}}
        .kids-safe-footer{{background:#fff;border-top:3px dashed #ffe9a8;text-align:center;padding:2.5rem 1.5rem;margin-top:2rem;}}
        .kids-safe-footer p{{max-width:600px;margin:0.4rem auto;color:#666;}}
        .back-home{{display:inline-block;margin-top:1rem;background:#1a3a2a;color:#fff;padding:0.6rem 1.4rem;border-radius:999px;font-weight:700;}}
    </style>
</head>
<body>
<header class="masthead">
    <a href="index.html"><img src="logo.svg" alt="Black World News"></a>
    <h1>Black World News</h1>
</header>

{hero}

<section class="cast">
    <h2>Meet the cast</h2>
    <div class="cast-grid">{cast}</div>
</section>

<footer class="kids-safe-footer">
    <p>&#10084;&#65039;</p>
    <p>This page is just for you. No comments, no chats, no sign-ups. We never collect anything about you.</p>
    <a href="kids.html" class="back-home">&larr; Back to BWN Kids</a>
</footer>
{PWA_SCRIPT}
{CLOUDFLARE_ANALYTICS}
</body>
</html>"""


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
        ("Institute of the Black World 21st Century", "https://ibw21.org", "Research and advocacy grounded in the long tradition of Black freedom thought."),
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
    country_counts  = Counter(s.get("country", "") for s in stories if s.get("country") and s.get("country") != "Other/Global")
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


def build_kids():
    # "For the Children" — a safe, colourful room for young children.
    # All content is hand-curated in the kids_*.json files. No live news, no AI here.
    # One simple reading level for the young; older readers use the main site.
    figures      = load_json_file("kids_figures.json")
    countries    = load_json_file("kids_countries.json")
    vocab        = load_json_file("kids_vocab.json")
    news         = load_json_file("kids_news.json")
    affirmations = load_json_file("kids_affirmations.json")

    title_balloon = colorize_kids_text("For the Children")

    # --- Module: Say It Out Loud (affirmations as a tap-through deck) ---
    # One big card with the rest stacked behind it. Tapping brings the next
    # affirmation forward. Renders the first card server-side so it still shows
    # one affirmation if JavaScript is off.
    affirm_json = json.dumps(affirmations)
    first = affirmations[0] if affirmations else {"text": "", "color": "#1a3a2a"}
    affirm_deck = f"""
        <div class="affirm-deck" id="affirmDeck" tabindex="0" role="button" aria-label="Tap the card for another good thing about you">
            <div class="affirm-back affirm-back2"></div>
            <div class="affirm-back affirm-back1"></div>
            <div class="affirm-top" id="affirmTop" style="background:{first.get("color","#1a3a2a")}">
                <span class="affirm-text" id="affirmText">{first.get("text","")}</span>
            </div>
        </div>
        <p class="affirm-hint">Tap the card for another &#10024;</p>"""

    # --- Module: Meet Someone Special (historical figures) ---
    figure_cards = ""
    for f in figures:
        initials = f.get("initials", "")
        color    = f.get("color", "#1a3a2a")
        image    = f.get("image", "")
        # A figure shows a local photo if one is set; otherwise a designed initials
        # medallion (used where no freely-licensed portrait exists, e.g. Yaa Asantewaa).
        # NOTE: live Pollinations generation was dropped — the service now returns
        # HTTP 402 (paywalled), so it only produced broken images.
        # The medallion is always present; if a photo fails to load, onerror reveals it.
        circle = f'<div class="kid-portrait kid-portrait-initials" style="background-color:{color}{{disp}}">{initials}</div>'
        if image:
            portrait = (
                f'<img class="kid-portrait" src="{image}" alt="{f.get("name","")}" loading="lazy" '
                f'onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'">'
                + circle.format(disp=";display:none")
            )
        else:
            portrait = circle.format(disp="")
        figure_cards += f"""
        <div class="kid-card">
            {portrait}
            <h3 class="kid-card-name">{f.get("name","")}</h3>
            <p class="kid-card-place">{f.get("flag","")} {f.get("place","")}</p>
            <p class="kid-text">{f.get("little","")}</p>
            <p class="kid-quote">&ldquo;{f.get("quote","")}&rdquo;</p>
        </div>"""

    # --- Module: A Place to Know (countries) ---
    country_cards = ""
    for c in countries:
        color = c.get("color", "#1a3a2a")
        image = c.get("image", "")
        code  = c.get("code", "")
        name  = c.get("name", "")
        if image:
            # An explicit photo banner takes priority if one is ever set.
            banner = f'<img class="kid-place-img" src="{image}" alt="{name}" loading="lazy">'
        elif code:
            # Real flag image (renders on every device, unlike flag emoji). If the
            # CDN ever fails, onerror falls back to the emoji inside the colour box.
            banner = (
                f'<div class="kid-place-img kid-place-flag" style="background-color:{color}">'
                f'<img class="kid-flag-img" src="https://flagcdn.com/{code}.svg" '
                f'alt="Flag of {name}" loading="lazy" '
                f'onerror="this.style.display=\'none\';this.parentElement.classList.add(\'flag-fallback\')">'
                f'<span class="flag-emoji">{c.get("flag","")}</span></div>'
            )
        else:
            banner = f'<div class="kid-place-img kid-place-flag" style="background-color:{color}">{c.get("flag","")}</div>'
        country_cards += f"""
        <div class="kid-card kid-place-card">
            {banner}
            <h3 class="kid-card-name">{c.get("flag","")} {c.get("name","")}</h3>
            <span class="kid-place-accent" style="background-color:{color}"></span>
            <p class="kid-text">{c.get("little","")}</p>
            <p class="kid-oneline"><strong>Did you know?</strong> {c.get("oneThing","")}</p>
            <p class="kid-oneline"><strong>A word from here:</strong> {c.get("oneWord","")}</p>
        </div>"""

    # --- Module: From the Big News (rewritten for kids) ---
    news_cards = ""
    for n in news:
        news_cards += f"""
        <div class="kid-news-card">
            <h3 class="kid-card-name">{n.get("title","")}</h3>
            <p class="kid-text">{n.get("text","")}</p>
        </div>"""

    # --- Module: Learn a Word ---
    vocab_cards = ""
    for v in vocab:
        vocab_cards += f"""
        <div class="kid-word-card">
            <p class="kid-word">{v.get("word","")}</p>
            <p class="kid-word-say">say it: {v.get("say","")}</p>
            <p class="kid-word-means">{v.get("means","")}</p>
            <p class="kid-word-from">{v.get("flag","")} {v.get("lang","")}, from {v.get("place","")}</p>
            <p class="kid-word-example">&ldquo;{v.get("example","")}&rdquo;</p>
        </div>"""

    # --- Module: Quiz Time (built from the curated content, JS only) ---
    # Three simple questions whose answers live on this very page.
    quiz = [
        {
            "q": "Where was Marcus Garvey born?",
            "options": ["Jamaica", "Canada", "Australia"],
            "answer": 0,
        },
        {
            "q": "Which country was the first where free Black people ruled themselves?",
            "options": ["Haiti", "Germany", "Japan"],
            "answer": 0,
        },
        {
            "q": "What does the word Akwaaba mean?",
            "options": ["goodbye", "welcome", "run"],
            "answer": 1,
        },
    ]
    quiz_json = json.dumps(quiz)

    # --- BWN Kids launchpad: two doors → Comics and our videos (YouTube/TikTok) ---
    # Driven entirely by the COMICS_URL / YOUTUBE_URL / TIKTOK_URL constants up top.
    # An unset destination renders as a calm, non-clickable "Coming soon" door, so
    # the portal looks finished long before the content exists.
    def _kids_door(href, icon, title, sub, klass, chips=""):
        if href:
            tgt = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
            return (f'<a class="kids-door {klass}" href="{href}"{tgt}>'
                    f'<span class="kids-door-icon">{icon}</span>'
                    f'<span class="kids-door-title">{title}</span>'
                    f'<span class="kids-door-sub">{sub}</span>{chips}</a>')
        return (f'<div class="kids-door {klass} kids-door-soon" aria-disabled="true">'
                f'<span class="kids-door-icon">{icon}</span>'
                f'<span class="kids-door-title">{title}</span>'
                f'<span class="kids-door-sub">Coming soon</span></div>')

    comics_door = _kids_door(COMICS_URL, "&#128214;", "Comics",
                             "Our stories, told in pictures", "kids-door-comics")
    chips = ""
    if YOUTUBE_URL:
        chips += '<span class="kids-chip">YouTube</span>'
    if TIKTOK_URL:
        chips += '<span class="kids-chip">TikTok</span>'
    if chips:
        chips = f'<span class="kids-chips">{chips}</span>'
    watch_door = _kids_door(YOUTUBE_URL or TIKTOK_URL, "&#9654;&#65039;", "Watch &amp; Learn",
                            "Videos about our world", "kids-door-watch", chips)

    nav_html = make_two_tier_nav()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>For the Children | Black World News</title>
    <meta name="description" content="A safe, colourful place for young children to learn about the Black world. Stories, people, places, and words for our little ones.">
    <link rel="canonical" href="https://www.blackworldnews.world/kids.html">
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="favicon.svg">
    {PWA_META}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Bagel+Fat+One&family=Fredoka+One&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
        body{{background:#fff;color:#283028;font-family:'Nunito',sans-serif;font-size:18px;line-height:1.6;font-weight:600;}}
        a{{color:inherit;text-decoration:none;}}

        /* Masthead — same green DNA as the rest of the site */
        .masthead{{background:#1a3a2a;padding:1rem 1.5rem;display:flex;align-items:center;gap:1rem;}}
        .masthead-logo-link,.masthead-spacer{{flex:0 0 50px;display:flex;align-items:center;justify-content:center;}}
        .masthead-logo{{width:50px;height:50px;display:block;}}
        .masthead-center{{flex:1;text-align:center;}}
        .masthead h1{{font-family:'Playfair Display',serif;font-size:1.6rem;font-weight:900;color:#fff;letter-spacing:0.04em;}}
        .masthead h1 a:hover{{color:#c8d8c0;}}
        .masthead-tagline{{font-size:0.65rem;color:#8ab89a;letter-spacing:0.1em;text-transform:uppercase;margin-top:0.2rem;}}
        .site-nav{{background:#0a0a0a;border-bottom:3px solid #1a3a2a;display:flex;justify-content:flex-start;align-items:flex-end;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;padding-left:0.7rem;}}
        .site-nav::-webkit-scrollbar{{display:none;}}
        .site-nav a{{font-size:0.72rem;font-weight:700;letter-spacing:0.07em;text-transform:uppercase;white-space:nowrap;padding:0.65rem 0.8rem;border-bottom:2px solid transparent;transition:color 0.15s,border-color 0.15s;color:#888;}}
        .site-nav a:hover{{color:#fff;border-bottom-color:#1a3a2a;}}
        .site-nav a.nav-kids{{font-family:'Bagel Fat One',cursive;font-size:0.95rem;letter-spacing:0.01em;padding-top:0.5rem;padding-bottom:0.5rem;transform:translateY(-2px);}}
        .site-nav a.nav-kids:hover{{border-bottom-color:#ffd93d;}}
        {KIDS_LETTER_CSS}
        .nav-divider{{color:#444;padding:0 0.25rem;font-size:1rem;user-select:none;flex-shrink:0;}}

        /* Hero */
        .kids-hero{{text-align:center;padding:2.5rem 1.5rem 1.5rem;background:linear-gradient(180deg,#fffdf5 0%,#ffffff 100%);}}
        .kids-hero-title{{font-family:'Bagel Fat One',cursive;font-size:clamp(2.2rem,8vw,4.5rem);line-height:1.1;margin-bottom:0.5rem;}}
        .kids-hero-title .kids-letter{{filter:drop-shadow(0 3px 0 var(--deep)) drop-shadow(0 6px 8px rgba(0,0,0,0.2));}}
        .kids-hero-title .kids-space{{width:0.3em;}}
        .kids-hero-sub{{font-size:1.15rem;font-weight:700;color:#5e6b5e;line-height:1.5;max-width:600px;margin:0 auto;}}

        /* Layout */
        .kids-main{{max-width:1100px;margin:0 auto;padding:1rem 1.5rem 4rem;}}
        .kids-section{{margin-top:3.5rem;}}
        .kids-section-title{{font-family:'Fredoka One',cursive;font-size:clamp(1.7rem,5vw,2.3rem);color:#1a3a2a;margin-bottom:0.2rem;text-align:center;line-height:1.15;}}
        .kids-section-title::after{{content:"";display:block;width:64px;height:5px;border-radius:999px;background:linear-gradient(90deg,#e8602c,#ffd93d);margin:0.55rem auto 0;}}
        .kids-section-sub{{font-size:1.05rem;font-weight:700;color:#9aa39a;text-align:center;max-width:560px;margin:0 auto 1.8rem;}}
        .kids-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.5rem;}}

        /* BWN Kids launchpad — the two doors (Comics + Watch & Learn) */
        .kids-portals{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1.25rem;}}
        .kids-door{{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:0.4rem;padding:2.5rem 1.5rem;border-radius:26px;color:#fff;box-shadow:0 6px 20px rgba(0,0,0,0.16);transition:transform 0.15s,box-shadow 0.15s;min-height:200px;}}
        .kids-door:hover{{transform:translateY(-4px);box-shadow:0 12px 28px rgba(0,0,0,0.22);}}
        .kids-door-comics{{background:linear-gradient(150deg,#e8602c,#c8341a);}}
        .kids-door-watch{{background:linear-gradient(150deg,#7a3cc0,#4a2398);}}
        .kids-door-icon{{font-size:3rem;line-height:1;}}
        .kids-door-title{{font-family:'Bagel Fat One',cursive;font-size:1.8rem;}}
        .kids-door-sub{{font-size:1rem;opacity:0.95;}}
        .kids-door-soon{{background:#cfcabe;color:#5a554a;box-shadow:none;cursor:default;}}
        .kids-door-soon:hover{{transform:none;box-shadow:none;}}
        .kids-chips{{display:flex;gap:0.5rem;justify-content:center;flex-wrap:wrap;margin-top:0.3rem;}}
        .kids-chip{{background:rgba(255,255,255,0.22);border-radius:999px;padding:0.3rem 0.9rem;font-size:0.8rem;font-weight:700;}}

        /* Say It Out Loud — one big card, the rest stacked behind (tap to advance) */
        .affirm-deck{{position:relative;max-width:430px;height:230px;margin:0 auto;cursor:pointer;
                -webkit-tap-highlight-color:transparent;}}
        .affirm-deck:focus{{outline:none;}}
        .affirm-back,.affirm-top{{position:absolute;inset:0;border-radius:24px;}}
        .affirm-back{{box-shadow:0 6px 16px rgba(0,0,0,0.10);}}
        .affirm-back1{{background:#ece4d0;transform:rotate(-4deg) translateY(9px) scale(0.97);}}
        .affirm-back2{{background:#e1d8c2;transform:rotate(4deg) translateY(15px) scale(0.94);}}
        .affirm-top{{display:flex;align-items:center;justify-content:center;text-align:center;padding:2rem 1.6rem;
                box-shadow:0 14px 30px rgba(0,0,0,0.17);
                transition:transform 0.28s cubic-bezier(.2,.7,.2,1),opacity 0.28s ease;}}
        .affirm-top.swap{{transform:translateY(-26px) rotate(-6deg) scale(0.92);opacity:0;}}
        .affirm-deck:focus-visible .affirm-top{{box-shadow:0 0 0 4px #ffd93d,0 14px 30px rgba(0,0,0,0.17);}}
        .affirm-text{{font-family:'Fredoka One',cursive;font-size:clamp(1.5rem,5.5vw,2.1rem);line-height:1.25;color:#fff;text-shadow:0 2px 4px rgba(0,0,0,0.20);}}
        .affirm-hint{{text-align:center;color:#9aa39a;font-weight:700;margin-top:1.5rem;}}

        /* Cards */
        .kid-card{{background:#fff;border:none;border-radius:22px;padding:1.5rem;text-align:center;box-shadow:0 8px 24px rgba(0,0,0,0.08);transition:transform 0.2s ease,box-shadow 0.2s ease;}}
        .kid-card:hover{{transform:translateY(-6px);box-shadow:0 18px 38px rgba(0,0,0,0.14);}}
        .kid-portrait{{width:120px;height:120px;border-radius:50%;object-fit:cover;display:block;margin:0 auto 1rem;border:4px solid #fff;box-shadow:0 0 0 3px #1a3a2a;}}
        .kid-portrait-initials{{display:flex;align-items:center;justify-content:center;font-family:'Bagel Fat One',cursive;font-size:2.7rem;color:#fff;text-shadow:0 2px 4px rgba(0,0,0,0.22);
                background-image:radial-gradient(circle at 32% 26%,rgba(255,255,255,0.40),rgba(255,255,255,0) 58%),linear-gradient(150deg,rgba(255,255,255,0.10),rgba(0,0,0,0.20));}}
        .kid-card:hover .kid-portrait-initials{{transform:scale(1.04);transition:transform 0.2s ease;}}
        .kid-card-name{{font-family:'Fredoka One',cursive;font-size:1.45rem;color:#1f2a20;margin-bottom:0.2rem;line-height:1.2;}}
        .kid-card-place{{font-size:0.95rem;font-weight:700;color:#8a938a;margin-bottom:0.8rem;}}
        .kid-text{{font-size:1.05rem;color:#3a423a;line-height:1.5;margin-bottom:0.8rem;}}
        .kid-facts{{text-align:left;margin:0 auto 0.8rem;max-width:90%;padding-left:1.2rem;color:#444;font-size:0.95rem;}}
        .kid-facts li{{margin-bottom:0.3rem;}}
        .kid-quote{{font-style:italic;color:#1a3a2a;font-weight:600;border-top:2px dashed #eee;padding-top:0.8rem;}}
        .kid-oneline{{font-size:0.95rem;color:#444;margin-top:0.5rem;}}

        /* Place cards */
        .kid-place-img{{width:100%;height:150px;object-fit:cover;border-radius:16px;display:block;margin-bottom:1rem;}}
        .kid-place-flag{{display:flex;align-items:center;justify-content:center;font-size:4rem;
                background-image:radial-gradient(circle at 30% 20%,rgba(255,255,255,0.30),rgba(255,255,255,0) 55%),linear-gradient(150deg,rgba(255,255,255,0.12),rgba(0,0,0,0.16));}}
        .kid-flag-img{{height:98px;width:auto;max-width:80%;border-radius:8px;border:3px solid #fff;
                box-shadow:0 8px 18px rgba(0,0,0,0.32);transition:transform 0.2s ease;}}
        .kid-card:hover .kid-flag-img{{transform:scale(1.06) rotate(-1.5deg);}}
        .flag-emoji{{display:none;}}
        .kid-place-flag.flag-fallback .flag-emoji{{display:block;}}
        .kid-place-accent{{display:block;width:46px;height:5px;border-radius:999px;margin:0.1rem auto 0.7rem;}}
        .kid-place-card .kid-oneline{{background:#f5f8f6;border-radius:14px;padding:0.55rem 0.9rem;margin-top:0.6rem;}}

        /* News cards */
        .kid-news-card{{background:#fffdf5;border:2px solid #ffe9a8;border-radius:18px;padding:1.5rem;}}
        .kid-news-card .kid-card-name{{font-size:1.15rem;margin-bottom:0.6rem;}}
        .kid-news-link{{display:inline-block;margin-top:0.5rem;font-family:'Fredoka One',cursive;font-size:0.9rem;color:#1a3a2a;}}
        .kid-news-link:hover{{text-decoration:underline;}}

        /* Word cards */
        .kid-word-card{{background:#f4f9ff;border:2px solid #cfe5ff;border-radius:18px;padding:1.5rem;text-align:center;}}
        .kid-word{{font-family:'Bagel Fat One',cursive;font-size:2rem;color:#1e5fb3;margin-bottom:0.2rem;}}
        .kid-word-say{{font-size:0.9rem;color:#888;font-style:italic;margin-bottom:0.6rem;}}
        .kid-word-means{{font-size:1.15rem;color:#222;font-weight:600;margin-bottom:0.4rem;}}
        .kid-word-from{{font-size:0.85rem;color:#777;margin-bottom:0.6rem;}}
        .kid-word-example{{font-style:italic;color:#444;}}

        /* Quiz */
        .quiz-box{{background:#1a3a2a;border-radius:20px;padding:2rem;color:#fff;}}
        .quiz-q{{margin-bottom:1.5rem;}}
        .quiz-q:last-child{{margin-bottom:0;}}
        .quiz-q-text{{font-family:'Fredoka One',cursive;font-size:1.2rem;margin-bottom:0.8rem;}}
        .quiz-options{{display:flex;flex-wrap:wrap;gap:0.6rem;}}
        .quiz-opt{{font-family:'Nunito',sans-serif;font-size:1rem;font-weight:700;padding:0.6rem 1.2rem;border:2px solid #fff;background:transparent;color:#fff;border-radius:999px;cursor:pointer;transition:all 0.15s;}}
        .quiz-opt:hover{{background:rgba(255,255,255,0.15);}}
        .quiz-opt.right{{background:#2ec167;border-color:#2ec167;}}
        .quiz-opt.wrong{{background:#e63946;border-color:#e63946;}}
        .quiz-feedback{{margin-top:0.6rem;font-weight:700;min-height:1.4rem;}}

        /* Safe footer */
        .kids-safe-footer{{background:#fffdf5;border-top:3px dashed #ffe9a8;text-align:center;padding:2.5rem 1.5rem;margin-top:3rem;}}
        .kids-safe-footer p{{max-width:600px;margin:0.4rem auto;color:#666;}}
        .kids-safe-footer .big-heart{{font-size:2rem;}}
        .kids-back-home{{display:inline-block;margin-top:1rem;font-family:'Fredoka One',cursive;color:#1a3a2a;border:3px solid #1a3a2a;border-radius:999px;padding:0.6rem 1.6rem;}}
        .kids-back-home:hover{{background:#1a3a2a;color:#fff;}}

        @media(max-width:768px){{
            .masthead h1{{font-size:1.2rem;}}
            .kids-grid{{grid-template-columns:1fr;}}
        }}
    </style>
</head>
<body>
<header class="masthead">
    <a href="index.html" class="masthead-logo-link"><img src="logo.svg" alt="BWN" class="masthead-logo"></a>
    <div class="masthead-center">
        <h1><a href="index.html">BLACK WORLD NEWS</a></h1>
        <p class="masthead-tagline">A world of their own</p>
    </div>
    <div class="masthead-spacer"></div>
</header>
{nav_html}

<section class="kids-hero">
    <h1 class="kids-hero-title">{title_balloon}</h1>
    <p class="kids-hero-sub">You are brave. You are beautiful. You belong to a family that reaches all around the world. This is your place to grow strong and proud, together.</p>
</section>

<main class="kids-main">

    <section class="kids-section kids-portals-section">
        <h2 class="kids-section-title">Choose a door</h2>
        <p class="kids-section-sub">Tap to begin.</p>
        <div class="kids-portals">{comics_door}{watch_door}</div>
    </section>

    <section class="kids-section">
        <h2 class="kids-section-title">Say It Out Loud</h2>
        <p class="kids-section-sub">Read these out loud. Every one of them is true about you.</p>
        {affirm_deck}
    </section>

    <section class="kids-section">
        <h2 class="kids-section-title">Meet Our Leaders</h2>
        <p class="kids-section-sub">Brave people who show us how to stand tall.</p>
        <div class="kids-grid">{figure_cards}</div>
    </section>

    <section class="kids-section">
        <h2 class="kids-section-title">A Place to Know</h2>
        <p class="kids-section-sub">Wonderful places around the Black world.</p>
        <div class="kids-grid">{country_cards}</div>
    </section>

    <section class="kids-section">
        <h2 class="kids-section-title">From the Big News</h2>
        <p class="kids-section-sub">Good things happening, told just for you.</p>
        <div class="kids-grid">{news_cards}</div>
    </section>

    <section class="kids-section">
        <h2 class="kids-section-title">Learn a Word</h2>
        <p class="kids-section-sub">New words from across the Black world.</p>
        <div class="kids-grid">{vocab_cards}</div>
    </section>

    <section class="kids-section">
        <h2 class="kids-section-title">Quiz Time</h2>
        <p class="kids-section-sub">See what you remember. There is no score. Just have fun.</p>
        <div class="quiz-box" id="quiz"></div>
    </section>

</main>

<footer class="kids-safe-footer">
    <p class="big-heart">&#10084;&#65039;</p>
    <p><strong>Ask a grown-up if you have any questions.</strong></p>
    <p>This page is just for you. There are no comments, no chats, and no sign-ups. We never collect anything about you.</p>
    <a href="index.html" class="kids-back-home">&larr; Back to the main page</a>
</footer>

<script>
    // Say It Out Loud — tap the deck to bring the next affirmation forward.
    const AFFIRMS = {affirm_json};
    (function(){{
        const deck=document.getElementById('affirmDeck');
        const top=document.getElementById('affirmTop');
        const txt=document.getElementById('affirmText');
        if(!deck||!top||AFFIRMS.length<1) return;
        let i=0, busy=false;
        function paint(idx){{ txt.textContent=AFFIRMS[idx].text; top.style.background=AFFIRMS[idx].color; }}
        function next(){{
            if(busy||AFFIRMS.length<2) return; busy=true;
            top.classList.add('swap');
            setTimeout(function(){{ i=(i+1)%AFFIRMS.length; paint(i); top.classList.remove('swap'); setTimeout(function(){{busy=false;}},280); }},280);
        }}
        deck.addEventListener('click',next);
        deck.addEventListener('keydown',function(e){{ if(e.key==='Enter'||e.key===' '){{ e.preventDefault(); next(); }} }});
    }})();

    // Quiz — built from the curated questions. No grading, no saving.
    const QUIZ = {quiz_json};
    const quizBox = document.getElementById('quiz');
    QUIZ.forEach((item, qi) => {{
        const q = document.createElement('div');
        q.className = 'quiz-q';
        const qt = document.createElement('p');
        qt.className = 'quiz-q-text';
        qt.textContent = (qi + 1) + '. ' + item.q;
        q.appendChild(qt);
        const opts = document.createElement('div');
        opts.className = 'quiz-options';
        const feedback = document.createElement('p');
        feedback.className = 'quiz-feedback';
        item.options.forEach((opt, oi) => {{
            const b = document.createElement('button');
            b.className = 'quiz-opt';
            b.textContent = opt;
            b.addEventListener('click', () => {{
                // Clear previous marks on this question
                opts.querySelectorAll('.quiz-opt').forEach(o => o.classList.remove('right','wrong'));
                if (oi === item.answer) {{
                    b.classList.add('right');
                    feedback.textContent = 'Right! Well done.';
                    feedback.style.color = '#2ec167';
                }} else {{
                    b.classList.add('wrong');
                    feedback.textContent = 'Try again!';
                    feedback.style.color = '#ffd93d';
                }}
            }});
            opts.appendChild(b);
        }});
        q.appendChild(opts);
        q.appendChild(feedback);
        quizBox.appendChild(q);
    }});
</script>

{PWA_SCRIPT}
{CLOUDFLARE_ANALYTICS}
</body>
</html>"""


SECTION_BANNER_CSS = """
.section-banner{display:flex;align-items:center;justify-content:center;gap:0.6rem;flex-wrap:wrap;
    padding:1.4rem 1rem;background:#fff;border-bottom:1px solid #e5e5e5;}
.section-banner-brand{font-family:'Playfair Display',serif;font-weight:900;
    font-size:1.05rem;letter-spacing:0.04em;color:#1a3a2a;text-transform:uppercase;}
.section-banner-sep{color:#bbb;font-size:1.1rem;line-height:1;}
.section-banner-name{font-family:'Playfair Display',serif;font-weight:700;
    font-size:1.05rem;color:#222;}
.section-subtitle{text-align:center;font-size:0.85rem;color:#888;padding:0.7rem 1rem 0;margin:0;}
"""


def section_banner(label):
    """BBC-style breadcrumb path: BLACK WORLD NEWS > Section."""
    return (
        '<div class="section-banner">'
        '<span class="section-banner-brand">Black World News</span>'
        '<span class="section-banner-sep">&rsaquo;</span>'
        f'<span class="section-banner-name">{label}</span>'
        '</div>'
    )


def build_sports(all_stories, cache):
    # The Sports section — Black nations on the world stage, World Cup front and centre.
    sport_stories = [s for s in all_stories
                     if derive_theme(s) == "Sport" and not is_report(s) and not is_low_quality(s)]

    def is_focus(s):
        t = ((s.get("title_en") or s.get("title") or "") + " " + (s.get("summary") or "")).lower()
        return ("world cup" in t) or any(b in t for b in BLACK_NATIONS)

    sport_stories.sort(key=lambda s: s.get("saved_at", ""), reverse=True)
    sport_stories.sort(key=lambda s: 0 if is_focus(s) else 1)  # stable: focus (WC / our nations) first

    used_images = set()
    cards = "".join(story_card(s, cache=cache, used_images=used_images) for s in sport_stories)
    if not cards:
        cards = '<p style="color:#666;padding:1rem">Sport stories are on the way.</p>'
    count = len(sport_stories)
    color = "#1a3a2a"
    wc_ticker_js = _WC_TICKER_JS.replace("__NATIONS__", json.dumps(BLACK_NATIONS))
    wc_schedule_js = _WC_SCHEDULE_JS.replace("__NATIONS__", json.dumps(BLACK_NATIONS))

    content = f"""
    {section_banner("Sports")}
    <p class="section-subtitle">Black nations on the world stage. Right now &mdash; all eyes on the World Cup.</p>
    <style>
        {SECTION_BANNER_CSS}
        .wc-ticker {{ background:#0a0a0a; overflow:hidden; white-space:nowrap; border:2px solid #1a3a2a; border-radius:8px; margin:1.5rem 0; }}
        .wc-schedule {{ margin:1.5rem 0 2.5rem; }}
        .wc-sched-title {{ font-family:'Playfair Display',serif; font-size:1.4rem; font-weight:900; color:#1a3a2a; margin-bottom:0.3rem; }}
        .wc-sched-sub {{ font-size:0.85rem; color:#888; margin-bottom:1rem; }}
        .wc-day {{ font-size:0.82rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:#1a3a2a; background:#eef4f0; padding:0.4rem 0.8rem; border-radius:6px; margin:1.2rem 0 0.4rem; }}
        .wc-match {{ display:flex; justify-content:space-between; align-items:center; gap:1rem; padding:0.55rem 0.8rem; border-bottom:1px solid #eee; }}
        .wc-teams {{ font-size:0.95rem; color:#222; }}
        .wc-teams b {{ color:#1a3a2a; }}
        .wc-meta {{ font-size:0.78rem; color:#888; white-space:nowrap; text-align:right; }}
        .wc-empty {{ color:#888; font-style:italic; }}
        @media(max-width:768px) {{ .wc-match {{ flex-direction:column; align-items:flex-start; gap:0.15rem; }} .wc-meta {{ text-align:left; }} }}
        .wc-track {{ display:inline-block; padding:0.5rem 0; animation:wcscroll 60s linear infinite; will-change:transform; }}
        .wc-ticker:hover .wc-track {{ animation-play-state:paused; }}
        .wc-item {{ color:#fff; font-size:0.85rem; font-weight:600; padding:0 0.55rem; }}
        .wc-item b {{ color:#ffd93d; }}
        .wc-item i {{ color:#8ab89a; font-style:normal; font-size:0.74rem; }}
        .wc-sep {{ color:#555; padding:0 0.2rem; }}
        .wc-label {{ background:#e8602c; color:#fff; font-weight:800; font-size:0.72rem; padding:0.15rem 0.6rem; border-radius:3px; margin:0 0.9rem; letter-spacing:0.08em; }}
        @keyframes wcscroll {{ from {{ transform:translateX(0); }} to {{ transform:translateX(-50%); }} }}
        .card-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); gap:1rem; margin-top:1rem; }}
        .card {{ background:#fff; border:1px solid #ddd; border-top:3px solid transparent; padding:1.25rem 1.5rem; transition:border-top-color 0.2s,box-shadow 0.2s; }}
        .card:hover {{ border-top-color:{color}; box-shadow:0 4px 16px rgba(0,0,0,0.1); }}
        .card-img {{ width:100%; height:180px; object-fit:cover; display:block; margin-bottom:1rem; }}
        .card-meta {{ display:flex; flex-wrap:wrap; align-items:center; gap:0.5rem; margin-bottom:0.75rem; }}
        .flag-country {{ font-size:0.8rem; color:{color}; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; }}
        .theme-tag {{ font-size:0.66rem; text-transform:uppercase; letter-spacing:0.07em; background:#1a3a2a; color:#fff; padding:0.2rem 0.6rem; border-radius:999px; font-weight:700; }}
        .framing-dot {{ display:inline-block; width:8px; height:8px; border-radius:50%; vertical-align:middle; }}
        .card-title {{ font-family:'Playfair Display',serif; font-size:1.1rem; font-weight:700; color:#111; margin-bottom:0.5rem; line-height:1.3; }}
        .card-title a:hover {{ color:{color}; }}
        .card-summary {{ font-size:0.88rem; color:#444; margin-bottom:0.5rem; }}
        .narrative-analysis {{ font-size:0.82rem; color:#666; font-style:italic; border-left:3px solid #ddd; padding-left:0.75rem; margin-bottom:0.5rem; }}
        .cui-bono {{ font-size:0.72rem; color:#aaa; font-style:italic; padding-left:0.75rem; margin-bottom:0.5rem; }}
        .factors {{ display:flex; flex-wrap:wrap; gap:0.4rem; margin-bottom:0.5rem; }}
        .factor {{ font-size:0.62rem; color:#bbb; font-weight:600; }}
        .card-footer {{ display:flex; justify-content:space-between; align-items:center; margin-top:0.75rem; padding-top:0.75rem; border-top:1px solid #eee; }}
        .saved-at {{ font-size:0.75rem; color:#aaa; }}
        .read-more {{ font-size:0.8rem; color:{color}; font-weight:700; }}
        @media(max-width:768px) {{ .card-grid {{ grid-template-columns:1fr; }} }}
    </style>
    <div class="wc-ticker" id="wcTicker" hidden><div class="wc-track" id="wcTrack"></div></div>
    <section class="wc-schedule">
        <h2 class="wc-sched-title">World Cup &mdash; full schedule</h2>
        <p class="wc-sched-sub">Times shown in your local timezone. &#9733; marks a Black nation. Scores update live.</p>
        <div id="wcSchedule"><p class="wc-empty">Loading fixtures&hellip;</p></div>
    </section>
    <h2 class="wc-sched-title">From the newsroom</h2>
    <div class="card-grid">{cards}</div>
    {wc_ticker_js}
    {wc_schedule_js}
    """

    nav_html = make_two_tier_nav(active_issue="sports")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sports | Black World News</title>
    <meta name="description" content="Black nations on the world stage. World Cup results, fixtures and stories about Black athletes and teams.">
    <meta property="og:title" content="Sports | Black World News">
    <meta property="og:description" content="Black nations on the world stage. World Cup front and centre.">
    <link rel="canonical" href="https://www.blackworldnews.world/sports.html">
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="favicon.svg">
    {PWA_META}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@400;600&family=Fredoka+One&family=Bagel+Fat+One&display=swap" rel="stylesheet">
    <style>
        *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
        body{{background:#f2f2f2;color:#111;font-family:'Source Sans 3',sans-serif;font-size:16px;line-height:1.6;}}
        a{{color:inherit;text-decoration:none;}}
        .masthead{{background:#1a3a2a;padding:1rem 1.5rem;display:flex;align-items:center;gap:1rem;}}
        .masthead-logo-link,.masthead-spacer{{flex:0 0 50px;display:flex;align-items:center;justify-content:center;}}
        .masthead-logo{{width:50px;height:50px;display:block;}}
        .masthead-center{{flex:1;text-align:center;}}
        .masthead h1{{font-family:'Playfair Display',serif;font-size:1.6rem;font-weight:900;color:#fff;letter-spacing:0.04em;}}
        .masthead h1 a:hover{{color:#c8d8c0;}}
        .masthead-tagline{{font-size:0.65rem;color:#8ab89a;letter-spacing:0.1em;text-transform:uppercase;margin-top:0.2rem;}}
        .site-nav{{background:#0a0a0a;border-bottom:3px solid #1a3a2a;display:flex;justify-content:flex-start;align-items:flex-end;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;padding-left:0.7rem;}}
        .site-nav::-webkit-scrollbar{{display:none;}}
        .site-nav a{{font-size:0.72rem;font-weight:700;letter-spacing:0.07em;text-transform:uppercase;white-space:nowrap;padding:0.65rem 0.8rem;border-bottom:2px solid transparent;transition:color 0.15s,border-color 0.15s;color:#888;}}
        .site-nav a:hover{{color:#fff;border-bottom-color:#1a3a2a;}}
        .site-nav a.nav-kids{{font-family:'Bagel Fat One',cursive;font-size:0.95rem;letter-spacing:0.01em;padding-top:0.5rem;padding-bottom:0.5rem;transform:translateY(-2px);}}
        .site-nav a.nav-kids:hover{{border-bottom-color:#ffd93d;}}
        {KIDS_LETTER_CSS}
        .site-nav a.nav-active{{border-bottom-color:#1a3a2a;color:#fff;}}
        .nav-divider{{color:#444;padding:0 0.25rem;font-size:1rem;user-select:none;flex-shrink:0;}}
        .page-container{{max-width:1200px;margin:0 auto;padding:3rem 1.5rem;}}
        .page-title{{font-family:'Playfair Display',serif;font-size:2rem;font-weight:900;margin-bottom:0.5rem;}}
        .page-subtitle{{font-size:1rem;color:#666;margin-bottom:2rem;}}
        footer{{background:#111;border-top:4px solid #1a3a2a;text-align:center;padding:2rem;font-size:0.8rem;color:#555;margin-top:4rem;}}
        footer strong{{color:#8ab89a;}}
        @media(max-width:768px){{.masthead{{padding:0.75rem 1rem;}}.masthead h1{{font-size:1.2rem;}}.page-container{{padding:2rem 1rem;}}.page-title{{font-size:1.5rem;}}.site-nav a{{padding:0.5rem 0.65rem;font-size:0.68rem;}}.nav-divider{{padding:0 0.15rem;}}}}
    </style>
</head>
<body>
<header class="masthead">
    <a href="index.html" class="masthead-logo-link"><img src="logo.svg" alt="BWN" class="masthead-logo"></a>
    <div class="masthead-center">
        <h1><a href="index.html">BLACK WORLD NEWS</a></h1>
        <p class="masthead-tagline">What matters to you, today</p>
    </div>
    <div class="masthead-spacer"></div>
</header>
{nav_html}
<div class="page-container">
    {content}
</div>
<footer>
    <p><strong>BLACK WORLD NEWS</strong></p>
    <p style="margin-top:0.5rem">Live scores via TheSportsDB. Stories sourced from the open web with AI summaries.</p>
    {social_bar_html()}
    {footer_legal_html()}
</footer>
{PWA_SCRIPT}
{CLOUDFLARE_ANALYTICS}
</body>
</html>"""


def build_region_page(region_id, region, all_stories, cache):
    # Builds a full page for one region — all its stories, newest first
    all_stories = [s for s in all_stories if not is_report(s) and not is_low_quality(s)]
    by_country = defaultdict(list)
    for s in all_stories:
        by_country[s.get("country", "Other/Global")].append(s)

    region_stories = []
    for country in region["countries"]:
        region_stories.extend(by_country.get(country, []))
    region_stories = sorted(region_stories, key=lambda s: s.get("saved_at",""), reverse=True)

    used_images = set()
    cards = "".join(story_card(s, cache=cache, used_images=used_images) for s in region_stories)

    color = region["color"]
    label = region["label"]
    count = len(region_stories)

    content = f"""
    {section_banner(label)}
    <p class="section-subtitle">{count} stories collected so far. Newest first.</p>
    <style>
        {SECTION_BANNER_CSS}
        .card-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); gap:1rem; margin-top:1.5rem; }}
        .card {{ background:#fff; border:1px solid #ddd; border-top:3px solid transparent; padding:1.25rem 1.5rem; transition:border-top-color 0.2s,box-shadow 0.2s; }}
        .card:hover {{ border-top-color:{color}; box-shadow:0 4px 16px rgba(0,0,0,0.1); }}
        .card-img {{ width:100%; height:180px; object-fit:cover; display:block; margin-bottom:1rem; }}
        .card-meta {{ display:flex; flex-wrap:wrap; align-items:center; gap:0.5rem; margin-bottom:0.75rem; }}
        .flag-country {{ font-size:0.8rem; color:{color}; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; }}
        .category {{ font-size:0.68rem; text-transform:uppercase; letter-spacing:0.08em; background:#f5f5f5; border:1px solid #ddd; padding:0.15rem 0.5rem; color:#555; font-weight:600; }}
        .theme-tag {{ font-size:0.66rem; text-transform:uppercase; letter-spacing:0.07em; background:#1a3a2a; color:#fff; padding:0.2rem 0.6rem; border-radius:999px; font-weight:700; }}
        .framing-dot {{ display:inline-block; width:8px; height:8px; border-radius:50%; vertical-align:middle; cursor:default; }}
        .card-title {{ font-family:'Playfair Display',serif; font-size:1.1rem; font-weight:700; color:#111; margin-bottom:0.5rem; line-height:1.3; }}
        .card-title a:hover {{ color:{color}; }}
        .card-summary {{ font-size:0.88rem; color:#444; margin-bottom:0.5rem; }}
        .narrative-analysis {{ font-size:0.82rem; color:#666; font-style:italic; border-left:3px solid #ddd; padding-left:0.75rem; margin-bottom:0.5rem; }}
        .cui-bono{{font-size:0.72rem;color:#aaa;font-style:italic;padding-left:0.75rem;margin-bottom:0.5rem;letter-spacing:0.01em;}}
        .factors {{ display:flex; flex-wrap:wrap; gap:0.4rem; margin-bottom:0.5rem; }}
        .factor {{ font-size:0.62rem; color:#bbb; font-weight:600; }}
        .card-footer {{ display:flex; justify-content:space-between; align-items:center; margin-top:0.75rem; padding-top:0.75rem; border-top:1px solid #eee; }}
        .saved-at {{ font-size:0.75rem; color:#aaa; }}
        .read-more {{ font-size:0.8rem; color:{color}; font-weight:700; }}
        .read-more:hover {{ text-decoration:underline; }}
        @media(max-width:768px) {{ .card-grid {{ grid-template-columns:1fr; }} }}
    </style>
    <div class="card-grid">{cards}</div>
    """

    # Nav for region pages — highlight the active region in row 2
    nav_html = make_two_tier_nav(active_region=region_id)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{label} | Black World News</title>
    <meta name="description" content="News from {label} covering Black communities. {count} stories and counting.">
    <meta property="og:title" content="{label} | Black World News">
    <meta property="og:description" content="News from {label} covering Black communities.">
    <meta name="author" content="Black World News">
    <link rel="canonical" href="https://www.blackworldnews.world/{region_id}.html">
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="favicon.svg">
    {PWA_META}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@400;600&family=Fredoka+One&family=Bagel+Fat+One&display=swap" rel="stylesheet">
    <style>
        *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
        body{{background:#f2f2f2;color:#111;font-family:'Source Sans 3',sans-serif;font-size:16px;line-height:1.6;}}
        a{{color:inherit;text-decoration:none;}}
        .masthead{{background:#1a3a2a;padding:1rem 1.5rem;display:flex;align-items:center;gap:1rem;}}
        .masthead-logo-link,.masthead-spacer{{flex:0 0 50px;display:flex;align-items:center;justify-content:center;}}
        .masthead-logo{{width:50px;height:50px;display:block;}}
        .masthead-center{{flex:1;text-align:center;}}
        .masthead h1{{font-family:'Playfair Display',serif;font-size:1.6rem;font-weight:900;color:#fff;letter-spacing:0.04em;}}
        .masthead h1 a:hover{{color:#c8d8c0;}}
        .masthead-tagline{{font-size:0.65rem;color:#8ab89a;letter-spacing:0.1em;text-transform:uppercase;margin-top:0.2rem;}}
        .site-nav{{background:#0a0a0a;border-bottom:3px solid #1a3a2a;display:flex;justify-content:flex-start;align-items:flex-end;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;padding-left:0.7rem;}}
        .site-nav::-webkit-scrollbar{{display:none;}}
        .site-nav a{{font-size:0.72rem;font-weight:700;letter-spacing:0.07em;text-transform:uppercase;white-space:nowrap;padding:0.65rem 0.8rem;border-bottom:2px solid transparent;transition:color 0.15s,border-color 0.15s;color:#888;}}
        .site-nav a:hover{{color:#fff;border-bottom-color:#1a3a2a;}}
        .site-nav a.nav-kids{{font-family:'Bagel Fat One',cursive;font-size:0.95rem;letter-spacing:0.01em;padding-top:0.5rem;padding-bottom:0.5rem;transform:translateY(-2px);}}
        .site-nav a.nav-kids:hover{{border-bottom-color:#ffd93d;}}
        {KIDS_LETTER_CSS}
        .site-nav a.nav-active{{border-bottom-color:#1a3a2a;color:#fff;}}
        .nav-divider{{color:#444;padding:0 0.25rem;font-size:1rem;user-select:none;flex-shrink:0;}}
        .page-container{{max-width:1200px;margin:0 auto;padding:3rem 1.5rem;}}
        .page-title{{font-family:'Playfair Display',serif;font-size:2rem;font-weight:900;margin-bottom:0.5rem;}}
        .page-subtitle{{font-size:1rem;color:#666;margin-bottom:2rem;}}
        footer{{background:#111;border-top:4px solid #1a3a2a;text-align:center;padding:2rem;font-size:0.8rem;color:#555;margin-top:4rem;}}
        footer strong{{color:#8ab89a;}}
        @media(max-width:768px){{.masthead{{padding:0.75rem 1rem;}}.masthead h1{{font-size:1.2rem;}}.page-container{{padding:2rem 1rem;}}.page-title{{font-size:1.5rem;}}.site-nav a{{padding:0.5rem 0.65rem;font-size:0.68rem;}}.nav-divider{{padding:0 0.15rem;}}}}
    </style>
</head>
<body>
<header class="masthead">
    <a href="index.html" class="masthead-logo-link"><img src="logo.svg" alt="BWN" class="masthead-logo"></a>
    <div class="masthead-center">
        <h1><a href="index.html">BLACK WORLD NEWS</a></h1>
        <p class="masthead-tagline">What matters to you, today</p>
    </div>
    <div class="masthead-spacer"></div>
</header>
{nav_html}
<div class="page-container">
    {content}
</div>
<footer>
    <p><strong>BLACK WORLD NEWS</strong></p>
    <p style="margin-top:0.5rem">Stories sourced from the open web. AI summaries. Links always go to the original source.</p>
    {social_bar_html()}
    {footer_legal_html()}
</footer>
{PWA_SCRIPT}
{CLOUDFLARE_ANALYTICS}
</body>
</html>"""


def build_issue_page(issue_id, issue, all_stories, cache):
    # Builds a full page for one issue — all matching stories, newest first
    categories = issue["categories"]
    color      = issue["color"]
    label      = issue["label"]

    issue_stories = [s for s in all_stories if s.get("category", "") in categories
                     and not is_report(s) and not is_low_quality(s)]
    issue_stories = sorted(issue_stories, key=lambda s: s.get("saved_at", ""), reverse=True)
    count = len(issue_stories)

    used_images = set()
    cards = "".join(story_card(s, cache=cache, used_images=used_images) for s in issue_stories)

    if not cards:
        cards = "<p style='color:#666;font-style:italic;padding:2rem 0'>No stories collected yet for this topic.</p>"

    nav_html = make_two_tier_nav(active_issue=issue_id)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{label} | Black World News</title>
    <meta name="description" content="News covering {label.lower()} and Black communities worldwide. {count} stories and counting.">
    <meta property="og:title" content="{label} | Black World News">
    <meta property="og:description" content="News covering {label.lower()} and Black communities worldwide.">
    <meta name="author" content="Black World News">
    <link rel="canonical" href="https://www.blackworldnews.world/{issue_id}.html">
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="favicon.svg">
    {PWA_META}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@400;600&family=Fredoka+One&family=Bagel+Fat+One&display=swap" rel="stylesheet">
    <style>
        *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
        body{{background:#f2f2f2;color:#111;font-family:'Source Sans 3',sans-serif;font-size:16px;line-height:1.6;}}
        a{{color:inherit;text-decoration:none;}}
        .masthead{{background:#1a3a2a;padding:1rem 1.5rem;display:flex;align-items:center;gap:1rem;}}
        .masthead-logo-link,.masthead-spacer{{flex:0 0 50px;display:flex;align-items:center;justify-content:center;}}
        .masthead-logo{{width:50px;height:50px;display:block;}}
        .masthead-center{{flex:1;text-align:center;}}
        .masthead h1{{font-family:'Playfair Display',serif;font-size:1.6rem;font-weight:900;color:#fff;letter-spacing:0.04em;}}
        .masthead h1 a:hover{{color:#c8d8c0;}}
        .masthead-tagline{{font-size:0.65rem;color:#8ab89a;letter-spacing:0.1em;text-transform:uppercase;margin-top:0.2rem;}}
        .site-nav{{background:#0a0a0a;border-bottom:3px solid #1a3a2a;display:flex;justify-content:flex-start;align-items:flex-end;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;padding-left:0.7rem;}}
        .site-nav::-webkit-scrollbar{{display:none;}}
        .site-nav a{{font-size:0.72rem;font-weight:700;letter-spacing:0.07em;text-transform:uppercase;white-space:nowrap;padding:0.65rem 0.8rem;border-bottom:2px solid transparent;transition:color 0.15s,border-color 0.15s;color:#888;}}
        .site-nav a:hover{{color:#fff;border-bottom-color:#1a3a2a;}}
        .site-nav a.nav-kids{{font-family:'Bagel Fat One',cursive;font-size:0.95rem;letter-spacing:0.01em;padding-top:0.5rem;padding-bottom:0.5rem;transform:translateY(-2px);}}
        .site-nav a.nav-kids:hover{{border-bottom-color:#ffd93d;}}
        {KIDS_LETTER_CSS}
        .site-nav a.nav-active{{border-bottom-color:{color};color:#fff;}}
        .nav-divider{{color:#444;padding:0 0.25rem;font-size:1rem;user-select:none;flex-shrink:0;}}
        .page-container{{max-width:1200px;margin:0 auto;padding:3rem 1.5rem;}}
        .page-title{{font-family:'Playfair Display',serif;font-size:2rem;font-weight:900;margin-bottom:0.5rem;}}
        .page-subtitle{{font-size:1rem;color:#666;margin-bottom:2rem;}}
        .card-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:1rem;}}
        .card{{background:#fff;border:1px solid #ddd;border-top:3px solid transparent;padding:1.25rem 1.5rem;transition:border-top-color 0.2s,box-shadow 0.2s;}}
        .card:hover{{border-top-color:{color};box-shadow:0 4px 16px rgba(0,0,0,0.1);}}
        .card-img{{width:100%;height:180px;object-fit:cover;display:block;margin-bottom:1rem;}}
        .card-meta{{display:flex;flex-wrap:wrap;align-items:center;gap:0.5rem;margin-bottom:0.75rem;}}
        .flag-country{{font-size:0.8rem;color:{color};font-weight:700;text-transform:uppercase;letter-spacing:0.05em;}}
        .category{{font-size:0.68rem;text-transform:uppercase;letter-spacing:0.08em;background:#f5f5f5;border:1px solid #ddd;padding:0.15rem 0.5rem;color:#555;font-weight:600;}}
        .theme-tag{{font-size:0.66rem;text-transform:uppercase;letter-spacing:0.07em;background:#1a3a2a;color:#fff;padding:0.2rem 0.6rem;border-radius:999px;font-weight:700;}}
        .framing-dot{{display:inline-block;width:8px;height:8px;border-radius:50%;vertical-align:middle;cursor:default;}}
        .card-title{{font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;color:#111;margin-bottom:0.5rem;line-height:1.3;}}
        .card-title a:hover{{color:{color};}}
        .card-summary{{font-size:0.88rem;color:#444;margin-bottom:0.5rem;}}
        .narrative-analysis{{font-size:0.82rem;color:#666;font-style:italic;border-left:3px solid #ddd;padding-left:0.75rem;margin-bottom:0.5rem;}}
        .factors{{display:flex;flex-wrap:wrap;gap:0.4rem;margin-bottom:0.5rem;}}
        .factor{{font-size:0.62rem;color:#bbb;font-weight:600;}}
        .card-footer{{display:flex;justify-content:space-between;align-items:center;margin-top:0.75rem;padding-top:0.75rem;border-top:1px solid #eee;}}
        .saved-at{{font-size:0.75rem;color:#aaa;}}
        .read-more{{font-size:0.8rem;color:{color};font-weight:700;}}
        .read-more:hover{{text-decoration:underline;}}
        footer{{background:#111;border-top:4px solid #1a3a2a;text-align:center;padding:2rem;font-size:0.8rem;color:#555;margin-top:4rem;}}
        footer strong{{color:#8ab89a;}}
        @media(max-width:768px){{.masthead{{padding:0.75rem 1rem;}}.masthead h1{{font-size:1.2rem;}}.page-container{{padding:2rem 1rem;}}.page-title{{font-size:1.5rem;}}.card-grid{{grid-template-columns:1fr;}}.site-nav a{{padding:0.5rem 0.65rem;font-size:0.68rem;}}.nav-divider{{padding:0 0.15rem;}}}}
    </style>
</head>
<body>
<header class="masthead">
    <a href="index.html" class="masthead-logo-link"><img src="logo.svg" alt="BWN" class="masthead-logo"></a>
    <div class="masthead-center">
        <h1><a href="index.html">BLACK WORLD NEWS</a></h1>
        <p class="masthead-tagline">What matters to you, today</p>
    </div>
    <div class="masthead-spacer"></div>
</header>
{nav_html}
<div class="page-container">
    {section_banner(label)}
    <p class="section-subtitle">{count} stories collected. Newest first.</p>
    <div class="card-grid">{cards}</div>
</div>
<footer>
    <p><strong>BLACK WORLD NEWS</strong></p>
    <p style="margin-top:0.5rem">Stories sourced from the open web. AI summaries. Links always go to the original source.</p>
    {social_bar_html()}
    {footer_legal_html()}
</footer>
{PWA_SCRIPT}
{CLOUDFLARE_ANALYTICS}
</body>
</html>"""


def build_search_page():
    # Fully client-side search. Fetches stories.json, filters live in the browser.
    nav_html = make_two_tier_nav()

    flags_json   = json.dumps(COUNTRY_FLAGS)
    framing_json = json.dumps(FRAMING_COLORS)
    regions_json = json.dumps({k: v["countries"] for k, v in REGION_GROUPS.items()})
    topics_json  = json.dumps({k: v["categories"] for k, v in ISSUE_GROUPS.items()})
    themes_json  = json.dumps(_THEME_PATTERNS)   # [[theme, regex], ...] — same config as server
    cat_theme_json = json.dumps(_CAT_THEME)

    topic_chips = "".join(
        f'<button class="chip" data-group="topic" data-value="{k}">{v["label"]}</button>'
        for k, v in ISSUE_GROUPS.items()
    )
    region_chips = "".join(
        f'<button class="chip" data-group="region" data-value="{k}">{v["label"]}</button>'
        for k, v in REGION_GROUPS.items()
    )
    framing_chips = "".join(
        f'<button class="chip" data-group="framing" data-value="{f}"><span class="chip-dot" style="background:{c}"></span>{f}</button>'
        for f, c in FRAMING_COLORS.items()
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search | Black World News</title>
    <meta name="description" content="Search every story in the Black World News archive. Filter by topic, region, and framing.">
    <link rel="canonical" href="https://www.blackworldnews.world/search.html">
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="favicon.svg">
    {PWA_META}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@400;600&family=Fredoka+One&family=Bagel+Fat+One&display=swap" rel="stylesheet">
    <style>
        *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
        body{{background:#f2f2f2;color:#111;font-family:'Source Sans 3',sans-serif;font-size:16px;line-height:1.6;}}
        a{{color:inherit;text-decoration:none;}}
        .masthead{{background:#1a3a2a;padding:1rem 1.5rem;display:flex;align-items:center;gap:1rem;}}
        .masthead-logo-link,.masthead-spacer{{flex:0 0 50px;display:flex;align-items:center;justify-content:center;}}
        .masthead-logo{{width:50px;height:50px;display:block;}}
        .masthead-center{{flex:1;text-align:center;}}
        .masthead h1{{font-family:'Playfair Display',serif;font-size:clamp(1.4rem,4vw,1.8rem);font-weight:900;color:#fff;letter-spacing:0.05em;line-height:1;}}
        .masthead h1 a:hover{{color:#c8d8c0;}}
        .masthead-tagline{{font-size:0.65rem;color:#8ab89a;letter-spacing:0.1em;text-transform:uppercase;margin-top:0.25rem;}}
        .site-nav{{background:#111;border-bottom:3px solid #1a3a2a;display:flex;justify-content:flex-start;align-items:center;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;padding-left:0.7rem;}}
        .site-nav::-webkit-scrollbar{{display:none;}}
        .site-nav a{{font-size:0.72rem;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;color:#888;white-space:nowrap;padding:0.65rem 0.8rem;border-bottom:2px solid transparent;transition:color 0.15s,border-color 0.15s;}}
        .site-nav a:hover{{color:#fff;border-bottom-color:#1a3a2a;}}
        .site-nav a.nav-active{{color:#fff;border-bottom-color:#1a3a2a;}}
        .site-nav a.nav-kids{{font-family:'Bagel Fat One',cursive;font-size:0.95rem;letter-spacing:0.01em;padding-top:0.5rem;padding-bottom:0.5rem;transform:translateY(-2px);}}
        .site-nav a.nav-kids:hover{{border-bottom-color:#ffd93d;}}
        {KIDS_LETTER_CSS}
        .site-nav a.nav-search{{color:#8ab89a;}}
        .nav-divider{{color:#444;padding:0 0.25rem;font-size:1rem;user-select:none;flex-shrink:0;}}

        .search-bar{{background:#fff;border-bottom:1px solid #ddd;padding:1.5rem;}}
        .search-bar-inner{{max-width:1200px;margin:0 auto;}}
        #search-input{{width:100%;font-family:'Source Sans 3',sans-serif;font-size:1.1rem;padding:0.85rem 1rem;border:2px solid #1a3a2a;background:#fff;color:#111;outline:none;transition:border-color 0.15s;}}
        #search-input:focus{{border-color:#0a2a1a;}}

        .filters{{max-width:1200px;margin:0 auto;padding:1.5rem 1.5rem 0.5rem;}}
        .filter-row{{margin-bottom:0.9rem;display:flex;flex-wrap:wrap;align-items:center;gap:0.5rem;}}
        .filter-label{{font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;color:#666;margin-right:0.4rem;min-width:75px;}}
        .chip{{font-family:inherit;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.04em;padding:0.35rem 0.75rem;background:#fff;border:1px solid #ccc;color:#555;cursor:pointer;transition:all 0.15s;display:inline-flex;align-items:center;gap:0.35rem;}}
        .chip:hover{{border-color:#1a3a2a;color:#1a3a2a;}}
        .chip.chip-active{{background:#1a3a2a;color:#fff;border-color:#1a3a2a;}}
        .chip-dot{{display:inline-block;width:8px;height:8px;border-radius:50%;}}

        .results-meta{{max-width:1200px;margin:0 auto;padding:1rem 1.5rem;font-size:0.85rem;color:#666;border-top:1px solid #ddd;}}
        .results-meta strong{{color:#1a3a2a;}}

        .results-container{{max-width:1200px;margin:0 auto;padding:0 1.5rem 3rem;}}
        .card-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:0.75rem;}}
        .card{{background:#fff;border:1px solid #ddd;border-top:3px solid transparent;padding:0.85rem 1rem;transition:border-top-color 0.2s,box-shadow 0.2s;}}
        .card:hover{{border-top-color:#1a3a2a;box-shadow:0 2px 8px rgba(0,0,0,0.08);}}
        .card-img{{width:100%;height:160px;object-fit:cover;display:block;margin-bottom:0.75rem;}}
        .card-meta{{display:flex;flex-wrap:wrap;align-items:center;gap:0.4rem;margin-bottom:0.4rem;}}
        .flag-country{{font-size:0.78rem;color:#1a3a2a;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;}}
        .category{{font-size:0.65rem;text-transform:uppercase;letter-spacing:0.08em;background:#eef4f0;border:1px solid #c5daca;padding:0.15rem 0.5rem;color:#1a3a2a;font-weight:600;}}
        .theme-tag{{font-size:0.64rem;text-transform:uppercase;letter-spacing:0.07em;background:#1a3a2a;color:#fff;padding:0.2rem 0.6rem;border-radius:999px;font-weight:700;}}
        .framing-dot{{display:inline-block;width:8px;height:8px;border-radius:50%;}}
        .card-title{{font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;color:#111;margin-bottom:0.35rem;line-height:1.3;}}
        .card-title a:hover{{color:#1a3a2a;}}
        .card-summary{{font-size:0.85rem;color:#444;line-height:1.45;}}

        .empty{{padding:3rem 1rem;text-align:center;color:#888;font-style:italic;}}
        .clear-all{{background:none;border:none;color:#1a3a2a;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.06em;cursor:pointer;padding:0.35rem 0.5rem;}}
        .clear-all:hover{{text-decoration:underline;}}

        footer{{background:#111;border-top:4px solid #1a3a2a;text-align:center;padding:2rem;font-size:0.8rem;color:#555;}}
        footer strong{{color:#8ab89a;}}

        @media (max-width:768px){{
            .masthead h1{{font-size:1.3rem;}}
            #search-input{{font-size:1rem;}}
            .filter-label{{min-width:auto;width:100%;margin-bottom:0.25rem;}}
            .card-grid{{grid-template-columns:1fr;}}
        }}
    </style>
</head>
<body>
<header class="masthead">
    <a href="index.html" class="masthead-logo-link"><img src="logo.svg" alt="BWN" class="masthead-logo"></a>
    <div class="masthead-center">
        <h1><a href="index.html">BLACK WORLD NEWS</a></h1>
        <p class="masthead-tagline">What matters to you, today</p>
    </div>
    <div class="masthead-spacer"></div>
</header>
{nav_html}

<div class="search-bar">
    <div class="search-bar-inner">
        <input id="search-input" type="search" placeholder="Search by keyword. Try: police, Ghana, debt, students..." autocomplete="off">
    </div>
</div>

<div class="filters">
    <div class="filter-row">
        <span class="filter-label">Topic</span>
        {topic_chips}
    </div>
    <div class="filter-row">
        <span class="filter-label">Region</span>
        {region_chips}
    </div>
    <div class="filter-row">
        <span class="filter-label">Framing</span>
        {framing_chips}
        <button class="clear-all" id="clear-all">Clear all</button>
    </div>
</div>

<div class="results-meta">
    Showing <strong id="result-count">0</strong> of <strong id="total-count">0</strong> stories
</div>

<div class="results-container">
    <div id="results" class="card-grid"></div>
</div>

<footer>
    <p><strong>BLACK WORLD NEWS</strong></p>
    <p style="margin-top:0.5rem">Stories sourced from the open web. Links go to the original source.</p>
    {social_bar_html()}
    {footer_legal_html()}
</footer>

<script>
    const FLAGS    = {flags_json};
    const FRAMING  = {framing_json};
    const REGIONS  = {regions_json};
    const TOPICS   = {topics_json};
    const THEME_PATTERNS = {themes_json};
    const CAT_THEME = {cat_theme_json};
    const _THEME_RE = THEME_PATTERNS.map(function(p){{ return [p[0], new RegExp(p[1], 'i')]; }});
    function deriveTheme(s){{
        const text = ((s.title_en||s.title||'') + ' ' + (s.summary||'')).toLowerCase();
        for (let i=0;i<_THEME_RE.length;i++){{ if (_THEME_RE[i][1].test(text)) return _THEME_RE[i][0]; }}
        return CAT_THEME[s.category] || 'World';
    }}

    let allStories = [];
    let filters = {{ q: '', topic: new Set(), region: new Set(), framing: new Set() }};

    const $ = sel => document.querySelector(sel);
    const $$ = sel => document.querySelectorAll(sel);

    function escapeHtml(s) {{
        return String(s == null ? '' : s).replace(/[<>&"']/g, c => (
            {{'<':'&lt;','>':'&gt;','&':'&amp;','"':'&quot;',"'":'&#39;'}}[c]
        ));
    }}

    function matches(story) {{
        if (filters.q) {{
            const hay = (
                (story.title_en || story.title || '') + ' ' +
                (story.title    || '') + ' ' +
                (story.summary  || '') + ' ' +
                (story.country  || '') + ' ' +
                (story.category || '')
            ).toLowerCase();
            if (!hay.includes(filters.q)) return false;
        }}
        if (filters.topic.size > 0) {{
            let hit = false;
            for (const t of filters.topic) {{
                if ((TOPICS[t] || []).includes(story.category)) {{ hit = true; break; }}
            }}
            if (!hit) return false;
        }}
        if (filters.region.size > 0) {{
            let hit = false;
            for (const r of filters.region) {{
                if ((REGIONS[r] || []).includes(story.country)) {{ hit = true; break; }}
            }}
            if (!hit) return false;
        }}
        if (filters.framing.size > 0) {{
            if (!filters.framing.has(story.narrative_framing)) return false;
        }}
        return true;
    }}

    function cardHtml(s) {{
        const isGlobal = !s.country || s.country === 'Other/Global';
        const flag     = FLAGS[s.country] || '';
        const loc      = isGlobal ? '' : `<span class="flag-country">${{(flag + ' ' + escapeHtml(s.country)).trim()}}</span>`;
        const fcolor   = FRAMING[s.narrative_framing] || '';
        const dot      = fcolor ? `<span class="framing-dot" style="background:${{fcolor}}" title="${{escapeHtml(s.narrative_framing)}}"></span>` : '';
        // Use English title and summary; fall back to original
        const title    = s.title_en || s.title || '';
        const summary  = s.summary || '';
        const img      = s.image ? `<img class="card-img" src="${{escapeHtml(s.image)}}" alt="" loading="lazy" onerror="this.remove()">` : '';
        return `
            <div class="card">
                ${{img}}
                <div class="card-meta">
                    <span class="theme-tag">${{escapeHtml(deriveTheme(s))}}</span>
                    ${{loc}}
                    ${{dot}}
                </div>
                <h2 class="card-title"><a href="${{escapeHtml(s.url)}}" target="_blank" rel="noopener">${{escapeHtml(title)}}</a></h2>
                <p class="card-summary">${{escapeHtml(summary)}}</p>
            </div>`;
    }}

    function render() {{
        const matching = allStories.filter(matches);
        $('#result-count').textContent = matching.length;
        if (matching.length === 0) {{
            $('#results').innerHTML = '<div class="empty">No stories match your search. Try clearing some filters.</div>';
            return;
        }}
        // Cap at 150 cards for performance — enough to scroll through
        $('#results').innerHTML = matching.slice(0, 150).map(cardHtml).join('');
        if (window.__bwnStripFlags) window.__bwnStripFlags($('#results'));
    }}

    // Wire up the search input (debounced)
    let searchTimer;
    $('#search-input').addEventListener('input', e => {{
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => {{
            filters.q = e.target.value.toLowerCase().trim();
            render();
        }}, 120);
    }});

    // Wire up chips
    $$('.chip').forEach(chip => {{
        chip.addEventListener('click', () => {{
            const group = chip.dataset.group;
            const value = chip.dataset.value;
            chip.classList.toggle('chip-active');
            if (chip.classList.contains('chip-active')) {{
                filters[group].add(value);
            }} else {{
                filters[group].delete(value);
            }}
            render();
        }});
    }});

    // Clear all
    $('#clear-all').addEventListener('click', () => {{
        filters = {{ q: '', topic: new Set(), region: new Set(), framing: new Set() }};
        $('#search-input').value = '';
        $$('.chip.chip-active').forEach(c => c.classList.remove('chip-active'));
        render();
    }});

    // Fetch and render
    fetch('stories.json')
        .then(r => r.json())
        .then(stories => {{
            allStories = stories.sort((a, b) => (b.saved_at || '').localeCompare(a.saved_at || ''));
            $('#total-count').textContent = stories.length;
            render();
        }})
        .catch(() => {{
            $('#results').innerHTML = '<div class="empty">Could not load stories. Try refreshing the page.</div>';
        }});
</script>

{PWA_SCRIPT}
{CLOUDFLARE_ANALYTICS}
</body>
</html>"""


# ============================================================
# ORIGINAL ARTICLES — long-form explainers we write ourselves.
# Mirrors the comic system: articles.json holds the content, each PUBLISHED
# article renders to article-<slug>.html, and the homepage shows an "Explainers"
# shelf. Drafts (published:false) render nowhere public — no shelf card, no page
# on disk, no sitemap entry — so an unfinished piece can never leak live.
# ============================================================

def article_slug_page(slug):
    # The on-disk filename for a single article's reader page.
    return f"article-{slug}.html"


def published_articles():
    # Published pieces only, newest first (by date).
    arts = [a for a in load_json_file("articles.json") if a.get("published")]
    return sorted(arts, key=lambda a: a.get("date", ""), reverse=True)


def _article_theme_color(theme):
    # Reuse the theme palette the placeholders already use, so an article's
    # colour matches its theme everywhere on the site.
    return _PH_COLORS.get(theme, "#1a3a2a")


def render_article_body(body):
    # Friendly authoring so writing in articles.json stays painless. body may be:
    #   - a raw HTML string (used as-is if it already contains <p>/<h tags),
    #   - a plain-text string (blank lines split into paragraphs), or
    #   - a list of lines, where "## " = heading, "### " = subheading,
    #     "> " = pull quote, "- " = bullet, anything else = paragraph.
    if isinstance(body, str):
        if "<p" in body or "<h" in body:
            return body
        paras = [p.strip() for p in body.split("\n\n") if p.strip()]
        return "".join(f"<p>{p}</p>" for p in paras)

    html, bullets = "", []

    def flush():
        nonlocal bullets, html
        if bullets:
            html += "<ul>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>"
            bullets = []

    for raw in (body or []):
        line = (raw or "").strip()
        if not line:
            continue
        if line.startswith("## "):
            flush(); html += f"<h2>{line[3:].strip()}</h2>"
        elif line.startswith("### "):
            flush(); html += f"<h3>{line[4:].strip()}</h3>"
        elif line.startswith("> "):
            flush(); html += f"<blockquote>{line[2:].strip()}</blockquote>"
        elif line.startswith("- "):
            bullets.append(line[2:].strip())
        else:
            flush(); html += f"<p>{line}</p>"
    flush()
    return html


def build_article_reader(article):
    # One original article as a clean, editorial long-read. Self-contained (like
    # the comic reader) so it can carry a slug-based canonical URL, an og:image,
    # and Article schema that page_shell can't.
    slug   = article.get("slug", "")
    title  = article.get("title", "Untitled")
    dek    = article.get("dek", "")
    theme  = article.get("theme", "")
    series = article.get("series", "")
    date   = article.get("date", "")
    author = article.get("author", "Black World News")
    hero   = article.get("hero_image", "")
    hero_credit = article.get("hero_credit", "")
    colour = _article_theme_color(theme)
    body_html = render_article_body(article.get("body", ""))

    import re as _re
    words   = len(_re.sub("<[^>]+>", " ", body_html).split())
    minutes = max(1, round(words / 200))

    url = f"https://www.blackworldnews.world/{article_slug_page(slug)}"
    og_image = (f"https://www.blackworldnews.world/{hero}" if hero
                else "https://www.blackworldnews.world/logo.svg")

    theme_chip = (f'<span class="theme-chip" style="background:{colour}">{theme}</span>'
                  if theme else "")
    series_html = (f'<p class="series-line">Part of the <strong>{series}</strong> series</p>'
                   if series else "")
    hero_html = ""
    if hero:
        credit = f'<span class="hero-credit">{hero_credit}</span>' if hero_credit else ""
        hero_html = (f'<figure class="article-hero-img">'
                     f'<img src="{hero}" alt="" loading="lazy">{credit}</figure>')

    sources = article.get("sources", [])
    sources_html = ""
    if sources:
        items = "".join(
            f'<li><a href="{s.get("url","#")}" target="_blank" rel="noopener">{s.get("label","")}</a></li>'
            for s in sources)
        sources_html = f'<section class="sources"><h2>Sources</h2><ul>{items}</ul></section>'

    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": dek,
        "datePublished": date,
        "author": {"@type": "Organization", "name": author},
        "publisher": {"@type": "Organization", "name": "Black World News"},
        "image": og_image,
        "mainEntityOfPage": url,
    }, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Black World News</title>
    <meta name="description" content="{dek}">
    <link rel="canonical" href="{url}">
    <meta property="og:type" content="article">
    <meta property="og:site_name" content="Black World News">
    <meta property="og:url" content="{url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{dek}">
    <meta property="og:image" content="{og_image}">
    <meta property="article:published_time" content="{date}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{dek}">
    <meta name="twitter:image" content="{og_image}">
    <meta name="author" content="{author}">
    <script type="application/ld+json">{schema}</script>
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="favicon.svg">
    {PWA_META}
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
        body{{background:#f2f2f2;color:#1a1a1a;font-family:'Source Sans 3',sans-serif;font-size:19px;line-height:1.75;}}
        a{{color:inherit;}}
        .masthead{{background:#1a3a2a;border-bottom:3px solid #111;padding:1rem 1.5rem;display:flex;align-items:center;gap:0.8rem;justify-content:center;}}
        .masthead img{{width:46px;height:46px;}}
        .masthead .brand{{font-family:'Playfair Display',serif;font-size:1.4rem;font-weight:900;color:#fff;letter-spacing:0.04em;text-decoration:none;}}
        .article{{max-width:720px;margin:0 auto;padding:2.5rem 1.5rem 1rem;background:#fff;}}
        @media(min-width:760px){{.article{{margin:2rem auto;border-radius:6px;box-shadow:0 4px 24px rgba(0,0,0,0.06);}}}}
        .theme-chip{{display:inline-block;color:#fff;font-size:0.72rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;padding:0.28rem 0.7rem;border-radius:999px;}}
        .article-title{{font-family:'Playfair Display',serif;font-weight:900;font-size:clamp(1.8rem,5.5vw,2.7rem);line-height:1.12;margin:0.9rem 0 0.6rem;color:#111;}}
        .article-dek{{font-size:1.18rem;color:#444;line-height:1.5;margin-bottom:1.1rem;}}
        .byline{{font-size:0.85rem;color:#777;border-bottom:1px solid #e3e3e3;padding-bottom:1.2rem;letter-spacing:0.02em;}}
        .series-line{{font-size:0.82rem;color:#1a3a2a;margin:1.1rem 0 0;}}
        .article-hero-img{{margin:1.4rem 0 0;}}
        .article-hero-img img{{width:100%;height:auto;border-radius:6px;display:block;}}
        .hero-credit{{display:block;font-size:0.72rem;color:#999;margin-top:0.35rem;}}
        .article-body{{margin-top:1.4rem;}}
        .article-body p{{margin:0 0 1.15rem;}}
        .article-body p:first-of-type::first-letter{{font-family:'Playfair Display',serif;font-size:3.1rem;font-weight:900;float:left;line-height:0.78;margin:0.2rem 0.6rem 0 0;color:#1a3a2a;}}
        .article-body h2{{font-family:'Playfair Display',serif;font-size:1.5rem;font-weight:700;color:#1a3a2a;margin:2rem 0 0.8rem;}}
        .article-body h3{{font-size:1.15rem;font-weight:700;color:#111;margin:1.5rem 0 0.6rem;}}
        .article-body blockquote{{border-left:4px solid #1a3a2a;background:#f6f8f6;margin:1.6rem 0;padding:1rem 1.3rem;font-family:'Playfair Display',serif;font-size:1.3rem;font-style:italic;color:#1a3a2a;}}
        .article-body ul{{margin:0 0 1.15rem 1.3rem;}}
        .article-body li{{margin-bottom:0.5rem;}}
        .sources{{max-width:720px;margin:0 auto;padding:0 1.5rem 1.5rem;background:#fff;}}
        @media(min-width:760px){{.sources{{border-radius:0 0 6px 6px;}}}}
        .sources h2{{font-family:'Playfair Display',serif;font-size:1.1rem;color:#1a3a2a;margin-bottom:0.6rem;}}
        .sources ul{{list-style:none;}}
        .sources li{{font-size:0.9rem;margin-bottom:0.4rem;}}
        .sources a{{color:#1a3a2a;font-weight:600;text-decoration:underline;}}
        .article-end{{text-align:center;padding:1.5rem;}}
        .back-btn{{display:inline-block;background:#1a3a2a;color:#fff;padding:0.6rem 1.4rem;border-radius:999px;font-weight:700;text-decoration:none;}}
        footer{{background:#111;border-top:4px solid #1a3a2a;text-align:center;padding:2rem;font-size:0.8rem;color:#555;margin-top:2rem;}}
        footer strong{{color:#8ab89a;}}
    </style>
</head>
<body>
<header class="masthead">
    <a href="index.html"><img src="logo.svg" alt="Black World News"></a>
    <a href="index.html" class="brand">Black World News</a>
</header>

<article class="article">
    {theme_chip}
    <h1 class="article-title">{title}</h1>
    <p class="article-dek">{dek}</p>
    <p class="byline">By {author} &middot; {date} &middot; {minutes} min read</p>
    {series_html}
    {hero_html}
    <div class="article-body">{body_html}</div>
</article>
{sources_html}
<section class="article-end">
    <a href="index.html#explainers" class="back-btn">&larr; More explainers</a>
</section>
<footer>
    <p><strong>BLACK WORLD NEWS</strong> Your World Today</p>
    {social_bar_html()}
    {footer_legal_html()}
</footer>
{PWA_SCRIPT}
{CLOUDFLARE_ANALYTICS}
</body>
</html>"""


def explainers_shelf_html():
    # "Explainers" shelf for the homepage — our own long-form pieces. Returns ""
    # when nothing is published yet, so the homepage simply omits the section.
    arts = published_articles()
    if not arts:
        return ""
    cards = ""
    for a in arts[:6]:
        slug   = a.get("slug", "")
        theme  = a.get("theme", "")
        colour = _article_theme_color(theme)
        hero   = a.get("hero_image", "")
        thumb = (f'<div class="exp-thumb" style="background-image:url(\'{hero}\')"></div>'
                 if hero else
                 f'<div class="exp-thumb" style="background:{colour}"></div>')
        chip = f'<span class="exp-chip" style="background:{colour}">{theme}</span>' if theme else ""
        cards += f"""
        <a class="exp-card" href="{article_slug_page(slug)}">
            {thumb}
            <div class="exp-body">{chip}
                <h3 class="exp-title">{a.get('title','')}</h3>
                <p class="exp-dek">{a.get('dek','')}</p>
            </div>
        </a>"""
    return f"""
    <!-- EXPLAINERS — our own long-form pieces -->
    <div class="container" id="explainers">
        <p class="section-label">Explainers</p>
        <div class="exp-grid">{cards}
        </div>
    </div>
    <style>
      .exp-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1.1rem;}}
      .exp-card{{display:flex;flex-direction:column;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,0.08);transition:transform .15s;text-decoration:none;color:inherit;}}
      .exp-card:hover{{transform:translateY(-3px);}}
      .exp-thumb{{aspect-ratio:16/9;background-size:cover;background-position:center;}}
      .exp-body{{padding:0.9rem 1rem 1.1rem;}}
      .exp-chip{{display:inline-block;color:#fff;font-size:0.62rem;font-weight:700;letter-spacing:0.07em;text-transform:uppercase;padding:0.2rem 0.55rem;border-radius:999px;margin-bottom:0.5rem;}}
      .exp-title{{font-family:'Playfair Display',serif;font-size:1.15rem;font-weight:700;color:#111;line-height:1.2;margin-bottom:0.35rem;}}
      .exp-dek{{font-size:0.9rem;color:#666;line-height:1.4;}}
    </style>"""


def main():
    stories = load_stories()
    if not stories:
        print("No stories to display.")
        return

    cache = load_image_cache()
    html  = build_html(stories, cache)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    # Build the four content pages
    for filename, builder in [
        ("about.html",     build_about),
        ("reports.html",   build_reports),
        ("resources.html", build_resources),
        ("trends.html",    build_trends),
        ("community.html", build_community),
        ("privacy.html",   build_privacy),
        ("comics.html",    build_comics),
    ]:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(builder())
        print(f"Page generated: {filename}")

    # Build the five region pages
    for region_id, region in REGION_GROUPS.items():
        filename = f"{region_id}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(build_region_page(region_id, region, stories, cache))
        print(f"Region page generated: {filename}")

    # Build the six issue pages
    for issue_id, issue in ISSUE_GROUPS.items():
        filename = f"{issue_id}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(build_issue_page(issue_id, issue, stories, cache))
        print(f"Issue page generated: {filename}")

    # Build the Sports section (theme-filtered, World Cup front and centre)
    with open("sports.html", "w", encoding="utf-8") as f:
        f.write(build_sports(stories, cache))
    print("Sports page generated: sports.html")

    # Build the search page (client-side, reads stories.json in browser)
    with open("search.html", "w", encoding="utf-8") as f:
        f.write(build_search_page())
    print("Search page generated: search.html")

    # Build the kids page (hand-curated content from kids_*.json)
    with open("kids.html", "w", encoding="utf-8") as f:
        f.write(build_kids())
    print("Kids page generated: kids.html")

    # Build one reader page per PUBLISHED comic strip (from comics.json). Only
    # published strips get a deployed page, so a draft can never leak live at its
    # direct URL; unpublished strips also stay off the shelf and out of the sitemap.
    # Any stale page from a now-unpublished strip is removed so it's actually pulled.
    published_comic_pages = []
    for strip in load_json_file("comics.json"):
        slug = strip.get("slug", "")
        if not slug:
            continue
        page = comic_slug_page(slug)
        if strip.get("published"):
            with open(page, "w", encoding="utf-8") as f:
                f.write(build_comic_reader(strip))
            print(f"Comic reader generated: {page}")
            published_comic_pages.append(page)
        elif os.path.exists(page):
            os.remove(page)
            print(f"Comic reader removed (unpublished): {page}")

    # Build one reader page per PUBLISHED article (from articles.json). Same
    # safety as comics: drafts (published:false) get no deployed page, and a
    # now-unpublished article's stale page is removed so it's truly pulled.
    published_article_pages = []
    for art in load_json_file("articles.json"):
        slug = art.get("slug", "")
        if not slug:
            continue
        page = article_slug_page(slug)
        if art.get("published"):
            with open(page, "w", encoding="utf-8") as f:
                f.write(build_article_reader(art))
            print(f"Article generated: {page}")
            published_article_pages.append(page)
        elif os.path.exists(page):
            os.remove(page)
            print(f"Article removed (unpublished): {page}")

    save_image_cache(cache)
    print(f"Site generated: {OUTPUT_FILE}")
    print(f"Total stories: {len(stories)}")
    print(f"Images cached: {len(cache)}")

    # --- SITEMAP ---
    # Tells Google every page that exists on the site
    today = datetime.now().strftime("%Y-%m-%d")
    comic_sitemap_urls = "".join(
        f'\n  <url><loc>https://www.blackworldnews.world/{page}</loc>'
        f'<lastmod>{today}</lastmod><priority>0.6</priority></url>'
        for page in published_comic_pages
    )
    article_sitemap_urls = "".join(
        f'\n  <url><loc>https://www.blackworldnews.world/{page}</loc>'
        f'<lastmod>{today}</lastmod><priority>0.7</priority></url>'
        for page in published_article_pages
    )
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://www.blackworldnews.world/</loc><lastmod>{today}</lastmod><priority>1.0</priority></url>
  <url><loc>https://www.blackworldnews.world/namerica.html</loc><lastmod>{today}</lastmod><priority>0.9</priority></url>
  <url><loc>https://www.blackworldnews.world/caribbean.html</loc><lastmod>{today}</lastmod><priority>0.9</priority></url>
  <url><loc>https://www.blackworldnews.world/samerica.html</loc><lastmod>{today}</lastmod><priority>0.9</priority></url>
  <url><loc>https://www.blackworldnews.world/africa.html</loc><lastmod>{today}</lastmod><priority>0.9</priority></url>
  <url><loc>https://www.blackworldnews.world/europe.html</loc><lastmod>{today}</lastmod><priority>0.9</priority></url>
  <url><loc>https://www.blackworldnews.world/asia.html</loc><lastmod>{today}</lastmod><priority>0.9</priority></url>
  <url><loc>https://www.blackworldnews.world/policing.html</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>
  <url><loc>https://www.blackworldnews.world/politics.html</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>
  <url><loc>https://www.blackworldnews.world/economics.html</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>
  <url><loc>https://www.blackworldnews.world/health.html</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>
  <url><loc>https://www.blackworldnews.world/education.html</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>
  <url><loc>https://www.blackworldnews.world/culture.html</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>
  <url><loc>https://www.blackworldnews.world/sports.html</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>
  <url><loc>https://www.blackworldnews.world/kids.html</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>
  <url><loc>https://www.blackworldnews.world/search.html</loc><lastmod>{today}</lastmod><priority>0.7</priority></url>
  <url><loc>https://www.blackworldnews.world/about.html</loc><lastmod>{today}</lastmod><priority>0.6</priority></url>
  <url><loc>https://www.blackworldnews.world/resources.html</loc><lastmod>{today}</lastmod><priority>0.6</priority></url>
  <url><loc>https://www.blackworldnews.world/reports.html</loc><lastmod>{today}</lastmod><priority>0.5</priority></url>
  <url><loc>https://www.blackworldnews.world/trends.html</loc><lastmod>{today}</lastmod><priority>0.6</priority></url>
  <url><loc>https://www.blackworldnews.world/community.html</loc><lastmod>{today}</lastmod><priority>0.5</priority></url>
  <url><loc>https://www.blackworldnews.world/privacy.html</loc><lastmod>{today}</lastmod><priority>0.3</priority></url>
  <url><loc>https://www.blackworldnews.world/comics.html</loc><lastmod>{today}</lastmod><priority>0.6</priority></url>{comic_sitemap_urls}{article_sitemap_urls}
</urlset>"""
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap)
    print("Sitemap generated: sitemap.xml")

    # --- ROBOTS.TXT ---
    # Tells search engine crawlers they are allowed in and where the sitemap is
    robots = """User-agent: *
Allow: /

Sitemap: https://www.blackworldnews.world/sitemap.xml
"""
    with open("robots.txt", "w", encoding="utf-8") as f:
        f.write(robots)
    print("robots.txt generated.")


if __name__ == "__main__":
    main()
