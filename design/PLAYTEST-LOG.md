# PLAYTEST-LOG — build, play, revise

The record of how LANTERNWAKE was proven. Three verifications, in
order of strictness:

| Tool | What it proves | Status |
|---|---|---|
| `norns validate --pack worlds/lanternwake` | geometry, reachability, voices, books, rules shape | green |
| `tools/rules_test.mjs` (jsdom, real woven file) | the spine logic: lights, once-only, Beacon condition, beliefs | 14/14 |
| `tools/playtest.py` (Playwright, real browser) | the journey: title, walk, book, talk, whisper, phase rail, bag, door, combat | all steps held |

## Round 1 — scaffold and the geometry gate

Built 10 hand regions + 5 delve floors. The builder's own reachability
checker (flood fill from every `hero_start`) caught seven real breaks
before the engine ever saw them: Moss walled in behind the inn's
furniture, a scatter of barrels sealing the boneyard's north path,
the causeway island cut off from its own road, hut doors opening into
tables, a barrow door opening into a grave. Each was a layout bug, not
an engine bug; each is fixed in `tools/build_pack.py`.

## Round 2 — the first playtest

Findings, in the order the harness met them:

1. **The first-visit book pops the reader open** on arrival (the
   earned `the-coast-road`). Good onboarding; it intercepts input
   until closed. The harness learned to close overlays; the game
   needs nothing.
2. **Doors open with Interact, not by stepping.** The guides' line
   ("a door is stepped on, not stood on") describes an older seam;
   the live player shows "Go through the door" on the Interact button
   and only that verb crosses. Recorded in LIMITATIONS (L13); the
   playtest now presses Interact beside the door and asserts the
   button's own words.
3. Talk, whisper, phase rail, bag, combat all worked on first contact.
   Quill varied his line between runs (the fragment banks re-splice);
   the whisper that came back was flagged "A lie, or close enough." -
   the grammar whisper's truth flag doing its job.

## Round 3 — art review (the mock-room rule)

The contact sheet review caught four misidentified Kenney tiles that
the ASCII probes could not: `cabin-wall` was ski-lift signage, `tree`
was a flower, `moor.2` a sapling, and two monster sprites (a spider
for the "gull swarm", a second spider for the "chorister") did not
match their names. Fixed: barn-slat walls, real pines, a field
variant, a red cliff-crab, a hue-shifted ghost. Verified by pixel
statistics afterwards (the image reader in this session was serving
stale renders; pixel forensics and the harness assertions are the
evidence).

## Round 4 — the rules spine (jsdom)

`tools/rules_test.mjs` fires the game's own rules engine from the
real woven file: the Evercan is given at Begin; a lamp stays dark
without it and lights with it; a lit lamp never repeats; the Beacon
refuses four lamps and lights on five; Aisling's blame is written
into the game file and the ledger quiets it. One test-shape fix
(beliefs are `{value, source}` objects, not booleans) - a harness
bug, not a game bug.

## Honest gaps

- **Duration is designed, not measured.** ~40 hours is a content
  ledger target (CONTENT-PLAN); proving it needs 40 hours of play.
  What is proven: every system runs and every content piece is in
  place. What is not: a full completionist playthrough.
- No live model was reachable in this environment, so NPC talk was
  tested in its offline path (fragments + grammars), which is the
  shipping default. `player.model: "optional"` lets a player bring a
  model for fresh lines; that path is the engine's, tested by the
  engine.
- The studio journal was not exercised (the woven player is static);
  `vefr handbok` therefore has no real-play journal to read here.
