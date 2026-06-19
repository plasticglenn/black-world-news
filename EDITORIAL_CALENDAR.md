# Editorial Calendar — Black World News

> A repeatable weekly rhythm. Lean, defensible, no burnout.
> Edit this as your real cadence emerges.
> Last updated: 2026-05-27

---

## The weekly skeleton

Each week looks roughly the same. Day-of-week is suggested, not rigid.

| Day | What happens | Who does it | Time |
|---|---|---|---|
| **Sun** | Plan the week. Pick the upcoming featured story. Review last week's analytics. | You | 30 min |
| **Mon** | Agent runs at 3am (automated). Review fresh stories. Pick this week's "Story of the Week". | You + agent | 20 min |
| **Mon** | Update `featured.json`, rotate `highlights.json`. Regenerate + push. | You | 5 min |
| **Mon** | Draft 5 social posts (`python social_post.py 5`). Review + post 1-2 of them. | You | 15 min |
| **Tue** | Post 1-2 more from the queue. | You | 5 min |
| **Wed** | Mid-week check: any new direct-source stories worth fast-tracking? | You | 10 min |
| **Wed** | Post 1-2 more from the queue. | You | 5 min |
| **Thu** | Agent runs at 3am (automated). Quick scan, no posting. | Agent | — |
| **Thu** | Post 1 from the queue. | You | 5 min |
| **Fri** | Reflect on the week. What got traction? What didn't? Note one thing for next week's plan. | You | 15 min |
| **Sat** | Off. Let the work breathe. Maybe post one historical/educational post. | You | 0-5 min |
| **Sun** | Loop back to planning. | You | 30 min |

**Total time per week:** ~2 hours of editorial work. Not full-time. Sustainable.

---

## Story selection — what becomes a Featured Story

Look for stories that meet at least 2 of these:

- ✅ A clear human angle (not just statistics)
- ✅ Cross-border relevance (story matters to more than one country)
- ✅ Counter-narrative (Black communities as resistant / human / building, not just as victims)
- ✅ Recent (within last 7 days, ideally)
- ✅ Has a strong image we can use
- ✅ Source is credible (avoid tabloid-tier outlets)

If you're stuck, pick the most-read story from the past week (Cloudflare analytics will show you this once you have 48+ hours of data).

---

## Highlights rotation — what goes in "In Focus"

Three slots, always filled. Rotate at least once a week. Mix:

- 🏛️ One **historical figure** (Garvey, Lumumba, Mandela, Sojourner Truth, Walter Rodney, etc.)
- 📚 One **educational deep-dive** (scholarly article, doc film)
- 🎵 One **cultural piece** (music, literature, art)

**Two hard rules for every highlight (the build will warn you if you break them):**
1. **Reputable news organisation only** — same allowlist as the hero (`REPUTABLE` in `pick_featured.py`): major wire/quality press plus vetted diaspora, African, Caribbean and Latin American outlets. No Wikipedia, no blogs, no commentary/advocacy sites in the highlight slots.
2. **Controlled local image only** — never hotlink the source's photo. Download it into `images/` first (so it can't break or change), and check it's on-objective: dignified, shows agency, no competitor watermark, no off-message optics. If the source's own image fails any of those, swap in a clean image we control.

**Source list to draw from:**
- Our own reputable allowlist (see `pick_featured.py`)
- The Conversation (free, scholarly)
- Africa is a Country (analytical, magazine-style)
- Past entries from our own archive

Edit `highlights.json`, localise the images, then run `python generate_site.py` to refresh.

---

## Social posting rules

Hard rules — never break these:
- 🚫 No buzzwords ("Pan-African", "systemic", "narrative framing", "diaspora", "BIPOC")
- 🚫 No hyphens in copy
- 🚫 No emojis in posts (the icons on the SITE are fine; in posts they cheapen the tone)
- 🚫 No replying to baiting or trolling — silence is the answer

Soft rules — try to follow:
- ✅ Lead every post with the most striking fact in the story
- ✅ Tag the country with a clean hashtag (#Brazil, #Ghana — never #PanAfrica or #BLM)
- ✅ Always link to the original source, not blackworldnews.world (we are the index, not the destination)
- ✅ Sundays are the day for educational/historical content, not breaking news

---

## Numbers to track weekly

Pull from Cloudflare Web Analytics + the Trends page once a week.

- **Total visitors** (Cloudflare)
- **Top 5 pages** (Cloudflare)
- **Top referring sources** (Cloudflare — where visitors come from)
- **Total stories in archive** (`stories.json` count)
- **Stories added this week** (count saved_at within last 7 days)
- **Social follower count** (manual, IG/X/Threads/TikTok)

Drop these into a `metrics_log.md` once a week. Trends will only show after a few weeks.

---

## When to break the rhythm

Skip the calendar if:
- 🌍 A major news event hits Black communities (post in real time, don't wait)
- 💔 You are exhausted — better to post nothing than to post low-quality
- 🎉 You hit a milestone (1k visitors, 100 followers, etc.) — celebrate quietly

---

## The quarterly review

Every 3 months, sit down for 1 hour and answer:

1. What's working? (which stories got most traction)
2. What's not? (what to drop)
3. New direct sources to add?
4. Any geographic gap to fill?
5. Should we invest in any paid tools yet?
6. Time to launch a new platform? (e.g. native app, newsletter)

Next quarterly review: 2026-08-27
