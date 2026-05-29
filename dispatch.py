# ============================================================
# BLACK WORLD NEWS — News Agent
# This script searches the web for stories, reads them,
# and uses AI to analyze how Black people are being portrayed.
# Run it to collect new stories into your archive.
# ============================================================

# Tools we need — each one has a specific job
import sys                           # used to set output encoding
import json                          # saves and reads the archive file
import os                            # talks to the operating system

# Make sure emojis print correctly on Windows
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from datetime import datetime        # adds timestamps to stories
from ddgs import DDGS                # searches DuckDuckGo for articles
import requests                      # fetches web pages
from bs4 import BeautifulSoup        # pulls text out of web pages
from groq import Groq                # sends articles to AI for analysis
from json_repair import repair_json  # fixes AI responses that aren't perfect JSON

# ---- SETTINGS ----

# Where stories get saved
ARCHIVE_FILE = "stories.json"

# Which AI model to use (running on Groq's free servers)
MODEL = "llama-3.3-70b-versatile"

# Connect to Groq using your API key (stored safely in Windows, not here)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# The countries we sort stories into
COUNTRIES = [
    "Canada", "United States", "United Kingdom", "France", "Germany",
    "Brazil", "South Africa", "Nigeria", "Ghana", "Australia", "Other/Global"
]

# The topics we sort stories into
CATEGORIES = [
    "Policing", "Housing", "Employment", "Education", "Healthcare",
    "Politics", "Culture", "Hate Crime", "Immigration", "Other"
]

# ---- SEARCH QUERIES ----
# These are the searches we run every time the agent collects stories.
# Each one is designed to look at root causes, not repeat Western media framing.

QUERIES = [
    # Explicit racism
    "anti-Black racism news 2025",
    "Black discrimination police brutality 2025",

    # Poverty and homelessness
    "Black homelessness poverty news 2025",
    "African poverty housing crisis 2025",

    # Healthcare
    "Black maternal mortality 2025",
    "Black mental health crisis 2025",
    "Black addiction alcohol drug healthcare 2025",

    # Education
    "Black students suspended expelled 2025",

    # Crime and drug war framing
    "Black crime statistics media framing 2025",
    "war on drugs Black communities impact 2025",
    "drug policy racial disparity Black 2025",

    # Unemployment and economic exclusion
    "Black unemployment economic exclusion 2025",
    "African American jobless rate systemic 2025",

    # Africa
    "Nigeria inequality foreign investment news 2025",
    "South Africa land rights economic justice 2025",
    "Ghana sovereignty development news 2025",
    "West Africa foreign interference economic 2025",
    "Africa debt IMF World Bank 2025",
    "African land grab foreign corporations 2025",
    "East Africa political sovereignty news 2025",
    "African resistance movements 2025",
    "Africa drug trafficking foreign networks 2025",
    "Africa youth unemployment foreign investment 2025",
    "Africa alcohol industry Black communities 2025",

    # Brazil — covered broadly. Largest Black-majority country outside Africa.
    # Whatever happens there shapes millions of Black lives whether framed that way or not.
    "Brazil politics economy news 2025",
    "Brazil police violence favela poverty 2025",
    "Brazil land rights MST inequality 2025",
    "Brazil prison mass incarceration 2025",
    "Brazil corruption economic crisis 2025",
    "Brazil racial democracy myth inequality 2025",
    "Brazil health education public services 2025",
    "Afro-Brazilian quilombo land rights 2025",

    # Colombia — large Black population, largely invisible in national politics
    "Colombia Afro communities Chocó poverty 2025",
    "Colombia Black population land rights violence 2025",
    "Colombia drug war community displacement 2025",
    "Colombia peace deal Black communities 2025",

    # United States
    "African American systemic inequality 2025",
    "Black capital economic power United States 2025",
    "Black business ownership wealth building 2025",
    "US prison industrial complex Black 2025",
    "African American voting rights suppression 2025",
    "Black reparations movement United States 2025",
    "Black community land ownership development 2025",
    "war on drugs African American communities 2025",
    "Black unemployment systemic United States 2025",
    "African American alcohol addiction systemic 2025",

    # Caribbean
    "Caribbean reparations colonial debt 2025",
    "Haiti sovereignty foreign intervention 2025",
    "Jamaica inequality colonial legacy 2025",
    "Caribbean economic sovereignty IMF 2025",
    "Trinidad Barbados decolonization 2025",
    "Caribbean drug war Black communities 2025",
    "Caribbean youth unemployment colonial legacy 2025",
    "Caribbean alcohol industry colonial legacy 2025",

    # Diaspora — UK, France, Netherlands
    "Black British poverty discrimination 2025",
    "Black British drug war stop and search 2025",
    "Black British unemployment systemic 2025",
    "African French discrimination sovereignty 2025",
    "Black French drug policy racial disparity 2025",
    "Afro-Dutch discrimination unemployment 2025",
    "Black British alcohol addiction systemic 2025",
    "Afro-French alcohol drug community impact 2025",

    # ---- RESOURCE EXTRACTION & BUSINESS TRANSACTIONS ----
    # Who is signing deals over African land and resources — and on what terms.
    "Africa mining deal contract foreign company 2026",
    "Congo DRC cobalt lithium mining deal 2026",
    "West Africa gold mining extraction deal 2026",
    "South Africa platinum mining investment 2026",
    "Africa oil gas contract extraction revenue 2026",
    "Africa cocoa coffee commodities trade price 2026",
    "Africa rare earth minerals foreign acquisition 2026",
    "Nigeria oil revenue corruption contracts 2026",
    "Ghana gold cocoa export deal foreign 2026",
    "African resources sovereign wealth fund 2026",

    # ---- LARGE-SCALE FINANCIAL DECISIONS ----
    # IMF conditions, World Bank loans, bilateral agreements, bond markets.
    "IMF loan conditions Africa austerity 2026",
    "World Bank Africa development loan conditions 2026",
    "African Development Bank investment decision 2026",
    "G7 G20 Africa investment pledge 2026",
    "Africa sovereign debt restructuring default 2026",
    "EU Africa trade partnership deal 2026",
    "Africa bilateral trade agreement signed 2026",
    "Africa bond market foreign investor 2026",
    "African currency devaluation economic impact 2026",
    "Black community federal investment United States 2026",
    "opportunity zone Black neighborhood investment United States 2026",

    # ---- FACTORY CLOSURES & ECONOMIC DISPLACEMENT ----
    # When jobs leave — who bears the cost.
    "factory closure Black community United States 2026",
    "manufacturing plant closure Africa job losses 2026",
    "company layoffs Black workers 2026",
    "South Africa manufacturing closure unemployment 2026",
    "Nigeria factory closure economic crisis 2026",
    "deindustrialisation Black community 2026",
    "mine closure Africa community jobs 2026",
    "corporate divestment Africa 2026",

    # ---- CONFLICT & DISPLACEMENT ----
    # Armed conflict, humanitarian crisis, displacement affecting Black communities.
    "Sudan conflict war displacement crisis 2026",
    "Congo DRC conflict war minerals displacement 2026",
    "Sahel conflict security crisis 2026",
    "Somalia conflict humanitarian crisis 2026",
    "Mozambique insurgency conflict 2026",
    "Haiti gang violence crisis humanitarian 2026",
    "Ethiopia conflict displacement 2026",
    "Nigeria Boko Haram banditry conflict 2026",
    "Mali Burkina Faso conflict coup 2026",
    "Africa refugee displaced persons conflict 2026",

    # Asia and Pacific — Africa trade and geopolitics
    # Our angle: how do the largest Asian economies shape conditions on the African continent?
    "China Africa investment debt sovereignty 2025",
    "China Belt and Road Africa infrastructure 2025",
    "China Africa land deals mining resources 2025",
    "India Africa trade summit cooperation 2025",
    "India Africa investment development 2025",
    "Asia Africa trade relations economic 2025",
    "China Africa military presence influence 2025",
    "IMF World Bank Africa debt Asian alternatives 2025",
]


# ---- FUNCTIONS ----

def load_archive():
    # Open the saved stories file. If it doesn't exist yet, start with empty list.
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, "r") as f:
            return json.load(f)
    return []


def save_archive(stories):
    # Write the full list of stories to the file on your drive.
    with open(ARCHIVE_FILE, "w") as f:
        json.dump(stories, f, indent=2)


def search_stories(query, max_results=10):
    # Search DuckDuckGo and return a clean list of results.
    results = []
    with DDGS() as ddgs:
        search_results = ddgs.text(query, max_results=max_results)
        for result in search_results:
            results.append({
                "title":   result["title"],
                "url":     result["href"],
                "snippet": result["body"]
            })
        return results


def get_article_image(url, soup):
    # Try to find the main image of the article (the one that shows on social media).
    # Websites store this in hidden tags called og:image or twitter:image.
    for prop in ["og:image", "twitter:image"]:
        tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        if tag and tag.get("content"):
            return tag["content"]
    return ""


def analyze_story(title, url, snippet, article_text):
    # Send the article to the AI and get back a structured analysis.
    # We use the full article text if we got it, otherwise the short snippet.
    content = article_text if article_text else snippet

    # This is the instruction we send to the AI — it tells it who it is
    # and exactly what format we want back.
    prompt = f"""You are a media analyst for a news service covering Black communities globally. Analyze news stories through the lens of how Black communities are affected by structural inequality, colonial legacy, and economic exploitation.

You understand that anti-Black racism is rarely explicit. It often appears in how stories about poverty, crime, drugs, alcohol, unemployment, and healthcare are framed when Black people are involved.

Title: {title}
URL: {url}
Content: {content}

Respond in JSON format only with these exact fields:
- "country": one of {COUNTRIES}
- "category": one of {CATEGORIES}
- "summary": 2-3 sentences in English summarizing the story
- "title_en": the headline translated to English (if it is already English, repeat it verbatim)
- "title_es": the headline translated to Spanish
- "title_pt": the headline translated to Portuguese
- "title_fr": the headline translated to French
- "summary_es": the summary translated to Spanish
- "summary_pt": the summary translated to Portuguese
- "summary_fr": the summary translated to French
- "translated": true if the original content was not in English, false otherwise
- "explicit_racism": true if racism is directly named, false if it is implied or structural
- "narrative_framing": one of ["Victim", "Criminal", "Statistic", "Human", "Resistant", "Exploited"]
- "narrative_analysis": 1-2 sentences describing how Black people are framed in this story and what that framing implies
- "structural_factors": list up to 3 systemic factors at play from ["Colonial legacy", "Drug war", "Engineered unemployment", "Alcohol industry targeting", "Land theft", "Foreign debt", "Mass incarceration", "Media bias", "Police violence", "Voter suppression", "Corporate extraction", "None identified"]
- "cui_bono": one plain sentence, maximum 15 words, naming the specific entity or group that benefits most from the conditions described. Name the corporation, government, or industry. If genuinely unclear write "Unclear." No moralizing. Just who gains.

Important: keep all translations natural and concise. Do not add commentary — only translated text.
"""

    raw = ""
    try:
        # Send the prompt to Groq and get the AI's response
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.choices[0].message.content

        # Sometimes AI wraps the response in code blocks — strip those off
        if "```" in raw:
            raw = raw.split("```")[-2] if raw.count("```") >= 2 else raw
            if raw.startswith("json"):
                raw = raw[4:]

        # Pull out just the JSON part and fix any formatting errors
        raw = raw[raw.find("{"):raw.rfind("}")+1].strip()
        data = json.loads(repair_json(raw))

        # Add fields the AI didn't include
        data["title"]    = title
        data["url"]      = url
        data["saved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        return data

    except Exception as e:
        print(f"    ⚠️  Analysis failed: {e}")
        print(f"    Raw (first 300): {raw[:300]}")
        return None


def is_duplicate(story, archive):
    # Check if we already saved this story by comparing URLs.
    for saved in archive:
        if saved.get("url") == story.get("url"):
            return True
    return False


# ---- DIRECT SOURCES ----
# These are sites we visit directly every run — not via search.
# Add any reliable source here and we will always check it.

DIRECT_SOURCES = [
    {
        "name":    "GhanaWeb",
        "url":     "https://www.ghanaweb.com/GhanaHomePage/NewsArchive/",
        "base":    "https://www.ghanaweb.com",
        # CSS selector that finds article links on the page
        "link_selector": "a[href*='/GhanaHomePage/NewsArchive/']",
        "country": "Ghana",
    },
    {
        # Brasil de Fato — independent left Brazilian outlet.
        # Strong on quilombo, racial justice, police violence, MST land struggles.
        "name":    "Brasil de Fato",
        "url":     "https://www.brasildefato.com.br/",
        "base":    "https://www.brasildefato.com.br",
        "link_selector": "a[href*='/2026/'], a[href*='/2025/'], h2 a, h3 a, article a",
        "country": "Brazil",
    },
    {
        # Alma Preta — flagship Afro-Brazilian news outlet.
        # Direct coverage of Black communities, culture, politics, racial justice.
        "name":    "Alma Preta",
        "url":     "https://almapreta.com.br/",
        "base":    "https://almapreta.com.br",
        "link_selector": "h2 a, h3 a, article a, .post-title a",
        "country": "Brazil",
    },
    {
        # RAYA — Colombian investigative outlet.
        # Covers Afro-Colombian communities, ethnic territories, conflict displacement.
        "name":    "RAYA",
        "url":     "https://revistaraya.com/",
        "base":    "https://revistaraya.com",
        "link_selector": "h2 a, h3 a, article a, .entry-title a",
        "country": "Colombia",
    },
    {
        # El Heraldo — Colombian Caribbean-coast daily.
        # Region with largest Afro-Colombian population. Strong local coverage.
        "name":    "El Heraldo",
        "url":     "https://www.elheraldo.co/",
        "base":    "https://www.elheraldo.co",
        "link_selector": "h2 a, h3 a, article a",
        "country": "Colombia",
    },
    {
        # South China Morning Post — Hong Kong independent angle on China-Africa.
        # Better balanced than mainland state media, often covers Belt and Road.
        "name":    "South China Morning Post",
        "url":     "https://www.scmp.com/topics/africa",
        "base":    "https://www.scmp.com",
        "link_selector": "a[href*='/article/'], h2 a, h3 a",
        "country": "Other/Global",
    },
    {
        # Dawn — Pakistan's oldest English daily.
        # Covers South Asia and global affairs including Africa.
        "name":    "Dawn",
        "url":     "https://www.dawn.com/world",
        "base":    "https://www.dawn.com",
        "link_selector": "article a, h2 a, h3 a, .story__link",
        "country": "Other/Global",
    },
    {
        # The Wire (India) — independent, global south perspective.
        # Strong on India-Africa relations, decolonization themes.
        "name":    "The Wire",
        "url":     "https://thewire.in/category/world",
        "base":    "https://thewire.in",
        "link_selector": "article a, h2 a, h3 a, .post-title a",
        "country": "Other/Global",
    },
    {
        # The Japan Times — Japan's main English daily.
        "name":    "The Japan Times",
        "url":     "https://www.japantimes.co.jp/tag/africa/",
        "base":    "https://www.japantimes.co.jp",
        "link_selector": "article a, h2 a, h3 a, .article_list a",
        "country": "Other/Global",
    },

    # ---- UNITED STATES ----
    {
        # The Root — largest Black American news and culture platform.
        "name":    "The Root",
        "url":     "https://www.theroot.com/",
        "base":    "https://www.theroot.com",
        "link_selector": "h2 a, h3 a, article a, .headline a",
        "country": "United States",
    },
    {
        # The Grio — Black American news, politics, entertainment.
        "name":    "The Grio",
        "url":     "https://thegrio.com/",
        "base":    "https://thegrio.com",
        "link_selector": "h2 a, h3 a, article a, .entry-title a",
        "country": "United States",
    },

    # ---- UNITED KINGDOM ----
    {
        # The Voice — the UK's leading Black newspaper since 1982.
        "name":    "The Voice UK",
        "url":     "https://www.voice-online.co.uk/news/",
        "base":    "https://www.voice-online.co.uk",
        "link_selector": "h2 a, h3 a, article a, .post-title a",
        "country": "United Kingdom",
    },

    # ---- CARIBBEAN ----
    {
        # Jamaica Observer — Jamaica's leading daily.
        "name":    "Jamaica Observer",
        "url":     "https://www.jamaicaobserver.com/latest-news/",
        "base":    "https://www.jamaicaobserver.com",
        "link_selector": "h2 a, h3 a, article a, .story-title a",
        "country": "Other/Global",
    },
    {
        # Caribbean National Weekly — diaspora-focused Caribbean news.
        "name":    "Caribbean National Weekly",
        "url":     "https://www.caribbeannationalweekly.com/",
        "base":    "https://www.caribbeannationalweekly.com",
        "link_selector": "h2 a, h3 a, article a, .entry-title a",
        "country": "Other/Global",
    },

    # ---- SOUTH AFRICA ----
    {
        # Daily Maverick — South Africa's best investigative outlet.
        "name":    "Daily Maverick",
        "url":     "https://www.dailymaverick.co.za/",
        "base":    "https://www.dailymaverick.co.za",
        "link_selector": "h2 a, h3 a, article a, .article-title a",
        "country": "South Africa",
    },

    # ---- NIGERIA ----
    {
        # Premium Times — Nigeria's top investigative newspaper.
        "name":    "Premium Times Nigeria",
        "url":     "https://www.premiumtimesng.com/",
        "base":    "https://www.premiumtimesng.com",
        "link_selector": "h2 a, h3 a, article a, .post-title a",
        "country": "Nigeria",
    },
    {
        # The Punch — Nigeria's highest-circulation daily.
        "name":    "The Punch Nigeria",
        "url":     "https://punchng.com/",
        "base":    "https://punchng.com",
        "link_selector": "h2 a, h3 a, article a, .post-title a",
        "country": "Nigeria",
    },

    # ---- FRANCE / FRANCOPHONE AFRICA ----
    {
        # RFI English — Radio France Internationale, best Francophone Africa coverage in English.
        "name":    "RFI English",
        "url":     "https://www.rfi.fr/en/africa/",
        "base":    "https://www.rfi.fr",
        "link_selector": "h2 a, h3 a, article a, .article__title a",
        "country": "Other/Global",
    },

    # ---- BROADER AFRICA ----
    {
        # Africa Report — pan-African business and politics, English.
        "name":    "Africa Report",
        "url":     "https://www.theafricareport.com/",
        "base":    "https://www.theafricareport.com",
        "link_selector": "h2 a, h3 a, article a, .entry-title a",
        "country": "Other/Global",
    },

    {
        # BBC Africa — major English-language Africa desk.
        "name":    "BBC Africa",
        "url":     "https://www.bbc.com/news/world/africa",
        "base":    "https://www.bbc.com",
        "link_selector": "a[href*='/news/articles/'], a[href*='/news/world-africa-'], h2 a, h3 a",
        "country": "Other/Global",
    },
    {
        # Reuters Africa — newswire, most cited Africa source globally.
        "name":    "Reuters Africa",
        "url":     "https://www.reuters.com/world/africa/",
        "base":    "https://www.reuters.com",
        "link_selector": "a[href*='/world/africa/'], a[data-testid*='Heading'], h3 a",
        "country": "Other/Global",
    },
    {
        # Al Jazeera English — strong Africa, Caribbean, diaspora coverage.
        "name":    "Al Jazeera",
        "url":     "https://www.aljazeera.com/africa/",
        "base":    "https://www.aljazeera.com",
        "link_selector": "a[href*='/news/'], a[href*='/features/'], h3 a, .gc__title a",
        "country": "Other/Global",
    },
    {
        # AllAfrica — aggregator of every major African newspaper.
        "name":    "AllAfrica",
        "url":     "https://allafrica.com/latest/",
        "base":    "https://allafrica.com",
        "link_selector": "a[href*='/stories/'], a[href*='/view/group/'], h3 a, .headline a",
        "country": "Other/Global",
    },
]

def scrape_direct_source(source, archive):
    # Visits a source directly and pulls the latest headlines.
    # Returns a list of story dicts ready for analysis.
    results = []
    print(f"\n🌐 Checking direct source: {source['name']} ({source['url']})")
    try:
        r    = requests.get(source["url"], timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.select(source["link_selector"])

        seen_urls = set()
        for link in links[:20]:  # take up to 20 headlines per visit
            href  = link.get("href", "")
            title = link.get_text(strip=True)

            if not href or not title or len(title) < 15:
                continue

            # Build full URL if the link is relative
            if href.startswith("/"):
                href = source["base"] + href

            # Skip if already in archive or seen this loop
            if href in seen_urls or any(s.get("url") == href for s in archive):
                continue
            seen_urls.add(href)

            results.append({
                "title":   title,
                "url":     href,
                "snippet": "",
            })

    except Exception as e:
        print(f"  ⚠️  Could not reach {source['name']}: {e}")

    print(f"  Found {len(results)} new headlines from {source['name']}")
    return results


def run_agent(custom_query=None):
    # This is the main function that runs the whole pipeline.
    # It searches, reads, analyzes, and saves stories.

    archive = load_archive()
    new_stories = []

    # Use a single custom query if provided, otherwise run all 57
    queries = [custom_query] if custom_query else QUERIES
    total_queries = len(queries)

    # Always check direct sources first — these are sites we visit every run
    if not custom_query:
        for source in DIRECT_SOURCES:
            direct_stories = scrape_direct_source(source, archive)
            for story in direct_stories:
                if is_duplicate(story, archive):
                    continue
                print(f"Analyzing: {story['title'][:55]}...")
                try:
                    _r    = requests.get(story["url"], timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                    _soup = BeautifulSoup(_r.text, "html.parser")
                    article_text = " ".join([p.get_text() for p in _soup.find_all("p")])[:3000]
                    image_url    = get_article_image(story["url"], _soup)
                except:
                    article_text = ""
                    image_url    = ""

                analyzed = analyze_story(story["title"], story["url"], story["snippet"], article_text)
                if analyzed:
                    # Make sure country is set to Ghana for GhanaWeb stories
                    if not analyzed.get("country") or analyzed["country"] == "Other/Global":
                        analyzed["country"] = source.get("country", analyzed.get("country"))
                    analyzed["image"] = image_url
                    new_stories.append(analyzed)
                    archive.append(analyzed)
                    print(f"✅ {analyzed['country']} | {analyzed['category']} | {analyzed['narrative_framing']} | {analyzed['title'][:35]}")

    for q_index, query in enumerate(queries):
        print(f"\n🔍 [{q_index+1}/{total_queries}] Searching: {query}")
        stories = search_stories(query, max_results=5)
        print(f"Found {len(stories)} results. Analyzing...")

        for i, story in enumerate(stories):

            # Skip if we already have this story
            if is_duplicate(story, archive):
                print(f"⏭️  Skipping duplicate: {story['title'][:50]}")
                continue

            print(f"Analyzing {i+1} of {len(stories)}: {story['title'][:50]}...")

            # Fetch the full article page
            try:
                _r    = requests.get(story["url"], timeout=10)
                _soup = BeautifulSoup(_r.text, "html.parser")
                article_text = " ".join([p.get_text() for p in _soup.find_all("p")])[:3000]
                image_url    = get_article_image(story["url"], _soup)
            except:
                article_text = ""
                image_url    = ""

            # Send to AI for analysis
            analyzed = analyze_story(story["title"], story["url"], story["snippet"], article_text)

            if analyzed:
                analyzed["image"] = image_url
                new_stories.append(analyzed)
                archive.append(analyzed)
                print(f"✅ {analyzed['country']} | {analyzed['category']} | {analyzed['narrative_framing']} | {analyzed['title'][:35]}")

    # Save everything to disk
    save_archive(archive)
    print(f"\n✅ Done! Found {len(new_stories)} new stories. Archive now has {len(archive)} total.\n")
    return new_stories


# ---- START HERE ----
# Run manually:      python dispatch.py
# Run in background: python dispatch.py --all
if __name__ == "__main__":
    if "--all" in sys.argv:
        # Skip the prompt — run all queries automatically (used for scheduled runs)
        run_agent(None)
    else:
        try:
            query = input("Enter a search term (or press Enter to run all queries): ")
        except EOFError:
            query = ""
        run_agent(query if query else None)
