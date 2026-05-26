# BLACK WORLD NEWS — Project Bible
> Last updated: May 2026
> Written so any developer, AI, or Glenn himself can pick this up and continue.

---

## WHAT THIS IS

Black World News is a Pan-African news aggregation and analysis platform.
It automatically searches the web for stories involving Black communities globally,
analyzes them using AI through a Pan-African lens, and publishes them to a website.

Live site: https://www.blackworldnews.world
GitHub: https://github.com/plasticglenn/black-world-news

---

## WHERE EVERYTHING LIVES

All project files are in one folder:
```
C:\Users\glenn\dispatch-agent\
```

| File | What it does |
|------|-------------|
| `dispatch.py` | The news agent — searches web, analyzes stories, saves to archive |
| `generate_site.py` | Reads the archive and builds the website (index.html) |
| `stories.json` | The full story archive — every saved story lives here |
| `image_cache.json` | Cached Pexels image URLs so we don't re-fetch every time |
| `index.html` | The generated website — this is what gets published |
| `CNAME` | Tells GitHub Pages to use blackworldnews.world |
| `README.md` | This file |

---

## HOW TO RUN IT

### Step 1 — Collect new stories
```powershell
cd C:\Users\glenn\dispatch-agent
python dispatch.py
```
- Press Enter to run all 57 queries
- Or type a specific search term for a targeted run
- Takes 20-40 minutes for a full run
- Saves results to stories.json

### Step 2 — Generate the website
```powershell
python generate_site.py
```
- Reads stories.json
- Fetches images from Pexels
- Builds index.html
- First run takes a few minutes (fetching images)
- Subsequent runs are fast (images cached)

### Step 3 — Publish to live site
```powershell
git add index.html image_cache.json stories.json
git commit -m "Update stories"
git push origin main
```
- Wait 2-3 minutes for GitHub Pages to rebuild
- Check https://www.blackworldnews.world

---

## API KEYS & ENVIRONMENT VARIABLES

These are stored as Windows environment variables — NOT in any file.
To check they're set:
```powershell
echo $env:GROQ_API_KEY
echo $env:PEXELS_API_KEY
```

To reset them if lost:
```powershell
[System.Environment]::SetEnvironmentVariable("GROQ_API_KEY", "your-key-here", "User")
[System.Environment]::SetEnvironmentVariable("PEXELS_API_KEY", "your-key-here", "User")
```

| Service | Purpose | Get key at |
|---------|---------|-----------|
| Groq | AI analysis (free) | console.groq.com |
| Pexels | Story images (free) | pexels.com/api |

---

## PYTHON LIBRARIES REQUIRED

If you ever set this up on a new machine, install these:
```powershell
pip install groq ddgs requests beautifulsoup4 json-repair
```

Python version: 3.13
Ollama is installed locally but no longer used (replaced by Groq)

---

## HOW THE AGENT WORKS (dispatch.py)

1. Loops through 57 search queries in QUERIES list
2. For each query, DuckDuckGo returns 5 results
3. For each result:
   - Fetches full article text with requests + BeautifulSoup
   - Grabs og:image from the page if available
   - Sends title + content to Groq (Llama 3.3 70B model)
   - Groq analyzes and returns JSON with:
     - country, category, summary
     - narrative_framing (Criminal/Victim/Human/Resistant/Exploited/Statistic)
     - narrative_analysis (1-2 sentence framing assessment)
     - structural_factors (up to 3 systemic forces)
     - explicit_racism (true/false)
     - translated (true/false)
4. Checks for duplicates by URL before saving
5. Saves all new stories to stories.json

### To change the AI model:
In dispatch.py, line near top:
```python
MODEL = "llama-3.3-70b-versatile"
```
Replace with any Groq-supported model. See: console.groq.com/docs/models

### To add new search queries:
In dispatch.py, find the QUERIES list and add new strings.
Keep them specific and framed from a Pan-African lens — not Western media framing.

---

## HOW THE SITE WORKS (generate_site.py)

1. Loads stories.json
2. Loads image_cache.json
3. Finds featured story by matching FEATURED_KEYWORD
4. For each story card:
   - Uses og:image if available
   - Otherwise searches Pexels by category + country + title
   - Caches the result so it's not fetched again
5. Builds full HTML with embedded CSS
6. Writes index.html

### To change the featured story:
In generate_site.py, near the top:
```python
FEATURED_KEYWORD = "Youth Unemployment"
```
Change to any word or phrase from the title of the story you want featured.
Run python generate_site.py again to regenerate.

### To change the tagline:
Search for "Let my people go" in generate_site.py and replace.

---

## WRITING RULES (always follow these)

- **No hyphens in copy. Ever.** Not in headlines, summaries, page text, or UI labels. Use a period or rewrite the sentence instead.
- **No buzzwords.** Words like "Pan-African", "systemic", "narrative framing", "structural forces" do not appear in visible copy. The analysis happens quietly under the hood.
- **Neutral tone in public-facing text.** The site sounds like a wire service. Plain, direct, no jargon, no signals of advocacy.
- **Serious and simple. Not academic.** The subject is serious. The writing is not in a classroom.

---

## GITHUB & HOSTING

- Repo: https://github.com/plasticglenn/black-world-news
- Hosting: GitHub Pages (free)
- Domain: blackworldnews.world (registered on Namecheap, C$3.40/yr)
- Domain DNS: Configured in Namecheap Advanced DNS pointing to GitHub Pages IPs
- CNAME file in repo tells GitHub Pages about the custom domain

### GitHub login:
Username: plasticglenn

### If GitHub Pages stops working:
1. Go to github.com/plasticglenn/black-world-news
2. Settings → Pages
3. Make sure Source is set to "main" branch, "/" root

---

## ROADMAP (as of May 2026)

### Done ✅
- News agent collecting stories from 57 queries
- AI narrative analysis with Pan-African framing
- Website with featured story, latest grid, kids section, archive by region
- Mobile app-style layout
- Pexels images on cards
- Custom domain blackworldnews.world
- GitHub Pages hosting

### Up next 🔜
1. AI reads stories aloud to kids (text-to-speech in Kids Corner)
2. Search and filter on the website
3. Kids section comic-style images via Pollinations
4. Weekly digest email to subscribers
5. Narrative trends dashboard (framing stats over time)
6. Auto-run on a schedule (when ready — not yet)
7. Language support (French, Portuguese for West Africa and Brazil)
8. Community features (reader story submissions)

---

## IF YOU'RE STARTING FRESH WITH A NEW AI

Give the AI this file and say:
> "Read this README. This is my Black World News project.
> All files are in C:\Users\glenn\dispatch-agent\
> I want to continue building from where we left off."

The AI will have everything it needs to pick up where we left off.

---

## THE VISION (in Glenn's words)

Black World News is for Black community members keeping up with stories
involving the Black community around the world. Researchers and activists
will find it useful but it's not built for academics. It's built for families —
parents reading with kids, kids reading alone, and eventually AI reading
stories to kids.

The site analyzes not just explicit racism but the narrative framing of
how Black people are portrayed across global media — framing them as
criminals, statistics, victims, or (correctly) as resistant and human.

The goal is a Pan-African media monitor that feels like a professional
news outlet, not an alternative media site. Think BBC. Think CNN. But
with a Black world lens.

---

## CONTACT / ACCOUNTS

| Service | Username/Login |
|---------|---------------|
| GitHub | plasticglenn |
| Namecheap | glenna.asare@gmail.com |
| Groq | glenna.asare@gmail.com |
| Pexels | glenna.asare@gmail.com |

---

*Built with Claude (Anthropic) — May 2026*
*"Let my people go, that they may serve me." – Exodus 8:1*
