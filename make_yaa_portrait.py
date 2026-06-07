"""
Original illustrated portrait of Yaa Asantewaa for the BWN Kids page.

No free-licensed photo of her exists, and our image generator (Pollinations) is
now paywalled, so this draws an ORIGINAL, dignified flat-illustration portrait of
an Asante queen mother -- humble but thoughtful -- entirely offline with Pillow.
Supersampled 3x then downscaled for smooth, antialiased edges.

Run:  python make_yaa_portrait.py   ->  images/yaa-asantewaa.jpg
"""
from PIL import Image, ImageDraw, ImageFilter

SS = 3                      # supersample factor
S = 400                     # final size
W = S * SS

def x(v): return int(v * SS)

img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# ---- palette -------------------------------------------------------------
BG1   = (247, 226, 178)     # warm cream-gold background
BG2   = (238, 208, 150)
SKIN  = (141, 90, 58)       # warm brown
SKIN_SH = (112, 70, 44)     # shadow side
SKIN_HI = (165, 110, 74)    # lit side
LIP   = (150, 78, 66)
EYE   = (40, 26, 20)
GOLD  = (224, 170, 44)
GOLD_D= (190, 138, 30)
CLOTH = (28, 110, 104)      # her teal, dignified headwrap base
CLOTH_D = (20, 86, 82)
GARMENT = (168, 60, 44)     # warm earthy red garment
KENTE = [(224,170,44),(30,132,73),(192,57,46),(20,20,20)]  # gold/green/red/black

# ---- background: flat warm + soft radial glow behind the head ------------
d.rectangle([0, 0, W, W], fill=BG1)
# vertical warm shift
grad = Image.new("L", (1, W))
for i in range(W):
    grad.putpixel((0, i), int(0 + (i / W) * 60))
grad = grad.resize((W, W))
img.paste(Image.new("RGBA", (W, W), BG2), (0, 0), grad)

glow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([x(70), x(40), x(330), x(300)], fill=(255, 244, 214, 200))
glow = glow.filter(ImageFilter.GaussianBlur(x(28)))
img = Image.alpha_composite(img, glow)
d = ImageDraw.Draw(img)

# ---- garment / shoulders (drawn first; head overlaps) --------------------
# broad rounded shoulders sweeping off the bottom
d.pieslice([x(40), x(250), x(360), x(560)], 180, 360, fill=GARMENT)
d.rectangle([x(40), x(360), x(360), x(400)], fill=GARMENT)
# kente trim band across the chest
ty = x(330)
bandh = x(10)
for i in range(7):
    col = KENTE[i % len(KENTE)]
    d.rectangle([x(120) + i * x(24), ty, x(120) + (i + 1) * x(24), ty + bandh], fill=col)

# ---- neck ---------------------------------------------------------------
d.rectangle([x(173), x(232), x(227), x(300)], fill=SKIN_SH)
d.rectangle([x(176), x(228), x(224), x(290)], fill=SKIN)

# ---- head ---------------------------------------------------------------
# face oval
d.ellipse([x(132), x(96), x(268), x(266)], fill=SKIN)
# soft shadow on the left side for form
sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
shd = ImageDraw.Draw(sh)
shd.ellipse([x(126), x(96), x(214), x(266)], fill=(*SKIN_SH, 150))
sh = sh.filter(ImageFilter.GaussianBlur(x(10)))
# clip shadow to the face area roughly by pasting then redrawing lit side
img = Image.alpha_composite(img, sh)
d = ImageDraw.Draw(img)
# lit cheek highlight
hi = Image.new("RGBA", (W, W), (0, 0, 0, 0))
hid = ImageDraw.Draw(hi)
hid.ellipse([x(196), x(150), x(256), x(232)], fill=(*SKIN_HI, 120))
hi = hi.filter(ImageFilter.GaussianBlur(x(14)))
img = Image.alpha_composite(img, hi)
d = ImageDraw.Draw(img)

# ears + gold earrings
d.ellipse([x(126), x(168), x(146), x(200)], fill=SKIN_SH)
d.ellipse([x(254), x(168), x(274), x(200)], fill=SKIN)
d.ellipse([x(128), x(198), x(142), x(214)], fill=GOLD)      # left earring
d.ellipse([x(258), x(198), x(272), x(214)], fill=GOLD)      # right earring

# ---- facial features (calm, thoughtful, eyes softly lowered) ------------
# eyebrows: low, gentle, unhurried
d.arc([x(152), x(160), x(190), x(180)], 200, 350, fill=(70, 45, 32), width=x(3))
d.arc([x(210), x(160), x(248), x(180)], 190, 340, fill=(70, 45, 32), width=x(3))
# eyes: softly lowered almond shapes (calm, thoughtful, gaze gently down)
for (ex, mirror) in [(172, 0), (228, 1)]:
    # eye white (kept small so the gaze reads gentle, not wide)
    d.ellipse([x(ex-14), x(182), x(ex+14), x(196)], fill=(243, 238, 230))
    # heavy upper lid cuts the eye down to a soft, lowered gaze
    d.chord([x(ex-15), x(175), x(ex+15), x(196)], 180, 360, fill=SKIN)
    # iris sitting low in the eye
    d.ellipse([x(ex-6), x(187), x(ex+6), x(197)], fill=EYE)
    d.ellipse([x(ex-2), x(189), x(ex+1), x(192)], fill=(220, 210, 200))  # tiny catchlight
    # soft lower lash line
    d.arc([x(ex-14), x(184), x(ex+14), x(200)], 20, 160, fill=(70, 45, 32), width=x(2))

# nose: soft shadow + nostrils
nd = Image.new("RGBA", (W, W), (0, 0, 0, 0))
ndd = ImageDraw.Draw(nd)
ndd.polygon([x(200), x(192), x(190), x(214), x(210), x(214)], fill=(*SKIN_SH, 110))
nd = nd.filter(ImageFilter.GaussianBlur(x(4)))
img = Image.alpha_composite(img, nd)
d = ImageDraw.Draw(img)
d.ellipse([x(190), x(214), x(197), x(220)], fill=SKIN_SH)
d.ellipse([x(203), x(214), x(210), x(220)], fill=SKIN_SH)

# mouth: gentle, calm, full lips (thoughtful, not smiling)
d.chord([x(182), x(226), x(218), x(244)], 0, 180, fill=LIP)
d.line([x(184), x(232), x(216), x(232)], fill=(110, 56, 48), width=x(2))

# ---- headwrap (gele): dignified, modest, with a gold brow band ----------
wrap = Image.new("RGBA", (W, W), (0, 0, 0, 0))
wd = ImageDraw.Draw(wrap)
# main wrap dome above the brow
wd.pieslice([x(120), x(70), x(280), x(210)], 180, 360, fill=CLOTH)
# a wrapped fold rising to one side (gives it presence without being ornate)
wd.polygon([x(248), x(98), x(289), x(76), x(282), x(118), x(256), x(138)], fill=CLOTH_D)
wd.pieslice([x(120), x(70), x(280), x(150)], 180, 360, fill=CLOTH_D)
wrap = wrap.filter(ImageFilter.GaussianBlur(1))
img = Image.alpha_composite(img, wrap)
d = ImageDraw.Draw(img)
# thin kente accent stripes along the wrap
for i, col in enumerate(KENTE):
    yy = x(150) + i * x(7)
    d.arc([x(126), x(96), x(274), x(214)], 182, 358, fill=col, width=x(3))
    break  # one subtle accent line only (humble)
# gold brow band
d.arc([x(130), x(150), x(270), x(220)], 188, 352, fill=GOLD, width=x(7))
d.arc([x(130), x(150), x(270), x(220)], 188, 352, fill=GOLD_D, width=x(2))
# small gold jewel centred on the band
d.ellipse([x(193), x(150), x(207), x(164)], fill=GOLD)
d.ellipse([x(196), x(153), x(204), x(161)], fill=(255, 230, 150))

# ---- finish: downscale for smooth edges, flatten onto warm bg, save -----
out = img.resize((S, S), Image.LANCZOS)
flat = Image.new("RGB", (S, S), BG1)
flat.paste(out, (0, 0), out)
flat.save("images/yaa-asantewaa.jpg", quality=90)
print("saved images/yaa-asantewaa.jpg")
