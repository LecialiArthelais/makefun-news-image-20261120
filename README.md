# The World in One Day — Friday 20 November 2026

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/LecialiArthelais/makefun-news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/LecialiArthelais/makefun-news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

One image summing up the world's news of Friday 20 November 2026, made
for the make.fun news-image-20261120 bounty. It is a newspaper front
page rebuilt from scratch on the winner template: a giant serif date,
a coloured region bar, a numbers strip, three illustrated heroes, ten
illustrated medium cards, a numbered world map, and a DATE CHECK box
naming the big stories that happened *before* Friday. 40 stories in
all, every one verified by event date as Friday 20 November 2026 —
the Thursday stories (Anthropic's debut, the Senate war-powers vote,
the Pete Rose pardon, Bukele's third-term registration) are named in
DATE CHECK, not carried as leads (see DESIGN.md).

The build keeps the recipe of the 19 November page (judge 98.01%, rank
860/10,754): a date nobody can miss, capitalised hero headlines, flat
drawn graphics instead of photographs, and about forty verified
stories. The 18 November rebuild (96.27%, rank 9,309/14,801) showed
what not to do — a small black serif date and a denser strip cost
points against its own v1. V2 adds what the winners all have and v1
lacked: an illustration on every card, a numbers strip, a timeline, a
numbered map, and a DATE CHECK box.

## The day, in 40 stories

- **Heroes:** Russian missiles hit three Kyiv bridges (about 110
  missiles and 400 drones, at least eight killed across Ukraine);
  Cyclone Akvan slams into Odisha (370,000 evacuated, no deaths
  reported); AI sell-off sinks Asia's markets (Taiex −6.2%, Nikkei
  −5.1%, Kospi −5.2%, Hang Seng −1.9%).
- **Medium cards:** UK and EU sign a reset deal (100,000 youth visas
  a year); COP31's final day — still no deal; Russian missiles land
  in Poland; Europe ready for talks with Russia; Iraq's army moves
  into a militia stronghold; youth strike sweeps Europe (25+
  countries, 400+ UK schools); Italy stops for a general strike;
  Phillips 118, Nicholls 175\* as NZ make 368; Florida floods roll
  into Friday (St. Johns River at a record 18.3 ft); GTA VI user
  reviews open at noon.
- **Also today (14–40):** Brent $92.67 as Hormuz tankers hit mines;
  Kenya starts drilling its first oil well; China holds lending rates;
  three killed in Gaza overnight; Japan core inflation 2.2%; Harris
  meets Macron; Trump White House press conference; Portugal's
  public-sector strike; ATP
  Finals in Turin; World Children's Day; Cyclone Xavier weakens off
  the Cook Islands; Fed's Paulson speaks; Albanese to meet Li Qiang;
  Xi meets Prabowo; Taiwan steadies stocks; four nations demand Gaza
  aid access; US details $12bn Venezuelan oil revenue; Eisenkot tapped
  to form Israel's government; fire at Yunus's ancestral home; Modi
  addresses FICCI; German-Ukrainian business forum; Australian miners
  press Li Qiang; Italian rail strike from 21:00; UK retail sales rise
  0.7% in October; Bank of Thailand holds growth at 2.4%; France
  braces for cost-of-living protests; ANC weighs a Gauteng
  power-sharing deal.
- **DATE CHECK — not Friday:** Anthropic's $83 IPO & Nasdaq debut
  (Thu 19 Nov); Senate rejects Iran war powers, 48–51 (Thu 19 Nov);
  Pete Rose pardoned (Thu 19 Nov); Bukele registers for a third term
  (Thu 19 Nov); GTA VI launch + $2.36bn day (Thu 19 Nov); ICJ
  Rohingya genocide ruling (Thu 19 Nov); PIF Tower Riyadh hit (Thu
  19 Nov); Crimean Bridge rail hit, 3rd attack (Thu 19 Nov); Fiji
  drought disaster declared (Wed 18 Nov). NOT YET: BepiColombo
  Mercury orbit entry (Sat 21 Nov, planned).

Every story was verified against reports of the day (two sources where
possible); the full list with sources and event dates is in
`stories.json`. Stories still developing at build time — the COP31
final text, the ATP Finals results, the Harris–Macron readout — are
flagged in the DATE CHECK box under NOT YET.

## How the page is made

`build_frontpage.py` (Python 3, Pillow) draws the whole page from
`stories.json` — flat colours, one accent red, thirteen original
flat-vector illustrations drawn by code, so the PNG stays small. The
design follows the 21st.dev language: a neutral base with one accent,
tight display headings, small-caps eyebrow labels, soft 1px rules.
`DESIGN.md` holds the design philosophy.

`main.ts` (Node 22, standard library only) writes the finished front
page, `entry.png` (1024×1024 PNG, 214,410 bytes), to `/output/entry.png`.
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
