# BLACK WORLD NEWS — Project Checklist

> Live tracker for what's built, what's next, and what's parked.
> Edit this file directly when you complete or change anything.
> Last updated: 2026-05-29

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
