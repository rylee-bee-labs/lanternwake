#!/usr/bin/env python3
"""Build LANTERNWAKE's art from the Kenney source packs.

Proof, pick, bulk, process, see it in the game, keep the record.
This is the PROCESS step, made repeatable: one command turns the
approved Kenney sources into the pack's tiles and sprites, at the
sizes the woven player draws (tiles 32px 1:1, sprites 48px tall).

Sources (CC0, Kenney.nl) live in the estate's shared library and are
referenced RELATIVE to this repo by default (never a baked absolute
path). Override with KENNEY_ROOT.

  python3 art/tools/build_art.py            # build everything
  python3 art/tools/build_art.py --mock     # + a mock scene to look at

What it writes:
  acts/<act>/<region>/tiles/*.webp   every region gets the full set
  sprites/*.png                      people, monsters, items (pack root)
  assets/title.webp                  the title picture
  assets/kenney/                     licenses + credits (the record)

Every picture here is identified by looking (see design/ART.md).
"""

from __future__ import annotations

import argparse
import colorsys
import glob
import os
import shutil
import sys
from pathlib import Path

from PIL import Image

PACK = Path(__file__).resolve().parents[2]
DEFAULT_KENNEY = PACK.parents[2] / "media_files" / "game_assets" / "Kenney"
KENNEY = Path(os.environ.get("KENNEY_ROOT", DEFAULT_KENNEY))

TILE_OUT = 32   # 16px Kenney source x2, drawn 1:1 on the 32px canvas
SPRITE_OUT = 48  # 16px source x3, the engine's 1.5-tile character height
ICON_OUT = 32   # item markers


def src(pack: str, idx: int) -> Path:
    p = KENNEY / "2D assets" / pack / "Tiles" / f"tile_{idx:04d}.png"
    if not p.exists():
        raise SystemExit(f"missing Kenney source: {p}")
    return p


def pixel_resize(im: Image.Image, size: int) -> Image.Image:
    return im.resize((size, size), Image.NEAREST)


# ---------------------------------------------------------------- tiles
# name -> [(pack, index), ...] in variant order. Identifications are
# recorded in design/ART.md; every one was checked by looking at an
# ASCII or pixel preview before it landed here.
TILES: dict[str, list[tuple[str, int]]] = {
    # --- ground ---
    "snow":        [("Tiny Ski", 0), ("Tiny Ski", 16), ("Tiny Ski", 24)],
    "frost":       [("Tiny Ski", 13), ("Tiny Ski", 12)],
    "ice":         [("Tiny Ski", 26), ("Tiny Ski", 27), ("Tiny Ski", 37)],
    "sea":         [("Tiny Town", 60), ("Tiny Town", 61)],
    "moor":        [("Tiny Farm", 48), ("Tiny Farm", 37)],
    "grass":       [("Tiny Town", 0), ("Tiny Town", 1), ("Tiny Town", 2)],
    "soil":        [("Tiny Farm", 37)],
    "shingle":     [("Tiny Farm", 64)],
    "plank":       [("Tiny Farm", 62)],
    "wood-floor":  [("Tiny Dungeon", 0), ("Tiny Dungeon", 12)],
    "dark-floor":  [("Tiny Dungeon", 11)],
    "flagstone":   [("Tiny Dungeon", 30), ("Tiny Dungeon", 42)],
    "sand":        [("Tiny Dungeon", 42), ("Tiny Dungeon", 48), ("Tiny Dungeon", 71)],
    "cobble":      [("Tiny Town", 102)],
    "brick":       [("Tiny Town", 116)],
    # --- walls ---
    "stone-wall":  [("Tiny Dungeon", 39), ("Tiny Dungeon", 40),
                    ("Tiny Dungeon", 57), ("Tiny Dungeon", 58)],
    "timber-wall": [("Tiny Dungeon", 33), ("Tiny Dungeon", 34)],
    "cabin-wall":  [("Tiny Farm", 114), ("Tiny Farm", 116)],
    "rock":        [("Tiny Dungeon", 5), ("Tiny Dungeon", 2),
                    ("Tiny Dungeon", 3), ("Tiny Dungeon", 4)],
    "ruin":        [("Tiny Dungeon", 25), ("Tiny Dungeon", 26), ("Tiny Dungeon", 27)],
    "dark-wall":   [("Tiny Dungeon", 10), ("Tiny Dungeon", 22)],
    # --- props (drawn as a tile picture, alpha over the ground) ---
    "lamp":        [("Tiny Dungeon", 29)],
    "torch":       [("Tiny Dungeon", 129), ("Tiny Dungeon", 130)],
    "pine":        [("Tiny Ski", 30), ("Tiny Ski", 6)],
    "pine-bare":   [("Tiny Farm", 2)],
    "tree":        [("Tiny Farm", 27), ("Tiny Farm", 15)],
    "bush":        [("Tiny Ski", 18)],
    "well":        [("Tiny Dungeon", 56)],
    "table":       [("Tiny Dungeon", 93)],
    "bench":       [("Tiny Farm", 75)],
    "barrel":      [("Tiny Dungeon", 82)],
    "crate":       [("Tiny Farm", 9)],
    "door":        [("Tiny Dungeon", 66)],
    "gate":        [("Tiny Dungeon", 7)],
    "stair":       [("Tiny Dungeon", 36), ("Tiny Dungeon", 37)],
    "fence":       [("Tiny Dungeon", 76), ("Tiny Dungeon", 77)],
    "bridge":      [("Tiny Dungeon", 69)],
    "grave":       [("Tiny Dungeon", 64), ("Tiny Dungeon", 65)],
    "statue":      [("Tiny Dungeon", 41)],
    "bed":         [("Tiny Dungeon", 96)],
    "shelf":       [("Tiny Dungeon", 75)],
    "window":      [("Tiny Dungeon", 44), ("Tiny Dungeon", 45)],
}

# --------------------------------------------------------------- sprites
# people: base figure per speaker key (+hue-shifted twins where a cast
# of 30 needs more faces than the pack ships). Monsters and items are
# plain extractions.
PEOPLE: dict[str, tuple[str, int, int]] = {
    # key: (pack, index, hue-shift degrees)
    "hero":           ("Tiny Dungeon", 87, 0),
    "marta":          ("Tiny Dungeon", 85, 0),
    "hobb":           ("Tiny Dungeon", 111, 0),
    "ilva":           ("Tiny Dungeon", 100, -25),
    "quill":          ("Tiny Dungeon", 86, 15),
    "pip":            ("Tiny Dungeon", 85, 135),
    "serren":         ("Tiny Dungeon", 84, 0),
    "aisling":        ("Tiny Dungeon", 99, -40),
    "vetch":          ("Tiny Dungeon", 88, 25),
    "holt":           ("Tiny Dungeon", 88, -30),
    "moss":           ("Tiny Farm", 124, 0),
    "toll-yann":      ("Tiny Dungeon", 112, -20),
    "ferry":          ("Tiny Dungeon", 86, 180),
    "wren":           ("Tiny Dungeon", 99, 60),
    "sable":          ("Tiny Dungeon", 85, -70),
    "grandmother-ash": ("Tiny Dungeon", 100, 105),
    "orra":           ("Tiny Dungeon", 87, 200),
    "bett":           ("Tiny Dungeon", 99, 150),
    "drennan":        ("Tiny Dungeon", 84, -105),
    "skua":           ("Tiny Dungeon", 112, 95),
    "halloran":       ("Tiny Dungeon", 111, 130),
    "bonepicker":     ("Tiny Dungeon", 88, -120),
    "edric":          ("Tiny Dungeon", 112, -60),
    "barrow-keeper":  ("Tiny Dungeon", 98, -140),
    "sef":            ("Tiny Dungeon", 97, 220),
    "osric":          ("Tiny Dungeon", 96, -160),
    "corwin":         ("Tiny Dungeon", 98, 165),
    "lise":           ("Tiny Dungeon", 85, -145),
    "keeper-gull":    ("Tiny Dungeon", 86, -95),
    "traveler":       ("Tiny Dungeon", 88, 75),
}

MONSTERS: dict[str, tuple[str, int, int]] = {
    # key: (pack, index, hue-shift degrees)
    "gloam-rat":        ("Tiny Dungeon", 123, 0),
    "hush-wisp":        ("Tiny Dungeon", 121, 0),
    "salt-wight":       ("Tiny Dungeon", 124, 0),
    "weald-husk":       ("Tiny Dungeon", 112, 0),
    "drowned-chorister": ("Tiny Dungeon", 121, 170),
    "mimic":            ("Tiny Dungeon", 92, 0),
    "barrow-sentinel":  ("Tiny Dungeon", 97, 0),
    "cliff-crab":       ("Tiny Dungeon", 110, 0),
    "the-drowned-warden": ("Tiny Dungeon", 98, 0),
}

ITEMS: dict[str, tuple[str, int]] = {
    "the-evercan":       ("Tiny Dungeon", 116),
    "lamp-hook":         ("Tiny Dungeon", 107),
    "bell-rope":         ("Tiny Dungeon", 131),
    "the-wardens-seal":  ("Tiny Dungeon", 101),
    "a-halfburnt-ledger": ("Tiny Dungeon", 126),
    "a-saltstiff-letter": ("Tiny Dungeon", 127),
    "corwins-last-entry": ("Tiny Dungeon", 128),
    "brine-chowder":     ("Tiny Dungeon", 113),
    "honey-biscuit":     ("Tiny Dungeon", 114),
    "marsh-tea":         ("Tiny Dungeon", 115),
    "blackberry-cordial": ("Tiny Dungeon", 116),
    "smoked-fish":       ("Tiny Farm", 109),
    "pitch-torch":       ("Tiny Dungeon", 130),
    "storm-lantern":     ("Tiny Dungeon", 129),
    "chalked-tide-map":  ("Tiny Dungeon", 125),
    "amber-glass":       ("Tiny Dungeon", 117),
    "gloam-glass":       ("Tiny Dungeon", 108),
    "whale-ivory":       ("Tiny Dungeon", 118),
    "rope-coil":         ("Tiny Dungeon", 119),
    "candle-box":        ("Tiny Dungeon", 91),
    "sea-salt":          ("Tiny Dungeon", 124),
    "wake-token":        ("Tiny Dungeon", 90),
    "choristers-bell":   ("Tiny Dungeon", 111),
}


def hue_shift(im: Image.Image, degrees: int) -> Image.Image:
    """Rotate hue, sparing skin tones, so a recoloured villager reads
    as another person rather than another species."""
    if degrees == 0:
        return im
    d = degrees / 360.0
    out = im.copy()
    px, op = out.load(), im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = op[x, y]
            if a < 8:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            skin = s > 0.15 and 0.02 <= h <= 0.14
            if s < 0.12 or skin:
                nh = h
            else:
                nh = (h + d) % 1.0
            nr, ng, nb = colorsys.hsv_to_rgb(nh, s, v)
            px[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), a)
    return out


def build_tiles() -> int:
    regions = sorted({Path(p).parent for p in
                      glob.glob(str(PACK / "acts" / "*" / "*" / "contract.json"))})
    if not regions:
        print("no regions yet - tiles staged in art/out/tiles only")
    n = 0
    staged = PACK / "art" / "out" / "tiles"
    staged.mkdir(parents=True, exist_ok=True)
    for name, variants in TILES.items():
        for i, (pack, idx) in enumerate(variants, start=1):
            im = pixel_resize(Image.open(src(pack, idx)).convert("RGBA"), TILE_OUT)
            suffix = "" if i == 1 else f".{i}"
            fname = f"{name}{suffix}.webp"
            im.save(staged / fname, "WEBP", quality=92)
            for rdir in regions:
                tdir = rdir / "tiles"
                tdir.mkdir(exist_ok=True)
                shutil.copyfile(staged / fname, tdir / fname)
            n += 1
    return n


def build_sprites() -> int:
    sdir = PACK / "sprites"
    sdir.mkdir(exist_ok=True)
    n = 0
    for key, (pack, idx, hue) in PEOPLE.items():
        im = pixel_resize(Image.open(src(pack, idx)).convert("RGBA"), SPRITE_OUT)
        hue_shift(im, hue).save(sdir / f"{key}.png")
        n += 1
    for key, (pack, idx, hue) in MONSTERS.items():
        im = pixel_resize(Image.open(src(pack, idx)).convert("RGBA"), SPRITE_OUT)
        hue_shift(im, hue).save(sdir / f"{key}.png")
        n += 1
    for key, (pack, idx) in ITEMS.items():
        pixel_resize(Image.open(src(pack, idx)).convert("RGBA"), ICON_OUT)\
            .save(sdir / f"{key}.png")
        n += 1
    return n


def build_title() -> None:
    """A night sky over the coast, composed from the same kit:
    snow fields, the mountains, the pines, and one red lamp glow."""
    W, H = 1400, 500
    canvas = Image.new("RGB", (W, H))
    # a graded dusk sky: deep blue -> slate at the horizon
    for y in range(H):
        t = y / H
        canvas.paste((
            int(18 + 26 * t), int(22 + 30 * t), int(48 + 22 * t)), (0, y, W, y + 1))
    moon = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
    for y in range(120):
        for x in range(120):
            if (x - 60) ** 2 + (y - 60) ** 2 <= 54 ** 2:
                moon.putpixel((x, y), (232, 228, 210, 255))
    canvas.paste(moon, (W - 320, 60), moon)
    # mountains: scaled-up rock tiles along the horizon
    rock = pixel_resize(Image.open(src("Tiny Dungeon", 5)).convert("RGBA"), 160)
    for i in range(10):
        canvas.paste(rock, (i * 150 - 40, H - 330), rock)
    # snow ground
    snow = pixel_resize(Image.open(src("Tiny Ski", 0)).convert("RGBA"), 96)
    for y in range(H - 200, H, 96):
        for x in range(0, W, 96):
            canvas.paste(snow, (x, y), snow)
    # pines along the ground
    pine = pixel_resize(Image.open(src("Tiny Ski", 30)).convert("RGBA"), 192)
    for x in range(40, W, 210):
        canvas.paste(pine, (x, H - 320), pine)
    # the lamp, and its glow
    lamp = pixel_resize(Image.open(src("Tiny Dungeon", 29)).convert("RGBA"), 128)
    lx, ly = W // 2 - 64, H - 300
    glow = Image.new("RGBA", (360, 360), (0, 0, 0, 0))
    for y in range(360):
        for x in range(360):
            d2 = (x - 180) ** 2 + (y - 180) ** 2
            if d2 <= 180 ** 2:
                glow.putpixel((x, y), (220, 150, 60, max(0, 90 - d2 // 720)))
    canvas.paste(glow, (lx - 116, ly - 116), glow)
    canvas.paste(lamp, (lx, ly), lamp)
    out = PACK / "assets" / "title.webp"
    out.parent.mkdir(exist_ok=True)
    canvas.save(out, "WEBP", quality=88)
    print(f"title -> {out.relative_to(PACK)}")


def write_credits() -> None:
    adir = PACK / "assets" / "kenney"
    adir.mkdir(parents=True, exist_ok=True)
    packs = set()
    for variants in TILES.values():
        packs |= {p for p, _ in variants}
    packs |= {p for p, *_ in PEOPLE.values()}
    packs |= {p for p, *_ in MONSTERS.values()}
    packs |= {p for p, _ in ITEMS.values()}
    for pack in sorted(packs):
        lic = KENNEY / "2D assets" / pack / "License.txt"
        if lic.exists():
            shutil.copyfile(lic, adir / f"LICENSE-{pack.lower().replace(' ', '-')}.txt")
    (adir / "README.md").write_text(
        "# Kenney art in this pack\n\n"
        "All third-party art in LANTERNWAKE comes from Kenney.nl asset\n"
        "packs (CC0 1.0). Sources are the estate library copies of\n"
        "Kenney Game Assets All-in-1 3.7.0.\n\n"
        "| Pack | Used for |\n|---|---|\n"
        "| Tiny Dungeon | people, monsters, items, dungeon tiles |\n"
        "| Tiny Farm | fields, trees, props |\n"
        "| Tiny Ski | snow, ice, pines, cabin walls |\n"
        "| Tiny Town | sea, grass, cobbles |\n\n"
        "Processing (this folder's `../../art/tools/build_art.py`): nearest-\n"
        "neighbour upscale, hue-shifted villager variants (skin tones\n"
        "spared), a composited title. Every source tile was identified by\n"
        "looking; the identifications are recorded in design/ART.md.\n\n"
        "Credit (appreciated, not required): Kenney - www.kenney.nl\n",
        encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mock", action="store_true", help="also render art/tools/mock_scene.py")
    args = ap.parse_args()
    if not KENNEY.is_dir():
        raise SystemExit(f"Kenney library not found at {KENNEY}")
    t = build_tiles()
    s = build_sprites()
    build_title()
    write_credits()
    print(f"tiles staged: {t}  sprites: {s}")
    if args.mock:
        import subprocess
        subprocess.run([sys.executable, str(PACK / "art" / "tools" / "mock_scene.py")],
                       check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
