import json 
import os
from datetime import datetime 
from ddgs import DDGS
import requests 
from bs4 import BeautifulSoup
from groq import Groq
from json_repair import repair_json

ARCHIVE_FILE = "stories.json"
MODEL = "llama-3.3-70b-versatile"
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
COUNTRIES = ["Canada", "United States", "United Kingdom", "France", "Germany", "Brazil", "South Africa", "Nigeria", "Ghana", "Australia", "Other/Global"]
CATEGORIES = ["Policing", "Housing", "Employment", "Education", "Healthcare", "Politics", "Culture", "Hate Crime", "Immigration", "Other"]
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

def load_archive():
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, "r") as f:
            return json.load(f)
    return []

def save_archive(stories):
    with open(ARCHIVE_FILE, "w") as f:
        json.dump(stories, f, indent=2)

def search_stories(query, max_results=10):
    results = []
    with DDGS() as ddgs:
        search_results = ddgs.text(query, max_results=max_results)
        for result in search_results:
            results.append({"title": result["title"], "url": result["href"], "snippet": result["body"]})
        return results

def get_article_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = " ".join([p.get_text() for p in paragraphs])
        return text[:3000]
    except:
        return ""

def get_article_image(url, soup):
    for prop in ["og:image", "twitter:image"]:
        tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        if tag and tag.get("content"):
            return tag["content"]
    return ""
    
def analyze_story(title, url, snippet, article_text):
    content = article_text if article_text else snippet 
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
        response = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
        raw = response.choices[0].message.content
        # Strip markdown code fences if present
        if "```" in raw:
            raw = raw.split("```")[-2] if raw.count("```") >= 2 else raw
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw[raw.find("{"):raw.rfind("}")+1].strip()
        data = json.loads(repair_json(raw))
        data["title"] = title
        data["url"] = url
        data["saved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        return data
    except Exception as e:
        print(f"    ⚠️  Analysis failed: {e}")
        print(f"    Raw (first 300): {raw[:300]}")
        return None
    
def is_duplicate(story, archive):
    for saved in archive:
        if saved.get("url") == story.get("url"):
            return True
    return False

def run_agent(custom_query=None):
    archive = load_archive()
    new_stories = []
    queries = [custom_query] if custom_query else QUERIES
    total_queries = len(queries)

    for q_index, query in enumerate(queries):
        print(f"\n🔍 [{q_index+1}/{total_queries}] Searching: {query}")
        stories = search_stories(query, max_results=5)
        print(f"Found {len(stories)} results. Analyzing...")

        for i, story in enumerate(stories):
            if is_duplicate(story, archive):
                print(f"⏭️  Skipping duplicate: {story['title'][:50]}")
                continue
            print(f"Analyzing {i+1} of {len(stories)}: {story['title'][:50]}...")
            try:
                _r = requests.get(story["url"], timeout=10)
                _soup = BeautifulSoup(_r.text, "html.parser")
                article_text = " ".join([p.get_text() for p in _soup.find_all("p")])[:3000]
                image_url = get_article_image(story["url"], _soup)
            except:
                article_text = ""
                image_url = ""
            analyzed = analyze_story(story["title"], story["url"], story["snippet"], article_text)
            if analyzed:
                analyzed["image"] = image_url
                new_stories.append(analyzed)
                archive.append(analyzed)
                print(f"✅ {analyzed['country']} | {analyzed['category']} | {analyzed['narrative_framing']} | {analyzed['title'][:35]}")

    save_archive(archive)
    print(f"\n✅ Done! Found {len(new_stories)} new stories. Archive now has {len(archive)} total.\n")
    return new_stories

if __name__ == "__main__":
    query = input("Enter custom query (or press Enter to run all queries): ")
    query = query if query else None
    run_agent(query)


        


