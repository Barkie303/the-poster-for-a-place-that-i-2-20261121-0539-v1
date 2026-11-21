#!/usr/bin/env python3
"""Render the travel poster for TIDEFALL, an invented cliff town where a
river falls from the cliffs into a turquoise bay at golden hour.

Drawn at 2x (2048x2048) with Pillow and downscaled to 1024x1024 for
smooth edges. Fully deterministic: no randomness, no network, no
borrowed images. Run: python3 render.py  ->  entry.png
"""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2  # supersample factor
W = H = 1024 * S

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

SKY_TOP = (14, 62, 92)
SKY_MID = (96, 156, 168)
SKY_HORIZON = (255, 196, 138)
SEA_TOP = (52, 150, 158)
SEA_BOTTOM = (26, 104, 124)
SAND = (238, 214, 170)
CLIFF = (232, 196, 150)
CLIFF_DARK = (206, 150, 108)
TERRACOTTA = (198, 96, 60)
WALL = (246, 241, 226)
CREAM = (255, 246, 230)
GOLD = (255, 205, 120)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, y0, y1, c0, c1):
    for y in range(y0, y1):
        draw.line([(0, y), (W, y)], fill=lerp(c0, c1, (y - y0) / max(1, y1 - y0)))


def tracked_text(draw, cx, y, text, font, fill, tracking, shadow=None):
    """Draw centred text with letter tracking. Returns text height."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    if shadow is not None:
        sx, sy, scol = shadow
        xx = x
        for ch, wch in zip(text, widths):
            draw.text((xx + sx, y + sy), ch, font=font, fill=scol)
            xx += wch + tracking
    xx = x
    for ch, wch in zip(text, widths):
        draw.text((xx, y), ch, font=font, fill=fill)
        xx += wch + tracking
    return font.size


def main():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img, "RGBA")

    # ---- sky: three-stop gradient, deep teal to warm gold ----
    vgrad(d, 0, 700, SKY_TOP, SKY_MID)
    vgrad(d, 700, 1180, SKY_MID, SKY_HORIZON)

    # ---- sun + glow ----
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    sx, sy, sr = 1420, 1010, 128
    for r, a in ((300, 22), (230, 34), (180, 50)):
        g.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 200, 110, a))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 216, 132, 255))
    d.ellipse([sx - sr + 26, sy - sr + 26, sx + sr - 26, sy + sr - 26],
              fill=(255, 232, 170, 255))

    # ---- soft clouds ----
    cloud = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    c = ImageDraw.Draw(cloud)
    for cx, cy, cw, ch, a in ((420, 660, 380, 34, 38), (980, 600, 460, 30, 32),
                              (1620, 720, 400, 32, 36), (300, 840, 320, 28, 28)):
        c.ellipse([cx - cw, cy - ch, cx + cw, cy + ch], fill=(255, 226, 200, a))
    cloud = cloud.filter(ImageFilter.GaussianBlur(18))
    img.paste(Image.alpha_composite(img.convert("RGBA"), cloud).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # ---- birds ----
    for bx, by, s in ((480, 700, 30), (640, 770, 24), (1150, 660, 28), (1280, 740, 22)):
        d.arc([bx - s, by - s // 2, bx, by + s // 2], 200, 340,
              fill=(30, 50, 66, 220), width=5)
        d.arc([bx, by - s // 2, bx + s, by + s // 2], 200, 340,
              fill=(30, 50, 66, 220), width=5)

    # ---- sea (drawn down past the beach top edge so no gap shows) ----
    vgrad(d, 1180, 1950, SEA_TOP, SEA_BOTTOM)
    # sun reflection: shimmering gold dashes under the sun
    for i in range(26):
        y = 1200 + i * 19
        half = 26 + int(150 * (i / 26))
        x0 = sx - half + ((i * 37) % 60) - 30
        d.line([(x0, y), (x0 + 90 + (i * 53) % 120, y)],
               fill=(255, 214, 140, 90), width=6)
    # wave strokes
    for i in range(40):
        y = 1210 + (i * 47) % 460
        x = (i * 389) % 1900
        d.line([(x, y), (x + 60 + (i * 29) % 90, y)],
               fill=(255, 255, 255, 26), width=4)

    # ---- right cliff + lighthouse ----
    d.polygon([(2048, 2048), (2048, 1120), (1760, 1180), (1620, 1330),
               (1560, 2048)], fill=CLIFF_DARK)
    d.polygon([(2048, 2048), (2048, 1120), (1760, 1180), (1700, 1500),
               (1800, 2048)], fill=(188, 128, 92))
    # strata lines on the right cliff
    for i, y in enumerate((1300, 1420, 1560, 1720)):
        d.line([(1620 + i * 40, y), (2048, y - 60)], fill=(170, 110, 78, 90), width=4)
    # lighthouse on the cliff point
    lx, ly = 1690, 1180  # base
    d.polygon([(lx - 46, ly), (lx - 30, ly - 300), (lx + 30, ly - 300),
               (lx + 46, ly)], fill=(250, 246, 238))
    d.polygon([(lx - 40, ly - 100), (lx - 34, ly - 150), (lx + 34, ly - 150),
               (lx + 40, ly - 100)], fill=(214, 84, 52))
    d.polygon([(lx - 36, ly - 210), (lx - 32, ly - 250), (lx + 32, ly - 250),
               (lx + 36, ly - 210)], fill=(214, 84, 52))
    d.rectangle([lx - 34, ly - 330, lx + 34, ly - 300], fill=(40, 56, 66))
    d.ellipse([lx - 22, ly - 356, lx + 22, ly - 312], fill=(255, 226, 140))
    d.polygon([(lx - 40, ly - 330), (lx + 40, ly - 330), (lx + 26, ly - 362),
               (lx - 26, ly - 362)], fill=(40, 56, 66))
    # light beam over the sea (daytime: a faint warm glow at the lamp only)
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    b = ImageDraw.Draw(beam)
    b.ellipse([lx - 90, ly - 420, lx + 90, ly - 240], fill=(255, 240, 180, 46))
    beam = beam.filter(ImageFilter.GaussianBlur(16))
    img.paste(Image.alpha_composite(img.convert("RGBA"), beam).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # ---- left cliff ----
    d.polygon([(0, 2048), (0, 900), (300, 940), (560, 1060), (700, 1420),
               (640, 2048)], fill=CLIFF)
    d.polygon([(0, 2048), (0, 1500), (300, 1560), (420, 2048)], fill=(214, 172, 128))
    # strata lines on the left cliff
    for i, y in enumerate((1080, 1240, 1420, 1620)):
        d.line([(0, y), (560 - i * 40, y + 90)], fill=(196, 148, 106, 90), width=4)
    # waterfall: the river pours off the cliff's edge into the bay.
    # The cascade follows the cliff edge down to the waterline.
    fall = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = ImageDraw.Draw(fall)
    # the little river arriving at the lip, along the cliff top
    f.line([(440, 1002), (545, 1030)], fill=(210, 236, 242, 230), width=10)
    # the cascade body, hugging the cliff edge
    f.polygon([(528, 1022), (592, 1038), (668, 1186), (614, 1186)],
              fill=(238, 248, 250, 235))
    # inner streaks for falling water
    f.line([(556, 1040), (632, 1176)], fill=(255, 255, 255, 255), width=10)
    f.line([(578, 1046), (650, 1178)], fill=(255, 255, 255, 255), width=6)
    # foam and mist where the fall meets the sea
    f.ellipse([592, 1166, 706, 1214], fill=(255, 255, 255, 200))
    f.ellipse([616, 1180, 694, 1206], fill=(255, 255, 255, 150))
    f.ellipse([600, 1140, 680, 1176], fill=(255, 255, 255, 90))
    fall = fall.filter(ImageFilter.GaussianBlur(2))
    img.paste(Image.alpha_composite(img.convert("RGBA"), fall).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # ---- town houses on the left cliff top ----
    def house(x, y, w, h, roof_h=34):
        d.rectangle([x, y, x + w, y + h], fill=WALL)
        d.polygon([(x - 8, y), (x + w // 2, y - roof_h), (x + w + 8, y)],
                  fill=TERRACOTTA)
        d.rectangle([x + w // 2 - 10, y + h // 2, x + w // 2 + 10, y + h],
                    fill=(90, 70, 60))
        d.rectangle([x + 12, y + 16, x + 30, y + 34], fill=(52, 84, 96))
        d.rectangle([x + w - 30, y + 16, x + w - 12, y + 34], fill=(52, 84, 96))

    house(60, 830, 110, 84)
    house(190, 800, 96, 96)
    house(300, 840, 120, 78)
    house(430, 810, 100, 92)
    house(120, 880, 88, 70)
    house(250, 890, 104, 66)
    # a couple of houses on the right cliff
    house(1820, 1060, 100, 80)
    house(1930, 1090, 84, 66)

    # ---- sailboat on the bay ----
    bx, by = 1060, 1380
    d.polygon([(bx - 70, by), (bx + 70, by), (bx + 44, by + 34),
               (bx - 44, by + 34)], fill=(52, 66, 74))
    d.polygon([(bx, by - 6), (bx, by - 150), (bx + 84, by - 6)],
              fill=(250, 246, 238))
    d.polygon([(bx - 8, by - 6), (bx - 8, by - 110), (bx - 62, by - 6)],
              fill=(224, 96, 62))
    d.line([(bx, by - 156), (bx, by)], fill=(52, 66, 74), width=6)

    # ---- beach: a narrower sandy crescent, sea stays the hero ----
    d.polygon([(0, 2048), (0, 1880), (420, 1830), (900, 1870), (1400, 1830),
               (2048, 1900), (2048, 2048)], fill=SAND)
    d.line([(0, 1880), (420, 1830), (900, 1870), (1400, 1830), (2048, 1900)],
           fill=(255, 255, 255, 150), width=9)
    for i in range(12):
        x = 120 + (i * 173) % 1800
        y = 1930 + (i * 61) % 90
        d.line([(x, y), (x + 40, y + 4)], fill=(206, 178, 132, 160), width=4)

    # ---- title ----
    title_font = ImageFont.truetype(SERIF_BOLD, 196)
    sub_font = ImageFont.truetype(SANS, 54)
    tracked_text(d, W // 2, 150, "TIDEFALL", title_font, CREAM, 30,
                 shadow=(8, 10, (18, 48, 66, 180)))
    tracked_text(d, W // 2, 400, "WHERE THE RIVER MEETS THE SKY",
                 sub_font, (255, 236, 205), 16,
                 shadow=(4, 5, (18, 48, 66, 160)))
    d.line([(W // 2 - 320, 500), (W // 2 + 320, 500)], fill=GOLD, width=5)

    img = img.resize((1024, 1024), Image.LANCZOS)
    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
