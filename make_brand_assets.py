# ============================================================
# MAKE BRAND ASSETS — generates the social media banner and
# profile picture used across Twitter, Instagram, Threads, etc.
#
# Run once whenever the brand changes:
#   python make_brand_assets.py
#
# Outputs to brand/ folder:
#   banner_twitter.png    1500 x 500   (X / Twitter banner)
#   banner_facebook.png   1640 x 624   (Facebook cover)
#   profile_400.png       400  x 400   (X profile, large)
#   profile_320.png       320  x 320   (Instagram profile)
#   profile_180.png       180  x 180   (smaller fallback)
# ============================================================

import os
import sys
import math
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from PIL import Image, ImageDraw, ImageFont

BRAND_DIR = "brand"
os.makedirs(BRAND_DIR, exist_ok=True)

GREEN  = (26, 58, 42, 255)
WHITE  = (255, 255, 255, 255)
BLACK  = (0, 0, 0, 255)
ACCENT = (138, 184, 154, 255)   # #8ab89a — the soft green used for taglines


def find_font(*candidates):
    for path in candidates:
        try:
            return ImageFont.truetype(path, 10)  # size irrelevant here, just check
        except (OSError, IOError):
            continue
    return None


SERIF_BOLD = None
for p in [
    "C:/Windows/Fonts/georgiab.ttf",
    "C:/Windows/Fonts/timesbd.ttf",
    "georgiab.ttf",
    "Georgia.ttf",
]:
    try:
        SERIF_BOLD = p
        ImageFont.truetype(p, 10)
        break
    except (OSError, IOError):
        SERIF_BOLD = None

SANS = None
for p in [
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "arial.ttf",
]:
    try:
        SANS = p
        ImageFont.truetype(p, 10)
        break
    except (OSError, IOError):
        SANS = None


def star_points(cx, cy, outer_r, inner_r, points=5, rotation=-math.pi / 2):
    pts = []
    for i in range(points * 2):
        r = outer_r if i % 2 == 0 else inner_r
        a = rotation + i * math.pi / points
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_logo(draw, cx, cy, radius):
    """Draws the BWN logo (green circle + Black Star + BWN text) centered."""
    # Outer green circle
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=GREEN,
        outline=(255, 255, 255, 30),
        width=max(1, int(radius * 0.02)),
    )
    # Faint globe lines for richness
    draw.ellipse(
        [cx - radius, cy - radius * 0.45, cx + radius, cy + radius * 0.45],
        outline=(255, 255, 255, 22),
        width=max(1, int(radius * 0.01)),
    )
    draw.ellipse(
        [cx - radius * 0.45, cy - radius, cx + radius * 0.45, cy + radius],
        outline=(255, 255, 255, 22),
        width=max(1, int(radius * 0.01)),
    )
    # Black Star — top portion
    star_outer = radius * 0.22
    star_inner = star_outer * 0.45
    star_cy    = cy - radius * 0.58
    draw.polygon(
        star_points(cx, star_cy, star_outer, star_inner),
        fill=BLACK,
        outline=(255, 255, 255, 100),
    )
    # BWN monogram
    if SERIF_BOLD:
        font_size = int(radius * 0.55)
        font = ImageFont.truetype(SERIF_BOLD, font_size)
        text = "BWN"
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(
            (cx - w / 2 - bbox[0], cy + radius * 0.05 - h / 2 - bbox[1]),
            text,
            fill=WHITE,
            font=font,
        )


# ---- PROFILE PICTURES ----
def make_profile(size, filename):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx = cy = size / 2
    radius = size / 2 - 2
    draw_logo(draw, cx, cy, radius)
    img.save(filename, "PNG")
    print(f"  ✅ {filename} ({size}x{size})")


# ---- BANNER ----
def make_banner(width, height, filename, safe_x=None):
    """
    Wide banner image. `safe_x` is the horizontal range that should not be
    occluded by avatar overlays on platforms like Twitter.
    """
    img = Image.new("RGBA", (width, height), GREEN)
    draw = ImageDraw.Draw(img)

    # Subtle radial glow behind the title — adds depth
    glow_r = int(height * 0.9)
    glow_cx = int(width * 0.55)
    glow_cy = int(height * 0.5)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    # paint a few concentric ellipses for a soft halo
    for i in range(15):
        alpha = max(0, 12 - i)
        r = glow_r - i * 30
        odraw.ellipse(
            [glow_cx - r, glow_cy - r * 0.8, glow_cx + r, glow_cy + r * 0.8],
            fill=(138, 184, 154, alpha),
        )
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # Logo on the left
    logo_radius = int(height * 0.35)
    logo_cx = int(height * 0.55)   # roughly one logo-diameter from the left edge
    logo_cy = int(height * 0.5)
    draw_logo(draw, logo_cx, logo_cy, logo_radius)

    # Title + tagline on the right of the logo
    text_x = logo_cx + logo_radius + int(height * 0.35)
    if SERIF_BOLD:
        title_font   = ImageFont.truetype(SERIF_BOLD, int(height * 0.22))
        tag_font     = ImageFont.truetype(SANS or SERIF_BOLD, int(height * 0.07))
    else:
        title_font   = ImageFont.load_default()
        tag_font     = title_font

    title = "BLACK WORLD NEWS"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    th = title_bbox[3] - title_bbox[1]
    draw.text(
        (text_x, logo_cy - th * 0.85 - title_bbox[1]),
        title,
        fill=WHITE,
        font=title_font,
    )

    tagline = "WHAT MATTERS TO YOU, TODAY"
    tag_bbox = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(
        (text_x, logo_cy + th * 0.25 - tag_bbox[1]),
        tagline,
        fill=ACCENT,
        font=tag_font,
    )

    # URL bottom-right corner
    url = "blackworldnews.world"
    if SANS:
        url_font = ImageFont.truetype(SANS, int(height * 0.05))
    else:
        url_font = title_font
    url_bbox = draw.textbbox((0, 0), url, font=url_font)
    url_w = url_bbox[2] - url_bbox[0]
    draw.text(
        (width - url_w - int(height * 0.1),
         height - (url_bbox[3] - url_bbox[1]) - int(height * 0.08) - url_bbox[1]),
        url,
        fill=ACCENT,
        font=url_font,
    )

    img.save(filename, "PNG")
    print(f"  ✅ {filename} ({width}x{height})")


print("Generating brand assets...")
make_profile(400, os.path.join(BRAND_DIR, "profile_400.png"))
make_profile(320, os.path.join(BRAND_DIR, "profile_320.png"))
make_profile(180, os.path.join(BRAND_DIR, "profile_180.png"))
make_banner(1500, 500, os.path.join(BRAND_DIR, "banner_twitter.png"))
make_banner(1640, 624, os.path.join(BRAND_DIR, "banner_facebook.png"))
print("Done.")
