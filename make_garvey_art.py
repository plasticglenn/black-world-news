"""
Generate the art for Comic #1 "Kojo & Ama Meet Marcus Garvey" via the live
image engine (Cloudflare Workers AI / FLUX). Panels are drawn CLEAN (no text) --
the dialogue is overlaid by the site from comics.json. Character descriptions are
repeated verbatim each panel to hold consistency as much as FLUX allows.

Run (PowerShell, with the Cloudflare keys in env):
    python make_garvey_art.py
Outputs to images/comics/garvey/  (cover.png, panel-1.png ... panel-6.png)
"""
import os
import generate_image as gi

BASE = os.path.dirname(os.path.abspath(__file__))

KOJO = ("Kojo, a cheerful 9-year-old Black boy with a short rounded afro, round face, "
        "big bright eyes and a gap-toothed smile, wearing a mustard-yellow t-shirt with a "
        "small black star, green shorts and white trainers")
AMA = ("Ama, a confident 9-year-old Black girl with two afro puffs tied with red beads, "
       "round face, big bright eyes and a warm smile, wearing a teal dress with a small "
       "black star, orange leggings and white trainers")
GARVEY = ("Marcus Garvey, a stocky Black Jamaican man from the 1920s with a round kind face "
          "and short hair, wearing a smart dark double-breasted military-style suit and a tall "
          "plumed ceremonial hat")

STYLE = ("warm friendly children's picture-book comic illustration, clean bold outlines, "
         "bright flat colours, soft shading, kind expressive faces, wholesome, "
         "no text, no speech bubbles, no words, no captions")

PANELS = {
    "cover.png":
        f"Children's comic book cover. {KOJO}, and {AMA}, standing proudly either side of a "
        f"glowing black star, with {GARVEY} smiling warmly behind them, a sunny harbour with a "
        f"tall ship flying a black star flag in the distance. {STYLE}",
    "panel-1.png":
        f"{KOJO}, and {AMA}, crouched together in a sunny green backyard looking down at a small "
        f"glowing black star resting in the grass, soft golden light on their faces, lots of open "
        f"blue sky above them. {STYLE}",
    "panel-2.png":
        f"{KOJO}, and {AMA}, rising gently upward into a swirl of warm golden light and soft "
        f"glowing stars, their hair and clothes floating, faces full of wonder and joy, plenty of "
        f"glowing open space at the top. {STYLE}",
    "panel-3.png":
        f"{KOJO}, and {AMA}, standing on a bright 1920s Jamaican street with palm trees, market "
        f"stalls and a warm blue sky, a small crowd of proud well-dressed Black people in the "
        f"background. {STYLE}",
    "panel-4.png":
        f"{GARVEY}, kneeling down to meet two children at eye level, with one hand resting warmly "
        f"on the shoulder of {KOJO}, and {AMA} beside them, smiling kindly, a softly blurred 1920s "
        f"Jamaican street behind them. {STYLE}",
    "panel-5.png":
        f"Seen from behind: {GARVEY}, standing between {KOJO}, and {AMA}, all three looking out at "
        f"a harbour where tall ships fly a black star flag, bright sun sparkling on the water. {STYLE}",
    "panel-6.png":
        f"{KOJO}, and {AMA}, back in the sunny backyard standing tall and proud with chins up, a "
        f"small black star glowing softly in Ama's open hand, both grinning at each other, open "
        f"blue sky above. {STYLE}",
}

if __name__ == "__main__":
    name, fn = gi.available_provider()
    if not fn:
        raise SystemExit("No image provider key found in env. Set Cloudflare keys first.")
    print(f"Using provider: {name}")
    for filename, prompt in PANELS.items():
        out = os.path.join(BASE, "images", "comics", "garvey", filename)
        print(f"\n--- {filename} ---")
        gi.generate_image(prompt, out, kids=False)
    print("\nAll panels generated.")
