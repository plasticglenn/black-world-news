# Writing Calendar — Black World News

> The **when** for our original writing. Pairs with `ARTICLES.md` (the backlog —
> *what* and *why*) and slots into the weekly rhythm in `EDITORIAL_CALENDAR.md`
> (the news-curation loop). Comic quality bar lives in `COMIC_CRAFT_BRIEF.md`.
> Voice on every piece: structural lens as the engine, surface copy neutral and
> un-deplatformable — *define the mechanism, don't flag it.*
> Last updated: 2026-06-21

---

## ✅ Prerequisite — DONE (built 2026-06-21)

The article-publishing path now exists, mirroring the comic system:

- **`articles.json`** holds every piece (friendly authoring: `## ` heading,
  `> ` pull quote, `- ` bullet, blank line = paragraph).
- **`build_article_reader()`** renders each published piece to
  `article-<slug>.html` — editorial long-read template with theme chip, dek,
  auto reading-time, drop-cap, pull quotes, sources block, og:image + Article
  schema for SEO.
- **Explainers shelf** on the homepage (`#explainers`) shows published pieces.
- **Draft safety** (same as comics): `published:false` → no page on disk, no
  shelf card, no sitemap entry. A draft can never leak live.

**To publish any piece:** set `"published": true` in `articles.json`, run
`python generate_site.py`, verify, push.

The CFA franc starter draft is already seeded (`slug: cfa-franc`,
`published:false`) — polish it (or paste your own), add a `hero_image`, confirm
the source links, flip `published`, and Drop 1 is live.

---

## The cadence

- **One original piece every 2 weeks**, dropping **Thursday** (midweek, lands
  before the weekend reading bump). Sustainable on top of the ~2h/week news loop
  — budget **~1–2h/week** of writing on drop weeks.
- **Weekly is possible** once drafts flow — these are tight "define the
  mechanism" explainers (~800–1,200 words), not essays.
- **One piece in flight at a time.** Block rhythm: *draft-by Monday → polish
  Tue–Wed → drop Thursday → that piece feeds the week's socials* (and, where
  noted, a video).
- Protect the cadence, not the ego: **better to slip a drop than ship thin**
  (same rule as `EDITORIAL_CALENDAR.md` — post nothing over low-quality).

---

## How it slots into the weekly skeleton

| Day | Existing (news loop) | + Writing (on a drop week) |
|---|---|---|
| **Sun** | Plan the week | Confirm the piece in flight; 30-min outline |
| **Mon** | Agent runs · featured · 5 social drafts | **Draft-by today** |
| **Tue–Wed** | Post from queue | Polish slot (~1h) |
| **Thu** | Post from queue | **DROP** — generate + push; draft socials from the new piece |
| **Fri** | Reflect on traction | Note how the drop landed |

---

## The drop schedule

| # | Drop date | Piece | Series | Notes / tie-in | Status |
|---|---|---|---|---|---|
| 1 | **Thu 25 Jun 2026** | The CFA franc | Debt Trap (opener) | **Already drafted** — polish + ship first | ✅ ready |
| 2 | Thu 09 Jul 2026 | Babylon — what the word means | Keystone | Unlocks public use of "Babylon"; also do the kid-gentle version | 💡 idea |
| 3 | Thu 23 Jul 2026 | Structural adjustment | Debt Trap 2 | "Cut spending, chase exports, repay" — what it did to schools & clinics | 💡 idea |
| 4 | Thu 06 Aug 2026 | Odious debt | Debt Trap 3 | Name the lenders who knew | 💡 idea |
| 5 | Thu 20 Aug 2026 | The word "aid" | Debt Trap 4 (capstone) | Which way the money really flows | 💡 idea |
| 6 | Thu 03 Sep 2026 | Your chocolate & the farmer | Land & Resources | **Cocoa TikTok script already exists** → article + video the same week | 💡 idea |
| 7 | Thu 17 Sep 2026 | Windrush — invited, then betrayed | Throughline | Image already made (`images/windrush.jpg`) | 💡 idea |
| 8 | Thu 01 Oct 2026 | *(buffer / next backlog pick)* | — | Catch-up week or a fresh idea | ⬜ open |

> **Why CFA is #1 and Babylon #2:** ship the thing that's already written first.
> Babylon still lands (Drop 2) before the word "Babylon" appears anywhere in
> public copy.

**Weekly option:** if drafts flow, halve the gaps — drops every Thursday
(25 Jun, 02 Jul, 09 Jul, …) clears the whole backlog by mid-August.

---

## Comics track (parallel — gated on art, not writing, ~every 6 weeks)

Apply `COMIC_CRAFT_BRIEF.md` to each. Characters already locked in
`CHARACTER_BIBLE.md`.

| # | Target week | Strip | Hook | Status |
|---|---|---|---|---|
| 1 | week of 22 Jun 2026 | Kojo & Ama Meet Marcus Garvey | Scripted & dialogued; **ship when Dashtoon art lands** | 🎨 art pending |
| 2 | week of 03 Aug 2026 | Kojo & Ama Meet Yaa Asantewaa | "Girls lead too" + Ghana (ties to kids countries) | ✍️ to script |
| 3 | week of 14 Sep 2026 | Kojo & Ama Meet Toussaint Louverture | Being brave can change everything + Haiti | ✍️ to script |
| 4 | week of 26 Oct 2026 | *(open)* | — | ⬜ open |

---

## This week — Sun 21 Jun 2026

1. ~~Build the article-publishing path~~ — **done.**
2. Polish the seeded **CFA franc** draft (or paste your own); add a hero image; confirm source links.
3. Set `"published": true`, rebuild, and **drop it Thu 25 Jun.**

---

## Standing rules

- **Voice:** structural lens as engine, neutral un-deplatformable surface (see `ARTICLES.md` + the Rodney content-voice memory).
- **One piece in flight.** Don't start #3 while #2 is unfinished.
- **Draft-by Monday or the drop slips** — and that's fine; thin pieces hurt more than a skipped week.
- **Every drop has a downstream life:** a newsletter section (once the list exists) + a social repurpose (carousel + short). The article is the source; socials are the echo.
