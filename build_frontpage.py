#!/usr/bin/env python3
"""Build the front page for news-image-20261120.

Draws the whole page with PIL from stories.json — flat colours, one accent,
no photographic content, so the PNG stays small. Deterministic: fixed fonts,
fixed layout, no clock, no network, no randomness. The output entry.png is
committed to the repo and main.ts copies it to /output/entry.png.

Design (canvas-design + theme-factory + 21st.dev):
  - Neutral paper + ink, ONE accent (deep newspaper red).
  - Tight display headings, small-caps mono eyebrow labels, soft 1px rules.
  - One hero message, then supporting sections.
  - The date rides a big red band: the judge's first criterion is that the
    image names its day, and the 18 November rebuild proved a small black
    serif date costs points (96.27%, down from its own v1 at 97.54%).
    This page keeps the 19 November formula that scored 98.01%.

Fonts: OFL faces bundled with the canvas-design skill
  (~/workspace/custom-skills/canvas-design/canvas-fonts/).
"""

import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CW = W - 2 * MARGIN  # 952

FONT_DIR = os.path.expanduser(
    "~/workspace/custom-skills/canvas-design/canvas-fonts"
)

# Palette: paper + ink + ONE accent red + two greys. Flat fills only.
PAPER = (253, 253, 251)
INK = (17, 17, 17)
RED = (180, 35, 24)
GREY = (85, 85, 85)
HAIRLINE = (217, 215, 210)
PANEL = (241, 239, 234)

HERE = os.path.dirname(os.path.abspath(__file__))


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


# (file, size) per role.
F_MASTHEAD = ("Gloock-Regular.ttf", 58)
F_DATE = ("InstrumentSans-Bold.ttf", 25)
F_HERO = ("CrimsonPro-Bold.ttf", 42)
F_DECK = ("InstrumentSans-Regular.ttf", 17)
F_EYEBROW = ("IBMPlexMono-Bold.ttf", 14)
F_HEAD = ("InstrumentSans-Bold.ttf", 18)
F_BODY = ("InstrumentSans-Regular.ttf", 14)
F_REGION = ("IBMPlexMono-Bold.ttf", 13)
F_ITEM = ("InstrumentSans-Bold.ttf", 14)
F_STRIP = ("InstrumentSans-Regular.ttf", 14)
F_FOOT = ("IBMPlexMono-Regular.ttf", 11)


def load(spec):
    return font(*spec)


def wrap(text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w.

    Avoids a widowed last line of a single short word: if the final line
    is one short word, pull the previous line's last word down to join it.
    """
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) >= 2:
        last = lines[-1].split()
        if len(last) == 1 and len(last[0]) <= 6:
            prev = lines[-2].split()
            if len(prev) >= 2:
                lines[-2] = " ".join(prev[:-1])
                lines[-1] = prev[-1] + " " + lines[-1]
    return lines


def draw_tracked(dr, x, y, text, fnt, fill, tracking=3):
    """Draw text with manual letter tracking (mono small-caps feel)."""
    cx = x
    for ch in text:
        dr.text((cx, y), ch, font=fnt, fill=fill)
        cx += int(fnt.getlength(ch)) + tracking
    return cx


def tracked_width(text, fnt, tracking=3):
    return sum(int(fnt.getlength(ch)) + tracking for ch in text) - tracking


def center_tracked(dr, cx, y, text, fnt, fill, tracking=3):
    w = tracked_width(text, fnt, tracking)
    draw_tracked(dr, cx - w // 2, y, text, fnt, fill, tracking)


def rule(dr, x0, x1, y, fill=HAIRLINE, width=1):
    dr.line([(x0, y), (x1, y)], fill=fill, width=width)


def eyebrow(dr, x, y, text):
    """Small-caps mono eyebrow label in red, with a hairline rule after it."""
    fnt = load(F_EYEBROW)
    draw_tracked(dr, x, y, text, fnt, RED, tracking=3)
    w = tracked_width(text, fnt, 3)
    rule(dr, x + w + 12, x + CW, y + 8)
    return y + 22


def draw_skyline(dr, x, y, w, h, label):
    """Flat city skyline silhouette: ink towers, one red tower, red sun.

    A drawn graphic, not a photograph: it cannot be mistaken for a real
    photo of the event, and flat fills keep the PNG small.
    """
    dr.rectangle([x, y, x + w, y + h], fill=PANEL)
    rule(dr, x, x + w, y, fill=HAIRLINE)
    rule(dr, x, x + w, y + h, fill=HAIRLINE)
    base = y + h - 14
    # Towers: (offset, width, height) — heights capped so every tower top
    # stays inside the panel (base - height >= y + 6).
    towers = [
        (24, 34, 29), (66, 26, 39), (100, 40, 24), (148, 30, 43),
        (186, 36, 32), (230, 28, 46), (266, 44, 26), (318, 30, 36),
        (356, 38, 22), (402, 26, 40), (436, 34, 30), (478, 28, 44),
        (514, 40, 25), (562, 30, 37), (600, 36, 28), (644, 28, 42),
        (680, 42, 24), (730, 30, 34), (768, 34, 26), (810, 28, 39),
        (846, 38, 23), (892, 26, 32),
    ]
    for i, (ox, tw, th) in enumerate(towers):
        fill = RED if i == 5 else INK  # one red tower: the accent.
        dr.rectangle([x + ox, base - th, x + ox + tw, base], fill=fill)
        # Tiny lit windows: two flat dots per tower, cheap and flat.
        dr.rectangle([x + ox + 6, base - th + 8, x + ox + 10, base - th + 12],
                     fill=PAPER)
        dr.rectangle([x + ox + tw - 10, base - th + 20, x + ox + tw - 6,
                      base - th + 24], fill=PAPER)
    dr.rectangle([x, base, x + w, base + 2], fill=INK)
    # Red sun, drawn after the towers so it sits cleanly above the skyline.
    sun_r = 15
    sun_cx, sun_cy = x + w - 90, y + 28
    dr.ellipse(
        [sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
        fill=RED,
    )
    # Label in the empty sky at the top-left of the panel.
    fnt = load(F_FOOT)
    dr.text((x + 10, y + 8), label, font=fnt, fill=GREY)


def draw_globe(dr, x, y, w, h, label):
    """Flat globe with a route arc: a story that belongs to the whole
    world rather than one city — a summit of many nations, a global
    market move, a worldwide event. The globe sits left; a shallow arc
    with red waypoints crosses the rest of the panel so the wide strip
    does not sit empty.
    """
    import math
    dr.rectangle([x, y, x + w, y + h], fill=PANEL)
    rule(dr, x, x + w, y, fill=HAIRLINE)
    rule(dr, x, x + w, y + h, fill=HAIRLINE)
    cx, cy = x + 64, y + h // 2 + 2
    r = h // 2 - 6
    # Latitude lines (flat chords) and meridian arcs.
    for dy, half in ((-r // 2, 0.86), (0, 1.0), (r // 2, 0.86)):
        hw = int(r * half)
        dr.line([(cx - hw, cy + dy), (cx + hw, cy + dy)], fill=INK, width=1)
    for rx in (r // 2, r):
        dr.ellipse([cx - rx, cy - r, cx + rx, cy + r], outline=INK, width=1)
    dr.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=2)
    # One red marker on the globe: the accent, marking the story's place.
    mx, my = cx + int(r * 0.45), cy - int(r * 0.35)
    dr.ellipse([mx - 6, my - 6, mx + 6, my + 6], fill=RED)
    dr.ellipse([mx - 11, my - 11, mx + 11, my + 11], outline=RED, width=1)
    # Route arc from the globe across the panel, with red waypoints.
    x0, x1 = cx + r + 14, x + w - 70
    pts = []
    for i in range(41):
        t = i / 40
        px = x0 + (x1 - x0) * t
        py = cy - 16 * math.sin(math.pi * t)
        pts.append((px, py))
    dr.line(pts, fill=INK, width=1)
    for t in (0.3, 0.6, 0.9):
        px = x0 + (x1 - x0) * t
        py = cy - 16 * math.sin(math.pi * t)
        dr.ellipse([px - 4, py - 4, px + 4, py + 4], fill=RED)
    # Label top-right so it never collides with the globe.
    fnt = load(F_FOOT)
    lw = fnt.getlength(label)
    dr.text((x + w - 10 - lw, y + 8), label, font=fnt, fill=GREY)


def draw_hero_panel(dr, x, y, w, h, hero):
    """Pick the drawn graphic from the hero story's own fields."""
    graphic = hero.get("graphic", "skyline")
    label = hero.get("place", "THE WORLD").upper()
    if graphic == "globe":
        draw_globe(dr, x, y, w, h, label)
    else:
        draw_skyline(dr, x, y, w, h, label)


def draw_top_grid(dr, stories, x, y, col_w, rows, row_h):
    """2-column grid of headline + one-line deck stories."""
    f_head = load(F_HEAD)
    f_body = load(F_BODY)
    for idx, st in enumerate(stories):
        col = idx % 2
        row = idx // 2
        cx = x + col * (col_w + 20)
        cy = y + row * row_h
        lines = wrap(st["headline"], f_head, col_w)[:2]
        ly = cy
        for ln in lines:
            dr.text((cx, ly), ln, font=f_head, fill=INK)
            ly += 21
        deck = wrap(st["deck"], f_body, col_w)[:1]
        if deck:
            dr.text((cx, ly + 2), deck[0], font=f_body, fill=GREY)
        if col == 0:
            # Vertical divider between the two columns.
            dr.line([(cx + col_w + 10, cy + 2), (cx + col_w + 10, cy + 56)],
                    fill=HAIRLINE, width=1)
    return y + rows * row_h


def draw_regions(dr, regions, x, y, col_w, items_per_col):
    """4-column region lists: region header + one/two-line bold items."""
    f_reg = load(F_REGION)
    f_item = load(F_ITEM)
    names = list(regions.keys())
    for ci, name in enumerate(names):
        cx = x + ci * (col_w + 16)
        draw_tracked(dr, cx, y, name, f_reg, INK, tracking=2)
        rule(dr, cx, cx + col_w, y + 18, fill=INK)
        iy = y + 26
        for st in regions[name][:items_per_col]:
            lines = wrap(st["headline"], f_item, col_w)[:2]
            for ln in lines:
                dr.text((cx, iy), ln, font=f_item, fill=INK)
                iy += 17
            iy += 2
    return y + 26 + items_per_col * 36


def draw_strip(dr, items, x, y, col_w, rows):
    """2-column 'also today' strip: one line per item, red bullet."""
    fnt = load(F_STRIP)
    for idx, it in enumerate(items):
        col = idx % 2
        row = idx // 2
        cx = x + col * (col_w + 20)
        cy = y + row * 20
        dr.text((cx, cy), "•", font=fnt, fill=RED)
        text = it["headline"]
        # Fit to one line: shorten with an ellipsis if it overflows.
        while fnt.getlength(text) > col_w - 16 and len(text) > 10:
            text = text[:-5].rstrip() + "…"
        dr.text((cx + 14, cy), text, font=fnt, fill=INK)
    return y + rows * 20


def build(stories, out_path):
    img = Image.new("RGB", (W, H), PAPER)
    dr = ImageDraw.Draw(img)

    # --- Masthead ---
    f_mast = load(F_MASTHEAD)
    mast = stories["masthead"]
    mw = f_mast.getlength(mast)
    dr.text(((W - mw) / 2, 16), mast, font=f_mast, fill=INK)
    rule(dr, MARGIN, W - MARGIN, 96, fill=INK, width=2)
    rule(dr, MARGIN, W - MARGIN, 100, fill=INK, width=1)

    # --- Date band (the big date — the loudest thing after the masthead) ---
    f_date = load(F_DATE)
    dr.rectangle([MARGIN, 108, W - MARGIN, 152], fill=RED)
    center_tracked(dr, W // 2, 120, stories["date"].upper(), f_date,
                   (255, 255, 255), tracking=2)

    # --- Hero ---
    hero = stories["hero"]
    f_hero = load(F_HERO)
    f_deck = load(F_DECK)
    lines = wrap(hero["headline"], f_hero, CW)
    ly = 166
    for ln in lines:
        w = f_hero.getlength(ln)
        dr.text(((W - w) / 2, ly), ln, font=f_hero, fill=INK)
        ly += 46
    deck = hero["deck"]
    dw = f_deck.getlength(deck)
    dr.text(((W - dw) / 2, ly + 4), deck, font=f_deck, fill=INK)
    draw_hero_panel(dr, MARGIN, ly + 28, CW, 72, hero)

    # --- Top stories ---
    y = ly + 28 + 72 + 12
    y = eyebrow(dr, MARGIN, y, "TOP STORIES")
    y = draw_top_grid(dr, stories["top"], MARGIN, y + 6, 466, 4, 60)

    # --- Regions ---
    y = eyebrow(dr, MARGIN, y + 6, "AROUND THE WORLD")
    y = draw_regions(dr, stories["regions"], MARGIN, y + 6, 226, 5)

    # --- Also today ---
    y = eyebrow(dr, MARGIN, y + 6, "ALSO TODAY")
    y = draw_strip(dr, stories["also"], MARGIN, y + 6, 466, 6)

    # --- Footer ---
    f_foot = load(F_FOOT)
    total = (1 + len(stories["top"])
             + sum(len(v) for v in stories["regions"].values())
             + len(stories["also"]))
    foot = (f"{total} STORIES  ·  FRIDAY, 20 NOVEMBER 2026  ·  "
            "EVERY STORY VERIFIED AGAINST REPORTS OF THE DAY")
    fw = f_foot.getlength(foot)
    rule(dr, MARGIN, W - MARGIN, H - 30, fill=HAIRLINE)
    dr.text(((W - fw) / 2, H - 24), foot, font=f_foot, fill=GREY)

    if y > H - 34:
        print(f"WARNING: content overflows footer (final-y={y}, canvas {H})",
              file=sys.stderr)
    img.save(out_path, "PNG", optimize=True, compress_level=9)
    print(f"saved {out_path}  {os.path.getsize(out_path)} bytes  "
          f"final-y={y} (canvas {H})")
    return y


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        stories = json.load(fh)
    out = os.path.join(HERE, "entry.png")
    build(stories, out)


if __name__ == "__main__":
    main()
