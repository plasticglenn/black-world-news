# Social Video Strategy — Black World News

> Goal: turn each article we publish (our originals, plus outside stories Glenn
> chooses) into a short vertical video with an AI voiceover reading a tight
> summary, and put it on four channels: YouTube, TikTok, Instagram, Facebook.
> Built to run lean and cloud based, because the machine is low on compute.

---

## The idea in one line

One article becomes one master video (vertical, about 60 to 90 seconds, our
voiceover, burned in captions, our own generated visuals). That single file
goes to all four channels, each with its own caption and tags.

---

## The pipeline (article to four channels)

| Stage | What happens | Tool | Cost |
|---|---|---|---|
| 1. Article | Written and published on the site | articles.json | free |
| 2. Script | A 150 to 220 word summary, hook first, call to action last | written to `shorts/<slug>.txt` | free |
| 3. Voiceover | Script read aloud as an MP3 | `make_voiceover.py` (Cloudflare Aura) | free |
| 4. Visuals | Four to six vertical stills that match the script beats | `generate_image.py` (Cloudflare FLUX) | free |
| 5. Assemble | Stills with slow zoom, voiceover, burned captions, logo, end card | `make_short.py` (ffmpeg) | free |
| 6. Captions | Per channel text and hashtags | manual for now, `social_post.py` later | free |
| 7. Publish | Upload to the four channels | review then approve, API automation | free |

Stages 2, 3 and 4 are already scripted and cloud based, so they cost nothing
and add no load to the machine. Stage 5 is done once per video in CapCut, which
is free, has automatic captions, and runs on phone or desktop with no install.

---

## Assembly is automated (no CapCut)

`make_short.py` builds the whole video with one command, so there is no manual
editor step. It generates the voiceover (Cloudflare Aura), times the captions
from the exact script against the audio length (deterministic, always correct
words), and uses ffmpeg to assemble the stills with a slow zoom, burn in the
captions, add the corner watermark and end card, and mux the audio. ffmpeg is a
one time install; the render of a short is light enough for a low compute
machine. CapCut is no longer needed.

    python make_short.py <slug>   ->   shorts/<slug>.mp4

---

## The master video format (same for all four channels)

- Size: 1080 by 1920, vertical, 9:16.
- Length: 60 to 90 seconds. Aim under 60 for YouTube Shorts eligibility when it fits.
- First 3 seconds: the hook line on screen, big, before anything else. This decides the view.
- Captions: burned in, high contrast, centered lower third. Most people watch on mute.
- Voiceover: one locked brand voice across every video for recognition.
- Branding: small logo in a corner throughout, plus a 3 second end card with the logo and blackworldnews.world.
- Call to action: spoken and on screen at the end, "Read the full piece at Black World News."

---

## Per channel notes

| Channel | Ceiling we use | What to get right |
|---|---|---|
| YouTube Shorts | Under 60 seconds ideal | Strong title, add #Shorts, a clear thumbnail frame |
| TikTok | 60 to 90 seconds | On screen captions, a sharp first line, 3 to 5 tags |
| Instagram Reels | Up to 90 seconds | A clean cover frame, 3 to 5 tags, keep the hook visible |
| Facebook Reels | Up to 90 seconds | Needs a Facebook Page, reuse the same file, plainer caption |

One asset, four uploads. Only the caption text and tags change per channel.

---

## Content sourcing

- Our originals (like this first article): full summary, our framing, our visuals.
- Outside stories Glenn selects: our own voiceover and our own generated images
  only. Name the source outlet out loud in the video and in the caption, and
  link the original story in the post. Never reuse the outlet's footage or photos.

---

## Distribution: manual first, automation next

Manual upload for the first videos while we lock the format. Automation later,
in order of how easy each is:

1. YouTube Data API v3. Free, well documented, good for automated uploads.
2. Meta Graph API for Instagram Reels and Facebook Reels. Needs a Business or
   Creator Instagram account linked to a Facebook Page, plus a Meta developer app.
3. TikTok Content Posting API. Needs an approved developer app, and approval can
   take time, so apply early and keep uploading by hand until it clears.

---

## SETUP CHECKLIST

### Accounts
- [x] YouTube channel for Black World News (exists)
- [x] TikTok account for Black World News (exists)
- [x] Instagram account for Black World News (created)
- [x] Facebook for Black World News (created)
- [ ] Confirm Facebook is a Page, not a personal profile (Reels and the API need a Page)
- [ ] Instagram: switch to Professional (Creator or Business) and link it to the Facebook Page
- [ ] TikTok: switch to a Business account
- [ ] Apply avatars, banners, bios and the website link to all four (asset map below)

### Branding assets for video
- [x] Corner watermark: `brand/video_watermark.png` (transparent)
- [x] End card frame 1080 by 1920: `brand/video_endcard.png`
- [x] YouTube channel banner (correct 2560 by 1440): `brand/banner_youtube.png`
- [x] Lock one voiceover voice: **arcas** (Deepgram Aura, calm male). Set as the default in make_voiceover.py.
- [ ] Lock a caption style: font, color, size, position (decide in CapCut on the first video)

### APIs (for later automation, not needed for the test run)
- [ ] Google Cloud project, enable YouTube Data API v3, create an OAuth client
- [ ] Meta developer app, add Instagram Graph API, generate a Page access token
- [ ] TikTok developer app, apply for Content Posting API access early

### Rights and safety
- [ ] For outside stories: our voiceover and our visuals only, name and link the source, no borrowed footage
- [ ] Keep the same editorial rules as the site: plain wire tone in captions, no buzzwords, no hyphens or dashes

---

## Cadence

Start at two to three shorts per week. One from a BWN original, the rest from
stories Glenn picks. Hold that steady for a few weeks before raising frequency,
the same trust before frequency rule as the text posts.

---

## Test run status (Article 1: The Crumbling Church of Money)

Produced and in the `shorts/` folder:
- [x] Script: `shorts/crumbling-church-of-money.txt`
- [x] Voiceover MP3 (Cloudflare Aura, arcas voice)
- [x] Hero still + three b-roll stills
- [x] Finished video: `shorts/crumbling-church-of-money.mp4` (about 59 seconds), built by `make_short.py`
- [ ] Per channel captions and tags (drafted, see the captions section)
- [ ] Upload to the four channels once the accounts are set

The next article is now literally one command: `python make_short.py <slug>`.
Write the article, drop a `shorts/<slug>.txt` script, run it, review the mp4.
