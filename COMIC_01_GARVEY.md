# Production Pack — Comic #1: "Kojo & Ama Meet Marcus Garvey"

Everything needed to generate this strip in **Dashtoon** (free tier, ~100 images/day).
Art is generated **clean — no speech bubbles** (the site draws dialogue on top from
`comics.json`). Output filenames must match `images/comics/garvey/` exactly.

---

## Generation budget
- Reference sheets (one-time, reused forever): 3 characters x ~4 tries ≈ **12 gens**
- Panels: 6 x ~4 tries ≈ **24 gens**
- Cover: ~4 gens
- **Strip total ≈ 40 gens** — one afternoon, well under the daily cap.
- Strip #2 onward ≈ ~28 gens (characters already locked).

---

## House style — paste on EVERY generation
> Warm, friendly children's-comic style. Clean bold outlines, bright flat colours,
> soft shading. Dignified and real, never caricature. Vertical webtoon panel, kind
> faces, expressive eyes. No text, no speech bubbles, no words in the image.

(The "no text" line matters — it stops the model garbling letters and keeps the art
clean for our HTML bubbles.)

---

## STEP 1 — Lock the 3 reference sheets first
For each: **Create character -> paste the lock phrase -> generate -> pick the best ->
save to the character library.** Do Kojo & Ama first (they're in nearly every panel).

**Kojo**
`Kojo, a cheerful 9-year-old Black boy, short rounded afro, round face, big bright eyes, gap-toothed smile, mustard-yellow t-shirt with a small black star, green shorts, white trainers` — front view, neutral standing pose, plain background.

**Ama**
`Ama, a confident 9-year-old Black girl, two afro puffs with red beads, round face, big bright eyes, warm smile, teal dress with a small black star, orange leggings, white trainers` — front view, neutral standing pose, plain background.

**Marcus Garvey**
`Marcus Garvey, Black Jamaican leader, 1920s, stocky build, round kind face, short hair, smart dark double-breasted suit, tall plumed ceremonial hat, confident warm expression` — front view, neutral pose, plain background.

---

## STEP 2 — Generate the 6 panels
Drop the locked characters in by name. Each prompt below already bakes in the house
style and the "leave room for bubbles" framing. **Save as the exact filename shown.**

### panel-1.png — the find  *(bubble headroom: TOP)*
Kojo and Ama crouched together in a sunny backyard, looking down at a small glowing
black star resting in the grass, soft golden light on their faces, lots of open sky
above them. Wide friendly shot.

### panel-2.png — the lift  *(bubble headroom: TOP)*
Kojo and Ama rising gently into a swirl of warm golden light and soft stars, hair and
clothes floating, faces full of wonder, not fear. Plenty of glowing open space at the top.

### panel-3.png — arrival  *(bubble headroom: TOP + BOTTOM)*
Kojo and Ama landing on a bright 1920s Jamaican street, palm trees, warm blue sky,
market stalls in the background, a crowd of proud well-dressed Black people. Open sky
above, open road below.

### panel-4.png — the meeting  *(bubble headroom: TOP + BOTTOM)*
Marcus Garvey kneeling to meet Kojo and Ama at eye level, one hand warmly on Kojo's
shoulder, smiling kindly. 1920s Jamaican street softly blurred behind. Calm space top
and bottom.

### panel-5.png — the ships  *(bubble headroom: TOP + BOTTOM)*
Back view of Garvey standing between Kojo and Ama, all three looking out at a harbour
where great ships fly a black star flag, sun on the water, the kids' faces lit with
wonder (shown in profile). Big open sky and water for text.

### panel-6.png — home, prouder  *(bubble headroom: TOP + BOTTOM)*
Kojo and Ama back in the sunny backyard, standing tall, chins up, proud, the little
black star glowing softly in Ama's open palm, both grinning at each other. Open sky
above.

### cover.png — shelf cover / share image
Portrait poster (about 4:5). Kojo and Ama standing proudly either side of the glowing
black star, Marcus Garvey's warm figure behind them, harbour with a black star ship in
the distance, bright and inviting. Leave a clear band across the top — we may add the
title later.

---

## STEP 3 — Publish
1. Put all 7 PNGs in `images/comics/garvey/` (names above, exact).
2. In `comics.json`, set the Garvey strip's `"published": true`.
3. `python generate_site.py`  (confirm EXIT=0)
4. Verify, then commit + push.

The dialogue is already written and placed in `comics.json` — you don't touch wording
here unless you want to change a line. To tweak a bubble's position, change its
`"anchor"` (top-left / top-right / bottom-left / bottom-right / top-center / bottom-center).
