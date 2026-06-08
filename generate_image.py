"""
BWN image generator — the replacement for Pollinations (now paywalled / HTTP 402).

Pluggable: auto-detects whichever provider key is set in your environment, so you
can pick a vendor without changing code. Saves a ready-to-use local image (we serve
images statically — this is a build-time/manual tool, NOT called on page load).

Set ONE of these (Windows User env vars, like DEEPSEEK_API_KEY — never in files):

  Cloudflare Workers AI  (recommended: free daily allowance, FLUX.1-schnell)
      CLOUDFLARE_ACCOUNT_ID = <your account id>
      CLOUDFLARE_API_TOKEN  = <token with "Workers AI" permission>

  OpenAI  (best quality / best for consistent comic characters; paid)
      OPENAI_API_KEY = sk-...

  Hugging Face  (free token, FLUX.1-schnell; can be slow / rate-limited)
      HF_API_TOKEN = hf_...

If several are set, the first available in this order wins, or force one with
IMAGE_PROVIDER = cloudflare | openai | huggingface

Usage:
  python generate_image.py "a red bicycle" images/bike.jpg
  python generate_image.py --kids "Yaa Asantewaa, Asante queen mother in kente, humble and thoughtful" images/yaa-asantewaa.jpg
  python generate_image.py --kids --size 400 "Kwame Nkrumah, Ghana's first leader, kind face" images/nkrumah.jpg

--kids wraps the prompt in our warm children's-illustration house style and crops
to a centred square (default 400x400) ready for the round kids portraits.
"""
import os
import sys
import json
import base64
import urllib.request
import urllib.error
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    Image = None

KIDS_STYLE = ("warm friendly children's book illustration portrait of {p}, "
              "proud and dignified, kind face, colourful, soft lighting, "
              "head and shoulders, simple background, no text, no words")


def _cloudflare(prompt, seed=None):
    acct = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    tok = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not (acct and tok):
        return None
    url = (f"https://api.cloudflare.com/client/v4/accounts/{acct}"
           f"/ai/run/@cf/black-forest-labs/flux-1-schnell")
    payload = {"prompt": prompt, "steps": 8}
    if seed is not None:
        payload["seed"] = int(seed)
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.load(r)
    # flux-1-schnell returns {"result": {"image": "<base64 jpeg>"}, ...}
    return base64.b64decode(d["result"]["image"])


def _openai(prompt, seed=None):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    url = "https://api.openai.com/v1/images/generations"
    body = json.dumps({"model": "gpt-image-1", "prompt": prompt,
                       "size": "1024x1024", "n": 1}).encode()  # gpt-image-1 has no seed
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.load(r)
    return base64.b64decode(d["data"][0]["b64_json"])


def _huggingface(prompt, seed=None):
    key = os.environ.get("HF_API_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")
    if not key:
        return None
    url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    payload = {"inputs": prompt}
    if seed is not None:
        payload["parameters"] = {"seed": int(seed)}
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()  # raw image bytes


PROVIDERS = [("cloudflare", _cloudflare), ("openai", _openai), ("huggingface", _huggingface)]


def available_provider():
    forced = os.environ.get("IMAGE_PROVIDER", "").strip().lower()
    order = ([p for p in PROVIDERS if p[0] == forced] + PROVIDERS) if forced else PROVIDERS
    for name, fn in order:
        # cheap presence check via the same env logic each fn uses
        if name == "cloudflare" and os.environ.get("CLOUDFLARE_ACCOUNT_ID") and os.environ.get("CLOUDFLARE_API_TOKEN"):
            return name, fn
        if name == "openai" and os.environ.get("OPENAI_API_KEY"):
            return name, fn
        if name == "huggingface" and (os.environ.get("HF_API_TOKEN") or os.environ.get("HUGGINGFACE_API_KEY")):
            return name, fn
    return None, None


def _square(im, size):
    w, h = im.size
    s = min(w, h)
    l, t = (w - s) // 2, (h - s) // 2
    return im.crop((l, t, l + s, t + s)).resize((size, size), Image.LANCZOS)


def generate_image(prompt, out_path, kids=False, size=400, seed=None):
    """Generate an image for `prompt` and save it to `out_path`. Returns the path,
    or None if no provider key is set. Raises on a provider/network error.
    `seed` (int) makes a roll reproducible on providers that support it (Cloudflare/HF)."""
    name, fn = available_provider()
    if not fn:
        return None
    final_prompt = KIDS_STYLE.format(p=prompt) if kids else prompt
    print(f"[generate_image] provider={name}" + (f" seed={seed}" if seed is not None else ""))
    data = fn(final_prompt, seed=seed)
    if not data:
        return None
    if Image is not None:
        im = Image.open(BytesIO(data)).convert("RGB")
        if kids:
            im = _square(im, size)
        im.save(out_path, quality=90)
    else:
        with open(out_path, "wb") as f:
            f.write(data)
    print(f"[generate_image] saved {out_path}")
    return out_path


def _main(argv):
    args = list(argv)
    kids = False
    size = 400
    if "--kids" in args:
        kids = True
        args.remove("--kids")
    if "--size" in args:
        i = args.index("--size")
        size = int(args[i + 1])
        del args[i:i + 2]
    if "--provider" in args:
        i = args.index("--provider")
        os.environ["IMAGE_PROVIDER"] = args[i + 1]
        del args[i:i + 2]
    seed = None
    if "--seed" in args:
        i = args.index("--seed")
        seed = int(args[i + 1])
        del args[i:i + 2]
    if len(args) < 2:
        print(__doc__)
        return 2
    prompt, out_path = args[0], args[1]
    name, fn = available_provider()
    if not fn:
        print("No image provider key found. Set CLOUDFLARE_ACCOUNT_ID + "
              "CLOUDFLARE_API_TOKEN, or OPENAI_API_KEY, or HF_API_TOKEN. "
              "See the header of this file.")
        return 1
    try:
        generate_image(prompt, out_path, kids=kids, size=size, seed=seed)
        return 0
    except urllib.error.HTTPError as e:
        print(f"Provider error {e.code}: {e.read()[:300]}")
        return 1


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
