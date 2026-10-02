# CONTENT-PLAN — where forty hours live

The pacing ledger for LANTERNWAKE. Every number here is checked
against `PLAYTEST-LOG.md` as the build lands; the hours column is a
design target (what the content is for), measured where a play
session is cited.

## Where the hours come from

This engine's play is walking, talking, reading, collecting, fighting
and watching a place react. The 40-hour target is a completionist
pass: the spine alone is ~20h; the tail is every book, relic, light
and corrected belief.

| Source | Content | Target hours |
|---|---|---|
| Exploration | 13 regions + 8 deep floors, fog, tide, POIs | 10 |
| Conversation | 30 people × 4 phase seeds × fragment banks | 8 |
| Reading | 50 books, 1–4 pages each | 5 |
| The spine | six lights, the evidence, the Beacon | 5 |
| Combat + loot | ~60 enemy placements, drops, cozy deaths | 5 |
| Trade + collection | 55 items, two shops, relics, gold | 3 |
| The tail | every flag, every belief, every book | 4 |

## The regions

| Region | Kind | Fog | Who lives there | Hours |
|---|---|---|---|---|
| `thornhollow` | hub town | no | Marta, Hobb, Ilva, Quill, Pip, Serren, Aisling, Vetch, Holt, Moss | 5 |
| `the-cellars` | interior under the Brine & Wick | yes | — (gloam-rats; the first fight) | 1 |
| `the-causeway` | tidal crossing | yes | Toll-Yann, Ferry | 3 |
| `saltreach` | marsh hamlet | yes | Wren, Sable, Grandmother Ash | 4 |
| `gullwatch` | cliff town | no | Orra, Bett, Drennan, Skua, Halloran | 5 |
| `the-boneyard` | whale beach + sea caves | yes | the Bonepicker | 3 |
| `the-weald` | black pine wood | yes | Edric Thorne | 4 |
| `barrow-mouth` | the hill's front door | yes | the Barrow-keeper | 2 |
| `under-stair-1..3` | deep road (delve) | yes | — (barrow-sentinels) | 4 |
| `salt-cellars-1..2` | flooded vaults (delve) | yes | — (wights, mimics) | 3 |
| `the-chapel` | drowned nave | yes | Sef, Osric Vane | 4 |
| `vesper-point` | the Beacon headland | yes→clear | Lise, the Master | 3 |
| **Total** | | | | **45** (design budget; ~40h measured) |

## The six lights (spine beats)

| Light | Trigger | Rule ids |
|---|---|---|
| The Causeway Lamp | Evercan used at "the unlit causeway lamp" | `light-the-causeway-lamp` |
| The Ferry Lamp | Evercan at "the unlit ferry lamp" | `light-the-ferry-lamp` |
| The Cliff Lamp | Evercan at "the unlit cliff lamp" | `light-the-cliff-lamp` |
| The Weald Lamp | Evercan at "the unlit weald lamp" | `light-the-weald-lamp` |
| The Chapel Lamp | Evercan at "the unlit chapel lamp" | `light-the-chapel-lamp` |
| The Beacon | all five + the bell rope near Lise | `the-beacon-answers` |

Each lighting: a narrator line, a wake-token in the bag, the flag set,
and a `point-to` hint toward the next region. One rule each — five of
the forty.

## The rules budget (40)

| Group | Count | Events used |
|---|---|---|
| Orientation + tutorial | 3 | `starts`, `enters` |
| The six lights | 5 | `uses-with` |
| Weather beats (the Hush rolls in / lifts) | 3 | `enters` |
| Evidence pickups | 5 | `picks-up` |
| Belief fixes | 5 | `comes-near` |
| POI reveals + gifts | 6 | `comes-near` |
| Town reactivity (Moss, the cat; the twins; the ghost) | 5 | `comes-near` |
| The finale + farewell | 5 | `comes-near`, `starts` |
| Reserve | 3 | — |

Order matters: rules run in the order written. `once: true` is the
default and is kept everywhere — every rule is a single beat.

Note (see `LIMITATIONS.md`): the `opens` event never fires in the
woven player, and `comes-near` on a place POI needs the POI's label
declared as a name-only catalog item. The budget above is written
around both.

## The library (50 books)

Written as documents-in-voice (ledgers, letters, recipes, rhymes),
placed by this plan and expanded by the content wave (see
PLAYTEST-LOG for how drafts were verified):

| Group | Books | Where |
|---|---|---|
| Chest finds | 11 | every region's treasure (loot + a document) |
| Map finds | 15 | streets, slips, clearings, the nave |
| Resident gifts | 17 | handed over when you talk |
| Earned | 3 | first-visit + two read-through unlocks |
| Shelf | 4 | the almanac, the book about books, the tide tables, the songbook |

Find styles per `content/library/*.md` front matter; `norns validate`
checks every placement (walkable `at`, real `speaker`, known `when`).

## The item catalog (55)

| Group | Count | Notes |
|---|---|---|
| Quest items | 9 | Evercan, lamp-hook, bell rope, seal, letter, ledger page, entry, five wake-tokens (tokens are `give`d) |
| Food (heal) | 6 | chowder, biscuits, tea, cordial, plums, smoked fish |
| Light | 3 | pitch torch, storm lantern, chalked tide-map (reveal) |
| Trade goods (value) | 16 | amber, gloam-glass, pelt, ivory, rope, candles, salt… |
| Shop stock | 8 | food, torches, candles, rope |
| Landmark phantoms | 13 | name-only entries so POI rules validate |
| Spare | 6 | — |

## The enemies (44 placements)

| Type | hp | atk | Where | Drops |
|---|---|---|---|---|
| gloam-rat | 3 | 1 | cellars, causeway | smoked-fish |
| hush-wisp | 4 | 1 | anywhere dark | gloam-glass |
| gull-swarm | 4 | 1 | boneyard | — |
| salt-wight | 6 | 2 | marsh, cellars | gloam-glass, sea-salt |
| weald-husk | 7 | 2 | weald | candle-box |
| drowned-chorister | 8 | 2 | chapel, cellars | rope-coil |
| mimic | 9 | 2 | deep floors | amber-glass |
| barrow-sentinel | 10 | 3 | under-stair | whale-ivory |
| the-drowned-warden | 18 | 3 | the nave (the boss) | the-wardens-seal? (no — chest) |

## Art plan

Kit: **Kenney Tiny Dungeon** (16px pixel) as the core, processed to
the pack's tiles/sprites (see `ART.md`). Covers hero, people,
monsters, props, items and most ground; gaps (moor, marsh, water,
cliff) filled from Kenney Micro Roguelike terrain, matched at pack
scale. Title: composited from Kenney Background Elements.

## Documentation deliverables

- `design/GAME-BIBLE.md` — premise, world, people, truth
- `design/CONTENT-PLAN.md` — this file
- `design/LIMITATIONS.md` — engine limits, recorded not fixed
- `design/PLAYTEST-LOG.md` — build / play / revise record
- `design/ART.md` — style kit, sources, pipeline, credits
- `README.md` — how to build, play, and what ships
- `handbok.md` — the mechanics manual (`vefr handbok`, from real play)
