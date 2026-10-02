#!/usr/bin/env python3
"""Dress the delve-generated floors of the deep road and the salt
cellars: the pack's own pixel tiles under delve's tile names, fog,
enemies (with the evidence drops that fire `picks-up`), and the deep
door out of the Under-Stair into the drowned chapel.

  python3 tools/dress_floors.py

Idempotent: re-running rewrites only this tool's own fields. Run
AFTER build_pack.py and both `norns delve` runs.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ACT = PACK / "acts" / "act-1"
TILES = PACK / "art" / "out" / "tiles"

# delve's legend names -> this pack's tile pictures
TILE_NAMES = {
    "dungeon-wall": "rock",
    "dungeon-floor": "dark-floor",
    "dungeon-stairs-up": "stair",
    "dungeon-stairs-down": "stair.2",
}

FLOOR_ENEMIES = {
    "under-stair-1": [
        ("stair1-sentinel-1", "a barrow-sentinel", "barrow-sentinel", 10, 3, ["candle-box"]),
        ("stair1-sentinel-2", "a barrow-sentinel", "barrow-sentinel", 10, 3, ["sea-salt"]),
        ("stair1-wisp", "a hush-wisp", "hush-wisp", 4, 1, []),
    ],
    "under-stair-2": [
        ("stair2-sentinel-1", "the rope-bearer", "barrow-sentinel", 12, 3, ["the-bell-rope"], 8),
        ("stair2-sentinel-2", "a barrow-sentinel", "barrow-sentinel", 10, 3, ["whale-ivory"]),
        ("stair2-wisp", "a hush-wisp", "hush-wisp", 4, 1, ["gloam-glass"]),
    ],
    "under-stair-3": [
        ("stair3-sentinel-1", "a barrow-sentinel", "barrow-sentinel", 10, 3, ["whale-ivory"]),
        ("stair3-sentinel-2", "a barrow-sentinel", "barrow-sentinel", 10, 3, ["amber-glass"]),
        ("stair3-wisp-1", "a hush-wisp", "hush-wisp", 4, 1, []),
        ("stair3-wisp-2", "a hush-wisp", "hush-wisp", 4, 1, ["gloam-glass"]),
    ],
    "salt-cellars-1": [
        ("cellar1-mimic", "the thing that ate the post", "mimic", 9, 2, ["a-saltstiff-letter"], 8),
        ("cellar1-wight-1", "a salt-wight", "salt-wight", 6, 2, ["gloam-glass"]),
        ("cellar1-wight-2", "a salt-wight", "salt-wight", 6, 2, ["sea-salt"]),
        ("cellar1-wisp", "a hush-wisp", "hush-wisp", 4, 1, []),
    ],
    "salt-cellars-2": [
        ("cellar2-mimic", "a mimic", "mimic", 9, 2, ["amber-glass"]),
        ("cellar2-wight-1", "a salt-wight", "salt-wight", 6, 2, ["gloam-glass"]),
        ("cellar2-wight-2", "a salt-wight", "salt-wight", 6, 2, ["marsh-tea"]),
        ("cellar2-chorister", "a drowned chorister", "drowned-chorister", 8, 2, ["rope-coil"]),
    ],
}

TIDE = {"dusk": "low", "moonrise": "low", "deep-night": "high", "first-light": "low"}


def floors() -> list[Path]:
    out = []
    for p in sorted(ACT.iterdir()):
        if p.is_dir() and (p.name.startswith("under-stair-")
                           or p.name.startswith("salt-cellars-")):
            out.append(p)
    return out


def place_slots(rows: list[str], n: int) -> list[tuple[int, int]]:
    """n standable tiles spread across a floor, away from the stairs."""
    h, w = len(rows), len(rows[0])
    open_tiles = [(x, y) for y, row in enumerate(rows) for x, ch in enumerate(row)
                  if ch == "."]
    stairs = [(x, y) for y, row in enumerate(rows) for x, ch in enumerate(row)
              if ch in "ud"]
    free = [(x, y) for (x, y) in open_tiles
            if all(abs(x - sx) + abs(y - sy) > 5 for sx, sy in stairs)]
    if not free:
        free = open_tiles
    step = max(1, len(free) // (n + 1))
    picks = []
    for i in range(n):
        idx = min(len(free) - 1, (i + 1) * step)
        picks.append(free[idx])
    return picks


def main() -> int:
    for rdir in floors():
        # 1. the pack's own pictures under delve's tile names
        tdir = rdir / "tiles"
        tdir.mkdir(exist_ok=True)
        for name, src in TILE_NAMES.items():
            shutil.copyfile(TILES / f"{src}.webp", tdir / f"{name}.webp")

        # 2. the contract: fog, tide, enemies
        cpath = rdir / "contract.json"
        contract = json.loads(cpath.read_text(encoding="utf-8"))
        rows = (rdir / "map.md").read_text(encoding="utf-8").splitlines()
        rows = [r for r in rows if r.strip()]
        enemies = []
        for spec in FLOOR_ENEMIES.get(rdir.name, []):
            eid, name, sprite, hp, atk, drops, *sight = spec
            enemies.append({"id": eid, "name": name, "at": [0, 0], "hp": hp,
                            "atk": atk, "sprite": sprite, "drops": drops,
                            **({"sight": sight[0]} if sight else {})})
        slots = place_slots(rows, len(enemies))
        for e, (x, y) in zip(enemies, slots):
            e["at"] = [x, y]
        contract["enemies"] = enemies
        contract["fog"] = {"radius": 4}
        contract["water_by_phase"] = TIDE
        contract.setdefault("sanctuary_tiles", ["u"])
        cpath.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
        print(f"{rdir.name}: {len(enemies)} enemies, tiles dressed")

    # 3. the deep door: out of the Under-Stair's bottom into the nave
    act_path = ACT / "world.json"
    act = json.loads(act_path.read_text(encoding="utf-8"))
    bottoms = [p for p in floors() if p.name.startswith("under-stair-")]
    if bottoms:
        bottom = bottoms[-1]
        rows = [r for r in (bottom / "map.md").read_text().splitlines() if r.strip()]
        hero = json.loads((bottom / "contract.json").read_text())["hero_start"]
        cand = next(((x, y) for y, row in enumerate(rows) for x, ch in enumerate(row)
                     if ch == "." and abs(x - hero[0]) + abs(y - hero[1]) > 4), None)
        if cand:
            door = {"from": bottom.name, "at": [cand[0], cand[1]],
                    "to": "the-chapel", "to_at": [29, 6]}
            have = {(t.get("from"), tuple(t.get("at", [])))
                    for t in act.get("transitions", [])}
            if (door["from"], tuple(door["at"])) not in have:
                act.setdefault("transitions", []).append(door)
                act_path.write_text(json.dumps(act, indent=2) + "\n",
                                    encoding="utf-8")
                print(f"deep door: {bottom.name} {door['at']} -> the-chapel [29, 6]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
