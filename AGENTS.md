# AGENTS.md — working on LANTERNWAKE

Agent-facing detail for the Lanternwake Coast pack. The human-facing
README is the short one; this is where the rest lives.

## What this repository is

A VEFR **pack** — data, not a program. This repository *is* the pack
root. It is its own repository; it is **not** inside a VEFR checkout and
does not need to be. The engine is fetched from its own repository (the
CI pins a commit; see `.github/workflows/pack-check.yml`).

Run everything from the repository root. `norns validate --pack .` is
the CI gate from here.

## Layout

| Path | What it is |
|---|---|
| `content/` | source of truth: `speakers.json`, `voices/`, `library/`, `root.world.json` |
| `world.json` | the generated pack contract — do not hand-edit |
| `acts/` | the act's regions: `map.md` + `contract.json` per region |
| `voices/`, `library/`, `sprites/`, `art/` | generated pack assets |
| `tools/` | `build_pack.py`, `dress_floors.py`, `playtest.py`, `rules_test.mjs` |
| `design/` | the written record (see below) |

Regenerate with `tools/build_pack.py` rather than editing `world.json`,
`acts/`, `voices/` or `library/` by hand — those are outputs.

## Build order

```sh
python3 tools/build_pack.py            # assemble from content/
python3 tools/build_pack.py --check    # layout + reachability only
python3 tools/dress_floors.py          # AFTER build_pack.py + both `norns delve` runs
```

Then the gate: `norns validate --pack .` (copy the pinned invocation
from `.github/workflows/pack-check.yml`).

`tools/playtest.py` (Playwright) and `tools/rules_test.mjs` (jsdom) are
manual checks, not CI gates. Run them by hand until the workflow adds
them.

## Publishing a build

`bin/publish-build.sh` weaves this pack into one offline HTML file with a VEFR checkout (`VEFR_DIR`,
default `~/code/Rylee-Bee/vefr`) and posts it to the dev gallery as project `lanternwake`, named for
the HEAD short sha. The VEFR checkout must contain the pack's own pin (`VEFR_REF` in
`.github/workflows/pack-check.yml`) or the script stops. `--dry-run` weaves and records the engine and
pack revisions in `build-info.txt` but posts nothing. A coordinator publishes merged main only, with
`~/.agents/bin/publish-build lanternwake`.

## Known stale path

`tools/playtest.py` computes its build directory as
`Path(__file__).resolve().parents[1] / "dist"`, i.e. **two levels above
this repository root**. That was correct when the pack lived at
`vefr/worlds/lanternwake/`; now it is not. There is no `dist/` in this
repository and no record of one ever having been committed
(`git log --all --oneline -- dist` is empty), so where `vefr weave`
writes its output today is UNKNOWN. Fix `newest_build()` before
trusting a playtest run.

`design/PLAYTEST-LOG.md` also still names the pre-move location
(`norns validate --pack worlds/lanternwake`) in its results table.

## The rule of this project

The engine was never modified for this game. Every seam the game hit is
recorded in `design/LIMITATIONS.md` and worked around in pack data or
tooling. Keep it that way: record, do not patch.

## Playing

The shipped game is one self-contained HTML file — no server, no model,
nothing leaves the device. A player running a local model can connect
one under the pause menu's Model settings for fresh character lines; the
game is complete without one.

Keys: arrows walk; `E`/`F`/`Space` interact; `E` talks; `Q` hears a
whisper; `B` opens the bag; `O` walks the dark, `V` toggles it; `Esc` is
the menu. The Interact button always names what the next press will do.
You cannot get anything wrong; the game narrates itself.

## Counts (verified against this tree)

15 regions (`find acts -name contract.json | wc -l`), 50 books
(`ls library/*.md | wc -l`), 27 voiced people (`ls voices/*.md` minus
`*.fragments.md`), 40 rules and 4 phases (keys of `world.json`).

## The documents

| File | What it is |
|---|---|
| `design/GAME-BIBLE.md` | the world, the people, the truth of the story |
| `design/MAKING-OF.md` | how it was made, including where the tooling lied |
| `design/LIMITATIONS.md` | engine seams found — recorded, never patched |
| `design/PLAYTEST-LOG.md` | build, play, revise — and the honest gaps |
| `design/CONTENT-PLAN.md` | where forty hours live; the content ledger |
| `design/WISHLIST.md` | what would be changed next |
| `design/ART.md` | the style kit, sources, identification record |
| `assets/kenney/` | CC0 licences and credits |

## Play-Nice pin and verification

This repository adopts shared behavioral contracts through [`.project/contracts/adoption.yaml`](.project/contracts/adoption.yaml). Read the [Play-Nice floor](https://github.com/rylee-bee-labs/play-nice-contracts/blob/main/contracts/everyone/FLOOR.md) and applicable packs; do not infer authority from adoption. CI [contract-freshness](.github/workflows/contract-freshness.yml) only checks revision currency. Run `playnice check .` with a verified Play-Nice checkout to assess the separate repo check and generate any truthful badge; no passing badge is claimed here. Keep the repo's own verify/deploy/canon and owner gates.
