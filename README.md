# LANTERNWAKE

## What this is

A cozy-dark game of lamplight along a winter coast, by Far Lantern
Studio. You are the Guild's last apprentice: re-light the five Great
Lanterns, carry news between the harbor towns, learn what happened the
night the bell drowned.

The game is data — a VEFR pack — and this repository is that pack.

## Is it running?

**UNKNOWN** from this document. A previous authoring environment lacked
`uv`, `uvx`, `node` and network access; that is **historical environment
evidence**, not an assertion about the machine reading this README now.

The gate runs from this pack root with the **pinned VEFR revision** in
`.github/workflows/pack-check.yml`, not a local engine checkout. A green
validation shows the pack passed *that revision's validator at that commit*;
it does not prove compatibility with newer VEFR, live deployment, physical
phone playability, or story acceptance. A failed/unrun check needs its own
evidence, not a claim that the game is broken.

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

## Play-Nice contract pin

The shared behavioral rules are pinned to a reviewed revision in [the adoption manifest](.project/contracts/adoption.yaml). [Contract freshness CI](.github/workflows/contract-freshness.yml) checks that pin against the authoritative Play-Nice source on PRs, pushes and weekly. A valid pin does **not** prove gameplay, runtime health, accessibility acceptance, or a passing `playnice check`; those require their own evidence. [Read the Play-Nice floor](https://github.com/rylee-bee-labs/play-nice-contracts/blob/main/contracts/everyone/FLOOR.md).
