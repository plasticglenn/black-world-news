"""
BWN voiceover generator — turns a script into a narration MP3 using Cloudflare
Workers AI (free daily allowance). Cloud only, no local rendering, so it runs
fine on a low-compute machine. Companion to generate_image.py.

Set (Windows User env vars, never in files):
  CLOUDFLARE_ACCOUNT_ID = <your account id>
  CLOUDFLARE_API_TOKEN  = <token with "Workers AI" permission>

Usage:
  python make_voiceover.py shorts/article1-crumbling-church.txt shorts/article1-crumbling-church.mp3
  python make_voiceover.py --voice mango script.txt out.mp3
  python make_voiceover.py --engine melotts script.txt out.mp3

Engines:
  aura    (default) Deepgram Aura-1, natural narrator voices. --voice picks the speaker.
  melotts MeloTTS, robust fallback. --voice sets language (en, es, fr, ...).
"""
import os
import sys
import json
import base64
import urllib.request
import urllib.error

# A calm, authoritative default that suits a serious analysis brand. Swap freely.
AURA_DEFAULT_VOICE = "arcas"


def _cloudflare_run(model, payload):
    acct = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    tok = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not (acct and tok):
        return None, "No Cloudflare keys set (CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_API_TOKEN)."
    url = f"https://api.cloudflare.com/client/v4/accounts/{acct}/ai/run/{model}"
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        return None, f"Provider error {e.code}: {e.read()[:300]}"
    # Aura returns raw MP3 bytes; MeloTTS returns JSON with base64 audio.
    if raw[:2] == b"\xff\xf3" or raw[:3] == b"ID3":
        return raw, None
    try:
        d = json.loads(raw)
        audio = d.get("result", {}).get("audio")
        if audio:
            return base64.b64decode(audio), None
        return None, f"Unexpected response: {str(d)[:200]}"
    except Exception:
        return raw, None  # assume it was audio bytes


def synthesize(text, out_path, engine="aura", voice=None):
    text = " ".join(text.split())  # collapse whitespace/newlines into flowing speech
    if engine == "aura":
        model = "@cf/deepgram/aura-1"
        payload = {"text": text, "speaker": voice or AURA_DEFAULT_VOICE}
    else:
        model = "@cf/myshell-ai/melotts"
        payload = {"prompt": text, "lang": voice or "en"}
    data, err = _cloudflare_run(model, payload)
    if err:
        print(err)
        return None
    with open(out_path, "wb") as f:
        f.write(data)
    print(f"[make_voiceover] engine={engine} voice={voice or '(default)'} -> {out_path} ({len(data)} bytes)")
    return out_path


def _main(argv):
    args = list(argv)
    engine, voice = "aura", None
    if "--engine" in args:
        i = args.index("--engine"); engine = args[i + 1]; del args[i:i + 2]
    if "--voice" in args:
        i = args.index("--voice"); voice = args[i + 1]; del args[i:i + 2]
    if len(args) < 2:
        print(__doc__)
        return 2
    script_path, out_path = args[0], args[1]
    with open(script_path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        print("Script file is empty.")
        return 1
    return 0 if synthesize(text, out_path, engine=engine, voice=voice) else 1


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
