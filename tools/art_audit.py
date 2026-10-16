#!/usr/bin/env python3
"""Read-only audit of LANTERNWAKE's generated art (issue #9).

Decision in force (2026-10-16, "Option a"): the audit only **reports**
the near-identical `hush-wisp` / `drowned-chorister` pair recorded as
LIMITATIONS L20. It makes **no** art change and promotes nothing.

The build tool `art/tools/build_art.py` is the single source of truth
for provenance: every generated tile and sprite has exactly one entry
in its TILES / PEOPLE / MONSTERS / ITEMS tables. This tool checks what
is on disk against those tables, then reports which sprites render
alike (silhouette-identical, near-identical colour). It never writes
into `sprites/`, `art/out/tiles/`, `acts/` or `assets/`.

  python3 tools/art_audit.py
  python3 tools/art_audit.py --sheet art/out/legibility-contact-sheet.png

Exit 0 = every parity check held; 1 = a provenance break (details
printed). Legibility findings are reported, never fail the run: the
twin pair is accepted for v1.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

from PIL import Image

PACK = Path(__file__).resolve().parents[1]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def tile_names(tiles: dict) -> set[str]:
    """build_art.TILES -> the staged file stems (name, name.2, ...)."""
    return {f"{n}{'' if i == 1 else '.' + str(i)}"
            for n, variants in tiles.items() for i, _ in enumerate(variants, 1)}


def sprite_pixels(a: Image.Image, b: Image.Image):
    """(alpha-identical fraction, visible-RGB-identical fraction).

    Two sprites that share a silhouette (alpha identical everywhere)
    and mostly share visible RGB read as the same picture.
    """
    if a.size != b.size:
        return 0.0, 0.0
    pa, pb = a.load(), b.load()
    w, h = a.size
    alpha_same = visible = rgb_same = 0
    for y in range(h):
        for x in range(w):
            ra, ga, ba, aa = pa[x, y]
            rb, gb, bb, ab = pb[x, y]
            if aa == ab:
                alpha_same += 1
            if aa > 8 or ab > 8:
                visible += 1
                if (ra, ga, ba) == (rb, gb, bb):
                    rgb_same += 1
    return alpha_same / (w * h), (rgb_same / visible if visible else 1.0)


def write_sheet(path: Path, names: list[str]) -> Path:
    """A human-viewable strip of the named sprites at 3x, tile colour
    behind them, so 'do these read alike?' is answered by looking."""
    scale = 3
    ims = [Image.open(PACK / "sprites" / f"{n}.png").convert("RGBA") for n in names]
    pad, cell = 12, max(i.width for i in ims) * scale
    w = pad + len(ims) * (cell + pad)
    h = pad * 2 + max(i.height for i in ims) * scale
    sheet = Image.new("RGB", (w, h), (36, 39, 46))
    x = pad
    for im in ims:
        big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        sheet.paste(big, (x, pad + (h - 2 * pad - big.height) // 2), big)
        x += cell + pad
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", type=Path,
                    help="also write a contact sheet of the reported pair")
    ap.add_argument("--read-alike", type=float, default=0.85,
                    help="visible-RGB fraction that counts as 'reads alike'")
    args = ap.parse_args()

    build_art = load(PACK / "art" / "tools" / "build_art.py", "build_art")
    dress = load(PACK / "tools" / "dress_floors.py", "dress_floors")

    fails: list[str] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        print(f"{'ok  ' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
        if not ok:
            fails.append(name)

    world = json.loads((PACK / "world.json").read_text(encoding="utf-8"))

    # --- provenance parity: sprites ---
    table = set(build_art.PEOPLE) | set(build_art.MONSTERS) | set(build_art.ITEMS)
    on_disk = {p.stem for p in (PACK / "sprites").glob("*.png")}
    check("sprites/ == build_art tables", on_disk == table,
          f"disk {len(on_disk)}, table {len(table)}, "
          f"only-disk {sorted(on_disk - table)}, only-table {sorted(table - on_disk)}")

    # --- provenance parity: items and enemy sprites ---
    item_sprites = {v["sprite"] for v in world["items"].values() if v.get("sprite")}
    check("world.json item sprites resolve", item_sprites <= set(build_art.ITEMS),
          f"{len(item_sprites)} items with an icon, all in ITEMS table")
    enemy_sprites = set()
    for c in (PACK / "acts").glob("*/*/contract.json"):
        for e in json.loads(c.read_text(encoding="utf-8")).get("enemies", []):
            if e.get("sprite"):
                enemy_sprites.add(e["sprite"])
    check("enemy sprites resolve", enemy_sprites <= set(build_art.MONSTERS),
          f"{len(enemy_sprites)} enemy sprites, all in MONSTERS table")

    # --- provenance parity: every player sprite path exists ---
    bad_paths = [v for v in world["player"]["sprites"].values()
                 if not (PACK / v).exists()]
    check("player.sprites paths exist", not bad_paths, f"{len(bad_paths)} missing")

    # --- provenance parity: tiles ---
    want_tiles = tile_names(build_art.TILES)
    delve = set(dress.TILE_NAMES)
    staged = {p.stem for p in (PACK / "art" / "out" / "tiles").glob("*.webp")}
    orphans = sorted(staged - want_tiles)
    print(f"note  staged-tile drift  "
          f"[orphans not made by build_art: {orphans or 'none'}]")
    bad_regions = []
    for rdir in sorted((PACK / "acts").glob("*/*/tiles")):
        extra = {p.stem for p in rdir.glob("*.webp")} - want_tiles - delve
        if extra:
            bad_regions.append((rdir.parent.name, sorted(extra)))
    check("region tiles made by build_art (+delve)", not bad_regions,
          f"{len(bad_regions)} regions with unknown tiles")

    # --- legibility: sprites that render alike (reported, not failed) ---
    t = Image.open(PACK / "sprites" / "hush-wisp.png").convert("RGBA")
    c = Image.open(PACK / "sprites" / "drowned-chorister.png").convert("RGBA")
    alpha, rgb = sprite_pixels(t, c)
    check("L20 twin shares one silhouette", alpha > 0.9999,
          f"hush-wisp/drowned-chorister alpha-identical {alpha * 100:.2f}%, "
          f"visible-RGB-identical {rgb * 100:.2f}%")
    print(f"\nlegibility (reported, never a failure):")
    print(f"  hush-wisp <- Tiny Dungeon {build_art.MONSTERS['hush-wisp'][1]}, "
          f"hue {build_art.MONSTERS['hush-wisp'][2]}")
    print(f"  drowned-chorister <- Tiny Dungeon "
          f"{build_art.MONSTERS['drowned-chorister'][1]}, "
          f"hue {build_art.MONSTERS['drowned-chorister'][2]}  "
          f"-> same source, recoloured; REPORTED only (L20, decision 2026-10-16)")
    files = sorted((PACK / "sprites").glob("*.png"))
    pairs = []
    for i, fa in enumerate(files):
        ia = Image.open(fa).convert("RGBA")
        for fb in files[i + 1:]:
            if (fa.stem, fb.stem) == ("drowned-chorister", "hush-wisp"):
                continue
            a, r = sprite_pixels(ia, Image.open(fb).convert("RGBA"))
            if a >= 0.999 and r >= args.read_alike:
                pairs.append((r, fa.stem, fb.stem))
    for r, x, y in sorted(pairs, reverse=True):
        print(f"  also read alike: {x} / {y}  ({r * 100:.2f}% visible pixels match)")

    if args.sheet:
        names = ["hush-wisp", "drowned-chorister"]
        out = write_sheet(args.sheet, names)
        out = out.resolve()
        try:
            out = out.relative_to(PACK)
        except ValueError:
            pass
        print(f"\ncontact sheet -> {out}")

    print(f"\n{'AUDIT OK' if not fails else 'AUDIT FAILED: ' + ', '.join(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
