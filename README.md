# LANTERNWAKE

## What this is

A cozy-dark game of lamplight along a winter coast, by Far Lantern
Studio. You are the Guild's last apprentice: re-light the five Great
Lanterns, carry news between the harbor towns, learn what happened the
night the bell drowned.

The game is data — a VEFR pack — and this repository is that pack.

## Is it running?

**UNKNOWN**: the gate was not run here — `uv`, `uvx` and `node` are
absent and the network is blocked.

The gate is one command from this root; the engine comes from its
own repository, not a local checkout. Copy the pinned form
from `.github/workflows/pack-check.yml`. Green means the pack is
well-formed and current; anything else means it is not.

## How to use it

Paths are relative to this repository's root. The pack validates in
place (`--pack .`); it need not live in a VEFR checkout.

```sh
python3 tools/build_pack.py            # assemble from content/
python3 tools/build_pack.py --check    # layout + reachability
python3 tools/dress_floors.py          # delve tiles, enemies, doors
```

The woven playable HTML is **UNKNOWN**: there is no `dist/` here, and
`tools/playtest.py` still searches two directories above this root — a
leftover from when the pack sat in `vefr/worlds/lanternwake/`.

## Where to read more

- [`AGENTS.md`](AGENTS.md) — controls, pack layout, build order.
- [`design/GAME-BIBLE.md`](design/GAME-BIBLE.md) — the world and story.
- [`design/PLAYTEST-LOG.md`](design/PLAYTEST-LOG.md) — verification and gaps.
- [`design/LIMITATIONS.md`](design/LIMITATIONS.md) — engine seams, unpatched.