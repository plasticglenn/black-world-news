# HANDOFF — Black World News

> Working pause: **2026-06-21 → resume ~2026-07-01**. This doc lets a free
> assistant pick up the work cold. **You** run the commands and edit files; the
> assistant writes, reviews, and advises from the context below.
> How to use it: paste the **"Project context"** block into a fresh chat first,
> then pick a task from **"What a free assistant can do for you."**

---

## ⚠️ Before you step away — deploy check

Everything from this session is **local and not yet live.** If you want it live,
run one build + deploy:

```
python generate_site.py        # must finish EXIT 0
```

then verify and push the way you normally deploy. Until you do, these stay
staged (not on the site):
- the **comic pulled down** (flawed art),
- the **reputable-source gate** on the hero,
- the **highlight image fixes**.

The **CFA article stays a draft** (`published:false`) — leave it that way until
it's polished.

**Git note:** `main` is ~155 ahead of `origin/master`. Confirm your real deploy
path before pushing — don't force anything blindly.

---

## Project context  *(paste this into the free assistant)*

**What BWN is:** a news + education site for the Black world, with a clear
anti-colonial editorial lens. Sections: news by region/theme, Sports, Reports
("The Paper Trail"), a Kids area, Comics, and Explainers (long-form pieces we write).

**Voice (non-negotiable):** the structural analysis is the *engine*; the surface
copy stays neutral and "un-deplatformable" — **define the mechanism, don't flag
it.** No buzzwords: never use "Pan-African", "systemic", "diaspora", "narrative",
or "framing" in public copy. Plain, factual, wire-service tone.

**Kids rules:** honest about what's happening, hopeful about what people are
doing, **never traumatic**; an adult reviews before publish; no data collection;
and never deceive or manipulate kids — form them with truth.

**Stack:** a static site built by `python generate_site.py` from hand-curated
JSON files. Free tools only (Groq, Pexels, Cloudflare Workers AI). The machine is
low-compute — keep everything lean and cloud-based; no heavy local rendering.

---

## What we did this session

1. **Pulled the flawed comic** off the live shelf, deleted its reader page, removed it from the sitemap, and fixed the generator so a draft strip can never leak live again.
2. **Reputable-source gate for the hero** (`pick_featured.py`): only vetted news organisations (wire/quality press + diaspora/African/Caribbean/Latin outlets) can be featured. Audited the highlights, replaced one off-objective image, and made all highlight images local so they can't break.
3. **Strategy lock-in:** the work is *political education, not slop or propaganda* — true + high-craft, kids held to a higher bar.
4. **Comic craft teardown** → `COMIC_CRAFT_BRIEF.md` (what the best kids' comics do, applied to our strips).
5. **Writing calendar** → `WRITING_CALENDAR.md` (a dated cadence for original pieces + comics).
6. **Built the article-publishing system** (was missing entirely): `articles.json` + a long-read template + a homepage "Explainers" shelf, with the same draft-safety as comics. Seeded a real **CFA franc starter draft** (`published:false`).

---

## What's next  *(priority order)*

1. **Ship the CFA franc piece (Drop 1).** Polish the draft in `articles.json` (or paste your own), add a `hero_image`, confirm the two source links, set `"published": true`, rebuild, push.
2. **Work the writing backlog** — Babylon (the keystone, must land before the word is used publicly), then the debt-trap series, cocoa, Windrush. All in `WRITING_CALENDAR.md` / `ARTICLES.md`.
3. **Comics** — generate the Garvey art in Dashtoon (`COMIC_01_GARVEY.md`), apply `COMIC_CRAFT_BRIEF.md`, then publish. Strip #2 = Yaa Asantewaa.
4. **Social + video pipeline** — not yet spec'd (the next big build when you're back).
5. **Newsletter** — the #1 owned-channel add (un-deplatformable). Not started.
6. **Older threads:** the Paper Trail "Decoded" layer (needs your extraction template); ~115 Africa image placeholders (self-fill on builds, not stuck); the book (parked till the USB turns up).

---

## What a free assistant can do for you  *(copy-paste tasks)*

It can't touch your files or run code — but it can write and review. Hand it work like:
- **Polish or write an article.** Paste the draft (or the angle from `ARTICLES.md`) + the voice rules above → get clean copy → you paste it into `articles.json`.
- **Write the next explainer** — e.g. "Write the Babylon piece: trace the word from Rastafari/reggae as the name for the whole machine of domination; neutral surface; no buzzwords."
- **Draft social posts** — paste a story, ask for IG / X / Threads captions + a 30-sec TikTok concept. Rules: no emojis, no hyphens, no buzzwords, lead with the strongest fact, link to the original source (not BWN).
- **Review a source or image** against the rules (reputable outlet? dignified, on-objective, no competitor watermark?).
- **Write a comic script** — strip #2 (Yaa Asantewaa) following the craft brief: one beat per panel, kid-funny moments, show-don't-tell, end on something the reader does.

---

## Key files

| File | What it is |
|---|---|
| `generate_site.py` | The builder. `python generate_site.py` regenerates the whole site. |
| `articles.json` | Original articles. Authoring: `## ` heading, `> ` pull-quote, `- ` bullet, blank line = paragraph. `published:false` = invisible. |
| `comics.json` | Comic strips + dialogue. `published:false` = off the shelf. |
| `featured.json` / `highlights.json` | The hero + "In Focus" cards. **Reputable sources only; local images only.** |
| `pick_featured.py` | `python pick_featured.py` rotates a fresh, reputable hero by the day. |
| `social_post.py` | `python social_post.py 5` drafts social posts for recent stories. |
| `WRITING_CALENDAR.md` | The dated schedule + how to publish. |
| `ARTICLES.md` | The backlog (what to write + the angle for each). |
| `COMIC_CRAFT_BRIEF.md` · `CHARACTER_BIBLE.md` · `COMIC_01_GARVEY.md` | Comic craft, characters, and the Garvey production pack. |
| `KIDS_STRATEGY.md` · `EDITORIAL_CALENDAR.md` | Kids rules + the weekly news rhythm. |

---

## How to publish anything (cheat sheet)

- **Article:** edit `articles.json` → `"published": true` → `python generate_site.py` → verify → push.
- **Comic:** art into `images/comics/<slug>/` (exact filenames) → `"published": true` in `comics.json` → build → push.
- **Featured/highlights:** edit the JSON (reputable sources, local images) → build.

When you're back on the 1st, just say **"resume from HANDOFF.md"** and we pick up at the CFA drop.
