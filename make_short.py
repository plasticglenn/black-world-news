"""
BWN short-video builder — one command turns an article into a finished vertical
video (1080x1920) with voiceover, Ken Burns stills, burned captions, corner
watermark and end card. No CapCut. Cloud for voice/captions (Cloudflare), local
ffmpeg only for the lightweight assembly.

Usage:
  python make_short.py crumbling-church-of-money

Inputs it expects:
  articles.json                  -> the article (hero image, title)
  shorts/<slug>.txt              -> the voiceover script (I write these)
  shorts/broll-*.jpg (optional)  -> extra stills; the hero is always used too
Outputs:
  shorts/<slug>.mp3              -> voiceover (generated if missing)
  shorts/<slug>.srt              -> caption timing (from Whisper)
  shorts/<slug>.mp4              -> the finished video to review before posting

Env: CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN
"""
import os, sys, json, glob, math, subprocess, urllib.request, urllib.error

REPO = os.path.dirname(os.path.abspath(__file__))
SHORTS = os.path.join(REPO, "shorts")
BRAND = os.path.join(REPO, "brand")
AURA_VOICE = "arcas"
WM = os.path.join(BRAND, "video_watermark.png")
ENDCARD = os.path.join(BRAND, "video_endcard.png")
END_SECS = 4.0


def find_bin(name):
    from shutil import which
    p = which(name)
    if p:
        return p
    base = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages")
    for root, _, files in os.walk(base):
        if name + ".exe" in files:
            return os.path.join(root, name + ".exe")
    raise SystemExit(f"{name} not found. Install ffmpeg (winget install Gyan.FFmpeg).")

FFMPEG = find_bin("ffmpeg")
FFPROBE = find_bin("ffprobe")


def cf_run(model, data, is_json):
    acct = os.environ["CLOUDFLARE_ACCOUNT_ID"]; tok = os.environ["CLOUDFLARE_API_TOKEN"]
    url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{model}"
    headers = {"Authorization": f"Bearer {tok}"}
    if is_json:
        headers["Content-Type"] = "application/json"; body = json.dumps(data).encode()
    else:
        body = data
    with urllib.request.urlopen(urllib.request.Request(url, data=body, headers=headers), timeout=180) as r:
        return r.read()


def ensure_voiceover(slug, script_text):
    mp3 = os.path.join(SHORTS, f"{slug}.mp3")
    if os.path.exists(mp3):
        return mp3
    text = " ".join(script_text.split())
    raw = cf_run("@cf/deepgram/aura-1", {"text": text, "speaker": AURA_VOICE}, True)
    with open(mp3, "wb") as f:
        f.write(raw)
    print(f"[voice] generated {mp3}")
    return mp3


def ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"


def srt_from_script(text, dur, out, max_chars=22):
    # Deterministic captions from the exact script, timed proportionally to word
    # count across the known audio length. Always monotonic, never overlapping,
    # and the words are always correct (no transcription mishears).
    words = text.split()
    total = max(1, len(words))
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(" ".join(cur)) >= max_chars or w[-1] in ".?!":
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    acc = 0
    with open(out, "w", encoding="utf-8") as f:
        for i, ch in enumerate(chunks, 1):
            start = acc / total * dur
            acc += len(ch)
            end = acc / total * dur
            f.write(f"{i}\n{ts(start)} --> {ts(end)}\n{' '.join(ch).strip()}\n\n")
    print(f"[captions] {len(chunks)} lines -> {out}")


def duration(path):
    out = subprocess.check_output([FFPROBE, "-v", "error", "-show_entries",
                                   "format=duration", "-of", "csv=p=0", path])
    return float(out.decode().strip())


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG ERROR:\n", r.stderr[-1500:]); raise SystemExit(1)


def make_clip(img, dur, out, zoom=True):
    frames = max(2, int(dur * 30))
    if zoom:
        vf = (f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
              f"zoompan=z='min(1.0+0.0009*on,1.12)':d=1:x='iw/2-(iw/zoom/2)':"
              f"y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,format=yuv420p")
    else:
        vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p"
    run([FFMPEG, "-y", "-loop", "1", "-i", img, "-t", f"{dur:.3f}", "-r", "30",
         "-vf", vf, "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "20", "-pix_fmt", "yuv420p", out])


def main(slug):
    script_path = os.path.join(SHORTS, f"{slug}.txt")
    if not os.path.exists(script_path):
        raise SystemExit(f"No script at {script_path}. Write the voiceover script first.")
    script_text = open(script_path, encoding="utf-8").read().strip()

    art = next((a for a in json.load(open(os.path.join(REPO, "articles.json"), encoding="utf-8"))
                if a.get("slug") == slug), None)
    if not art:
        raise SystemExit(f"No article with slug {slug} in articles.json")

    mp3 = ensure_voiceover(slug, script_text)
    voice_dur = duration(mp3)
    srt = os.path.join(SHORTS, f"{slug}.srt")
    srt_from_script(script_text, voice_dur, srt)

    hero = os.path.join(REPO, art.get("hero_image", "")) if art.get("hero_image") else None
    images = ([hero] if hero and os.path.exists(hero) else []) + sorted(glob.glob(os.path.join(SHORTS, "broll-*.jpg")))
    if hero and os.path.exists(hero):
        images.append(hero)  # bookend on the hero
    if not images:
        raise SystemExit("No images found (need a hero_image or shorts/broll-*.jpg).")

    beat = voice_dur / len(images)
    print(f"[plan] voice {voice_dur:.1f}s over {len(images)} stills ({beat:.1f}s each) + {END_SECS}s end card")

    clips = []
    for i, img in enumerate(images):
        c = os.path.join(SHORTS, f"_clip{i}.mp4"); make_clip(img, beat, c, zoom=True); clips.append(c)
    endc = os.path.join(SHORTS, "_endcard.mp4"); make_clip(ENDCARD, END_SECS, endc, zoom=False); clips.append(endc)

    listf = os.path.join(SHORTS, "_concat.txt")
    with open(listf, "w", encoding="utf-8") as f:
        for c in clips:
            f.write(f"file '{os.path.basename(c)}'\n")
    body = os.path.join(SHORTS, "_body.mp4")
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", "_concat.txt", "-c", "copy", "_body.mp4"], cwd=SHORTS)
    body_dur = voice_dur + END_SECS

    out = os.path.join(SHORTS, f"{slug}.mp4")
    style = ("FontName=Arial,FontSize=15,PrimaryColour=&H00FFFFFF&,OutlineColour=&H00000000&,"
             "BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=150")
    fc = (f"[2:v]scale=130:-1[wm];[0:v][wm]overlay=W-w-40:44[v1];"
          f"[v1]subtitles={slug}.srt:force_style='{style}'[v];[1:a]apad[a]")
    run([FFMPEG, "-y", "-i", "_body.mp4", "-i", os.path.basename(mp3), "-i", WM,
         "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", f"{body_dur:.3f}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac",
         "-b:a", "128k", "-pix_fmt", "yuv420p", os.path.basename(out)], cwd=SHORTS)

    for c in clips + [body, listf]:
        try: os.remove(c)
        except OSError: pass
    print(f"\n[done] {out}  ({body_dur:.1f}s)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); raise SystemExit(2)
    main(sys.argv[1])
