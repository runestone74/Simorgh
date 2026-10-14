#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Rune Eriksson (Simorgh fork of Felucca)
"""Original procedural Simorgh art (no third-party artwork), Persian-miniature palette.

  gen_simorgh_art.py [--font Vazirmatn-Bold.ttf]

Writes assets/simorgh/:
  simorgh_full.png      1024 x 1024 full-colour illustration (README / web)
  simorgh_banner.png    1600 x 400 README banner (Persian script needs --font, OFL Vazirmatn)
  splash_240.png        240 x 240 preview of the device boot splash (16 colours)
  santur_icon_24.png    santur icon preview
and firmware/src/simorgh_splash.h: the splash as 4 bpp pixels + a 16-entry RGB565 palette in the
ST7789's byte order (lcd_blit), drawn by ui_draw.c draw_splash.
"""
import argparse, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "simorgh"
LAPIS, LAPIS_D, TURQ, TURQ_L = (31, 58, 147), (16, 30, 82), (48, 178, 175), (130, 220, 210)
GOLD, GOLD_D, CREAM, CRIMSON, WHITE = (222, 176, 62), (150, 105, 30), (245, 232, 200), (178, 40, 52), (255, 255, 255)


def star8(cx, cy, r, rot=0.0):
    pts = []
    for i in range(16):
        rr = r if i % 2 == 0 else r * 0.62
        a = rot + i * math.pi / 8
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def girih_border(d, S, w):
    d.rectangle([0, 0, S, S], fill=LAPIS_D)
    n = 8
    step = S / n
    for i in range(n):
        for (cx, cy) in [(step * (i + .5), w / 2), (step * (i + .5), S - w / 2),
                         (w / 2, step * (i + .5)), (S - w / 2, step * (i + .5))]:
            d.polygon(star8(cx, cy, w * .42, math.pi / 8), fill=GOLD, outline=GOLD_D)
            d.polygon(star8(cx, cy, w * .2), fill=TURQ)
    d.rectangle([w, w, S - w, S - w], fill=LAPIS)
    d.rectangle([w, w, S - w, S - w], outline=GOLD, width=max(2, int(w * .08)))


def arabesque(d, S, w):
    c = S / 2
    for k in range(24):                    # faint rosette of vine arcs behind the bird
        a = k * math.pi / 12
        r = S * .34
        x, y = c + r * math.cos(a), c + r * math.sin(a)
        d.ellipse([x - S * .05, y - S * .05, x + S * .05, y + S * .05], outline=TURQ, width=max(1, S // 200))


def bird(d, S):
    c = S / 2
    u = S / 100.0
    P = lambda x, y: (c + x * u, c + y * u)
    # tail: five long flowing feathers, sweeping down-left
    for i, (col, sp) in enumerate([(TURQ, -22), (GOLD, -12), (CRIMSON, -2), (GOLD, 8), (TURQ, 18)]):
        pts = []
        for t in range(0, 41):
            s = t / 40
            x = 4 - 40 * s + sp * s * .6
            y = 6 + 30 * s + 8 * math.sin(s * math.pi * 1.5 + i)
            pts.append(P(x, y))
        d.line(pts, fill=col, width=int(5 * u))
        ex, ey = pts[-1]
        d.ellipse([ex - 4 * u, ey - 4 * u, ex + 4 * u, ey + 4 * u], fill=col, outline=GOLD_D)
        d.ellipse([ex - 1.6 * u, ey - 1.6 * u, ex + 1.6 * u, ey + 1.6 * u], fill=LAPIS_D)
    # wings raised: layered feather fans
    for side, base in ((-1, (-6, -2)), (1, (8, -4))):
        for j in range(6):
            a = math.radians(-90 + side * (20 + j * 11))
            L = 34 - j * 2.5
            bx, by = base
            tip = P(bx + L * math.cos(a), by + L * math.sin(a))
            col = [GOLD, TURQ, GOLD, TURQ_L, GOLD, TURQ][j]
            d.polygon([P(bx - 3, by), tip, P(bx + 3, by + 2)], fill=col, outline=GOLD_D)
    # body
    d.ellipse([*P(-10, -8), *P(16, 14)], fill=GOLD, outline=GOLD_D, width=int(u))
    d.ellipse([*P(-4, -2), *P(12, 10)], fill=CRIMSON)
    for k in range(4):                      # scale pattern on breast
        d.arc([*P(-2 + k * 3, 0), *P(4 + k * 3, 6)], 0, 180, fill=CREAM, width=max(1, int(u * .6)))
    # neck and head
    d.line([P(12, -2), P(20, -16), P(24, -24)], fill=GOLD, width=int(6 * u))
    d.ellipse([*P(19, -31), *P(31, -20)], fill=GOLD, outline=GOLD_D, width=int(u))
    d.polygon([P(30, -27), P(38, -24), P(30, -23)], fill=CRIMSON)          # beak
    d.ellipse([*P(25, -28), *P(28, -25)], fill=LAPIS_D)                       # eye
    for k in range(3):                                                       # crest
        d.line([P(22, -30), P(16 + k * 4, -42 + k)], fill=TURQ, width=int(2 * u))
        x, y = P(16 + k * 4, -42 + k)
        d.ellipse([x - 2 * u, y - 2 * u, x + 2 * u, y + 2 * u], fill=GOLD)


def illustration(S):
    ss = 4
    im = Image.new("RGB", (S * ss, S * ss))
    d = ImageDraw.Draw(im)
    girih_border(d, S * ss, S * ss * .1)
    arabesque(d, S * ss, S * ss * .1)
    bird(d, S * ss)
    return im.resize((S, S), Image.LANCZOS)


def santur_icon(S):
    ss = 8
    im = Image.new("RGBA", (S * ss, S * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    W = S * ss
    d.polygon([(W * .05, W * .8), (W * .95, W * .8), (W * .75, W * .25), (W * .25, W * .25)], fill=GOLD_D, outline=GOLD)
    for k in range(5):
        y = W * (.32 + k * .1)
        d.line([(W * (.22 - k * .03), y), (W * (.78 + k * .03), y)], fill=CREAM, width=max(1, W // 40))
    d.line([(W * .3, W * .1), (W * .45, W * .5)], fill=TURQ, width=W // 14)  # mezrab
    return im.resize((S, S), Image.LANCZOS)


def rgb565_swapped(c):
    v = ((c[0] >> 3) << 11) | ((c[1] >> 2) << 5) | (c[2] >> 3)
    return ((v >> 8) | (v << 8)) & 0xFFFF


def splash_header(im, path):
    q = im.quantize(colors=16, method=Image.MEDIANCUT, dither=Image.NONE)
    pal = q.getpalette()[:48]
    pal += [0] * (48 - len(pal))
    px = q.tobytes()
    packed = bytes((px[i] << 4) | px[i + 1] for i in range(0, len(px), 2))
    lines = ["/* generated by tools/gen_simorgh_art.py: the Simorgh boot splash, 240 x 240, 4 bpp, do not edit */",
             "#define SIMORGH_W 240", "#define SIMORGH_H 240",
             "static const uint16_t SIMORGH_PAL[16] = {" + ", ".join(
                 "0x%04X" % rgb565_swapped(pal[i * 3:i * 3 + 3]) for i in range(16)) + "};",
             "static const uint8_t SIMORGH_PX[%d] = {" % len(packed)]
    for i in range(0, len(packed), 24):
        lines.append("    " + ", ".join("0x%02X" % b for b in packed[i:i + 24]) + ",")
    lines.append("};")
    path.write_text("\n".join(lines) + "\n")
    return q.convert("RGB")


def banner(font):
    W, H = 1600, 400
    im = Image.new("RGB", (W, H), LAPIS_D)
    d = ImageDraw.Draw(im)
    for x in range(0, W + 100, 100):
        for y in (50, 350):
            d.polygon(star8(x, y, 40, math.pi / 8), fill=GOLD, outline=GOLD_D)
            d.polygon(star8(x, y, 18), fill=TURQ)
    d.rectangle([0, 100, W, 300], fill=LAPIS)
    im.paste(illustration(200), (40, 100))
    lat = ImageFont.truetype(str(ROOT / "assets/fonts/InterTight[wght].ttf"), 96)
    d.text((280, 140), "Simorgh", font=lat, fill=GOLD)
    small = ImageFont.truetype(str(ROOT / "assets/fonts/InterTight[wght].ttf"), 30)
    d.text((290, 250), "santur & dastgah firmware for M-VAVE FM-1 · fork of Felucca", font=small, fill=CREAM)
    if font:
        fa = ImageFont.truetype(font, 110, layout_engine=ImageFont.Layout.RAQM)
        d.text((W - 60, 200), "سیمرغ", font=fa, fill=TURQ_L, anchor="rm", direction="rtl", language="fa")
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", help="OFL Persian font (Vazirmatn) for the banner's Persian script")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    illustration(1024).save(OUT / "simorgh_full.png")
    banner(a.font).save(OUT / "simorgh_banner.png")
    splash_header(illustration(240), ROOT / "firmware/src/simorgh_splash.h").save(OUT / "splash_240.png")
    santur_icon(24).save(OUT / "santur_icon_24.png")
    santur_icon(256).save(OUT / "santur_icon_256.png")


if __name__ == "__main__":
    main()
