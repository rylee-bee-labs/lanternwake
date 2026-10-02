#!/usr/bin/env python3
"""A mock room at the game's real tile size (32px), plus a named
contact strip of every tile and sprite. One picture to look at, per
the studio's art rule: a single tile hides what a room shows.

  python3 art/tools/mock_scene.py     # writes art/out/mock-scene.png
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

PACK = Path(__file__).resolve().parents[2]
OUT = PACK / "art" / "out"
T = 32


def tiles() -> dict[str, Image.Image]:
    return {p.stem: Image.open(p).convert("RGBA")
            for p in sorted((OUT / "tiles").glob("*.webp"))}


def scene() -> Image.Image:
    """A small coast yard: snow, sea, pines, a cabin, a lamp, a hero."""
    ts = tiles()
    cols, rows = 22, 14
    canvas = Image.new("RGBA", (cols * T * 2, rows * T * 2), (19, 19, 17, 255))
    d = ImageDraw.Draw(canvas)

    def put(name: str, x: int, y: int, sz: int = 2) -> None:
        im = ts.get(name)
        if im is None:
            return
        canvas.paste(im.resize((T * sz, T * sz), Image.NEAREST), (x * T * sz, y * T * sz),
                     im.resize((T * sz, T * sz), Image.NEAREST))

    # ground plan (2x scale cells)
    plan = [
        ["sea", "sea", "sea", "sea", "sea", "sea", "sea", "sea", "sea", "sea", "sea"],
        ["sea", "shingle", "shingle", "snow", "snow", "snow", "snow", "snow", "snow", "snow", "sea"],
        ["sea", "shingle", "snow", "snow", "frost", "frost", "snow", "snow", "snow", "snow", "sea"],
        ["sea", "snow", "snow", "cabin-wall", "cabin-wall", "cabin-wall", "snow", "moor", "moor", "snow", "sea"],
        ["sea", "snow", "snow", "cabin-wall", "wood-floor", "cabin-wall", "snow", "moor", "moor", "snow", "sea"],
        ["sea", "snow", "snow", "cabin-wall", "door", "cabin-wall", "snow", "snow", "snow", "snow", "sea"],
        ["sea", "ice", "ice", "snow", "plank", "snow", "snow", "pine", "snow", "snow", "sea"],
        ["sea", "ice", "snow", "snow", "plank", "snow", "snow", "snow", "snow", "snow", "sea"],
        ["sea", "sea", "snow", "snow", "plank", "snow", "lamp", "snow", "snow", "snow", "sea"],
        ["sea", "sea", "sea", "snow", "snow", "snow", "snow", "snow", "snow", "sea", "sea"],
    ]
    for y, row in enumerate(plan):
        for x, cell in enumerate(row):
            put(cell, x, y)

    # figures and props on top (1x sprites at 2x cell scale)
    def sprite(name: str, x: int, y: int, scale: float = 1.5) -> None:
        p = PACK / "sprites" / f"{name}.png"
        if not p.exists():
            return
        im = Image.open(p).convert("RGBA")
        im = im.resize((int(T * 2 * scale), int(T * 2 * scale)), Image.NEAREST)
        canvas.paste(im, (x * T * 2 - im.width // 2 + T, y * T * 2 - im.height + T * 2), im)

    sprite("hero", 4, 7)
    sprite("marta", 6, 3)
    sprite("hobb", 8, 4)
    sprite("pip", 7, 6, 1.1)
    sprite("gloam-rat", 2, 2, 1.2)
    sprite("hush-wisp", 9, 2, 1.2)
    sprite("moss", 5, 8, 0.9)
    d.text((8, rows * T * 2 - 40), "LANTERNWAKE mock room - 32px tiles, 2x zoom",
           fill=(255, 230, 120))
    return canvas


def contact() -> Image.Image:
    """Every tile and sprite, named, to spot a wrong extraction at once."""
    ts = tiles()
    names = list(ts)
    cols = 12
    cell = 76
    rows = (len(names) + cols - 1) // cols
    sprs = sorted((PACK / "sprites").glob("*.png"))
    srows = (len(sprs) + cols - 1) // cols
    H = rows * (cell + 16) + srows * (cell + 16) + 40
    canvas = Image.new("RGB", (cols * cell, H), (25, 25, 32))
    d = ImageDraw.Draw(canvas)
    for i, n in enumerate(names):
        im = ts[n].resize((64, 64), Image.NEAREST)
        x, y = (i % cols) * cell, (i // cols) * (cell + 16)
        canvas.paste(im, (x + 6, y), im)
        d.text((x + 4, y + 66), n[:12], fill=(255, 220, 120))
    off = rows * (cell + 16) + 16
    for i, p in enumerate(sprs):
        im = Image.open(p).convert("RGBA")
        im.thumbnail((64, 64), Image.NEAREST)
        x, y = (i % cols) * cell, off + (i // cols) * (cell + 16)
        canvas.paste(im, (x + 6, y), im)
        d.text((x + 4, y + 66), p.stem[:12], fill=(160, 255, 180))
    return canvas


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    scene().save(OUT / "mock-scene.png")
    contact().save(OUT / "contact-sheet.png")
    print("wrote", OUT / "mock-scene.png", "and", OUT / "contact-sheet.png")
