# BLACK WORLD NEWS — Project Checklist

> Live tracker for what's built, what's next, and what's parked.
> Edit this file directly when you complete or change anything.
> Last updated: 2026-05-30

---

## 🧭 START HERE (new session, read this first)

**What this is:** news aggregation for Black communities globally + a confidence-first kids section. Live at **blackworldnews.world**. Repo `plasticglenn/black-world-news`, branch `main`, GitHub Pages auto-deploys ~2 min after push. All code in `C:\Users\glenn\dispatch-agent`.

**The pipeline:**
- `python dispatch.py --all` → collect + AI-analyze stories into `stories.json`
- `python generate_site.py` → build every HTML page from `stories.json`
- `git add -A && git commit && git push` → goes live
- After ANY change: build (confirm `EXIT=0`), commit, push, verify `git rev-parse HEAD` == `origin/main`.

**AI provider:** DeepSeek (pay-as-you-go, no daily wall) — auto-used when `DEEPSEEK_API_KEY` is set, else falls back to Groq. Key is set at Windows User level. NOTE: a persistent Bash shell may have a stale env; PowerShell picks it up fresh, or inject with `$env:DEEPSEEK_API_KEY = [System.Environment]::GetEnvironmentVariable("DEEPSEEK_API_KEY","User")`.

**⚠️ GOTCHAS (these bit us — don't repeat):**
1. **Always open `stories.json` (and all JSON) with `encoding="utf-8"`.** Default Windows cp1252 crashes on foreign characters.
2. **Never let two processes write `stories.json` at once** (e.g. agent + backfill). Concurrent writes corrupt it and break the build. Run one at a time.
3. **The Edit tool silently no-ops if whitespace doesn't match exactly** — several edits "succeeded" but reverted this project. After editing `generate_site.py`, VERIFY with a runtime check: `python -c "import generate_site as g; print(g.SOMETHING)"`, not just by re-reading.
4. **Hotlink-blocked image hosts** (e.g. The Voice) serve a red "blocked" placeholder. Add the host to `HOTLINK_BLOCKED_HOSTS` in `generate_site.py`; we generate our own Pollinations image instead.
5. **PowerShell writes UTF-16 logs** — decode when reading (`open(path,'rb').read().decode('utf-16')`). Prefer redirecting Python output to a UTF-8 file.
6. **Preview server** (`mcp__Claude_Preview__preview_start`, config `bwn-static` in `C:\Users\glenn\.claude\launch.json`) gets stuck — stop/restart it; it's flaky but the HTML on disk is the source of truth.

**Single sources of truth to edit (no code needed):**
- `BRAND = "#1a3a2a"` in `generate_site.py` — one colour across all sections (kids page is the only colourful one).
- `COUNTRY_FLAGS`, `REGION_GROUPS`, `ISSUE_GROUPS` (nav order: Home, Economics, Health, Education, Politics, Culture, Policing — Policing last).
- Kids content: `kids_affirmations.json`, `kids_figures.json`, `kids_countries.json`, `kids_vocab.json`, `kids_news.json`.
- `servants.json` (homepage tribute), `highlights.json` (In Focus).

**Editorial rules (never break):** no hyphens in visible copy; no buzzwords ("Pan-African", "systemic"); neutral wire-service tone. Kids tone = **belonging, not difference** (a global family of shared values — a zeitgeist); brave, beautiful, beautifully made. Framing analysis = one complete sentence, varied opener (never "The story frames…").

**Current state (2026-05-30):** 933 stories. DeepSeek run added 665. Caribbean (88) + 10 African countries with flags are live. Last code commit `c18f013` (country flags); `b620f35` added this handoff block. **Synced with `origin/main`** (the live branch). NOTE: local `main` tracks the stale `origin/master`, so `git status` falsely reports "ahead 92" — verify with `git rev-list --left-right --count main...origin/main` (should be `0  0`), and push with `git push origin main`.

**Next priorities:**
1. Re-tag the ~245 Africa "Other/Global" stories to specific countries (cheap DeepSeek backfill).
2. Prune/fix the ~18 direct sources that returned 0 headlines last run (GhanaWeb, The Voice, MyJoyOnline, Modern Ghana, Nation Africa, Daily Maverick, RAYA, SCMP, Reuters Africa, RFI, The Root, The Grio, Dawn, The Wire, Japan Times, Jamaica Gleaner, Loop Barbados, Trinidad Guardian).
3. Finish any remaining old-story framing backfill: `python backfill_framing.py`.

---

## ✅ LIVE & WORKING

### Core engine
- [x] News agent (`dispatch.py`) — 96 search queries + 8 direct sources
- [x] AI analysis per story (Pan-African lens, Groq Llama 3.3 70B)
- [x] 208+ stories archived in `stories.json`
- [x] Featured story picker (`pick_featured.py` → `featured.json`)
- [x] In Focus highlights — current news, hand-curated (`highlights.json`)
- [x] Servants of the Continent — tribute section below the news (`servants.json`)
- [x] 268 stories archived in `stories.json`
- [x] Single-URL ingest helper (`add_url.py`)
- [x] Site generator (`generate_site.py`)
- [x] Auto-publish pipeline (`run_all.bat`)
- [x] Windows Task Scheduler — every 3 days at 3am

### Direct sources (scraped every run)
- [x] GhanaWeb — Ghana
- [x] Brasil de Fato — Brazil
- [x] Alma Preta — Brazil (Afro-Brazilian focus)
- [x] RAYA — Colombia (Black + Indigenous focus)
- [x] El Heraldo — Colombia (Caribbean coast)
- [x] South China Morning Post — China-Africa angle
- [x] Dawn — Pakistan
- [x] The Wire — India
- [x] The Japan Times — Africa coverage

### Homepage
- [x] Sticky masthead with full BWN logo + Black Star
- [x] "Let my people go" — Exodus 8:1 tagline
- [x] Two-tier nav: topics | regions | search (left-aligned)
- [x] Breaking bar with live date
- [x] Hero block (3-column: text | image | In Focus sidebar)
- [x] Featured image at Pexels large2x (sharp, not grainy)
- [x] Latest grid (6 newest stories with images)
- [x] "For the Children" portal door (multi-color balloon paint title)
- [x] "Around the World" regional teasers grid (neutral colors)

### Topic pages
- [x] 5 region pages (N. America, S. America, Africa, Europe, Asia & Pacific)
- [x] 6 issue pages (Policing, Politics, Economics, Health, Education, Culture)
- [x] Centered masthead with full logo, "What matters to you, today" tagline
- [x] Cards filtered by country/category, newest first

### Search & content pages
- [x] `search.html` — text search + topic/region/framing filter chips
- [x] About, Resources, Trends, Community pages

### Visual identity
- [x] BWN logo with Marcus Garvey Black Star
- [x] Browser tab favicon
- [x] Multi-color balloon paint "Kids Corner" in nav, every page
- [x] Multi-color balloon paint "For the Children" portal title
- [x] All images clickable, link to story

### Mobile
- [x] Sticky compact masthead
- [x] Bottom tab bar on homepage (Home / Topics / World / Search)
- [x] Horizontal scroll nav on topic pages
- [x] Hero collapses cleanly (image first, text, sidebar)
- [x] Latest cards become horizontal swipe strip

### SEO & infrastructure
- [x] `sitemap.xml` with all pages
- [x] `robots.txt`
- [x] Open Graph + Twitter card meta tags
- [x] Canonical URLs
- [x] Custom domain `blackworldnews.world` on Namecheap
- [x] GitHub Pages hosting from `main` branch
- [x] Google Search Console verification
- [x] Cloudflare Web Analytics (privacy-respecting visitor tracking)

### Platforms
- [x] **Web** — blackworldnews.world (live)
- [x] **PWA** — installable on Android Chrome and iOS Safari (Add to Home Screen)
- [ ] **Social media accounts** — IG, X, TikTok, Threads (you sign up; pipeline ready)
- [x] **Social posting pipeline** — `social_post.py` drafts per-platform posts ✅
- [ ] **Android app** — Capacitor wrapper, Google Play Store ($25 one-time)
- [ ] **iOS app** — Capacitor wrapper, App Store ($99/year, much later)

### Admin
- [x] Hidden stats via `?admin` URL parameter
- [x] API keys stored in Windows env vars (never in files)

---

## 🆕 DONE 2026-05-30
- [x] **Caribbean is now its own region** (Jamaica, Barbados, Trinidad & Tobago, Haiti, Bahamas, Guyana) — not lumped into Other/Global. New `caribbean.html`, nav tab, search filter, 🌴 flag.
  - New direct sources scanned every run: Jamaica Gleaner, Nation News (Barbados), Loop Barbados, Trinidad Guardian, Trinidad Newsday (plus existing Jamaica Observer + Caribbean National Weekly).
- [x] **Framing analysis overhauled** — `narrative_analysis` must be ONE complete sentence with a varied opener (banned the repetitive "The story frames..."). `max_tokens=1200` so JSON never truncates mid-sentence. All FUTURE stories use this.
- [x] **Kids portraits** — real public-domain photos of Garvey & Toussaint served locally from `images/` (fixes the Wikimedia hotlink block). Yaa keeps her generated portrait.
- [~] **Framing backfill in progress** — `backfill_framing.py` re-writes old truncated/repetitive analyses + fills missing `cui_bono`. ~half done (boring openers 178→84, truncated 177→92, cui_bono 140→213). **Groq daily limit hit — re-run `python backfill_framing.py` after it resets to finish the rest.**

## 🆕 DONE 2026-05-29
- [x] Logo consolidated — one source of truth (`logo.svg`), homepage no longer has its own copy
- [x] Bugfix: news agent was crashing on startup (UTF-8 encoding in `load_archive`). Fixed.
- [x] News run added 60 stories (208 → 268)
- [x] In Focus now shows current events (African Development Bank, Brazil race quotas, Windrush), not Wikipedia bios
- [x] New "Servants of the Continent" tribute at foot of homepage — Garvey, Lumumba, Marley
  - Edit `servants.json` to change people. Add an `image` and `url` to each when our own articles exist; cards become clickable once `url` is filled.
- [x] **For the Children — Phase 1 LIVE** (`kids.html`). The broken kids link is fixed.
  - Confidence-first mission: teach our children they are brave, beautiful, and beautifully made.
  - Modules: Say It Out Loud (affirmations) → Meet Someone Special (Garvey, Toussaint, Yaa Asantewaa) → A Place to Know (Jamaica, Haiti, Ghana — flags) → From the Big News → Learn a Word → Quiz Time → safe footer.
  - Two age lanes (Little Ones 3-7 / Bigger Kids 8-13) toggle at the top.
  - All content hand-curated in `kids_affirmations.json`, `kids_figures.json`, `kids_countries.json`, `kids_vocab.json`, `kids_news.json`. Edit those to change content — no code needed.
  - Safety: no comments, no chat, no sign-ups, no data collection, no ads.
  - Yaa Asantewaa uses an initials circle (no free-licensed photo exists). Add a portrait URL to `kids_figures.json` if one is ever found.

---

## 🔄 IN PROGRESS

- [x] ✅ Translation backfill — **208 of 208 stories now translated to English** (completed 2026-05-27)
  - Original-language version preserved in `title` / `summary`
  - English in `title_en` / `summary_en`
  - All future stories translated on ingestion via `dispatch.py`

---

## 🚧 NEXT UP (priority order)

### 1. Tomorrow when Groq resets
- [ ] Finish translating the remaining 32 stories
- [ ] Run `python dispatch.py --all` with the 8 new direct sources
- [ ] Ingest any specific articles via `python add_url.py <url>`

### 2. For the Children — full page build
Door is up. **Phase 1 is LIVE** (see DONE 2026-05-29 above). Remaining phases below.

- [x] **Phase 1** — Static `kids.html` with hand-curated content ✅ LIVE
  - Say It Out Loud affirmations (confidence-first)
  - 3 historical figures ("Meet Someone Special")
  - 3 featured countries ("A Place to Know")
  - 3 news stories rewritten for kid language ("From the Big News")
  - Word of the Day vocab
  - Two age lanes toggle (Little Ones 3-7 / Bigger Kids 8-13)
  - Quiz (JavaScript only)
- [ ] **Phase 2** — `kids_content.py` auto-rewrites news at 3rd-grade reading level
- [ ] **Phase 3** — Pollinations AI comic panels (Comic of the Week)
- [x] **Phase 4** — Quiz module (JS only, no backend) — shipped in Phase 1
- [ ] **Phase 5** — Browser text-to-speech reading aloud (deferred — app-level)

**Future vision (Glenn):** the kids section becomes a *portal* — to an online comic and to
videos we generate from scripts we write/generate. The current kids.html is the doorway; the
comic and video experiences live behind it. Tone throughout: **belonging, not difference** —
our children are part of a global community of shared values (building a zeitgeist), brave,
beautiful, and beautifully made.

### 3. More direct sources (optional, low priority)
- [ ] Africa Report (Africa-focused English journalism)
- [ ] AllAfrica.com (continent aggregator)
- [ ] Daily Maverick (South Africa)
- [ ] The Root (US Black community)
- [ ] Caribbean National Weekly

---

## 💭 LATER (planned, not urgent)

- [ ] **Rotate highlights** — bigger pool in `highlights.json`, randomly show 3 per visit
- [ ] **Weekly digest email** — readers subscribe, get a Sunday roundup
- [ ] **Original articles** — you write with AI assistance, with framing guidance
- [ ] **Social media accounts** — IG, X, TikTok (AI-generated assets per platform)
- [ ] **Story submission form** — Community page placeholder is up, needs backend
- [ ] **Comment section / Reader voices** — moderated discussion under stories
- [ ] **Multilingual UI** — French, Portuguese, Spanish editions
- [ ] **Newsletter signup** in footer
- [ ] **Donation / patron support** — Ko-fi or Patreon link

---

## 🤔 MAYBE / FUTURE

- [ ] Native mobile app (iOS + Android)
- [ ] Audio articles (text-to-speech for adult section too)
- [ ] Translation toggle per story (read in English / read in original)
- [ ] Story reactions (emoji-based, no accounts)
- [ ] Switch from Groq to DeepSeek if rate-limits keep blocking
- [ ] Duplicate detection by content similarity (currently URL-based only)

---

## 📂 FILE MAP (for reference)

| File | Purpose |
|------|---------|
| `dispatch.py` | News agent — searches, scrapes, analyzes, saves |
| `add_url.py` | Ingest a single URL on demand |
| `pick_featured.py` | Pick the homepage featured story |
| `generate_site.py` | Build every HTML page from the archive |
| `run_all.bat` | Full pipeline: agent → site → commit → push |
| `stories.json` | Master archive (208+ stories) |
| `image_cache.json` | Cached Pexels image URLs |
| `highlights.json` | Curated In Focus sidebar items |
| `featured.json` | Chosen featured story for homepage |
| `logo.svg` | Full BWN logo (used in mastheads) |
| `favicon.svg` | Simplified logo for browser tabs |
| `CHECKLIST.md` | This file |
| `README.md` | Project bible |

---

## 🎯 RIGHT NOW — WHAT TO DECIDE

To unblock the next build sprint, I need answers on:

1. **For the Children Phase 1** — approve the structure (two age lanes / 5 modules / "What's News for Kids" tone)?
2. **First 3 historical figures** for the kids page — suggestion: Marcus Garvey, Kwame Nkrumah, Sojourner Truth
3. **First 3 featured countries** for "A Place to Know" — suggestion: Ghana, Brazil, Jamaica
4. **Direct sources beyond the current 9** — add any from the "More direct sources" list?

Once you answer those, I can start building For the Children Phase 1 the next time we sit down.
