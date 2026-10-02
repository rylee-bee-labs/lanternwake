# LANTERNWAKE

A cozy-dark game of lamplight along a winter coast. By **Far Lantern
Studio**, built on [VEFR](../../README.md) (the engine is the bones;
this pack is the flesh).

> The Long Dim has fallen on the Lanternwake Coast. You are the
> Guild's last apprentice. Re-light the five Great Lanterns, carry
> the news between the harbor towns, and find out what happened the
> night the bell drowned.

## Play it

The shipped game is one self-contained file - no server, no model,
nothing leaves the device:

```
dist/lanternwake-2026-10-01.html      # open in any browser
```

Arrow keys walk; `E`/`F`/`Space` is Interact; `E` talks; `Q` hears a
whisper; `B` opens the bag; `O` walks the dark; `V` toggles it;
`Esc` is the menu. The Interact button always says what the next
press will do. You cannot get anything wrong; the game tells you what
it is doing as it goes.

Players who run a local model may connect one under the pause menu's
Model settings for fresh character lines; the game is complete
without one.

## Make it

```sh
# regenerate maps, contracts, voices placement, the act
python3 tools/build_pack.py

# dress the delve floors (tiles, enemies, the deep door)
python3 tools/dress_floors.py

# the gate
cd ../.. && uv run norns validate --pack worlds/lanternwake

# the playable file
uv run vefr weave --pack lanternwake

# prove it (browser journey + the rules spine)
uv run python worlds/lanternwake/tools/playtest.py
node worlds/lanternwake/tools/rules_test.mjs

# the art
python3 worlds/lanternwake/art/tools/build_art.py --mock
```

Source of truth lives in `content/` (speakers, voices, books, the
root contract) and the layout code in `tools/build_pack.py`; the pack
on disk is generated and always re-validable.

## What is in the box

| Piece | Count |
|---|---|
| Regions | 15 (10 by hand, 5 deep floors from `norns delve`) |
| Named people | 27, each with a voice, a fragment bank, four watches |
| Books | 50 |
| Items | 25 real + 10 landmark names |
| Rules | 40 (the whole reactive spine) |
| Enemies | 44 across the coast and the deep road |
| Phases | the four watches: dusk, moonrise, deep-night, first-light |

## The documents

| File | What it is |
|---|---|
| `design/GAME-BIBLE.md` | the world, the people, the truth of the story |
| `design/CONTENT-PLAN.md` | where forty hours live; the content ledger |
| `design/LIMITATIONS.md` | engine seams found - recorded, never patched |
| `design/PLAYTEST-LOG.md` | build, play, revise - and the honest gaps |
| `design/ART.md` | the style kit, sources, identification record |
| `assets/kenney/` | CC0 licences and credits |

## The rule of this project

The engine was never modified for this game. Every seam the game hit
is recorded in `design/LIMITATIONS.md` and worked around in pack data
or tooling.
