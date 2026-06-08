"""
Panel-by-panel comic iterator. Generate a few variations of one panel, review,
then lock the chosen one by its seed. Prompts live in make_garvey_art.py (edit a
panel's prompt there to correct it, then re-run this).

Workflow:
  1) python panel.py panel-1            # 3 variations -> images/comics/garvey/_review/
  2) (look at them, note the seed in each filename)
  3) python panel.py panel-1 --lock 102 # regenerate that seed straight to panel-1.png

Keys: cover, panel-1 ... panel-6  (".png" optional).
Same prompt + same seed = same image on FLUX, so locking is reproducible.
"""
import os
import sys
import shutil
import generate_image as gi
import make_garvey_art as art

BASE = os.path.dirname(os.path.abspath(__file__))
GARVEY = os.path.join(BASE, "images", "comics", "garvey")
REVIEW = os.path.join(GARVEY, "_review")
SEEDS = [101, 102, 103, 104, 105, 106]   # fixed so variations are reproducible


def resolve(key):
    fn = key if key.endswith(".png") else key + ".png"
    if fn not in art.PANELS:
        raise SystemExit(f"Unknown panel '{key}'. Options: " + ", ".join(k[:-4] for k in art.PANELS))
    return fn, art.PANELS[fn]


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    key = argv[0]
    fn, prompt = resolve(key)

    if "--lock" in argv:
        seed = int(argv[argv.index("--lock") + 1])
        out = os.path.join(GARVEY, fn)
        gi.generate_image(prompt, out, kids=False, seed=seed)
        print(f"LOCKED {fn} at seed {seed} -> {out}")
        return 0

    n = 3
    if len(argv) > 1 and argv[1].isdigit():
        n = int(argv[1])
    os.makedirs(REVIEW, exist_ok=True)
    for seed in SEEDS[:n]:
        out = os.path.join(REVIEW, f"{fn[:-4]}__seed{seed}.png")
        gi.generate_image(prompt, out, kids=False, seed=seed)
        print(f"  variation seed {seed} -> {out}")
    print(f"\nReview {REVIEW}, then: python panel.py {key} --lock <seed>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
