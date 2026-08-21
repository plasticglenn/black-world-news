# HANDOFF — Black World News

> Paste the **"Project context"** block into a fresh chat first, then pick a task
> from **"What's next."** You run the commands and edit files; the assistant
> writes, reviews, and advises from the context below.
>
> Last updated: **2026-08-19**.

---

## Project context  *(paste this into a new window)*

**What BWN is:** a news and education site for the Black world, with a clear
anticolonial editorial lens. Sections: news by region and theme, Sports, Reports
("The Paper Trail"), a Kids area, Comics, and Explainers (original long reads we
write). It is live at **blackworldnews.world**.

**Voice (non negotiable):** the structural analysis is the *engine*; the surface
copy stays neutral and hard to deplatform. **Define the mechanism, do not flag
it.** No buzzwords: never use "Pan-African", "systemic", "diaspora", "narrative",
or "framing" in public copy. Plain, factual, wire service tone. Also, in prose I
write for Glenn: **no dash or hyphen characters at all**, and keep any piece to a
five minute read (about 800 to 900 words); split longer topics into parts.

**Kids rules:** honest about what is happening, hopeful about what people are
doing, **never traumatic**; an adult reviews before publish; no data collection;
never deceive or manipulate kids, form them with truth.

**Stack:** a static site built by `python generate_site.py` from hand curated
JSON files. Free tools only (Groq, Pexels, Cloudflare Workers AI). The machine is
low on compute, so keep everything lean and cloud based; no heavy local
rendering.

---

## Where things stand right now

- **Deploy path (confirmed):** branch `main` pushes to `origin/main`
  (github.com/plasticglenn/black-world-news), which serves GitHub Pages at
  blackworldnews.world via the `CNAME` file. As of 2026-08-19 local `main` is in
  sync with `origin/main`. Ignore the old `origin/master` branch; it is stale and
  the "ahead of master" count means nothing.
- **A daily automation is running.** Recent commits are "Daily refresh: rotate
  featured story" from `pick_featured.py`, which picks a fresh reputable hero each
  day. Expect the working tree to move on its own.
- **Recent design work already shipped:** a responsive narrow homepage layout in
  the BBC style, a compact "In Focus" list, and the logo and title now link home.
- **Explainers:** `crumbling-church-of-money` is **live** (`published:true`). The
  **CFA franc** piece (`slug: cfa-franc`) is still a **draft** (`published:false`)
  and has not shipped.

---

## What's next  *(priority order)*

1. **Ship the CFA franc piece.** Polish the draft in `articles.json`, add a
   `hero_image`, confirm the two source links, set `"published": true`, run
   `python generate_site.py`, verify, push.
2. **Work the writing backlog** in `WRITING_CALENDAR.md` and `ARTICLES.md`:
   Babylon (the keystone, must land before the word is used publicly), then the
   debt trap series, cocoa, Windrush.
3. **Comics.** Generate the Garvey art in Dashtoon (`COMIC_01_GARVEY.md`), apply
   `COMIC_CRAFT_BRIEF.md`, then publish. Strip #2 is Yaa Asantewaa.
4. **Newsletter.** The number one owned channel add (hard to deplatform). Not
   started.
5. **Social and video pipeline.** Drafting exists (`social_post.py`); the full
   pipeline is the next big build.
6. **Older threads:** the Paper Trail "Decoded" layer (needs an extraction
   template); the Africa image placeholders (they self fill on builds, not
   stuck); the book (parked until the USB turns up).

---

## How to publish anything  *(cheat sheet)*

- **Article:** edit `articles.json`, set `"published": true`, run
  `python generate_site.py`, verify, push `main`.
- **Comic:** art into `images/comics/<slug>/` (exact filenames), set
  `"published": true` in `comics.json`, build, push.
- **Featured or highlights:** edit the JSON (reputable sources only, local images
  only), then build. `python pick_featured.py` rotates a fresh reputable hero.

---

## Key files

| File | What it is |
|---|---|
| `generate_site.py` | The builder. Regenerates the whole site. Must finish EXIT 0. |
| `articles.json` | Original articles. Authoring: `## ` heading, `> ` pull quote, `- ` bullet, blank line is a paragraph. `published:false` hides it. |
| `comics.json` | Comic strips and dialogue. `published:false` keeps it off the shelf. |
| `featured.json` / `highlights.json` | The hero and "In Focus" cards. Reputable sources only, local images only. |
| `pick_featured.py` | Rotates a fresh reputable hero by the day (runs daily). |
| `social_post.py` | `python social_post.py 5` drafts social posts for recent stories. |
| `WRITING_CALENDAR.md` / `ARTICLES.md` | The dated schedule and the backlog with an angle for each piece. |
| `COMIC_CRAFT_BRIEF.md` · `CHARACTER_BIBLE.md` · `COMIC_01_GARVEY.md` | Comic craft, characters, and the Garvey production pack. |
| `KIDS_STRATEGY.md` · `EDITORIAL_CALENDAR.md` | Kids rules and the weekly news rhythm. |

When you open a new window, say **"resume from HANDOFF.md"** and pick up at the
CFA franc drop.
