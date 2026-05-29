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

# BWN brand palette
GREEN = (26, 58, 42, 255)       # #1a3a2a
GOLD  = (255, 216, 61, 255)     # #ffd83d
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)


def blend_on_green(white_alpha):
    a = white_alpha / 255.0
    return (
        int(GREEN[0] * (1 - a) + 255 * a),
        int(GREEN[1] * (1 - a) + 255 * a),
        int(GREEN[2] * (1 - a) + 255 * a),
        255,
    )


LINE_OUTER_RING = blend_on_green(38)
LINE_LAT_MAIN   = blend_on_green(30)
LINE_LAT_FAINT  = blend_on_green(20)
LINE_LON        = blend_on_green(30)
LINE_EQUATOR    = blend_on_green(38)
AFRICA_FILL     = blend_on_green(56)
AFRICA_EDGE     = blend_on_green(25)
BWN_COLOR       = blend_on_green(230)


def star_points(cx, cy, outer_r, inner_r, points=5, rotation=-math.pi / 2):
    pts = []
    for i in range(points * 2):
        r = outer_r if i % 2 == 0 else inner_r
        angle = rotation + i * math.pi / points
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts


def quad_bezier(p0, p1, p2, steps=22):
    out = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        out.append((x, y))
    return out


def africa_polygon(cx, cy, scale):
    def pt(x, y):
        return (cx - 50 * scale + x * scale, cy - 50 * scale + y * scale)
    start = pt(42, 18)
    segments = [
        (pt(54, 14), pt(62, 18)),
        (pt(67, 24), pt(68, 33)),
        (pt(71, 41), pt(68, 47)),
        (pt(65, 56), pt(61, 63)),
        (pt(56, 72), pt(50, 76)),
        (pt(45, 77), pt(41, 73)),
        (pt(37, 65), pt(35, 56)),
        (pt(29, 46), pt(27, 38)),
        (pt(27, 30), pt(32, 24)),
        (pt(37, 19), pt(42, 18)),
    ]
    points = [start]
    current = start
    for ctrl, end in segments:
        points.extend(quad_bezier(current, ctrl, end)[1:])
        current = end
    return points


def draw_full_logo(draw, cx, cy, radius):
    """Original BWN logo with pre-blended colours so PIL renders the faded
    white-on-green effect correctly. No star outline."""
    line_thin = max(1, int(radius * 0.012))

    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=GREEN,
        outline=LINE_OUTER_RING,
        width=max(1, int(radius * 0.018)),
    )
    draw.ellipse(
        [cx - radius, cy - radius * 0.47, cx + radius, cy + radius * 0.47],
        outline=LINE_LAT_MAIN, width=line_thin,
    )
    draw.ellipse(
        [cx - radius, cy - radius * 0.85, cx + radius, cy + radius * 0.85],
        outline=LINE_LAT_FAINT, width=line_thin,
    )
    draw.ellipse(
        [cx - radius * 0.47, cy - radius, cx + radius * 0.47, cy + radius],
        outline=LINE_LON, width=line_thin,
    )
    draw.line(
        [(cx - radius * 0.97, cy), (cx + radius * 0.97, cy)],
        fill=LINE_EQUATOR, width=line_thin,
    )
    # Black Star — large, prominent, top centre
    star_outer = radius * 0.39
    star_inner = star_outer * 0.45
    star_cy    = cy - radius * 0.40
    draw.polygon(
        star_points(cx, star_cy, star_outer, star_inner),
        fill=BLACK,
        outline=(255, 255, 255, 90),
    )

    # BWN — large, below star
    target_h = int(radius * 0.52)
    font = None
    for path in ["C:/Windows/Fonts/georgiab.ttf", "C:/Windows/Fonts/timesbd.ttf",
                 "C:/Windows/Fonts/arialbd.ttf", "georgiab.ttf"]:
        try:
            font = ImageFont.truetype(path, target_h)
            break
        except (OSError, IOError):
            continue
    if font is None:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), "BWN", font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(
        (cx - w / 2 - bbox[0], cy + radius * 0.25 - h / 2 - bbox[1]),
        "BWN", fill=BWN_COLOR, font=font,
    )


def make_icon(size, filename, maskable=False, rounded=False):
    """Render the BWN logo at the given pixel size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if maskable:
        # Maskable: square green background, logo in center-80% safe zone
        draw.rectangle([0, 0, size, size], fill=GREEN)
        radius = size * 0.4    # logo within the 80% safe zone
    else:
        radius = size / 2 - 2

    draw_full_logo(draw, size / 2, size / 2, radius)
    img.save(filename, "PNG")
    print(f"  {filename} ({size}x{size})")


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
