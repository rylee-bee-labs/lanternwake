# Lanternwake: agent reference

Detail moved out of `AGENTS.md`. Nothing here overrides it.

## Layout

| Path | What it is |
|---|---|
| `content/` | source of truth: `speakers.json`, `voices/`, `library/`, `root.world.json`, `logbok.md`, `ledger.md` |
| `world.json` | the generated pack contract: do not hand-edit |
| `acts/` | the act's regions: `map.md` + `contract.json` per region |
| `voices/`, `library/`, `sprites/`, `art/` | generated pack assets |
| `tools/` | `build_pack.py`, `dress_floors.py`, `art_audit.py`, `playtest.py`, `rules_test.mjs` |
| `design/` | the written record (see "The documents") |

Regenerate with `tools/build_pack.py` rather than editing `world.json`, `acts/`, `voices/` or `library/` by
hand: those are outputs. Run everything from the repository root.

## Build order

```sh
python3 tools/build_pack.py            # assemble from content/
python3 tools/build_pack.py --check    # layout + reachability only
python3 tools/dress_floors.py          # AFTER build_pack.py + both `norns delve` runs
```

Then the gate: `norns validate --pack .` (the pinned command is in `AGENTS.md`, "Run it").

`tools/playtest.py` (Playwright) and `tools/rules_test.mjs` (jsdom) are manual checks, not CI gates. Run them
by hand until the workflow adds them. `tools/art_audit.py` is a read-only report on the generated art
(decision in force, 2026-10-16: it reports, it changes no art; see `design/ART-AUDIT.md`).

## Publishing a build

`bin/publish-build.sh` weaves this pack into one offline HTML file with a VEFR checkout (`VEFR_DIR`, default
`~/code/Rylee-Bee/vefr`) and posts it to the dev gallery as project `lanternwake`, named for the HEAD short
sha. The VEFR checkout must contain the pack's own pin (`VEFR_REF` in `.github/workflows/pack-check.yml`) or
the script stops. `--dry-run` weaves and records the engine and pack revisions in `build-info.txt` but posts
nothing. A coordinator publishes merged main only, with `~/.agents/bin/publish-build lanternwake`.

## Known stale path

`tools/playtest.py` computes its build directory as `Path(__file__).resolve().parents[1] / "dist"` (inside
`newest_build()`), i.e. **two levels above this repository root**. That was correct when the pack lived at
`vefr/worlds/lanternwake/`; now it is not. There is no `dist/` in this repository and no record of one ever
having been committed (`git log --all --oneline -- dist` is empty), so where `vefr weave` writes its output
today is UNKNOWN. Fix `newest_build()` before trusting a playtest run.

## The rule of this project

The engine was never modified for this game. Every seam the game hit is recorded in `design/LIMITATIONS.md`
and worked around in pack data or tooling. Keep it that way: record, do not patch.

## Playing

The shipped game is one self-contained HTML file: no server, no model, nothing leaves the device. A player
running a local model can connect one under the pause menu's Model settings for fresh character lines; the
game is complete without one.

Keys: arrows walk; `E`/`F`/`Space` interact; `E` talks; `Q` hears a whisper; `B` opens the bag; `O` walks the
dark, `V` toggles it; `Esc` is the menu. The Interact button always names what the next press will do. You
cannot get anything wrong; the game narrates itself.

## Counts (derive them, do not copy them)

```sh
find acts -name contract.json | wc -l                    # regions
ls library/*.md | wc -l                                  # books
ls voices/*.md | grep -vc fragments                      # voiced people
python3 -c "import json; w=json.load(open('world.json')); print(len(w['rules']), len(w['phases']))"
```

## The documents

| File | What it is |
|---|---|
| `design/GAME-BIBLE.md` | the world, the people, the truth of the story |
| `design/MAKING-OF.md` | how it was made, including where the tooling lied |
| `design/LIMITATIONS.md` | engine seams found: recorded, never patched |
| `design/PLAYTEST-LOG.md` | build, play, revise, and the honest gaps |
| `design/CONTENT-PLAN.md` | where forty hours live; the content ledger |
| `design/WISHLIST.md` | what would be changed next |
| `design/ART.md` | the style kit, sources, identification record |
| `design/ART-AUDIT.md` | the art audit: provenance, legibility, source parity (issue #9) |
| `docs/design/` | dated decision notes (choices and consequences, 2026-10-16) |
| `assets/kenney/` | CC0 licences and credits |

## Play-Nice pin and verification

This repository adopts shared behavioral contracts through [`.project/contracts/adoption.yaml`](../.project/contracts/adoption.yaml). Read the [Play-Nice floor](https://github.com/rylee-bee-labs/play-nice-contracts/blob/main/contracts/everyone/FLOOR.md) and applicable packs; do not infer authority from adoption. CI [contract-freshness](../.github/workflows/contract-freshness.yml) only checks revision currency. Run `playnice check .` with a verified Play-Nice checkout to assess the separate repo check and generate any truthful badge; no passing badge is claimed here. Keep the repo's own verify/deploy/canon and owner gates.
