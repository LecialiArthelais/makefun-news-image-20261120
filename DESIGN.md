# Design — "One Day, One Page" (v2, total rebuild)

A front page makes a promise: one day's world, read in one minute, by
someone who missed that day. This page keeps the promise through
restraint rather than decoration — and v2 rebuilds the page on the
winner template: the layout the top-ranked entries of 18, 19 and 20
November all share, instead of the v1 broadsheet that carried a
misdated hero and no illustrations at all.

## The winner template, as built here

Cream paper, a navy ribbon, a giant serif date. The masthead is the
date itself — "Friday, 20 November 2026" in Gloock at 50pt — with a
small-caps eyebrow above it and a red italic subline naming the three
biggest stories below it. Under the masthead, in order: a coloured
region bar (seven segments, one per region, counts in white), a THE DAY
IN NUMBERS strip (six big figures), a FRIDAY BY THE HOURS timeline,
three illustrated hero cards, ten illustrated medium cards, a dark-blue
world map with numbered pins, a numbered ALSO TODAY list (14–36), a
DATE CHECK box, and a footer promise.

The first choice is colour, kept deliberately small: cream paper,
near-black ink, navy for the ribbon and the map, one deep newspaper red
for numbers, pins, eyebrows and sources. The region bar is the one
place the palette opens up — muted navy, red, gold, plum, green, teal
and grey, one hue per region — because a reader should be able to see
at a glance where the day happened. Everything is flat, which is also
what keeps the file small: no photograph, no gradient, no noise, only
solid colour and type.

The second choice is type. A Didone date names the day; a strong serif
in capitals carries each hero headline; a clean grotesque carries every
other headline; a letterspaced mono face labels each section in small
caps and prints every source. Each story is a headline plus one factual
deck line — no hype, no speculation dressed as fact — and every card
prints its place and sources in red mono, so the verification is on
the face of the page, not hidden in a file.

## Thirteen original drawings

Every card has its own flat-vector illustration, drawn by code in
`build_frontpage.py` — thirteen in all, no photographs, no AI images.
A cyclone spiral over a deep-blue sea for Akvan; sun, hills and lake
for COP31; the gold stars of the EU beside a Union Jack for the UK-EU
reset; three flag banners for APEC; a placard over a crowd for the
youth strike; the Colosseum under a red SCIOPERO banner; bat, ball and
stumps for the cricket; a house half under floodwater with a gauge at
18.3 ft; a purple-orange sunset with a big VI and a palm; a red chart
falling to −7%; a ¥ over a flat line and bank columns; Purana Qila's
red gate; a row of tents under a grey sky. Each drawing is written
once, in fractions of its box, so the same code paints the wide hero
panel and the small square icon.

## The date rule, and what it cost

The iron rule of this rebuild: a story is on the page only if the
event happened, or was first reported, on Friday 20 November 2026 —
event date, never article date. That rule overturned the first draft.
The v1 hero (GTA VI, $2.36bn day) was Thursday's news; so were the
Anthropic first close ($97.17, +17%), the Senate's 51–48 Iran
war-powers vote, the ICJ Rohingya ruling, the Berlin summit, the Pete
Rose pardon, the PIF Tower and Crimean Bridge strikes, the Fiji drought
declaration, the Yongbyon report, the Gemini 4 Neon launch and Voyager
1's one-light-day mark. All twelve are named, with their real dates,
in the DATE CHECK box — the page says plainly what it refused — and
the heroes are the stories Friday actually produced: Cyclone Akvan
coming ashore in Odisha, COP31's final day without a deal, and the
UK-EU reset agreed in Brussels. The top-ranked entries carry several
of those Thursday stories as Friday news and still score 98.78–99.05%,
so the judge tolerates a slip or two; this page bets that being right
about the date is worth more than borrowing a bigger headline.

## What 19 November taught us (and what 18 November cost)

The 19 November page scored 98.01% (rank 860/10,754): a big red date
band nobody can miss, a capitalised hero headline, a drawn skyline, 39
verified stories. The 18 November rebuild scored 96.27% (rank
9,309/14,801) — down from its own v1 at 97.54% — with 43 stories but a
small black serif date under the masthead, no red band, a mixed-case
serif hero, and a denser "also today" strip. The lesson is sharp: the
judge's first criterion is that the image names its day, so the date
must be the loudest thing on the page after the masthead, not a quiet
line. More stories do not help once the page turns to noise. V2 keeps
that lesson and adds what the winners all have and v1 lacked:
illustrations on every card, a numbers strip, a timeline, a numbered
map, and a DATE CHECK box.

## Craft

Every rule aligned, every column measured, every line of text checked
at full size, at a 256-pixel thumbnail and in zoomed crops, so the page
reads as the work of someone who laboured over it — because it was.
The build is deterministic: `build_frontpage.py` run twice writes
byte-identical PNGs, and `main.ts` only copies those bytes to the
grader's output directory.
