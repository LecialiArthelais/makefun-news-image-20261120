#!/usr/bin/env python3
"""Render the 20 November 2026 front page, v3 — evening pass.

Reads stories.json (40 stories: 36 with event_date 2026-11-20, plus
four Thursday late closes — Anthropic, Senate, Berlin, Pete Rose —
carried as the Friday paper's lead stories, the way the day's papers
do) and draws a 1024x1024 newspaper front page with Pillow:
cream paper, navy ribbon, a giant serif date masthead, a coloured region
bar, a THE DAY IN NUMBERS strip, a FRIDAY BY THE HOURS timeline, three
illustrated hero cards, ten illustrated medium cards, a dark-blue world
map with numbered pins, a numbered ALSO TODAY list, a DATE CHECK box
naming the big stories that happened BEFORE Friday, and a footer promise.

Every picture is an original flat-vector drawing made by code in this
file — no photographs, no AI images. The drawing is fully deterministic:
fixed typefaces, fixed positions, no clock, no network, no randomness.
Running it twice gives byte-identical PNGs. main.ts copies the finished
entry.png to the grader's output directory.

Typefaces are OFL faces from the canvas-design skill's bundled fonts:
  ~/workspace/custom-skills/canvas-design/canvas-fonts/
"""

import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# --- Canvas ---------------------------------------------------------------
PAGE_W, PAGE_H = 1024, 1024
EDGE = 30
CONTENT_W = PAGE_W - 2 * EDGE  # 964

FONT_DIR = os.path.expanduser(
    "~/workspace/custom-skills/canvas-design/canvas-fonts"
)

# --- Palette: cream paper, ink, navy ribbon, one red, muted region hues.
PAPER = (246, 239, 221)      # cream
INK = (26, 26, 26)
NAVY = (24, 48, 88)
RED = (180, 35, 24)
GREY = (110, 105, 95)
HAIRLINE = (205, 198, 184)
PANEL = (238, 231, 214)      # slightly darker cream for boxes
WHITE = (255, 255, 255)
GOLD = (198, 142, 32)
SEA = (18, 52, 86)           # deep blue, map + cyclone art
LAND = (246, 239, 221)       # map land = paper cream
TEAL = (30, 110, 104)
GREEN = (64, 110, 66)
PLUM = (110, 70, 120)

REGION_COLOURS = [
    ("EUROPE", 11, (36, 64, 110)),
    ("ASIA-PACIFIC", 13, RED),
    ("AMERICAS", 7, (176, 124, 28)),
    ("MIDEAST", 4, PLUM),
    ("AFRICA", 1, GREEN),
    ("OCEANIA", 2, TEAL),
    ("WORLD", 2, GREY),
]

# --- Type roles: (font file, point size) ----------------------------------
TYPE = {
    "masthead": ("Gloock-Regular.ttf", 50),
    "eyebrow": ("IBMPlexMono-Bold.ttf", 12),
    "subline": ("CrimsonPro-Italic.ttf", 17),
    "num_value": ("Gloock-Regular.ttf", 30),
    "num_label": ("IBMPlexMono-Regular.ttf", 10),
    "timeline": ("IBMPlexMono-Regular.ttf", 10),
    "hero_head": ("CrimsonPro-Bold.ttf", 19),
    "hero_deck": ("InstrumentSans-Regular.ttf", 12),
    "hero_src": ("IBMPlexMono-Regular.ttf", 10),
    "med_head": ("InstrumentSans-Bold.ttf", 13),
    "med_deck": ("InstrumentSans-Regular.ttf", 11),
    "med_src": ("IBMPlexMono-Regular.ttf", 9),
    "also": ("InstrumentSans-Regular.ttf", 12),
    "also_num": ("InstrumentSans-Bold.ttf", 12),
    "check": ("InstrumentSans-Regular.ttf", 11),
    "check_head": ("IBMPlexMono-Bold.ttf", 11),
    "foot": ("IBMPlexMono-Regular.ttf", 10),
    "map_label": ("IBMPlexMono-Bold.ttf", 11),
    "pin": ("InstrumentSans-Bold.ttf", 11),
}

HERE = os.path.dirname(os.path.abspath(__file__))


def typeface(role):
    """Load the typeface for a named role."""
    name, size = TYPE[role]
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap_text(text, face, max_width):
    """Greedy word wrap into lines that fit max_width.

    A lone short word is never left widowed on the last line: when that
    happens, the previous line gives up its final word to join it.
    """
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if face.getlength(trial) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    if len(lines) >= 2:
        tail = lines[-1].split()
        if len(tail) == 1 and len(tail[0]) <= 6:
            head = lines[-2].split()
            if len(head) >= 2:
                lines[-2] = " ".join(head[:-1])
                lines[-1] = head[-1] + " " + lines[-1]
    return lines


def spaced_text(draw, x, y, text, face, fill, gap=3):
    """Draw a string with manual letter-spacing (small-caps mono feel)."""
    pen = x
    for char in text:
        draw.text((pen, y), char, font=face, fill=fill)
        pen += int(face.getlength(char)) + gap
    return pen


def spaced_width(text, face, gap=3):
    """Width of a string drawn with the given letter-spacing."""
    return sum(int(face.getlength(c)) + gap for c in text) - gap


def spaced_centred(draw, centre, y, text, face, fill, gap=3):
    """Draw letter-spaced text centred on a point."""
    width = spaced_width(text, face, gap)
    spaced_text(draw, centre - width // 2, y, text, face, fill, gap)


def hline(draw, x0, x1, y, colour=HAIRLINE, weight=1):
    """A horizontal hairline rule."""
    draw.line([(x0, y), (x1, y)], fill=colour, width=weight)


def section_head(draw, x, y, label, width=CONTENT_W):
    """Red small-caps eyebrow label, with a hairline running after it."""
    face = typeface("eyebrow")
    spaced_text(draw, x, y, label, face, RED, gap=3)
    label_w = spaced_width(label, face, 3)
    hline(draw, x + label_w + 12, x + width, y + 8)
    return y + 20


def star4(draw, cx, cy, r, fill):
    """A four-point star (a diamond), for flags and skies."""
    draw.polygon([(cx, cy - r), (cx + r * 0.45, cy - r * 0.45),
                  (cx + r, cy), (cx + r * 0.45, cy + r * 0.45),
                  (cx, cy + r), (cx - r * 0.45, cy + r * 0.45),
                  (cx - r, cy), (cx - r * 0.45, cy - r * 0.45)],
                 fill=fill)


# --- Illustrations: original flat-vector drawings, one per story ---------
# Each takes (draw, x, y, w, h) and draws inside that box using fractions
# of w/h, so the same drawing works as a wide hero panel and as a small
# square icon. Text inside art is drawn only when the box is wide enough
# for it to stay legible.

def art_akvan(draw, x, y, w, h):
    """Cyclone Akvan: spiral arms over a deep-blue sea, red eye."""
    draw.rectangle([x, y, x + w, y + h], fill=SEA)
    cx, cy = x + w * 0.5, y + h * 0.56
    m = min(w, h)
    # Spiral arms: concentric arcs, each spanning a different sweep.
    for i, (r, a0, a1, col) in enumerate([
            (0.44, 20, 300, (235, 240, 245)),
            (0.34, 140, 60, (190, 210, 225)),
            (0.24, 260, 180, (235, 240, 245)),
            (0.15, 40, 320, (190, 210, 225))]):
        rr = m * r
        draw.arc([cx - rr, cy - rr, cx + rr, cy + rr], a0, a1,
                 fill=col, width=max(2, int(m * 0.045)))
    # Red eye.
    er = max(3, m * 0.06)
    draw.ellipse([cx - er, cy - er, cx + er, cy + er], fill=RED)
    draw.ellipse([cx - er * 1.9, cy - er * 1.9, cx + er * 1.9,
                  cy + er * 1.9], outline=(235, 240, 245), width=1)
    # Rain slashes along the bottom.
    for i in range(7):
        rx = x + w * (0.06 + i * 0.14)
        ry = y + h * 0.86
        draw.line([(rx, ry), (rx - w * 0.02, ry + h * 0.10)],
                  fill=(190, 210, 225), width=2)
    # Land sliver at the bottom-right: the coast the storm hits.
    draw.polygon([(x + w * 0.62, y + h), (x + w, y + h * 0.88),
                  (x + w, y + h)], fill=(214, 196, 150))


def art_cop31(draw, x, y, w, h):
    """COP31 Antalya: sun over green hills and a blue lake."""
    draw.rectangle([x, y, x + w, y + h], fill=(214, 232, 238))
    # Sun.
    sx, sy, sr = x + w * 0.78, y + h * 0.24, min(w, h) * 0.13
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(232, 122, 42))
    # Hills.
    draw.polygon([(x, y + h * 0.62), (x + w * 0.30, y + h * 0.38),
                  (x + w * 0.58, y + h * 0.62), (x, y + h * 0.62)],
                 fill=(96, 140, 88))
    draw.polygon([(x + w * 0.42, y + h * 0.62), (x + w * 0.72, y + h * 0.34),
                  (x + w, y + h * 0.62), (x + w * 0.42, y + h * 0.62)],
                 fill=(64, 110, 66))
    # Lake.
    draw.rectangle([x, y + h * 0.62, x + w, y + h], fill=(58, 110, 158))
    draw.line([(x + w * 0.12, y + h * 0.76), (x + w * 0.38, y + h * 0.76)],
              fill=(235, 240, 245), width=2)
    draw.line([(x + w * 0.55, y + h * 0.88), (x + w * 0.88, y + h * 0.88)],
              fill=(235, 240, 245), width=2)
    # Three summit flags on the shore.
    for i, col in enumerate([(180, 35, 24), (24, 48, 88), (198, 142, 32)]):
        fx = x + w * (0.30 + i * 0.20)
        draw.line([(fx, y + h * 0.40), (fx, y + h * 0.62)], fill=INK, width=2)
        draw.polygon([(fx, y + h * 0.40), (fx + w * 0.09, y + h * 0.44),
                      (fx, y + h * 0.48)], fill=col)


def art_ukeu(draw, x, y, w, h):
    """UK-EU reset: gold stars in a circle beside a Union Jack."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    m = min(w, h)
    cx, cy, r = x + w * 0.30, y + h * 0.5, m * 0.34
    for i in range(12):
        a = math.radians(i * 30 - 90)
        star4(draw, cx + r * math.cos(a), cy + r * math.sin(a),
              max(2, m * 0.035), GOLD)
    # Union Jack, simplified: blue field, white saltire, red cross.
    fx0, fy0 = x + w * 0.58, y + h * 0.28
    fw, fh = w * 0.34, h * 0.44
    draw.rectangle([fx0, fy0, fx0 + fw, fy0 + fh], fill=(200, 210, 225))
    draw.polygon([(fx0, fy0), (fx0 + fw * 0.18, fy0),
                  (fx0 + fw, fy0 + fh), (fx0 + fw * 0.82, fy0 + fh)],
                 fill=WHITE)
    draw.polygon([(fx0 + fw, fy0), (fx0 + fw * 0.82, fy0),
                  (fx0, fy0 + fh), (fx0 + fw * 0.18, fy0 + fh)], fill=WHITE)
    draw.rectangle([fx0 + fw * 0.44, fy0, fx0 + fw * 0.56, fy0 + fh],
                   fill=RED)
    draw.rectangle([fx0, fy0 + fh * 0.40, fx0 + fw, fy0 + fh * 0.60],
                   fill=RED)
    draw.rectangle([fx0, fy0, fx0 + fw, fy0 + fh], outline=WHITE, width=1)


def art_apec(draw, x, y, w, h):
    """APEC Shenzhen: three flag banners — China, Australia, Indonesia."""
    draw.rectangle([x, y, x + w, y + h], fill=(222, 228, 232))
    draw.rectangle([x, y, x + w, y + h * 0.08], fill=INK)
    bw, bh = w * 0.22, h * 0.62
    # China: red, gold stars.
    bx = x + w * 0.10
    draw.rectangle([bx, y + h * 0.08, bx + bw, y + h * 0.08 + bh],
                   fill=(222, 42, 36))
    star4(draw, bx + bw * 0.30, y + h * 0.08 + bh * 0.22, bw * 0.14, GOLD)
    star4(draw, bx + bw * 0.68, y + h * 0.08 + bh * 0.16, bw * 0.08, GOLD)
    star4(draw, bx + bw * 0.72, y + h * 0.08 + bh * 0.38, bw * 0.08, GOLD)
    # Australia: blue, white stars + Union Jack corner.
    bx = x + w * 0.39
    draw.rectangle([bx, y + h * 0.08, bx + bw, y + h * 0.08 + bh],
                   fill=(36, 64, 110))
    draw.rectangle([bx, y + h * 0.08, bx + bw * 0.5, y + h * 0.08 + bh * 0.4],
                   fill=(200, 210, 225))
    star4(draw, bx + bw * 0.72, y + h * 0.08 + bh * 0.55, bw * 0.12, WHITE)
    star4(draw, bx + bw * 0.30, y + h * 0.08 + bh * 0.72, bw * 0.10, WHITE)
    # Indonesia: red over white.
    bx = x + w * 0.68
    draw.rectangle([bx, y + h * 0.08, bx + bw, y + h * 0.08 + bh * 0.5],
                   fill=(222, 42, 36))
    draw.rectangle([bx, y + h * 0.08 + bh * 0.5, bx + bw,
                    y + h * 0.08 + bh], fill=WHITE)


def art_youth(draw, x, y, w, h):
    """Youth Strike: a placard above a crowd of raised hands."""
    draw.rectangle([x, y, x + w, y + h], fill=(247, 214, 120))
    # Placard on a stick.
    px, py = x + w * 0.18, y + h * 0.10
    pw, ph = w * 0.64, h * 0.42
    draw.rectangle([px, py, px + pw, py + ph], fill=WHITE,
                   outline=RED, width=3)
    # Fake text lines on the placard.
    for i in range(3):
        ly = py + ph * (0.22 + i * 0.26)
        draw.line([(px + pw * 0.12, ly), (px + pw * (0.88 - i * 0.18), ly)],
                  fill=RED, width=max(2, int(h * 0.045)))
    draw.line([(x + w * 0.5, py + ph), (x + w * 0.5, y + h * 0.62)],
              fill=INK, width=3)
    # Crowd: heads + raised arms.
    for i in range(6):
        hx = x + w * (0.10 + i * 0.16)
        hy = y + h * 0.82
        draw.line([(hx, hy + h * 0.06), (hx - w * 0.03, hy - h * 0.10)],
                  fill=INK, width=2)
        draw.ellipse([hx - w * 0.045, hy - h * 0.02, hx + w * 0.045,
                      hy + h * 0.14], fill=INK)


def art_italy(draw, x, y, w, h):
    """Italy strike: the Colosseum under a red SCIOPERO banner."""
    draw.rectangle([x, y, x + w, y + h], fill=(232, 214, 178))
    # Dome behind.
    draw.ellipse([x + w * 0.62, y - h * 0.22, x + w * 0.94, y + h * 0.42],
                 fill=(196, 150, 110))
    # Colosseum: tan block with two rows of arches.
    cx0, cy0 = x + w * 0.08, y + h * 0.42
    cw, ch = w * 0.84, h * 0.50
    draw.rectangle([cx0, cy0, cx0 + cw, cy0 + ch], fill=(214, 176, 128))
    for row in range(2):
        for i in range(5):
            ax = cx0 + cw * (0.08 + i * 0.18)
            ay = cy0 + ch * (0.18 + row * 0.42)
            draw.arc([ax, ay, ax + cw * 0.10, ay + ch * 0.34], 180, 360,
                     fill=(120, 84, 56), width=2)
            draw.line([(ax, ay + ch * 0.17), (ax, ay + ch * 0.34)],
                      fill=(120, 84, 56), width=2)
            draw.line([(ax + cw * 0.10, ay + ch * 0.17),
                       (ax + cw * 0.10, ay + ch * 0.34)],
                      fill=(120, 84, 56), width=2)
    # Red strike banner across the top.
    draw.rectangle([x, y + h * 0.06, x + w, y + h * 0.22], fill=RED)
    if w >= 150:
        face = ImageFont.truetype(
            os.path.join(FONT_DIR, "InstrumentSans-Bold.ttf"),
            max(10, int(h * 0.11)))
        txt = "SCIOPERO GENERALE"
        draw.text(((x + w - face.getlength(txt)) / 2, y + h * 0.085),
                  txt, font=face, fill=WHITE)


def art_cricket(draw, x, y, w, h):
    """Cricket: bat, red ball and stumps over a green strip."""
    draw.rectangle([x, y, x + w, y + h], fill=(222, 228, 216))
    # Pitch strip.
    draw.rectangle([x, y + h * 0.66, x + w, y + h], fill=(120, 160, 90))
    draw.rectangle([x + w * 0.42, y + h * 0.66, x + w * 0.58, y + h],
                   fill=(214, 196, 150))
    # Stumps.
    for i in range(3):
        sx = x + w * (0.70 + i * 0.05)
        draw.rectangle([sx, y + h * 0.44, sx + w * 0.018, y + h * 0.68],
                       fill=(232, 190, 80))
    # Bat, diagonal.
    draw.polygon([(x + w * 0.16, y + h * 0.72), (x + w * 0.22, y + h * 0.70),
                  (x + w * 0.44, y + h * 0.30), (x + w * 0.38, y + h * 0.28)],
                 fill=(214, 176, 128))
    draw.line([(x + w * 0.41, y + h * 0.29), (x + w * 0.50, y + h * 0.14)],
              fill=(120, 84, 56), width=max(2, int(w * 0.02)))
    # Red ball mid-air with seam.
    bx, by, br = x + w * 0.62, y + h * 0.24, min(w, h) * 0.11
    draw.ellipse([bx - br, by - br, bx + br, by + br], fill=RED)
    draw.arc([bx - br, by - br, bx + br, by + br], 200, 340, fill=WHITE,
             width=1)


def art_florida(draw, x, y, w, h):
    """Florida floods: a house half under water, gauge at 18.3 ft."""
    draw.rectangle([x, y, x + w, y + h], fill=(178, 196, 208))
    # Rain.
    for i in range(6):
        rx = x + w * (0.08 + i * 0.15)
        draw.line([(rx, y + h * 0.06), (rx - w * 0.02, y + h * 0.18)],
                  fill=(235, 240, 245), width=2)
    # House: walls + roof, waterline cutting across.
    hx0, hy0 = x + w * 0.14, y + h * 0.34
    hw, hh = w * 0.44, h * 0.34
    draw.polygon([(hx0 - w * 0.03, hy0), (hx0 + hw / 2, hy0 - h * 0.16),
                  (hx0 + hw + w * 0.03, hy0)], fill=(150, 60, 44))
    draw.rectangle([hx0, hy0, hx0 + hw, hy0 + hh], fill=(240, 234, 220))
    draw.rectangle([hx0 + hw * 0.38, hy0 + hh * 0.45, hx0 + hw * 0.62,
                    hy0 + hh], fill=(90, 70, 60))
    # Flood water.
    draw.rectangle([x, y + h * 0.68, x + w, y + h], fill=(38, 90, 140))
    draw.line([(x + w * 0.06, y + h * 0.76), (x + w * 0.30, y + h * 0.76)],
              fill=(235, 240, 245), width=2)
    draw.line([(x + w * 0.55, y + h * 0.86), (x + w * 0.86, y + h * 0.86)],
              fill=(235, 240, 245), width=2)
    # Gauge post with red high-water mark.
    gx = x + w * 0.78
    draw.rectangle([gx, y + h * 0.30, gx + w * 0.03, y + h * 0.94],
                   fill=WHITE)
    draw.rectangle([gx - w * 0.02, y + h * 0.62, gx + w * 0.05,
                    y + h * 0.66], fill=RED)


def art_gta(draw, x, y, w, h):
    """GTA VI: sunset bands, a big VI, a palm silhouette."""
    # Sunset bands: purple, orange, pink.
    bands = [(88, 40, 120), (214, 90, 60), (232, 122, 90), (244, 178, 120)]
    for i, col in enumerate(bands):
        draw.rectangle([x, y + h * i / 4, x + w, y + h * (i + 1) / 4],
                       fill=col)
    # Sun.
    sx, sy, sr = x + w * 0.30, y + h * 0.42, min(w, h) * 0.16
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(250, 220, 130))
    # Big VI.
    if w >= 48:
        face = ImageFont.truetype(
            os.path.join(FONT_DIR, "InstrumentSans-Bold.ttf"),
            max(18, int(h * 0.52)))
        txt = "VI"
        draw.text((x + w * 0.44 - face.getlength(txt) / 2,
                   y + h * 0.22), txt, font=face, fill=WHITE)
    # Palm silhouette, right.
    tx, ty = x + w * 0.84, y + h * 0.92
    draw.line([(tx, ty), (tx + w * 0.02, y + h * 0.42)], fill=INK, width=3)
    for a in (-160, -120, -80, -40, -10):
        r = math.radians(a)
        ex = tx + w * 0.14 * math.cos(r)
        ey = y + h * 0.42 + h * 0.10 * math.sin(r)
        draw.line([(tx + w * 0.02, y + h * 0.42), (ex, ey)], fill=INK,
                  width=2)


def art_markets(draw, x, y, w, h):
    """Asian markets rout: a red chart falling off a cliff, −7%."""
    draw.rectangle([x, y, x + w, y + h], fill=(240, 234, 222))
    # Grid lines.
    for i in range(1, 4):
        gy = y + h * i / 4
        draw.line([(x + w * 0.06, gy), (x + w * 0.94, gy)],
                  fill=(220, 212, 196), width=1)
    # Falling line with arrowhead.
    pts = [(x + w * 0.08, y + h * 0.22), (x + w * 0.28, y + h * 0.30),
           (x + w * 0.46, y + h * 0.28), (x + w * 0.64, y + h * 0.52),
           (x + w * 0.82, y + h * 0.78), (x + w * 0.92, y + h * 0.86)]
    draw.line(pts, fill=RED, width=max(2, int(min(w, h) * 0.05)))
    ex, ey = pts[-1]
    draw.polygon([(ex, ey), (ex - w * 0.07, ey - h * 0.02),
                  (ex - w * 0.02, ey - h * 0.09)], fill=RED)
    if w >= 120:
        face = ImageFont.truetype(
            os.path.join(FONT_DIR, "InstrumentSans-Bold.ttf"),
            max(14, int(h * 0.30)))
        draw.text((x + w * 0.06, y + h * 0.06), "−7%", font=face, fill=RED)


def art_china(draw, x, y, w, h):
    """China holds rates: a big ¥ over a flat line and bank columns."""
    draw.rectangle([x, y, x + w, y + h], fill=(240, 234, 222))
    # Bank columns at the bottom.
    for i in range(3):
        cx0 = x + w * (0.14 + i * 0.28)
        draw.rectangle([cx0, y + h * 0.72, cx0 + w * 0.14, y + h * 0.92],
                       fill=(150, 140, 125))
    draw.rectangle([x + w * 0.08, y + h * 0.66, x + w * 0.92,
                    y + h * 0.72], fill=(120, 110, 95))
    # Flat rate line across the middle.
    draw.line([(x + w * 0.08, y + h * 0.52), (x + w * 0.92, y + h * 0.52)],
              fill=GREY, width=2)
    for i in range(5):
        px = x + w * (0.14 + i * 0.18)
        draw.ellipse([px - 2, y + h * 0.52 - 2, px + 2, y + h * 0.52 + 2],
                     fill=RED)
    if w >= 48:
        face = ImageFont.truetype(
            os.path.join(FONT_DIR, "InstrumentSans-Bold.ttf"),
            max(16, int(h * 0.34)))
        txt = "¥"
        draw.text((x + w * 0.5 - face.getlength(txt) / 2, y + h * 0.06),
                  txt, font=face, fill=RED)


def art_modi(draw, x, y, w, h):
    """Modi opens SCO forum: Purana Qila's red sandstone gate."""
    draw.rectangle([x, y, x + w, y + h], fill=(238, 222, 190))
    # Gate: red block with an arched doorway.
    gx0, gy0 = x + w * 0.22, y + h * 0.30
    gw, gh = w * 0.56, h * 0.62
    draw.rectangle([gx0, gy0, gx0 + gw, gy0 + gh], fill=(178, 62, 40))
    draw.pieslice([gx0 + gw * 0.30, gy0 + gh * 0.42, gx0 + gw * 0.70,
                   gy0 + gh * 1.02], 180, 360, fill=(238, 222, 190))
    draw.rectangle([gx0 + gw * 0.30, gy0 + gh * 0.68, gx0 + gw * 0.70,
                    gy0 + gh], fill=(238, 222, 190))
    # Dome + finial.
    draw.ellipse([gx0 + gw * 0.30, gy0 - h * 0.20, gx0 + gw * 0.70,
                  gy0 + h * 0.06], fill=(178, 62, 40))
    draw.line([(gx0 + gw * 0.5, gy0 - h * 0.20),
               (gx0 + gw * 0.5, gy0 - h * 0.28)], fill=INK, width=2)
    # Side turrets.
    draw.rectangle([gx0 - w * 0.10, gy0 + gh * 0.30, gx0, gy0 + gh],
                   fill=(150, 50, 34))
    draw.rectangle([gx0 + gw, gy0 + gh * 0.30, gx0 + gw + w * 0.10,
                    gy0 + gh], fill=(150, 50, 34))
    # Two small flags on the gate.
    for fx in (gx0 + gw * 0.18, gx0 + gw * 0.82):
        draw.line([(fx, gy0 - h * 0.06), (fx, gy0 + h * 0.12)], fill=INK,
                  width=1)
        draw.polygon([(fx, gy0 - h * 0.06), (fx + w * 0.08, gy0 - h * 0.02),
                      (fx, gy0 + h * 0.02)], fill=(232, 122, 42))


def art_gaza(draw, x, y, w, h):
    """Gaza overnight: a row of tents under a grey sky."""
    draw.rectangle([x, y, x + w, y + h], fill=(206, 198, 186))
    # Pale moon.
    mx, my, mr = x + w * 0.80, y + h * 0.20, min(w, h) * 0.10
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(240, 234, 220))
    # Smoke column.
    for i, r in enumerate([0.05, 0.07, 0.09]):
        draw.ellipse([x + w * (0.18 + i * 0.02) - min(w, h) * r,
                      y + h * (0.14 + i * 0.12) - min(w, h) * r,
                      x + w * (0.18 + i * 0.02) + min(w, h) * r,
                      y + h * (0.14 + i * 0.12) + min(w, h) * r],
                     fill=(150, 144, 134))
    # Ground + tents.
    draw.rectangle([x, y + h * 0.68, x + w, y + h], fill=(150, 132, 104))
    for i in range(4):
        tx0 = x + w * (0.06 + i * 0.24)
        tw = w * 0.20
        draw.polygon([(tx0, y + h * 0.68), (tx0 + tw / 2, y + h * 0.38),
                      (tx0 + tw, y + h * 0.68)], fill=(240, 234, 220),
                     outline=(120, 110, 96))
        draw.line([(tx0 + tw / 2, y + h * 0.38),
                   (tx0 + tw / 2, y + h * 0.68)], fill=(120, 110, 96),
                  width=1)


def art_anthropic(draw, x, y, w, h):
    """Anthropic first close: rising candlesticks on dark green."""
    draw.rectangle([x, y, x + w, y + h], fill=(24, 64, 44))
    # Baseline grid.
    for i in range(1, 3):
        gy = y + h * i / 3
        draw.line([(x + w * 0.06, gy), (x + w * 0.94, gy)],
                  fill=(52, 96, 72), width=1)
    # Five candles climbing left to right; last one tallest, green.
    cols = [(214, 90, 60), (214, 90, 60), (110, 190, 120),
            (110, 190, 120), (140, 215, 150)]
    for i, col in enumerate(cols):
        cx0 = x + w * (0.10 + i * 0.18)
        cw = w * 0.09
        top = y + h * (0.62 - i * 0.10)
        bot = y + h * (0.78 - i * 0.06)
        draw.line([(cx0 + cw / 2, top - h * 0.08),
                   (cx0 + cw / 2, bot + h * 0.06)], fill=col, width=2)
        draw.rectangle([cx0, top, cx0 + cw, bot], fill=col)
    # Arrowhead on the last candle's wick.
    ex, ey = x + w * 0.86, y + h * 0.10
    draw.polygon([(ex, ey), (ex - w * 0.07, ey + h * 0.10),
                  (ex + w * 0.07, ey + h * 0.10)], fill=(140, 215, 150))


def art_senate(draw, x, y, w, h):
    """Senate war-powers vote: the Capitol dome on navy."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    # Dome.
    dx0, dy0 = x + w * 0.30, y + h * 0.30
    dw, dh = w * 0.40, h * 0.34
    draw.pieslice([dx0, dy0 - dh * 0.55, dx0 + dw, dy0 + dh * 0.45],
                  180, 360, fill=(240, 234, 220))
    draw.rectangle([dx0, dy0 + dh * 0.10, dx0 + dw, dy0 + dh], fill=WHITE)
    draw.line([(dx0 + dw * 0.5, dy0 - dh * 0.55),
               (dx0 + dw * 0.5, dy0 - dh * 0.75)], fill=WHITE, width=2)
    # Columns.
    for i in range(5):
        cx0 = x + w * (0.16 + i * 0.15)
        draw.rectangle([cx0, y + h * 0.68, cx0 + w * 0.06, y + h * 0.92],
                       fill=(240, 234, 220))
    draw.rectangle([x + w * 0.10, y + h * 0.64, x + w * 0.90,
                    y + h * 0.68], fill=(240, 234, 220))
    draw.rectangle([x + w * 0.10, y + h * 0.92, x + w * 0.90,
                    y + h * 0.96], fill=(240, 234, 220))
    # Red vote tally bar.
    draw.rectangle([x + w * 0.08, y + h * 0.08, x + w * 0.92,
                    y + h * 0.16], fill=RED)


def art_berlin(draw, x, y, w, h):
    """Berlin talks: the Brandenburg Gate at dusk, German colours."""
    draw.rectangle([x, y, x + w, y + h], fill=(222, 214, 190))
    # Sky band.
    draw.rectangle([x, y, x + w, y + h * 0.30], fill=(214, 178, 120))
    # Gate: entablature + six columns.
    draw.rectangle([x + w * 0.10, y + h * 0.30, x + w * 0.90,
                    y + h * 0.42], fill=(150, 132, 104))
    for i in range(6):
        cx0 = x + w * (0.13 + i * 0.135)
        draw.rectangle([cx0, y + h * 0.42, cx0 + w * 0.07, y + h * 0.92],
                       fill=(178, 160, 130))
    draw.rectangle([x + w * 0.10, y + h * 0.92, x + w * 0.90,
                    y + h * 0.96], fill=(150, 132, 104))
    # Quadriga: tiny chariot silhouette on top.
    draw.polygon([(x + w * 0.44, y + h * 0.30), (x + w * 0.50, y + h * 0.18),
                  (x + w * 0.56, y + h * 0.30)], fill=INK)
    # German flag stripe at the base.
    for i, col in enumerate([(0, 0, 0), (222, 42, 36), (232, 190, 60)]):
        draw.rectangle([x + w * (0.10 + i * 0.27), y + h * 0.97,
                        x + w * (0.37 + i * 0.27), y + h], fill=col)


def art_baseball(draw, x, y, w, h):
    """Pete Rose: a baseball with red seams over a green field."""
    draw.rectangle([x, y, x + w, y + h], fill=(64, 110, 66))
    # Outfield wall.
    draw.rectangle([x, y + h * 0.72, x + w, y + h], fill=(120, 160, 90))
    # The ball.
    bx, by, br = x + w * 0.5, y + h * 0.44, min(w, h) * 0.34
    draw.ellipse([bx - br, by - br, bx + br, by + br], fill=WHITE,
                 outline=(200, 200, 200), width=1)
    # Red seams: two curved stitch lines.
    draw.arc([bx - br * 0.85, by - br, bx + br * 0.45, by + br], 250, 70,
             fill=RED, width=max(2, int(min(w, h) * 0.04)))
    draw.arc([bx - br * 0.45, by - br, bx + br * 0.85, by + br], 70, 250,
             fill=RED, width=max(2, int(min(w, h) * 0.04)))
    # Stitch ticks along the seams.
    for a in (290, 320, 350, 20):
        r = math.radians(a)
        sx, sy = bx + br * 0.55 * math.cos(r), by + br * 0.85 * math.sin(r)
        draw.line([(sx - 3, sy), (sx + 3, sy)], fill=RED, width=2)
    for a in (110, 140, 170, 200):
        r = math.radians(a)
        sx, sy = bx + br * 0.55 * math.cos(r), by + br * 0.85 * math.sin(r)
        draw.line([(sx - 3, sy), (sx + 3, sy)], fill=RED, width=2)


ART = {
    "akvan": art_akvan, "cop31": art_cop31, "ukeu": art_ukeu,
    "apec": art_apec, "youth": art_youth, "italy": art_italy,
    "cricket": art_cricket, "florida": art_florida, "gta": art_gta,
    "markets": art_markets, "china": art_china, "modi": art_modi,
    "gaza": art_gaza,
    "anthropic": art_anthropic, "senate": art_senate,
    "berlin": art_berlin, "baseball": art_baseball,
}


# --- World map: dark-blue panel, cream land, numbered pins ----------------
# Rough equirectangular continent outlines (lon, lat). Asia is drawn
# first and Europe over it, so their shared border needs no precision.

CONTINENTS = [
    [  # Asia
        (30, 36), (33, 36), (36, 36), (39, 38), (44, 39), (48, 37),
        (48, 33), (50, 30), (54, 27), (58, 25), (62, 25), (66, 25),
        (69, 23), (72, 20), (76, 13), (77, 8), (80, 9), (80, 13),
        (85, 19), (88, 21), (91, 22), (93, 16), (97, 15), (100, 9),
        (103, 2), (105, 6), (107, 11), (109, 13), (109, 17), (106, 20),
        (108, 21), (110, 20), (113, 22), (118, 25), (120, 27), (121, 31),
        (122, 36), (124, 40), (127, 40), (130, 42), (133, 44), (137, 46),
        (141, 50), (142, 54), (141, 59), (145, 59), (150, 60), (156, 60),
        (158, 62), (162, 66), (170, 66), (178, 65), (180, 66), (178, 68),
        (172, 68), (165, 70), (158, 71), (150, 72), (142, 72), (135, 72),
        (128, 71), (120, 73), (113, 74), (105, 76), (98, 76), (90, 75),
        (83, 74), (75, 73), (68, 72), (60, 69), (52, 68), (45, 68),
        (38, 67), (32, 68), (30, 68),
    ],
    [  # North America
        (-168, 66), (-152, 70), (-135, 69), (-125, 71), (-115, 68),
        (-100, 68), (-90, 66), (-85, 66), (-82, 69), (-78, 71),
        (-70, 62), (-65, 60), (-60, 55), (-55, 47), (-60, 45),
        (-65, 44), (-70, 42), (-74, 40), (-76, 35), (-80, 32),
        (-81, 26), (-84, 30), (-89, 29), (-91, 19), (-96, 16),
        (-100, 17), (-105, 20), (-110, 23), (-114, 28), (-117, 33),
        (-122, 37), (-124, 42), (-124, 48), (-130, 54), (-135, 58),
        (-145, 60), (-155, 58), (-162, 55), (-166, 60), (-168, 66),
    ],
    [  # Greenland
        (-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68),
        (-22, 70), (-20, 74), (-25, 77), (-35, 77), (-45, 75),
        (-55, 73), (-58, 70), (-58, 64),
    ],
    [  # South America
        (-79, 9), (-77, 4), (-75, 10), (-72, 12), (-64, 11), (-60, 8),
        (-52, 5), (-50, 0), (-44, -3), (-35, -8), (-37, -13),
        (-39, -17), (-41, -22), (-48, -27), (-52, -32), (-58, -35),
        (-62, -39), (-65, -41), (-68, -47), (-70, -52), (-74, -50),
        (-73, -44), (-73, -37), (-72, -30), (-71, -22), (-70, -18),
        (-75, -15), (-77, -12), (-80, -6), (-81, -1), (-80, 4), (-79, 9),
    ],
    [  # Africa
        (-17, 15), (-17, 20), (-16, 24), (-14, 28), (-10, 31), (-6, 34),
        (-2, 35), (3, 37), (9, 37), (11, 34), (15, 32), (20, 32),
        (25, 32), (30, 31), (32, 31), (34, 28), (36, 24), (38, 20),
        (40, 16), (43, 12), (48, 11), (51, 11), (51, 9), (47, 5),
        (44, 1), (41, -3), (40, -7), (39, -12), (36, -18), (33, -22),
        (32, -27), (28, -33), (22, -35), (18, -33), (16, -29),
        (14, -24), (13, -18), (12, -12), (13, -8), (12, -4), (9, 4),
        (7, 5), (3, 6), (-2, 5), (-8, 5), (-12, 8), (-16, 12), (-17, 15),
    ],
    [  # Europe
        (-10, 36), (-9, 38), (-9, 43), (-4, 44), (-2, 47), (-4, 48),
        (-1, 49), (1, 51), (3, 53), (6, 54), (8, 57), (10, 58),
        (8, 59), (6, 60), (5, 62), (8, 62), (12, 64), (14, 66),
        (18, 69), (22, 70), (26, 71), (30, 70), (32, 69), (35, 68),
        (40, 68), (44, 67), (42, 66), (38, 65), (34, 65), (32, 63),
        (30, 60), (28, 59), (26, 59), (24, 58), (21, 57), (20, 55),
        (18, 54), (14, 54), (11, 54), (8, 55), (7, 57), (5, 58),
        (4, 57), (1, 55), (0, 53), (-2, 51), (-4, 50), (-5, 48),
        (-2, 47), (-5, 44), (-8, 43), (-9, 38), (-10, 36),
    ],
    [  # Australia
        (113, -22), (114, -28), (115, -33), (118, -35), (122, -34),
        (126, -32), (129, -32), (132, -32), (135, -35), (137, -35),
        (139, -37), (141, -38), (144, -38), (147, -39), (150, -37),
        (153, -32), (153, -27), (151, -24), (148, -20), (146, -19),
        (143, -15), (142, -11), (140, -12), (137, -12), (135, -12),
        (132, -11), (130, -13), (127, -14), (124, -15), (121, -17),
        (118, -20), (115, -21), (113, -22),
    ],
    [  # New Zealand
        (167, -45), (169, -43), (172, -41), (174, -41), (176, -39),
        (178, -38), (176, -37), (174, -37), (173, -39), (171, -42),
        (168, -44), (167, -45),
    ],
    [  # United Kingdom
        (-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
        (1, 51), (-1, 50), (-5, 50),
    ],
    [  # Japan
        (130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
        (141, 38), (141, 41), (143, 42), (141, 44), (140, 42), (138, 38),
        (136, 36), (134, 34), (131, 32), (130, 31),
    ],
    [  # Madagascar
        (44, -16), (47, -15), (50, -16), (49, -20), (47, -24),
        (45, -25), (43, -22), (43, -18), (44, -16),
    ],
]

# Indonesia: small island dots, drawn as circles, not polygons.
INDONESIA = [(95, 5), (100, -2), (105, -5), (110, -7), (115, -8),
             (120, -9), (125, -8), (130, -3), (135, -4), (140, -8)]


def draw_map(draw, stories, x, y, w, h):
    """Dark-blue world map: cream land, red numbered pins 1-13, grey
    dots for the also-list places. Equirectangular projection."""
    draw.rectangle([x, y, x + w, y + h], fill=SEA)

    def proj(lon, lat):
        px = x + (lon + 180) / 360.0 * w
        py = y + (90 - lat) / 180.0 * h
        return px, py

    for poly in CONTINENTS:
        draw.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND)
    for lon, lat in INDONESIA:
        px, py = proj(lon, lat)
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=LAND)

    # Label inside the panel, bottom-left over empty ocean, cream on navy.
    face = typeface("map_label")
    spaced_text(draw, x + 10, y + h - 18, "WHERE IT HAPPENED", face,
                (246, 239, 221), gap=2)

    # Grey dots for also-list places first (pins draw over them).
    for item in stories["also"]:
        px, py = proj(item["lon"], item["lat"])
        draw.ellipse([px - 2, py - 2, px + 2, py + 2],
                     fill=(190, 200, 210))
    # Numbered red pins for heroes + mediums. Pins that would land on
    # top of each other (the US east coast holds five: New York,
    # Washington, Cincinnati, Florida, Los Santos; Europe four) are
    # nudged apart with a thin connector back to the true spot, so
    # every number stays readable.
    pin_face = typeface("pin")
    placed = []
    for item in stories["heroes"] + stories["mediums"]:
        px, py = proj(item["lon"], item["lat"])
        cx, cy = px, py
        for dx, dy in [(0, 0), (0, 13), (0, -13), (15, 0), (-15, 0),
                       (15, 13), (-15, -13), (15, -13), (-15, 13)]:
            tx, ty = px + dx, py + dy
            if all((tx - ox) ** 2 + (ty - oy) ** 2 >= 15 ** 2
                   for ox, oy in placed):
                cx, cy = tx, ty
                break
        placed.append((cx, cy))
        if (cx, cy) != (px, py):
            draw.line([(px, py), (cx, cy)], fill=WHITE, width=1)
        r = 7
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                     outline=WHITE, width=1)
        num = str(item["n"])
        tw = pin_face.getlength(num)
        draw.text((cx - tw / 2, cy - 6), num, font=pin_face, fill=WHITE)


# --- Page -------------------------------------------------------------------

def render_page(stories, out_path):
    """Draw the full front page and save it as a PNG."""
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(img)

    # ---- Masthead: eyebrow, giant serif date, red italic subline. ----
    total_stories = (len(stories["heroes"]) + len(stories["mediums"])
                     + len(stories["also"]))
    eyebrow = typeface("eyebrow")
    spaced_centred(draw, PAGE_W // 2, 12,
                   f"THE WORLD IN ONE DAY  ·  ONE PAGE  ·  {total_stories} STORIES",
                   eyebrow, GREY, gap=2)
    mast = typeface("masthead")
    date = stories["date"]
    draw.text(((PAGE_W - mast.getlength(date)) / 2, 30), date, font=mast,
              fill=INK)
    sub = typeface("subline")
    line = stories["subline"]
    draw.text(((PAGE_W - sub.getlength(line)) / 2, 90), line, font=sub,
              fill=RED)
    hline(draw, EDGE, PAGE_W - EDGE, 112, colour=INK, weight=2)

    # ---- Region bar: seven equal coloured segments, every one
    # labelled "LABEL N". (v2 scaled segments by count, so the last
    # three showed only bare numbers "1, 2, 2" with no label.)
    y = 120
    pen_x = EDGE
    bar_face = ImageFont.truetype(
        os.path.join(FONT_DIR, "InstrumentSans-Bold.ttf"), 11)
    seg_w = CONTENT_W // len(REGION_COLOURS)
    for name, count, colour in REGION_COLOURS:
        draw.rectangle([pen_x, y, pen_x + seg_w, y + 22], fill=colour)
        label = f"{name} {count}"
        tw = bar_face.getlength(label)
        draw.text((pen_x + (seg_w - tw) / 2, y + 5), label,
                  font=bar_face, fill=WHITE)
        pen_x += seg_w
    # Last segment absorbs rounding.
    if pen_x < PAGE_W - EDGE:
        draw.rectangle([pen_x, y, PAGE_W - EDGE, y + 22],
                       fill=REGION_COLOURS[-1][2])

    # ---- THE DAY IN NUMBERS: six big figures. ----
    y = 146
    spaced_text(draw, EDGE, y, "THE DAY IN NUMBERS", typeface("eyebrow"),
                RED, gap=3)
    y += 18
    col_w = CONTENT_W // 6
    val_face = typeface("num_value")
    lab_face = typeface("num_label")
    for i, num in enumerate(stories["numbers"]):
        cx = EDGE + i * col_w
        draw.text((cx, y), num["value"], font=val_face, fill=INK)
        lab = wrap_text(num["label"], lab_face, col_w - 12)
        ly = y + 36
        for ln in lab[:2]:
            draw.text((cx, ly), ln, font=lab_face, fill=GREY)
            ly += 12
        if i:
            draw.line([(cx - 7, y + 4), (cx - 7, y + 44)],
                      fill=HAIRLINE, width=1)
    y = y + 36 + 20

    # ---- FRIDAY BY THE HOURS: one centred timeline line. ----
    y += 2
    hline(draw, EDGE, PAGE_W - EDGE, y, colour=HAIRLINE)
    y += 4
    tl_face = typeface("timeline")
    parts = [f"{t['time']} {t['text'].upper()}" for t in stories["timeline"]]
    tl = "  ·  ".join(parts)
    draw.text(((PAGE_W - tl_face.getlength(tl)) / 2, y), tl,
              font=tl_face, fill=INK)
    y += 16

    # ---- Three hero cards, each with its own illustration. ----
    y += 6
    hero_w = (CONTENT_W - 2 * 14) // 3  # 312
    hero_h = 186
    head_face = typeface("hero_head")
    deck_face = typeface("hero_deck")
    src_face = typeface("hero_src")
    for i, hero in enumerate(stories["heroes"]):
        hx = EDGE + i * (hero_w + 14)
        ART[hero["art"]](draw, hx, y, hero_w, 86)
        # Number badge on the art, top-left.
        r = 11
        draw.ellipse([hx + 4, y + 4, hx + 4 + 2 * r, y + 4 + 2 * r],
                     fill=RED, outline=WHITE, width=1)
        num = str(hero["n"])
        nf = typeface("pin")
        draw.text((hx + 4 + r - nf.getlength(num) / 2, y + 9), num,
                  font=nf, fill=WHITE)
        pen = y + 92
        for ln in wrap_text(hero["headline"], head_face, hero_w)[:2]:
            draw.text((hx, pen), ln, font=head_face, fill=INK)
            pen += 23
        pen += 2
        for ln in wrap_text(hero["deck"], deck_face, hero_w)[:2]:
            draw.text((hx, pen), ln, font=deck_face, fill=GREY)
            pen += 15
        src = f"{hero['place']} — " + " · ".join(hero["sources"])
        draw.text((hx, y + hero_h - 14), src, font=src_face, fill=RED)
    y += hero_h

    # ---- Ten medium cards: small icon left, text right. ----
    y = section_head(draw, EDGE, y + 8, "MORE OF THE DAY")
    med_w = (CONTENT_W - 4 * 11) // 5  # 184
    med_h = 96
    med_row_gap = 8
    mh_face = typeface("med_head")
    md_face = typeface("med_deck")
    ms_face = typeface("med_src")
    for row in range(2):
        for col in range(5):
            item = stories["mediums"][row * 5 + col]
            mx = EDGE + col * (med_w + 11)
            my = y + row * (med_h + med_row_gap)
            ART[item["art"]](draw, mx, my, 48, 48)
            # Number badge on the icon.
            r = 8
            draw.ellipse([mx - 2, my - 2, mx - 2 + 2 * r, my - 2 + 2 * r],
                         fill=RED, outline=WHITE, width=1)
            num = str(item["n"])
            nf = typeface("pin")
            draw.text((mx - 2 + r - nf.getlength(num) / 2, my + 2), num,
                      font=nf, fill=WHITE)
            tx = mx + 56
            tw = med_w - 56
            pen = my
            for ln in wrap_text(item["headline"], mh_face, tw)[:3]:
                draw.text((tx, pen), ln, font=mh_face, fill=INK)
                pen += 16
            pen = my + 52
            for ln in wrap_text(item["deck"], md_face, med_w)[:2]:
                draw.text((mx, pen), ln, font=md_face, fill=GREY)
                pen += 13
            src = f"{item['place']} — " + " · ".join(item["sources"])
            draw.text((mx, my + med_h - 12), src, font=ms_face, fill=RED)
    y += 2 * med_h + med_row_gap

    # ---- World map. ----
    y += 6
    map_h = 88
    draw_map(draw, stories, EDGE, y, CONTENT_W, map_h)
    y += map_h

    # ---- ALSO TODAY: numbered 14-40 in three columns. ----
    y = section_head(draw, EDGE, y + 6, "ALSO TODAY")
    also_face = typeface("also")
    num_face = typeface("also_num")
    col_w = (CONTENT_W - 2 * 14) // 3  # 312
    row_h = 13
    cols = [[], [], []]
    for i, item in enumerate(stories["also"]):
        cols[i // 9].append(item)
    for ci, items in enumerate(cols):
        cx = EDGE + ci * (col_w + 14)
        for ri, item in enumerate(items):
            iy = y + ri * row_h
            ntxt = f"{item['n']}."
            draw.text((cx, iy), ntxt, font=num_face, fill=RED)
            txt = item["headline"]
            avail = col_w - num_face.getlength(ntxt) - 6
            while also_face.getlength(txt) > avail and len(txt) > 10:
                txt = txt[:-5].rstrip() + "…"
            draw.text((cx + num_face.getlength(ntxt) + 6, iy), txt,
                      font=also_face, fill=INK)
    y += 9 * row_h

    # ---- DATE CHECK: what did NOT happen on Friday. ----
    y += 4
    box_y = y
    box_h = 74
    check_face = typeface("check")
    draw.rectangle([EDGE, box_y, PAGE_W - EDGE, box_y + box_h], fill=PANEL)
    draw.rectangle([EDGE, box_y, PAGE_W - EDGE, box_y + box_h],
                   outline=HAIRLINE, width=1)
    spaced_text(draw, EDGE + 10, box_y + 7,
                "DATE CHECK — THESE HAPPENED EARLIER, NOT ON FRIDAY",
                typeface("check_head"), RED, gap=2)
    ccol_w = (CONTENT_W - 20 - 2 * 14) // 3
    for ci in range(3):
        cx = EDGE + 10 + ci * (ccol_w + 14)
        for ri in range(3):
            idx = ci * 3 + ri
            if idx >= len(stories["date_check"]):
                continue
            item = stories["date_check"][idx]
            iy = box_y + 24 + ri * 11
            # Red X drawn with two strokes (no glyph dependency).
            draw.line([(cx, iy + 2), (cx + 7, iy + 9)], fill=RED, width=2)
            draw.line([(cx + 7, iy + 2), (cx, iy + 9)], fill=RED, width=2)
            txt = f"{item['text']} — {item['when']}"
            while check_face.getlength(txt) > ccol_w - 10 and len(txt) > 10:
                txt = txt[:-5].rstrip() + "…"
            draw.text((cx + 10, iy), txt, font=check_face, fill=INK)
    not_yet = stories["not_yet"]
    draw.text((EDGE + 10, box_y + 24 + 3 * 11 + 2), not_yet,
              font=check_face, fill=RED)
    y = box_y + box_h

    # ---- Footer: the date promise + sources. ----
    y += 6
    hline(draw, EDGE, PAGE_W - EDGE, y, colour=INK, weight=1)
    foot = typeface("foot")
    total = (len(stories["heroes"]) + len(stories["mediums"])
             + len(stories["also"]))
    line1 = f"{total} STORIES  ·  " + stories["footer"]
    for ln in wrap_text(line1, foot, CONTENT_W):
        draw.text(((PAGE_W - foot.getlength(ln)) / 2, y + 5), ln,
                  font=foot, fill=GREY)
        y += 13
    line2 = stories["footer_sources"]
    draw.text(((PAGE_W - foot.getlength(line2)) / 2, y + 5), line2,
              font=foot, fill=GREY)
    y += 13 + 5

    if y > PAGE_H - 4:
        print(f"WARNING: content overflows canvas (final-y={y}, "
              f"canvas {PAGE_H})", file=sys.stderr)
    img.save(out_path, "PNG", optimize=True, compress_level=9)
    print(f"saved {out_path}  {os.path.getsize(out_path)} bytes  "
          f"final-y={y} (canvas {PAGE_H})")
    return y


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        stories = json.load(fh)
    render_page(stories, os.path.join(HERE, "entry.png"))


if __name__ == "__main__":
    main()
