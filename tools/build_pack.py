#!/usr/bin/env python3
"""Assemble the LANTERNWAKE pack from its sources of truth.

The pack on disk (world.json, acts/, voices/, library/) is the game;
this tool regenerates the map-dependent parts deterministically so a
layout change never hand-edits a contract. Content lives in content/:

  content/speakers.json     who people are, their phase seeds
  content/voices/*.md       voice prompts + fragment banks
  content/library/*.md      the books
  content/root.world.json   the hand-authored pack contract parts
                            (items, rules, flags, claims, grammars...)

  python3 tools/build_pack.py            # assemble everything
  python3 tools/build_pack.py --check    # layout + reachability only

Maps are laid out by stamping terrain with helper calls (fixed seed),
then the builder writes map.md + contract.json per region, the act
contract, and the pack voices. Every speaker, door, book and lamp is
reachability-checked from the region's own start. `norns validate`
is the gate after.
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
from collections import Counter
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
CONTENT = PACK / "content"
ACT = PACK / "acts" / "act-1"

PHASES = {
    "dusk": "The day settles. Windows go gold one by one along the hollow.",
    "moonrise": "The moon comes off the water. The street goes silver and quiet.",
    "deep-night": "The deepest watch. The dark stands taller than the walls.",
    "first-light": "Grey-gold on the sea. The lamps grow pale and honest.",
}
TIDE = {"dusk": "low", "moonrise": "low", "deep-night": "high", "first-light": "low"}

# The palette: char -> (tile name, solid, base colour). One language
# across every region; a region's legend carries only what it uses.
PALETTE = {
    "#": ("rock", True, "#2c2f38"),
    "X": ("timber-wall", True, "#3a2b22"),
    "Y": ("cabin-wall", True, "#3d3a46"),
    "Z": ("dark-wall", True, "#232735"),
    "R": ("ruin", True, "#3c3730"),
    "W": ("window", True, "#4a3826"),
    "~": ("sea", True, "#1d2c40"),
    "i": ("ice", False, "#2b3a4c"),
    ".": ("snow", False, "#cfd6de"),
    ",": ("frost", False, "#b9c4cf"),
    "_": ("moor", False, "#7d6a4c"),
    "g": ("grass", False, "#3f5c3a"),
    "s": ("soil", False, "#5c4630"),
    "h": ("shingle", False, "#4a4238"),
    "n": ("sand", False, "#8a6f4d"),
    "p": ("plank", False, "#8f7346"),
    "w": ("wood-floor", False, "#5f3f31"),
    "f": ("flagstone", False, "#7a6a52"),
    "c": ("cobble", False, "#5a5a60"),
    "b": ("brick", False, "#6b4a3a"),
    "d": ("dark-floor", False, "#242733"),
    "T": ("pine", True, "#2c4a33"),
    "t": ("tree", True, "#31502f"),
    "B": ("pine-bare", True, "#4a3b2c"),
    "U": ("bush", True, "#42503c"),
    "O": ("barrel", True, "#4c4436"),
    "K": ("crate", True, "#57482f"),
    "E": ("well", True, "#4c4c52"),
    "A": ("table", True, "#5c4126"),
    "Q": ("bench", True, "#4c4238"),
    "H": ("bed", True, "#4c3a2c"),
    "P": ("shelf", True, "#54401f"),
    "M": ("grave", True, "#565660"),
    "V": ("statue", True, "#7a7a84"),
    "F": ("fence", True, "#4a4238"),
    "L": ("lamp", False, "#7a5a2c"),
    "J": ("bridge", False, "#6b5637"),
    "S": ("stair", False, "#5a5a62"),
    "D": ("door", False, "#7a5230"),
}
WALKABLE = {c for c, v in PALETTE.items() if not v[1]}


class Map:
    """A tiny deterministic layout canvas."""

    def __init__(self, w: int, h: int, fill: str, seed: int):
        self.w, self.h = w, h
        self.rows = [[fill] * w for _ in range(h)]
        self.rng = random.Random(seed)

    def rect(self, x: int, y: int, w: int, h: int, ch: str) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, ch)

    def frame(self, x: int, y: int, w: int, h: int, ch: str) -> None:
        for xx in range(x, x + w):
            self.put(xx, y, ch)
            self.put(xx, y + h - 1, ch)
        for yy in range(y, y + h):
            self.put(x, yy, ch)
            self.put(x + w - 1, yy, ch)

    def put(self, x: int, y: int, ch: str) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.rows[y][x] = ch

    def scatter(self, ch: str, count: int, *, on: str | None = None) -> None:
        placed, tries = 0, 0
        while placed < count and tries < count * 40:
            tries += 1
            x, y = self.rng.randrange(self.w), self.rng.randrange(self.h)
            if on and self.rows[y][x] != on:
                continue
            self.rows[y][x] = ch
            placed += 1

    def house(self, x: int, y: int, w: int, h: int, *, wall: str = "X",
              floor: str = "w", door: tuple[int, int] | None = None,
              windows: bool = True) -> None:
        self.rect(x, y, w, h, floor)
        self.frame(x, y, w, h, wall)
        if windows:
            self.put(x + w // 2, y, "W")
        if door:
            self.put(*door, "D")

    def char_at(self, x: int, y: int) -> str:
        return self.rows[y][x]

    def text(self) -> str:
        return "\n".join("".join(r) for r in self.rows)

    # --- safety: make a tile standable, the least surprising way ---
    def unstick(self, x: int, y: int) -> None:
        """If (x,y) is solid, repaint it with the most common walkable
        char of its neighbours (an interior keeps its floor)."""
        if self.char_at(x, y) in WALKABLE:
            return
        around = []
        for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.w and 0 <= ny < self.h \
                    and self.rows[ny][nx] in WALKABLE:
                around.append(self.rows[ny][nx])
        self.put(x, y, Counter(around).most_common(1)[0][0] if around else ".")

    def reach(self, start: tuple[int, int]) -> set[tuple[int, int]]:
        seen = {start}
        todo = [start]
        while todo:
            x, y = todo.pop()
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.w and 0 <= ny < self.h \
                        and (nx, ny) not in seen \
                        and self.rows[ny][nx] in WALKABLE:
                    seen.add((nx, ny))
                    todo.append((nx, ny))
        return seen

    def check(self) -> list[str]:
        errs = []
        widths = {len(r) for r in self.rows}
        if len(widths) != 1:
            errs.append(f"rows not rectangular: {sorted(widths)}")
        unknown = set("".join("".join(r) for r in self.rows)) - set(PALETTE)
        if unknown:
            errs.append(f"chars outside the palette: {sorted(unknown)}")
        return errs


# ------------------------------------------------------------- layouts
def layout_thornhollow() -> Map:
    m = Map(32, 20, ".", 11)
    m.frame(0, 0, 32, 20, "#")
    m.scatter("T", 14)
    m.scatter("B", 5)
    # the streets: cobble through the middle
    m.rect(2, 9, 28, 2, "c")
    m.rect(15, 2, 2, 16, "c")
    # the Brine & Wick (inn), west of the square
    m.house(3, 3, 9, 6, wall="X", floor="w", door=(7, 8))
    m.rect(5, 5, 3, 1, "A")
    m.put(4, 4, "H")
    m.put(10, 4, "H")
    m.put(4, 6, "P")
    # the smithy, east
    m.house(19, 3, 9, 6, wall="X", floor="c", door=(23, 8))
    m.put(21, 5, "A")
    m.put(25, 5, "O")
    # the candle-shrine and the well on the square
    m.rect(12, 12, 7, 5, "f")
    m.put(15, 14, "V")
    m.put(9, 13, "E")
    m.put(21, 13, "Q")
    m.put(24, 13, "M")
    # the Guildhall ruin, north-west, with a gap at its west wall
    m.rect(2, 12, 6, 4, "R")
    m.rect(3, 13, 2, 2, "d")
    m.put(2, 13, "d")
    # exits: north to the weald, south to the causeway, east to the boneyard
    m.put(15, 0, "D")
    m.put(15, 19, "D")
    m.put(31, 9, "D")
    # the cellar door inside the inn
    m.put(6, 4, "D")
    return m


def layout_the_cellars() -> Map:
    m = Map(22, 14, "#", 12)
    m.rect(1, 1, 20, 12, "d")
    m.rect(2, 2, 6, 4, "w")
    m.rect(12, 2, 7, 5, "d")
    m.rect(3, 8, 14, 3, "d")
    m.scatter("O", 5, on="d")
    m.scatter("K", 4, on="d")
    m.put(4, 3, "A")
    m.put(9, 4, "P")
    m.put(18, 11, "D")   # the stair up to the inn
    return m


def layout_the_causeway() -> Map:
    m = Map(36, 16, "~", 13)
    # the raised road over the tidal flats
    m.rect(1, 6, 34, 4, "h")
    m.rect(1, 7, 34, 2, "i")
    # Toll Rock: an island the road runs through
    m.rect(15, 3, 7, 10, "h")
    m.frame(15, 3, 7, 10, "#")
    m.rect(16, 4, 5, 8, ".")
    m.rect(1, 7, 34, 2, "i")     # the track cuts the island open
    m.put(0, 7, "D")
    m.put(35, 7, "D")
    m.put(18, 6, "L")            # the first Great Lamp, above the track
    # the toll booth, south of the track
    m.rect(15, 9, 3, 2, "Y")
    m.put(16, 9, ".")
    m.put(19, 9, ".")
    m.scatter("K", 3, on=".")
    return m


def layout_saltreach() -> Map:
    m = Map(30, 20, "_", 14)
    m.frame(0, 0, 30, 20, "#")
    m.scatter("U", 12)
    m.scatter("B", 6)
    # salt pans and the channel
    m.rect(2, 2, 26, 3, "s")
    m.rect(3, 12, 24, 4, "~")
    m.rect(3, 13, 24, 2, "J")    # the stilt walk
    # huts along the north bank, each with a door ON its wall
    m.house(4, 6, 6, 5, wall="Y", floor="p", door=(6, 10))
    m.house(12, 6, 6, 5, wall="Y", floor="p", door=(14, 10))
    m.house(20, 6, 6, 5, wall="Y", floor="p", door=(22, 10))
    # the ferry slip and the second Great Lamp
    m.rect(12, 15, 7, 4, "n")
    m.put(15, 16, "L")
    m.put(13, 17, "K")
    m.put(18, 17, "Q")
    m.put(0, 7, "D")
    m.put(29, 7, "D")
    return m


def layout_the_boneyard() -> Map:
    m = Map(32, 20, "h", 15)
    m.frame(0, 0, 32, 20, "#")
    m.rect(1, 1, 30, 6, "~")
    m.rect(1, 7, 30, 3, "n")
    m.scatter("M", 9, on="h")
    m.scatter("K", 4, on="h")
    m.scatter("U", 6, on="h")
    # the cliff path north runs over the shallows on shingle
    m.rect(16, 1, 1, 6, "h")
    m.put(16, 0, "D")
    # the sea cave: down to the salt cellars
    m.rect(24, 12, 5, 4, "#")
    m.rect(25, 13, 3, 2, "d")
    m.put(26, 12, "D")           # the cave mouth, through the rock
    # the bonepicker's camp
    m.rect(5, 12, 4, 3, "n")
    m.put(6, 13, "Q")
    m.put(8, 12, "O")
    m.put(0, 10, "D")
    return m


def layout_gullwatch() -> Map:
    m = Map(30, 20, ".", 16)
    m.frame(0, 0, 30, 20, "#")
    m.scatter("T", 10)
    m.scatter("B", 6)
    # the cliff edge: rock down the east, a shelf on the headland
    m.rect(25, 1, 4, 18, "#")
    m.rect(24, 8, 1, 6, "h")
    m.rect(25, 8, 4, 4, "h")
    m.rect(23, 9, 1, 2, "h")
    # the streets
    m.rect(1, 9, 22, 2, "c")
    m.rect(12, 3, 2, 8, "c")
    # the chandlery (shop)
    m.house(4, 3, 8, 5, wall="X", floor="w", door=(7, 7))
    m.put(6, 5, "P")
    m.put(9, 5, "A")
    # the chapel of gullwatch
    m.house(16, 3, 7, 5, wall="Z", floor="f", door=(19, 7))
    m.put(19, 5, "V")
    # houses along the south street
    m.house(3, 12, 6, 4, wall="X", floor="w", door=(5, 12))
    m.house(11, 12, 6, 4, wall="X", floor="p", door=(13, 12))
    m.house(18, 12, 5, 4, wall="Y", floor="p", door=(20, 12))
    # the third Great Lamp on the headland
    m.put(27, 9, "L")
    m.put(12, 19, "D")
    m.put(0, 9, "D")
    return m


def layout_the_weald() -> Map:
    m = Map(30, 22, "g", 17)
    m.frame(0, 0, 30, 22, "#")
    m.scatter("T", 70)
    m.scatter("B", 18)
    m.scatter("U", 14)
    # the riding: a snow path through the trees
    m.rect(14, 1, 2, 20, ",")
    m.rect(2, 10, 27, 2, ",")
    # the ash clearing: the fourth Great Lamp
    m.rect(18, 12, 7, 6, "g")
    m.put(21, 14, "L")
    m.put(19, 15, "Q")
    m.put(24, 13, "B")
    # the woodward's hut, with a dooryard to the riding
    m.house(4, 3, 6, 4, wall="Y", floor="p", door=(6, 6))
    m.rect(6, 7, 1, 3, ",")
    m.put(5, 5, "A")
    m.put(14, 0, "D")
    m.put(14, 21, "D")
    return m


def layout_barrow_mouth() -> Map:
    m = Map(26, 18, "_", 18)
    m.frame(0, 0, 26, 18, "#")
    m.scatter("B", 8)
    m.scatter("M", 6)
    # the barrow: a stone mound, its door punched through the south wall
    m.rect(6, 2, 14, 8, "#")
    m.rect(7, 3, 12, 6, ".")
    m.rect(10, 6, 5, 2, "M")
    m.put(12, 8, ".")            # the door's inside threshold
    m.put(12, 9, "D")
    # the keeper's road
    m.rect(2, 12, 22, 2, ",")
    m.put(21, 13, "Q")
    m.put(13, 17, "D")
    return m


def layout_the_chapel() -> Map:
    m = Map(30, 20, "d", 19)
    m.frame(0, 0, 30, 20, "#")
    # the nave, half-drowned
    m.rect(2, 2, 26, 16, "f")
    m.rect(3, 12, 24, 5, "~")
    m.rect(3, 13, 24, 2, "i")
    # pillars down the nave
    for x in range(5, 26, 5):
        m.put(x, 6, "Z")
        m.put(x, 9, "Z")
    # the drowned altar and the fifth Great Lamp (an aisle kept open)
    m.rect(12, 3, 6, 3, "Z")
    m.put(15, 4, "V")
    m.put(15, 5, "L")
    m.put(15, 6, "f")
    m.put(15, 7, "f")
    # the vestry (the Warden's room)
    m.house(3, 3, 6, 5, wall="Z", floor="d", door=(5, 7), windows=False)
    m.put(5, 5, "P")
    m.put(7, 5, "M")
    # exits: the deep door (from the Under-Stair), the cliff stair north
    m.put(29, 6, "D")
    m.put(15, 19, "D")
    return m


def layout_vesper_point() -> Map:
    m = Map(26, 18, ".", 20)
    m.frame(0, 0, 26, 18, "#")
    m.scatter("T", 8)
    m.scatter("B", 5)
    m.rect(1, 1, 24, 4, "~")
    # the Beacon: a tower on the headland, its door punched south
    m.rect(10, 6, 7, 9, "#")
    m.rect(11, 7, 5, 7, "f")
    m.rect(12, 12, 3, 2, "d")
    m.put(13, 7, "L")
    m.put(13, 14, "D")
    # the keeper's house
    m.house(3, 7, 6, 5, wall="X", floor="w", door=(5, 11))
    m.put(5, 9, "A")
    m.put(7, 9, "H")
    # the road south to the chapel
    m.rect(12, 15, 2, 3, ",")
    m.put(13, 17, "D")
    return m


REGIONS = [
    ("thornhollow", layout_thornhollow, {"fog": False}),
    ("the-cellars", layout_the_cellars, {"fog": True}),
    ("the-causeway", layout_the_causeway, {"fog": True, "floods": True}),
    ("saltreach", layout_saltreach, {"fog": True, "floods": True}),
    ("the-boneyard", layout_the_boneyard, {"fog": True, "floods": True}),
    ("gullwatch", layout_gullwatch, {"fog": False}),
    ("the-weald", layout_the_weald, {"fog": True}),
    ("barrow-mouth", layout_barrow_mouth, {"fog": True}),
    ("the-chapel", layout_the_chapel, {"fog": True, "floods": True}),
    ("vesper-point", layout_vesper_point, {"fog": True}),
]

# POIs: region -> {label: (x, y)}
POIS = {
    "thornhollow": {
        "the Guildhall ruin": (3, 13),
        "the candle-shrine": (15, 15),
        "the old well": (10, 13),
    },
    "the-causeway": {
        "the unlit causeway lamp": (18, 6),
    },
    "saltreach": {
        "the unlit ferry lamp": (15, 16),
    },
    "gullwatch": {
        "the unlit cliff lamp": (27, 9),
    },
    "the-weald": {
        "the unlit weald lamp": (21, 14),
    },
    "the-chapel": {
        "the unlit chapel lamp": (15, 5),
    },
    "vesper-point": {
        "the Beacon door": (13, 14),
    },
    "the-boneyard": {
        "the sea-cave mouth": (26, 12),
        "the whale fall": (10, 9),
    },
    "barrow-mouth": {
        "the barrow door": (12, 9),
    },
}

POI_TEXT = {
    "the Guildhall ruin": "The Guildhall's burned bones. The beams are charcoal; the stone is sound. Someone should rebuild it.",
    "the candle-shrine": "A hundred stubs of candle on a stone table. Someone keeps lighting them.",
    "the old well": "The old well of Thornhollow. The rope is frayed; the water is far below.",
    "the unlit causeway lamp": "A Great Lamp of the coast, dark. The glass is sound; the wick is cold. The Evercan would wake it.",
    "the unlit ferry lamp": "The ferry lamp, dark. Ferrylight sings to it when he poles past.",
    "the unlit cliff lamp": "The cliff lamp, dark. From here the whole reach can be seen - and the dark along it.",
    "the unlit weald lamp": "The weald lamp on the ash stump, dark. The trees lean toward it.",
    "the unlit chapel lamp": "The chapel lamp in the drowned nave, dark. The sea stands in the aisles.",
    "the Beacon door": "The Beacon's iron door. Cold hinges. A house of light, waiting for one flame.",
    "the sea-cave mouth": "A cave mouth in the shingle. The tide breathes in and out of it.",
    "the whale fall": "The ribs of a whale the sea gave back. The bonepicker keeps the names.",
    "the barrow door": "The barrow's dark door. The stone is older than the town.",
}

# doors: (from, at, to, to_at). The Under-Stair / Salt Cellars doors are
# wired by `norns delve`, not here.
TRANSITIONS = [
    ("thornhollow", [15, 0], "the-weald", [14, 20]),
    ("the-weald", [14, 21], "thornhollow", [15, 1]),
    ("thornhollow", [15, 19], "the-causeway", [2, 7]),
    ("the-causeway", [0, 7], "thornhollow", [15, 18]),
    ("thornhollow", [31, 9], "the-boneyard", [1, 10]),
    ("the-boneyard", [0, 10], "thornhollow", [30, 9]),
    ("thornhollow", [6, 4], "the-cellars", [18, 10]),
    ("the-cellars", [18, 11], "thornhollow", [6, 6]),
    ("the-causeway", [35, 7], "saltreach", [1, 7]),
    ("saltreach", [0, 7], "the-causeway", [34, 7]),
    ("saltreach", [29, 7], "the-boneyard", [1, 10]),
    ("the-boneyard", [16, 0], "gullwatch", [12, 18]),
    ("gullwatch", [12, 19], "the-boneyard", [16, 1]),
    ("gullwatch", [0, 9], "the-weald", [28, 10]),
    ("the-weald", [29, 10], "gullwatch", [1, 9]),
    ("the-weald", [14, 0], "barrow-mouth", [13, 16]),
    ("barrow-mouth", [13, 17], "the-weald", [14, 1]),
    ("the-chapel", [15, 19], "vesper-point", [13, 16]),
    ("vesper-point", [13, 17], "the-chapel", [15, 18]),
]
# The barrow door and the sea-cave door lead DOWN into delve-generated
# floors; `norns delve` wires those transitions itself. The deep door
# out of the Under-Stair into the drowned chapel is added by
# tools/dress_floors.py after the floors exist.

HERO_START = {
    "thornhollow": [4, 10], "the-cellars": [2, 2], "the-causeway": [2, 7],
    "saltreach": [2, 7], "the-boneyard": [2, 10], "gullwatch": [2, 10],
    "the-weald": [15, 10], "barrow-mouth": [3, 13], "the-chapel": [28, 6],
    "vesper-point": [2, 14],
}

# chests (library books with chest: yes) live on these tiles
CHESTS = {
    "thornhollow": [(2, 3), (9, 7)],
    "the-cellars": [(3, 2), (7, 5)],
    "saltreach": [(23, 7)],
    "the-boneyard": [(7, 13)],
    "gullwatch": [(22, 4)],
    "the-weald": [(7, 5)],
    "barrow-mouth": [(8, 4)],
    "the-chapel": [(4, 5)],
    "vesper-point": [(12, 13)],
}

# the living hazards. Evidence items ride on drops: a drop taken from
# the floor is the only pickup that fires the engine's `picks-up`.
ENEMIES = {
    "the-cellars": [
        {"id": "cellar-rat-1", "name": "a gloam-rat", "at": [14, 3], "hp": 3, "atk": 1, "sprite": "gloam-rat", "drops": ["smoked-fish"]},
        {"id": "cellar-rat-2", "name": "a gloam-rat", "at": [15, 9], "hp": 3, "atk": 1, "sprite": "gloam-rat", "drops": []},
        {"id": "cellar-rat-3", "name": "the ledger rat", "at": [10, 9], "hp": 4, "atk": 1, "sprite": "gloam-rat", "drops": ["a-halfburnt-ledger"], "sight": 8},
        {"id": "cellar-wisp", "name": "a hush-wisp", "at": [12, 5], "hp": 4, "atk": 1, "sprite": "hush-wisp", "drops": ["gloam-glass"]},
    ],
    "the-causeway": [
        {"id": "causeway-rat-1", "name": "a gloam-rat", "at": [5, 6], "hp": 3, "atk": 1, "sprite": "gloam-rat", "drops": []},
        {"id": "causeway-rat-2", "name": "a gloam-rat", "at": [30, 9], "hp": 3, "atk": 1, "sprite": "gloam-rat", "drops": ["sea-salt"]},
        {"id": "causeway-wisp", "name": "a hush-wisp", "at": [25, 6], "hp": 4, "atk": 1, "sprite": "hush-wisp", "drops": ["gloam-glass"]},
    ],
    "saltreach": [
        {"id": "marsh-wight-1", "name": "a salt-wight", "at": [8, 13], "hp": 6, "atk": 2, "sprite": "salt-wight", "drops": ["gloam-glass"]},
        {"id": "marsh-wight-2", "name": "a salt-wight", "at": [20, 13], "hp": 6, "atk": 2, "sprite": "salt-wight", "drops": ["sea-salt"]},
        {"id": "marsh-wight-3", "name": "a salt-wight", "at": [5, 3], "hp": 6, "atk": 2, "sprite": "salt-wight", "drops": ["marsh-tea"]},
    ],
    "the-boneyard": [
        {"id": "cliff-crab-1", "name": "a cliff-crab", "at": [4, 8], "hp": 4, "atk": 1, "sprite": "cliff-crab", "drops": []},
        {"id": "cliff-crab-2", "name": "a cliff-crab", "at": [26, 9], "hp": 4, "atk": 1, "sprite": "cliff-crab", "drops": ["sea-salt"]},
        {"id": "cliff-crab-3", "name": "a cliff-crab", "at": [12, 8], "hp": 4, "atk": 1, "sprite": "cliff-crab", "drops": []},
        {"id": "beach-wisp", "name": "a hush-wisp", "at": [20, 10], "hp": 4, "atk": 1, "sprite": "hush-wisp", "drops": ["gloam-glass"]},
    ],
    "the-weald": [
        {"id": "husk-1", "name": "a weald-husk", "at": [8, 8], "hp": 7, "atk": 2, "sprite": "weald-husk", "drops": ["candle-box"]},
        {"id": "husk-2", "name": "a weald-husk", "at": [20, 8], "hp": 7, "atk": 2, "sprite": "weald-husk", "drops": []},
        {"id": "husk-3", "name": "a weald-husk", "at": [10, 14], "hp": 7, "atk": 2, "sprite": "weald-husk", "drops": ["honey-biscuit"]},
        {"id": "husk-4", "name": "a weald-husk", "at": [22, 16], "hp": 7, "atk": 2, "sprite": "weald-husk", "drops": ["rope-coil"]},
    ],
    "barrow-mouth": [
        {"id": "sentinel-1", "name": "a barrow-sentinel", "at": [9, 4], "hp": 10, "atk": 3, "sprite": "barrow-sentinel", "drops": ["whale-ivory"]},
        {"id": "sentinel-2", "name": "a barrow-sentinel", "at": [15, 5], "hp": 10, "atk": 3, "sprite": "barrow-sentinel", "drops": ["candle-box"]},
    ],
    "the-chapel": [
        {"id": "chorister-1", "name": "a drowned chorister", "at": [22, 8], "hp": 8, "atk": 2, "sprite": "drowned-chorister", "drops": ["rope-coil"]},
        {"id": "chorister-2", "name": "a drowned chorister", "at": [24, 11], "hp": 8, "atk": 2, "sprite": "drowned-chorister", "drops": ["sea-salt"]},
        {"id": "nave-wisp", "name": "a hush-wisp", "at": [10, 10], "hp": 4, "atk": 1, "sprite": "hush-wisp", "drops": ["gloam-glass"]},
        {"id": "the-drowned-warden", "name": "the drowned Warden", "at": [18, 8], "hp": 18, "atk": 3, "sprite": "the-drowned-warden", "drops": ["the-wardens-seal"], "sight": 8},
    ],
    "vesper-point": [
        {"id": "point-wisp-1", "name": "a hush-wisp", "at": [20, 15], "hp": 4, "atk": 1, "sprite": "hush-wisp", "drops": ["gloam-glass"]},
        {"id": "point-wisp-2", "name": "a hush-wisp", "at": [4, 15], "hp": 4, "atk": 1, "sprite": "hush-wisp", "drops": ["amber-glass"]},
    ],
}


def legends_for(m: Map) -> dict:
    used = set("".join("".join(r) for r in m.rows))
    out = {}
    for ch in sorted(used):
        tile, solid, base = PALETTE[ch]
        entry = {"base": [base]}
        if solid:
            entry["solid"] = True
        entry["tile"] = tile
        out[ch] = entry
    return out


def flood_for(m: Map, floods: bool) -> list[list[int]]:
    if not floods:
        return []
    return [[x, y] for y, row in enumerate(m.rows) for x, ch in enumerate(row)
            if ch in ("~", "i") and (x + y) % 3 == 0][:24]


def check_region(name: str, m: Map, speakers: dict, meta: dict) -> list[str]:
    """The playability gate: from the hero's start, every person, door,
    lamp POI and chest must be standable and reachable."""
    errs: list[str] = []
    start = tuple(HERO_START[name])
    if m.char_at(*start) not in WALKABLE:
        errs.append(f"{name}: hero_start {start} is solid ({m.char_at(*start)})")
        return errs
    seen = m.reach(start)

    def want(x: int, y: int, what: str, *, stand: bool = True) -> None:
        if stand and m.char_at(x, y) not in WALKABLE:
            errs.append(f"{name}: {what} at ({x},{y}) is solid ({m.char_at(x, y)})")
        elif (x, y) not in seen:
            errs.append(f"{name}: {what} at ({x},{y}) is unreachable")

    for key, spec in speakers.items():
        if spec["region"] == name:
            want(*spec["at"], f"speaker {key}")
    for label, (x, y) in POIS.get(name, {}).items():
        want(x, y, f"POI {label!r}")
    for frm, at, to, to_at in TRANSITIONS:
        if frm == name:
            want(*at, f"door to {to}")
        if to == name:
            want(*to_at, f"arrival from {frm}")
    for x, y in CHESTS.get(name, []):
        want(x, y, "chest")
    for e in ENEMIES.get(name, []):
        want(*e["at"], f"enemy {e['id']}")
    return errs


def build_regions(speakers: dict) -> dict[str, dict]:
    meta: dict[str, dict] = {}
    all_errs: list[str] = []
    for name, fn, opts in REGIONS:
        m = fn()
        # make every human-placed tile standable, then verify
        for key, spec in speakers.items():
            if spec["region"] == name:
                m.unstick(*spec["at"])
        for x, y in CHESTS.get(name, []):
            m.unstick(x, y)
        for e in ENEMIES.get(name, []):
            m.unstick(*e["at"])
        for frm, at, to, to_at in TRANSITIONS:
            if frm == name:
                m.unstick(*at)
        m.unstick(*HERO_START[name])
        errs = m.check() + check_region(name, m, speakers, opts)
        all_errs += errs
        meta[name] = {"map": m, **opts}
    if all_errs:
        for e in all_errs:
            print("LAYOUT:", e)
        raise SystemExit(f"{len(all_errs)} layout problems")
    return meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    speakers = json.loads((CONTENT / "speakers.json").read_text(encoding="utf-8"))
    meta = build_regions(speakers)
    if args.check:
        for name, info in meta.items():
            m = info["map"]
            print(f"{name}: {m.w}x{m.h} ok")
        return 0

    root = json.loads((CONTENT / "root.world.json").read_text(encoding="utf-8"))

    # region contracts
    for name, info in meta.items():
        m: Map = info["map"]
        pois = {f"{x},{y}": label for label, (x, y) in POIS.get(name, {}).items()}
        contract = {
            "tile": 32,
            "bg": "#12141c",
            "hero_start": HERO_START[name],
            "hero_color": "#e8e5df",
            "speaker_color": "#8b939c",
            "speaker_head": "#d8d5df",
            "legend": legends_for(m),
            "pois": pois,
            "poi_text": {f"{x},{y}": POI_TEXT[label]
                         for label, (x, y) in POIS.get(name, {}).items()},
            "sanctuary_tiles": [c for c in ("w", "f", "d", "c") if c in legends_for(m)][:1],
            "water_by_phase": TIDE,
            "flood_tiles": flood_for(m, info.get("floods", False)),
            "enemies": ENEMIES.get(name, []),
        }
        if info.get("fog"):
            contract["fog"] = {"radius": 5}
        rdir = ACT / name
        rdir.mkdir(parents=True, exist_ok=True)
        (rdir / "map.md").write_text(m.text() + "\n", encoding="utf-8")
        (rdir / "contract.json").write_text(
            json.dumps(contract, indent=2) + "\n", encoding="utf-8")

    # act contract: regions in canonical order, speakers grouped.
    # Anything `norns delve` added (floor regions, stair doors) is kept:
    # build and delve take turns, and neither may clobber the other.
    old_act = {}
    act_path = ACT / "world.json"
    if act_path.exists():
        try:
            old_act = json.loads(act_path.read_text(encoding="utf-8"))
        except ValueError:
            old_act = {}
    hand_regions = [n for n, _, _ in REGIONS]
    extra_regions = [r for r in old_act.get("regions", [])
                     if isinstance(r, str) and r not in hand_regions]
    hand_doors = {(f, tuple(a)) for f, a, _, _ in TRANSITIONS}
    extra_doors = [t for t in old_act.get("transitions", [])
                   if isinstance(t, dict)
                   and (t.get("from"), tuple(t.get("at", []))) not in hand_doors]

    act_speakers = {}
    for key, spec in speakers.items():
        act_speakers[key] = {
            "name": spec["name"],
            "at": spec["at"],
            "near": spec["near"],
            "voice_file": f"voices/{key}.md",
            "region": spec["region"],
            "seeds": spec["seeds"],
        }
        if spec.get("shop"):
            act_speakers[key]["shop"] = "true"
    act = {
        "id": "act-1",
        "title": "Lanternwake",
        "regions": hand_regions + extra_regions,
        "speakers": act_speakers,
        "transitions": [{"from": f, "at": list(a), "to": t, "to_at": list(ta)}
                        for f, a, t, ta in TRANSITIONS] + extra_doors,
        "start": {"region": "thornhollow", "at": HERO_START["thornhollow"]},
        "vault_intro": "The Lanternwake ledger: what the coast keeps, and what it owes.",
        "verbs": ["attack", "soothe"],
        "floor": "costume",
        "tone": "warm",
        "ruleset": "ambient",
    }
    (ACT / "world.json").write_text(json.dumps(act, indent=2) + "\n", encoding="utf-8")

    # voices: content/voices -> pack root (the woven bake) + each region
    vroot = PACK / "voices"
    if vroot.exists():
        shutil.rmtree(vroot)
    vroot.mkdir()
    for f in sorted((CONTENT / "voices").glob("*.md")):
        shutil.copyfile(f, vroot / f.name)
    for key, spec in speakers.items():
        rdir = ACT / spec["region"] / "voices"
        rdir.mkdir(parents=True, exist_ok=True)
        for suffix in (".md", ".fragments.md"):
            src = CONTENT / "voices" / f"{key}{suffix}"
            if src.exists():
                shutil.copyfile(src, rdir / src.name)

    # library
    lroot = PACK / "library"
    if lroot.exists():
        shutil.rmtree(lroot)
    shutil.copytree(CONTENT / "library", lroot)

    # the pack root contract: hand-authored parts + the voices block
    voices_block = {
        key: {"file": f"voices/{key}.md", "strike": spec["strike"]}
        for key, spec in speakers.items()
    }
    world = {**root, "name": "lanternwake", "phases": PHASES, "voices": voices_block}
    (PACK / "world.json").write_text(json.dumps(world, indent=2) + "\n", encoding="utf-8")

    shutil.copyfile(CONTENT / "logbok.md", PACK / "logbok.md")
    shutil.copyfile(CONTENT / "ledger.md", PACK / "ledger.md")
    print(f"built {len(REGIONS)} regions, {len(act_speakers)} speakers, "
          f"{len(list(lroot.glob('*.md')))} books")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
