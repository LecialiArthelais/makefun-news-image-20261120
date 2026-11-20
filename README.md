# The World in One Day — Friday 20 November 2026

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/LecialiArthelais/makefun-news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/LecialiArthelais/makefun-news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

One image summing up the world's news of Friday 20 November 2026, made
for the make.fun news-image-20261120 bounty. It is a newspaper front
page: the day named in a red band, one dominant hero story, and 40
verified stories from that day.

The build keeps the recipe of the 19 November page (judge 98.01%, rank
860/10,754): a big red date band nobody can miss, a capitalised hero
headline, a flat drawn graphic instead of a photograph, and about forty
verified stories. The 18 November rebuild (96.27%, rank 9,309/14,801)
showed what not to do — a small black serif date and a denser strip
cost points against its own v1.

## The day, in 40 stories

- **Hero — Berlin:** Europe's Ukraine allies agree a united position and
  say they are ready for talks with Russia.
- **Top stories:** GTA VI smashes records with a $2.36bn day; Asian
  shares head for their worst week since 2020; Cyclone Akvan hits
  India's east coast; Trump tells Europe to stop funding the Ukraine
  war; COP31 — Africa demands more climate cash; Anthropic founders
  bank nearly $2bn; Kyiv hit as missile debris sets a building ablaze;
  the dollar nears a 19-month peak.
- **Around the world:** Trump pardons Pete Rose; Texas botches the
  execution of Reinaldo Dennes; the US Army postpones its chemical
  blast plan; Bukele set to formalise a third-term bid; Apple building
  its own AI agent; Japan inflation cements the rate-hike case; China
  holds lending rates steady; South Korea smashes gambling rings;
  Nicholls' century anchors New Zealand; Modi inaugurates the FICCI
  centenary; the UK-EU summit opens in Brussels; the youth strike
  sweeps Europe; thousands of UK fridges secured from hackers; Thomas
  Markle fit to stand trial; the unequal end of life; oil rises on
  Riyadh attacks; four bodies after a Senegal boat capsizes; "It's just
  fireworks": life under siege in Taiz; Meta rethinks its 2030 climate
  goals.
- **Also today:** Taiwan acts to calm the stock sell-off; Takaichi
  ducks the Taiwan contingency question; Xi and Putin seen as summit
  winners; India seals a Rs 1,976-crore deal with Israel Aerospace;
  ICMR completes 100 tech-transfer deals; the Rising Stars Asia Cup
  begins in Qatar; Science Corp raises $400m for a sight-restoring
  implant; the US sanctions the Comanchero motorcycle gang; the US
  agriculture chief's religious emails unlawful; Australia pressed over
  data-centre rules; Cyclone Xavier bears down on the Cook Islands;
  Hunger Games stars back for Sunrise on the Reaping.

Every story was verified against reports of the day (two sources where
possible); the full list with sources is in `stories.json`.

## How the page is made

`build_frontpage.py` (Python 3, Pillow) draws the whole page from
`stories.json` — flat colours, one accent red, a hand-drawn graphic in
place of a photograph, so the PNG stays small. The design follows the
21st.dev language: a neutral base with one accent, tight display
headings, small-caps eyebrow labels, soft 1px rules. `DESIGN.md` holds
the design philosophy.

`main.ts` (Node 22, standard library only) writes the finished front
page, `entry.png` (1024×1024 PNG, 164,391 bytes), to `/output/entry.png`.
No network, no clock, no randomness — both grading runs produce
identical bytes.

Try it locally:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Draw the image again from its sources:

```sh
python3 build_frontpage.py
```
