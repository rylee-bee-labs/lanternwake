# ART — the style kit, the sources, the record

One kit for one game. All third-party art is **Kenney.nl, CC0 1.0**
(from the estate's shared library copy of Game Assets All-in-1 3.7.0),
processed by `art/tools/build_art.py`. Licences and credits ship in
`assets/kenney/`.

## The kit

| Pack | Used for |
|---|---|
| **Tiny Dungeon** (16px) | people, monsters, items, dungeon props, stone |
| **Tiny Farm** | fields, slat walls, pines, bare trees, well, furniture |
| **Tiny Ski** | snow, ice, snow-pines, snow-bush |
| **Tiny Town** | sea, grass, cobbles |

One family, one palette: warm dark pixel art. Processing is minimal
and honest - nearest-neighbour upscale (tiles 16->32, sprites 16->48,
drawn 1:1 by the player), hue-shifted villager variants with skin
tones spared (`hue_shift` in the tool), and one composited title
(night sky, moon, mountains, pines, the lamp and its glow).

## The identification record (every tile chosen by looking)

Identified from labelled contact sheets and ASCII pixel probes; the
probes are the reliable channel when the image reader serves stale
renders. Four misidentifications were caught in the mock-room review
and fixed (see PLAYTEST-LOG round 3):

| Tile | Source | What it is |
|---|---|---|
| snow / frost / ice | Tiny Ski 0,16,24,13,12,26,27,37 | winter ground |
| sea | Tiny Town 60,61 | open water |
| moor / soil | Tiny Farm 48,37 | winter field, furrows |
| grass | Tiny Town 0,1,2 | sheltered green |
| shingle | Tiny Farm 64 | pebbled dark ground |
| sand / flagstone | Tiny Dungeon 42,48,71,30 | beach, floors |
| plank / wood-floor | Tiny Farm 62, Tiny Dungeon 0,12 | timber |
| cobble / brick | Tiny Town 102,116 | streets |
| stone-wall etc. | Tiny Dungeon 39,40,57,58,5,2,3,4,25-27,10,22 | walls |
| cabin-wall | Tiny Farm 114,116 | barn slats (was ski signage - fixed) |
| lamp / torch | Tiny Dungeon 29,129,130 | the Great Lamps, fire |
| pine / pine-bare / tree / bush | Tiny Ski 30,6, Tiny Farm 2,27,15, Tiny Ski 18 | the weald |
| well, table, bench, barrel, crate, door, gate, stair, fence, bridge, grave, statue, bed, shelf, window | Tiny Dungeon 56,93, Tiny Farm 75, Tiny Dungeon 82, Tiny Farm 9, Tiny Dungeon 66,7,36,37,76,77,69,64,65,41,96,75,44,45 | props |

People: 12 Tiny Dungeon figures, hue-shifted into 27 named characters
(the shift spares skin, changes cloth and hair). Monsters: rat,
ghosts (one hue-shifted blue for the drowned), slimes, a mimic, two
knights for the deep road, a red crab. Items: potions, tools, torches,
chests, shells - one icon per catalog entry.

## The art tools (kept beside the art)

```
art/tools/build_art.py    sources -> tiles/, sprites/, assets/
art/tools/build_normals.py  tiles -> <tile>.normal.png, for Lamplight (run after build_art.py)
art/tools/mock_scene.py   a mock room at 32px + a named contact sheet
tools/playtest.py         screenshots of the real build (also art review)
```

The loop the studio teaches: proof, pick, bulk, process, **see it in
the game**, keep the record. The mock room and the in-game screenshots
are the sees; this file and `assets/kenney/README.md` are the record.

## Lamplight (2026-10-30)

The coast is lit by VEFR's Lamplight: the `light` block in `content/root.world.json`
(and so `world.json`). It sets:

- the dark of each watch;
- the Evercan's glow, held beside the hero;
- the five Great Lamps, each shining once its rule sets
  `the-<lamp>-lamp-lit`;
- walls, rock and crates standing a tile tall to cast shadows.

Every tile has a normal map beside it for relief: `<tile>.normal.png`,
made by `art/tools/build_normals.py` with lab-kit `normals --from-light 1
--strength 1`. That is the light-rig spike's tile setting. Full strength
scratches snow and ice.

Sprites have no normal maps yet. VEFR lights people with the ground.
Rylee checked the look on a private preview (screenshots of the woven
game) and answered "Looks right" (Project Home card #367, 2026-10-30).
