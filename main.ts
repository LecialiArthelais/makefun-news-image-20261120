// The World in One Day — Friday 20 November 2026.
// A make.fun news-image entry (program/v1, Node 22, standard library only).
// The entry is a single finished front-page image, entry.png beside this
// file — a 1024x1024 PNG drawn by build_frontpage.py from stories.json.
// The program copies it, byte for byte, to the output path the grader
// reads. The page is a newspaper front page: masthead, red date band,
// one dominant hero story with a flat drawn graphic, then top stories,
// four region columns and an "also today" strip — see DESIGN.md.
//
// Deterministic by construction: no network, no clock, no randomness, no
// image processing at all — the same input file always yields the same
// output bytes, so the two grading runs agree exactly.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const sourcePath = fileURLToPath(new URL('./entry.png', import.meta.url));
const targetPath = join(outDir, 'entry.png');

mkdirSync(outDir, { recursive: true });
copyFileSync(sourcePath, targetPath);

// Guard the copy: the grader reads exactly these bytes, so a short or
// empty write must fail loudly here instead of shipping a broken image.
const copied = statSync(targetPath).size;
const expected = statSync(sourcePath).size;
if (copied !== expected) {
  throw new Error(`entry.png copy is incomplete (${copied} of ${expected} bytes)`);
}
