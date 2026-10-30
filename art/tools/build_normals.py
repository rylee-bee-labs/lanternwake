#!/usr/bin/env python3
"""Make LANTERNWAKE's tile normal maps for Lamplight (VEFR's light over the drawn map).

One normal map per tile picture, with lab-kit's `normals` (the estate's art toolkit, in the Studio
repository), at the settings the light-rig spike tuned for tiles: relief from the tile's own
lightness (`--from-light 1`), at a gentle strength (`--strength 1`), because full strength
scratches snow and ice. VEFR reads `tiles/<name>.normal.png` beside `tiles/<name>.webp`
(`<name>.normal.2.png` for variant 2), and a tile without one is lit flat.

  python3 art/tools/build_normals.py          # STUDIO_ROOT, or ../studio beside this repo

What it writes:
  art/out/tiles/<name>.normal[.N].png             one per staged tile
  acts/<act>/<region>/tiles/<name>.normal[.N].png  in every region that has that tile

Run it after art/tools/build_art.py: it reads the staged tiles that one writes. Sprites get none
yet: VEFR lights people with the ground.
"""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PACK = Path(__file__).resolve().parents[2]
STAGED = PACK / "art" / "out" / "tiles"
SETTINGS = ["--from-light", "1", "--strength", "1"]


def normal_name(tile: Path) -> str:
    """`grass.webp` -> `grass.normal.png`; `grass.2.webp` -> `grass.normal.2.png`."""
    stem = tile.stem
    base, _, num = stem.rpartition(".")
    if base and num.isdigit():
        return f"{base}.normal.{num}.png"
    return f"{stem}.normal.png"


def main() -> int:
    studio = Path(os.environ.get("STUDIO_ROOT", PACK.parent / "studio"))
    kit = studio / "bin" / "lab-kit"
    if not kit.is_file():
        print(f"lab-kit not found at {kit}; set STUDIO_ROOT to a Studio checkout", file=sys.stderr)
        return 2
    tiles = sorted(p for p in STAGED.glob("*.webp") if ".normal" not in p.name)
    regions = sorted({Path(p).parent / "tiles" for p in glob.glob(str(PACK / "acts" / "*" / "*" / "contract.json"))})
    copied = 0
    with tempfile.TemporaryDirectory() as tmp:
        for tile in tiles:
            out = STAGED / normal_name(tile)
            subprocess.run([str(kit), "normals", str(tile), "--out", str(Path(tmp) / "height.png"),
                            "--normal-map", str(out), "--force", *SETTINGS], check=True, capture_output=True)
            for tdir in regions:
                if (tdir / tile.name).is_file():
                    shutil.copyfile(out, tdir / out.name)
                    copied += 1
    print(f"normal maps: {len(tiles)} staged, {copied} placed in {len(regions)} regions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
