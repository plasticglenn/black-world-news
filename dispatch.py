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
# Each one is designed with a Pan-African lens — we're looking at root causes,
# not repeating Western media framing.

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

    # Brazil
    "Brazil racial inequality land rights 2025",
    "Afro-Brazilian quilombo land rights 2025",
    "Brazil anti-Black police violence favela 2025",
    "Brazil indigenous Black sovereignty 2025",
    "Brazil drug war Black communities 2025",
    "Afro-Brazilian unemployment economic exclusion 2025",
    "Brazil alcohol addiction Black communities 2025",

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
    prompt = f"""You are a Pan-African media analyst. Your job is to analyze news stories through the lens of how Black communities globally are affected by systemic racism, colonial legacy, and economic exploitation.

You understand that anti-Black racism is rarely explicit — it often appears in how stories about poverty, crime, drugs, alcohol, unemployment, and healthcare are framed when Black people are involved.

Title: {title}
URL: {url}
Content: {content}

Respond in JSON format only with these exact fields:
- "country": one of {COUNTRIES}
- "category": one of {CATEGORIES}
- "summary": 2-3 sentences in English summarizing the story
- "translated": true if the original content was not in English, false otherwise
- "explicit_racism": true if racism is directly named, false if it is implied or structural
- "narrative_framing": one of ["Victim", "Criminal", "Statistic", "Human", "Resistant", "Exploited"]
- "narrative_analysis": 1-2 sentences describing how Black people are framed in this story and what that framing implies
- "structural_factors": list up to 3 systemic factors at play from ["Colonial legacy", "Drug war", "Engineered unemployment", "Alcohol industry targeting", "Land theft", "Foreign debt", "Mass incarceration", "Media bias", "Police violence", "Voter suppression", "Corporate extraction", "None identified"]
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


def run_agent(custom_query=None):
    # This is the main function that runs the whole pipeline.
    # It searches, reads, analyzes, and saves stories.

    archive = load_archive()
    new_stories = []

    # Use a single custom query if provided, otherwise run all 57
    queries = [custom_query] if custom_query else QUERIES
    total_queries = len(queries)

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
