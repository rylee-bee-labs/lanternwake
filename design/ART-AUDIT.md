# ART AUDIT — provenance, legibility, source parity (issue #9)

**Decision in force (2026-10-16, "Option a"):** this audit only
**reports** the near-identical `hush-wisp` / `drowned-chorister` pair
(LIMITATIONS L20). It makes **no** art change, and promotes nothing.
Every "recommended replacement" below is a note for a future decision,
not work done here.

Method: a read-only tool, `tools/art_audit.py`, checks what is on disk
against `art/tools/build_art.py` (the single provenance source) and
reports which sprites render alike. Run it yourself:

```sh
python3 tools/art_audit.py --sheet art/out/legibility-contact-sheet.png
```

## Provenance and licence — verified

All third-party art is **Kenney.nl, CC0 1.0** (Creative Commons Zero).
Four licence files ship in `assets/kenney/`; `build_art.py` copies them
from the source library at build time, so they are regenerated, not
hand-written. No other licence is assumed and no third-party source is
used uncredited.

| Pack | CC0 licence on file | Used for | Tile sources | Sprite sources |
|---|---|---|---|---|
| Tiny Dungeon | `LICENSE-tiny-dungeon.txt` | people, monsters, items, dungeon props and stone | 43 | 60 |
| Tiny Farm | `LICENSE-tiny-farm.txt` | fields, trees, props | 12 | 2 |
| Tiny Ski | `LICENSE-tiny-ski.txt` | snow, ice, pines, cabin walls | 11 | 0 |
| Tiny Town | `LICENSE-tiny-town.txt` | sea, grass, cobbles | 7 | 0 |

Counts are per `build_art.TILES` / `PEOPLE` / `MONSTERS` / `ITEMS`
(73 staged tiles, 62 sprites). Every generated file has exactly one
table entry and every table entry one file (verified below).

## Generation and drift

- **Clean rebuild is deterministic.** `python3 tools/build_pack.py`
  followed by `git status --porcelain` prints nothing — no drift in
  `world.json`, `acts/`, `voices/` or `library/`.
- **Authored-source parity holds.** `diff -rq content/library library`
  and `diff -rq content/voices voices` are identical; `content/ledger.md`
  and `content/logbok.md` match their pack-root copies.
- **`build_art.py` could not be re-run here** — the Kenney library
  (`KENNEY_ROOT`, default `PACK.parents[2]/media_files/game_assets/Kenney`)
  is not present in this environment. Provenance is therefore verified
  *internally* (disk vs the tool's tables, and hue relationships of the
  committed sprites), not by re-extracting from source. A full clean
  art rebuild waits for a host with the library.
- **Staged-tile drift (reported, not fixed):** `art/out/tiles/` holds
  two orphans the current `build_art.TILES` no longer makes —
  `moor.3.webp`, `soil.2.webp` (an earlier TILES revision staged a
  third moor and a second soil). They are **not** copied into any
  region, so the shipped game is unaffected; the staging directory
  alone is dirty. Recommended cleanup: delete the two files (a
  one-line follow-up, not done here to honour "no art change").

## Legibility at actual game size

Tiles ship 32px (Kenney 16px ×2), sprites 48px tall (16px ×3, drawn at
1.5 tiles by the engine). The audit compared every sprite pair by
silhouette (alpha channel) and visible colour.

**The decision's pair — `hush-wisp` / `drowned-chorister` (L20), REPORTED, not changed:**

```
ok    L20 twin shares one silhouette  [hush-wisp/drowned-chorister
      alpha-identical 100.00%, visible-RGB-identical 0.00%]
```

Both come from the *same* source, Kenney Tiny Dungeon `tile_0121`
(`build_art.MONSTERS`); the chorister is the wisp hue-shifted 170°.
Measured: the **silhouette is pixel-for-pixel identical** (alpha
100% identical), and every one of the 1818 visible pixels is recoloured
(0% RGB-identical) — the sprite has **no** pixels in the hue-shift's
near-white no-op band, so L20's "no-op on near-white pixels" wording
does not hold for this sprite. The legibility consequence L20 records
still stands: the two share one shape and read as the same creature,
differing by name, hue and place.

A human-viewable contact sheet of the pair, drawn from the real pack
sprites at 3× nearest (same pixels the engine draws), is committed at
`art/out/legibility-contact-sheet.png` — the two are visually the same
ghost in a different tint.

**Other read-alike pairs the tool reported** (never a failure; none is
part of the decision, all are notes):

- `blackberry-cordial` / `the-evercan` — **100% identical**; both are
  Tiny Dungeon `tile_0116`. One item icon is reused verbatim for two
  different catalog items.
- `a-halfburnt-ledger` / `a-saltstiff-letter` / `corwins-last-entry` /
  `chalked-tide-map` — four "paper" icons from one source figure
  (Tiny Dungeon 126/127/128/125), shape-identical and 88% colour-same;
  they differ only by hue.

## Recommended small replacements (for a later decision — NOT applied)

1. `drowned-chorister`: give it its own silhouette, or a stronger,
   non-hue-only differentiation, so the drowned ghost is not the wisp.
2. `blackberry-cordial`: pick a distinct Kenney item tile (the pack's
   Tiny Dungeon 113/114/115 potion row is already used for the food
   items) so two catalog entries stop sharing one icon.
3. The four paper icons: vary at least the ledger vs the map stack so
   quest papers are told apart at a glance.

Each is small and local to `build_art.py`'s tables, but all three are
**art changes** and are out of scope for this decision.

## Accessibility record

- **Legible sprites/panels:** tiles 32px and sprites 48px, both from
  16px sources at integer nearest-neighbour scales (L11) — no blur, no
  resample. The twin pair above is the one legibility seam at that size.
- **Alternate input:** the engine plays on arrows plus one Interact
  button that names its next action (AGENTS.md "Playing"); the button
  is the touch/pointer path. The pack adds no input of its own.
- **Motion contrast / panels / phone size:** engine-owned, unverified
  here — the woven player (`web/packaged.html`) was not reachable
  (no VEFR checkout, no `norns`, no woven build in this environment).
  The pack ships `player.accent: "#C98049"` and one 1400×500 title
  image; canvas scaling, panel contrast, reduced-motion and font size
  cannot be judged from pack data alone.

## Engine / VEFR needs

Per the issue, engine art-import, render and schema needs go to VEFR
**only after confirming current engine behavior**. No engine checkout
is available here, so nothing is filed. If any surface is run later and
a seam is found (e.g. canvas scaling at phone width), record it in
`LIMITATIONS.md` first and crosslink the VEFR issue from there.

## Reproduce

```sh
python3 tools/build_pack.py            # deterministic; expect a clean tree
python3 tools/art_audit.py             # provenance + legibility report
python3 tools/art_audit.py --sheet art/out/legibility-contact-sheet.png
```
