# ============================================================
# MAKE PWA ICONS — generates PNG app icons from a simple design.
# Run once; the icons go into the icons/ folder.
#
# Usage:  python make_icons.py
# ============================================================

import os
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from PIL import Image, ImageDraw, ImageFont
import math

ICON_DIR = "icons"
os.makedirs(ICON_DIR, exist_ok=True)

GREEN = (26, 58, 42, 255)       # #1a3a2a
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)


def star_points(cx, cy, outer_r, inner_r, points=5, rotation=-math.pi / 2):
    """Return polygon points for an N-pointed star."""
    pts = []
    for i in range(points * 2):
        r = outer_r if i % 2 == 0 else inner_r
        angle = rotation + i * math.pi / points
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts


def make_icon(size, filename, maskable=False, rounded=False):
    """
    Render the BWN logo at the given pixel size.
    - maskable: keep all content inside the central 80% safe-zone
                so adaptive Android masks don't crop it.
    - rounded: clip into a circle (used for non-maskable iOS-style icons)
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background fill — square for maskable, circle for normal
    if maskable:
        draw.rectangle([0, 0, size, size], fill=GREEN)
        usable = size * 0.8        # center-80% safe zone
        offset = size * 0.1
    else:
        draw.ellipse([0, 0, size, size], fill=GREEN)
        usable = size
        offset = 0

    cx = size / 2
    cy = size / 2

    # Black Star — top portion of the icon
    star_cy   = offset + usable * 0.30
    star_outer = usable * 0.16
    star_inner = star_outer * 0.45
    draw.polygon(
        star_points(cx, star_cy, star_outer, star_inner),
        fill=BLACK,
        outline=(255, 255, 255, 100),
    )

    # BWN monogram — center / lower portion
    text = "BWN"
    target_h = int(usable * 0.32)
    # Try to find a usable font
    font = None
    for font_path in ["arial.ttf", "Arial.ttf", "DejaVuSans-Bold.ttf",
                      "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"]:
        try:
            font = ImageFont.truetype(font_path, target_h)
            break
        except (OSError, IOError):
            continue
    if font is None:
        font = ImageFont.load_default()

    # Center the text horizontally and place it lower-center
    bbox  = draw.textbbox((0, 0), text, font=font)
    tw    = bbox[2] - bbox[0]
    th    = bbox[3] - bbox[1]
    text_cy = offset + usable * 0.65
    draw.text(
        (cx - tw / 2 - bbox[0], text_cy - th / 2 - bbox[1]),
        text,
        fill=WHITE,
        font=font,
    )

    img.save(filename, "PNG")
    print(f"  ✅ {filename} ({size}x{size})")


# Standard PWA sizes Chrome / Android / iOS expect
SIZES = [
    (192,  "icon-192.png",          False, False),
    (512,  "icon-512.png",          False, False),
    (512,  "icon-maskable-512.png", True,  False),  # Android adaptive
    (180,  "apple-touch-icon.png",  True,  False),  # iOS home screen
    (167,  "apple-touch-icon-167.png", True, False),  # iPad
    (152,  "apple-touch-icon-152.png", True, False),  # older iPads
]


print("Generating PWA icons...")
for size, name, maskable, rounded in SIZES:
    path = os.path.join(ICON_DIR, name)
    make_icon(size, path, maskable=maskable, rounded=rounded)
print("Done.")
