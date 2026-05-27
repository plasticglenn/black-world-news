# For the Children — Full Strategy

> A sterile lab for kids 3-13 to explore the Black world safely.
> Same brand DNA as the main site, opened up into colour and play.
> Last updated: 2026-05-27

---

## 🎯 Vision (Glenn's words, kept honest)

> *"The kids button should be like a portal into a new world with the same colour branding but optimized for children of all literate ages. I want us to produce ai videos colourfully explaining complex concepts. Comics. And also a place for kids to learn about the world of black people safely. An almost sterile lab for kids to explore their world."*

After 13, kids graduate to the main site.

---

## 👶 Two age lanes inside the same room

Both lanes live on the same `kids.html` page. A tab at the top toggles between them.

### 🌱 Lane 1 — Little Ones (ages 3-7)
- Picture-first
- Short sentences, simple words
- AI reads stories aloud (browser text-to-speech)
- Lots of colour, friendly animals, smiling faces
- No statistics, no current events. Stories about people and places.

### 🌳 Lane 2 — Bigger Kids (ages 8-13)
- Comic-style explainers on real topics, rewritten for kid language
- Profiles of historical figures
- Country deep-dives ("A Place to Know")
- Mini-quizzes
- Some statistics, but always with kid-friendly framing

---

## 🧱 Modules (the building blocks)

Every kid lands on a page with these blocks in this order:

### 1. The Comic of the Week
- Full-bleed AI-generated comic via Pollinations
- Tells one real story from the past week in kid language
- 4-6 panels, no more
- Vibrant colours, no graphic violence, no scary imagery

### 2. Meet Someone Special
- Rotating profile of a historical figure
- Portrait + 3 facts + one quote (age-appropriate)
- Tap to hear it read aloud (Bigger Kids only — TTS app-level later)

### 3. A Place to Know
- One country featured at a time
- Flag, map, "one thing to know", "one word from this country"
- Photo: a kid-friendly scene (school, market, music — never violence)

### 4. From the Big News
- 3 stories from the main archive, rewritten at 3rd-grade reading level
- AI-generated; you approve before publishing
- Frame even hard topics with hope, action, "what people are doing about it"

### 5. Learn a Word
- One word per day, in a rotating language
- Languages cycle: Twi, Swahili, Yoruba, Portuguese, Spanish, French, Haitian Creole
- Word + pronunciation guide + meaning + one example sentence

### 6. Quiz Time
- 3 multiple-choice questions
- About the content above
- No grading, no leaderboard — just "Right!" / "Try again"
- JavaScript only, no backend

### 7. Safe Footer
- "Ask a grown-up if you have questions"
- No comments, no chat, no DMs anywhere
- Privacy promise reminder

---

## 🛠️ Build phases (in order)

### Phase 1 — Static skeleton (one sitting, ~3 hours)
- [ ] `kids.html` lives, looks like the rest of the site but child-friendly
- [ ] Manually written content for first batch:
  - 3 historical figures (suggestion: Garvey, Nkrumah, Sojourner Truth)
  - 3 featured countries (suggestion: Ghana, Brazil, Jamaica)
  - 3 stories rewritten by hand
  - 3 words to learn
- [ ] Quiz works (JavaScript only)
- [ ] No comics yet, no TTS yet

### Phase 2 — Auto-rewrite news (one sitting, ~2 hours)
- [ ] `kids_content.py` script
- [ ] Reads `stories.json`, picks 3 newest with framing "Human" or "Resistant"
- [ ] AI rewrites at 3rd-grade reading level
- [ ] Saves to `kids_content.json`
- [ ] Generator pulls from this file

### Phase 3 — Pollinations comics (one sitting, ~2 hours)
- [ ] Comic prompt builder: takes a story, generates 4-6 panel descriptions
- [ ] Calls Pollinations (`image.pollinations.ai/prompt/...`) per panel
- [ ] Stitches panels into a single comic image with PIL
- [ ] Caches results in `kids_comics/` folder

### Phase 4 — Curated content stores (ongoing)
- [ ] `kids_figures.json` — rotating list of historical figures
- [ ] `kids_countries.json` — rotating list of countries
- [ ] `kids_vocab.json` — rotating list of words
- [ ] You hand-curate these. Once-a-month effort.

### Phase 5 — Audio (when app launches — deferred)
- [ ] Browser text-to-speech for read-aloud
- [ ] Eventually offload to native app

---

## 🎨 Visual identity inside the kids page

Reuse what's already built:
- **Bagel Fat One** font for headings (the balloon paint we already use)
- Multi-color glossy paint letters for section titles
- White background (the "sterile lab" feel)
- Bright accent colours sparingly — red, gold, blue, green, orange, purple — no muddy tones
- Big buttons, big text, lots of whitespace
- No grids — kids think in cards and scrolls

Existing pieces that fit:
- The Kids Corner balloon nav link
- The For the Children portal door title
- `kids.html` would be the third place the balloon paint shows up

---

## 🛡️ Safety rules (non-negotiable)

These cannot be broken under any circumstance.

- 🚫 **No graphic violence, no police brutality scenes, no death imagery** — even when discussing news
- 🚫 **No statistics about death, harm, or victimization** for Little Ones
- 🚫 **No comments, no chat, no DMs** anywhere on the kids page
- 🚫 **No data collection of children** — no email signups, no quiz score saving, no cookies
- 🚫 **No outbound links to social media** (kids' privacy)
- 🚫 **No ads, ever** (not now, not later — even if monetisation comes elsewhere)
- ✅ **All external links open in a new tab with a "Ask a grown-up" notice** (for Bigger Kids)
- ✅ **AI-generated content must be reviewed by you** before publishing — no auto-publish for kids
- ✅ **Comply with COPPA** (US) and **UK Age Appropriate Design Code** — if we ever collect any data

---

## 📝 Content rules

How news gets translated for kids:

| Adult version | Kid version |
|---|---|
| "Homicides of Black people represent 77% of all murders in Brazil" | "A new report from Brazil shows that life is much harder for some families than others. People are working together to make Brazil safer for everyone." |
| "Police brutality in the United States" | "In some parts of the world, the rules about how police can treat people are being looked at again. Communities are working together to change them." |
| "Land theft in Zimbabwe" | "Zimbabwe is making decisions about who gets to grow food on the land where their families have always lived. It's a big question that lots of people are talking about." |

**The rule:** Honest about what's happening. Hopeful about what people are doing. Never traumatic.

---

## 🌍 First content batch (pick before Phase 1 build)

### Three historical figures (rotating monthly)
1. **Marcus Garvey** — the man behind the star on our logo
2. **Kwame Nkrumah** — Ghana's first president and what independence means
3. **Sojourner Truth** — a woman who walked across America asking for fairness

### Three featured countries (rotating monthly)
1. **Ghana** — kente cloth, gold, the Black Star, kids playing oware
2. **Brazil** — Bahia, capoeira, Carnival in Salvador
3. **Jamaica** — the music of Bob Marley, the food, the schools

### Three first stories to rewrite (pick from current archive)
- Pick 3 stories with framing tagged "Human" or "Resistant"
- Skip anything with framing "Victim" or "Criminal" for the kids' first impression
- Will look at the archive together to pick

### Three first words to learn
1. **Akwaaba** (Twi, Ghana) — welcome
2. **Tudo bem?** (Portuguese, Brazil) — how are you
3. **Ase** (Yoruba, Nigeria) — let it be so

---

## 🎬 Launch criteria — when "For the Children" goes live

Phase 1 ships when:
- ✅ Static page exists with all 6 modules
- ✅ 3 figures, 3 countries, 3 stories, 3 words hand-curated
- ✅ Quiz works
- ✅ Safety rules verified (no comments, no data, no ads, no scary content)
- ✅ You've read every word and approved it
- ✅ Tested on a real phone, real tablet, real laptop

Don't ship Phase 1 until all six tick. Better quiet for another week than launching shaky.

---

## 💵 Cost summary

Phase 1-3 are all free. Pollinations is free. Groq is free. PIL is free.

Real costs only kick in if:
- We add custom illustrations (artist work, ~$50-200 per piece)
- We license stock kid photos (~$30-100/year for service)
- We want a child voice actor for TTS (~$50/hour, one-time)

All optional. Not needed for launch.

---

## 🚦 Right now

**Blocked on:** decisions from you about first three figures / countries / words (suggestions above).
**Not blocked on:** Phase 1 build can start as soon as you give the green light.

When you're ready, say "build Phase 1" and I'll start with the static skeleton.
