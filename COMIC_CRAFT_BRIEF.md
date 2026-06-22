# Comic Craft Brief — what the best kids' comics do, applied to BWN

> A teardown of why the strongest kids' / educational comics work, turned into
> rules we can apply to every BWN strip. Pairs with `CHARACTER_BIBLE.md` (who)
> and `COMIC_01_GARVEY.md` (how to generate). This file is the *why*.
> Sources at the bottom.

---

## The 7 things that make a kids' comic work

**1. The art carries the story; the words stay light.**
Reluctant and young readers stay in because the *pictures* do the heavy lifting —
text is a thin layer on top. If a panel needs a sentence to be understood, the
drawing isn't doing its job. Our rule already: *1 idea per panel, few words.*

**2. One beat per panel.**
Webtoon grammar (our format) wants a single moment per panel — a glance, a line,
a reveal — not a busy multi-action page. This is *freeing*: we're not composing
dense pages, we're writing a sequence of clear moments.

**3. Gutters set the pace.** (the webtoon-specific craft — see table below)
The blank space *between* panels controls reading speed and emotion. Same art,
different gutters = different feeling. Most strips ignore this; it's our cheapest
upgrade.

**4. Humor pitched right — earnest, never edgy, never preachy.**
Dog Man works because real feeling is *snuck in between* the jokes. For us: let
**Kojo & Ama be funny** (a kid's "Um… kids?" beat) so the history never reads as
a lecture. The humor is the spoonful that carries the truth.

**5. Show, don't tell — let the reader *arrive* at the meaning.**
The best history comics don't state the moral; they stage a moment and trust the
reader to feel it. This is the line between *political education* (reader reasons
their way to pride) and *propaganda* (reader is told what to think). Have the
figure **ask** or **show**, not announce.

**6. Let the hero speak — in real quotes — and show the person, not the statue.**
Graphic biographies land when they weave the figure's **actual words** in and
show **character + childhood + emotion**, not a list of achievements. Garvey's
"Up, you mighty people" is real — use real lines, keep him warm and human.

**7. A child POV as the door, and an *active* ending.**
Kids enter history through a kid their own age (our Kojo & Ama = exactly this).
End on something the reader *does*, not just receives — an affirmation to say, a
question to answer — the "I could do this too" empowerment that makes Dog Man and
New Kid stick.

---

## The BWN shelf — real comics to study (all exist; go read them)

| Comic | Creator | What to steal |
|---|---|---|
| **New Kid / Class Act / School Trip** | Jerry Craft | Warmth + humor through a Black kid's POV; first graphic novel to win the Newbery. The tone we want. |
| **Strange Fruit; Tales of the Talented Tenth** | Joel Christian Gill | *Uncelebrated* Black history as comics — our exact lane. How to make a little-known figure gripping. |
| **Little Leaders: Bold Women in Black History** | Vashti Harrison | One dignified figure per spread, simple + proud. A model for our "Meet Someone Special" module. |
| **History Comics / Who Was…?** (graphic line) | various | Nonfiction structure for kids — how to frame a real event without it going dry. |
| **Dog Man** / **Smile** | Pilkey / Telgemeier | Not our subject, but the engagement *mechanics*: humor, pacing, "a kid made this." |

---

## Webtoon paneling rules — our exact format (vertical scroll, mobile)

- **One beat per panel.** Single column, top-to-bottom.
- **Gutter = pace.** Vary it on purpose; uniform gutters flatten the whole strip:

  | Gutter (blank space) | Reads as |
  |---|---|
  | 100–150px | fast action — keep the thumb moving |
  | 200–300px | an emotional beat — a glance, a line that should land |
  | 400–600px | a scene change |
  | 600–800px | a **cliffhanger pause** — force a stop before the reveal |

- **The most powerful gutter is the one *before* a reveal.** Big blank space =
  the reader stops scrolling and anticipates → the payoff hits harder.
- **800px wide native, 72dpi.** Keep any single panel **under ~1280px tall** or
  mobile viewports slice it awkwardly.
- **Always preview on a real phone.** Desktop lies about pacing.

---

## Applied: a craft pass on "Kojo & Ama Meet Marcus Garvey"

The strip is already in good shape — child-POV throughline, real Garvey quote,
humor beat, an echo-back ending. Notes are *sharpenings*, not a rewrite. Dialogue
lives in `comics.json` and stays yours to approve — these are suggestions.

**What's already working (keep):**
- Kojo & Ama as the door (Rule 7). ✅
- P3 "Where… are we?" / "Not where. When." — clean, funny, one beat. ✅
- P4 Garvey *asks* "Do you know what you are?" + Kojo's "Um… kids?" — humor +
  show-don't-tell setup (Rules 4–5). ✅
- P6 kids echo "Up, you mighty people!" — active, empowering close (Rule 7). ✅

**Sharpenings:**
- **P4 — the one 'told' beat.** "You are somebody. Stand tall." is the only line
  that *announces* the moral. It's defensible (it's the hero speaking directly,
  Rule 6) — but consider letting him *show* it: a beat where Garvey straightens
  and the kids straighten with him, the art doing the "stand tall."
- **P5 — make it a question, not a statement.** Instead of Garvey telling them
  "You can do anything," let him **point at the ships and ask** "Whose ships do
  you think those are?" — so the *reader* arrives at the pride (Rule 5). Keep
  "Built by our hands" and "Up, you mighty people" — those are the real, earned
  lines.
- **Pacing (Rule 3) — vary the gutters:**
  - Big gutter (600–800px) **before P2 (the lift)** — the magic should make them
    pause.
  - Biggest gutter of the strip **before P5 (the ships reveal)** — this is the
    emotional peak; make the thumb stop before the harbour appears.
  - Tight gutters (100–150px) inside the P1 dialogue — quick kid chatter.
- **The close → the kids page.** P6's "I feel taller" is the perfect bridge to
  the **affirmations tap-through deck** already on `kids.html`. End the reader on
  *their* turn: "What would *you* stand tall for?"

---

## Reusable 8-point checklist (run before publishing any strip)

1. Could a 6-year-old follow it **with the words covered**? (Rule 1)
2. Is each panel **one beat**? (Rule 2)
3. Have I **varied the gutters**, with the biggest one before the key reveal? (Rule 3)
4. Is there at least one **kid-funny** beat so it isn't a lecture? (Rule 4)
5. Does the reader **arrive** at the meaning, or is it announced? (Rule 5)
6. Does the figure speak in **real quotes** and read as a warm person? (Rule 6)
7. Does it end on something the reader **does**? (Rule 7)
8. Did I **preview on a real phone**? (webtoon rules)

---

## Sources
- [Why graphic novels work for reluctant readers — Brightly / Screenwise](https://www.readbrightly.com/books-like-dog-man-dav-pilkey/)
- [Jerry Craft — New Kid (Newbery Medal)](https://en.wikipedia.org/wiki/New_Kid)
- [Standout comics by Black creators — School Library Journal](https://www.schoollibraryjournal.com/story/black-comics-creators-and-characters-take-center-stage-in-these-works-graphic-novels)
- [Using comics & graphic novels to teach Black history — Edutopia](https://www.edutopia.org/article/comics-graphic-novels-teach-black-history)
- [How nonfiction comics teach history — Common Sense Media](https://www.commonsensemedia.org/lists/graphic-novels-that-teach-history)
- [Graphic biographies that bring figures to life — School Library Journal](https://www.slj.com/story/10-graphic-biographies-bring-notable-figures-to-life-stellar-panels-graphic-novels)
- [Visual & fun biography series for young readers — Brightly](https://www.readbrightly.com/visual-fun-biography-series-young-readers/)
- [Vertical-scroll webtoon paneling: 7 rules — Comistitch](https://comistitch.com/blog/webtoon-vertical-scroll-paneling-guide/)
