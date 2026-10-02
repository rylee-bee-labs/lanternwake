# LIMITATIONS — engine seams found while building Lanternwake

Rule of the project: **the engine is not modified for this game.**
Every seam found while building is recorded here with where it was
observed and how the pack works around it (or honestly lives with it).
Verified against vefr `ecbb1ea` (2026-10-01) by reading
`src/vefr/cli.py`, `src/vefr/world.py`, `src/vefr/maplab.py` and
`web/packaged.html`, plus one live `maplab.rules_errors` probe.

## Structure

### L1. Only the first act is playable
`cli.weave_html` bakes regions, transitions, speakers and enemies
from `world["acts"][0]`; `world["_current_act"]` is fixed at 0 ("for
now; future PRs advance this"). Multi-act packs can hold content but
only act 1 plays.
**Workaround:** the whole game lives in one act with 13 regions and
transitions. Chapters are content structure, not engine acts.

### L2. One play surface per game
`startPlaySurface()` in `web/packaged.html` picks the surface from
`acts[0].ruleset`: `cooking` opens the kitchen (town hidden), `desk`
opens the desk, anything else walks the town. A game cannot mix a
kitchen chapter with a walking chapter.
**Workaround:** `ruleset: ambient`. The cooking/desk loops are
recorded here as unavailable to this game rather than forced.

### L3. The rules engine: 40 rules, no chains
`maplab.RULE_LIMIT = 40`; a rule fires at most once (`once: true` is
the default) and returned actions are never fed back as events (a
`give` is not a `picks-up`). No numbers, no randomness, no timers, no
typed input (no `says` event).
**Workaround:** the spine is six one-rule lights; all quest *flavor*
lives in books, fragments and seeds where volume is unlimited. The
40-rule budget is spelled out in `CONTENT-PLAN.md`.

### L4. `opens` rules can never fire
The only `fireRule('opens', …)` call site is inside `useHere()`
(`web/packaged.html` ~3697), which nothing calls since one-button
Interact landed; `doInteract()`'s chest branch opens chests without
firing the event. Probe: the ROADMAP entry for the rules engine lists
"the chest (`opens`)" as a call site — the call site exists but is
orphaned at `ecbb1ea`.
**Workaround:** no rule uses `opens`. Chest beats are `picks-up`
(item drops from chests) and `comes-near` instead.

### L5. `comes-near` / `uses-with` and place POIs disagree with the validator
Runtime: stepping onto a named POI fires `comes-near {who: <POI
label>, distance: 0}`; using an item there fires `uses-with {item,
with: <POI label>}`. But `maplab` requires `who`/`with` to be a
declared thing id (item id, speaker key or region name) and
`comes-near` distance to be an integer **1..9**. Probe (live):

```
ERR: rule 'poi-test' when 'comes-near' who names unknown thing 'the sealed panel'
ERR: rule 'poi-test' when 'comes-near' distance must be an integer 1..9
ERR: rule 'use-test' when 'uses-with' with names unknown thing 'the sealed panel'
```

Runtime matching (`whenMatches`) is "within N tiles", so a distance-0
event does satisfy a rule written with distance ≥ 1 — only validation
blocks it.
**Workaround:** the pack declares each rule-relevant landmark as a
name-only catalog item whose **id is the POI's display label**
(e.g. `"the unlit causeway lamp": {"name": "the unlit causeway lamp"}`).
It has no `value`/`heal`/`sprite`, so it never shows in trade or the
bag; it makes the POI a declared "thing" so rules validate and fire.
Recorded here because the workaround is invisible in the pack data.

### L6. Custom combat verbs are words only
`applyVerb` maps only the literal verb `attack` to damage; any other
act-declared verb prints "You use X on Y." and spends the turn.
Fleeing, defending, or soothing for real are not possible.
**Workaround:** `verbs: ["attack", "soothe"]`; Soothe is honest
flavor. Bump-to-attack is the reliable damage path.

## Items, shops, people

### L7. Items cannot be taken, given or equipped
Rules can `give` items to the hero but never remove one; there is no
give-to-NPC action, no dropping, no equipping, no effects beyond
`heal` and `light`.
**Workaround:** deliveries are "carry the news" beats (a person sees
what you carry and speaks); the Evercan is a never-spent heirloom
("ever-full") instead of a consumed oil item; wake-tokens are pure
keepsakes.

### L8. Shops: one per region, whole catalog for sale
A speaker with `"shop": "true"` opens trade; the Buy list is every
catalog entry with a `value` (no stock, no haggling, selling always
pays `value`).
**Workaround:** two shops and one stall; values are tuned so selling
loot funds food and lanterns.

### L9. Beliefs are engine-state, seen only in the why-log
`believes`/`stops-believing`/`tells` change rule state only; nothing
in the player shows them (by design: "visible only in the why log at
first"). NPC lines do not branch on beliefs.
**Workaround:** every belief change is paired with a `say` beat so the
player *hears* the correction; the claim table lives in the bible.

### L10. Flood and tide are cosmetic
`water_by_phase: "high"` draws a blue overlay over `flood_tiles`; the
tiles stay walkable.
**Workaround:** the flooded causeway is dread, not a gate. Never
puzzle-design around tide timing (and the engine law says no timers).

## Art and text

### L11. Tile pictures are baked as-is
The player never resizes a pack tile; the pack must ship pictures at
the right pixel size (`tiles/` webp/png; `sprites/` scaled to 1.5
tiles tall). A tile the region and engine both lack is a validation
error in a region that has `tiles/`.
**Workaround:** the art pipeline (`art/tools/`) upscales Kenney 16px
sources to 64px squares and slices per tile; every region's `tiles/`
is complete and validated.

### L12. The speech box holds 280 characters (`RULE_SAY_LIMIT`)
**Workaround:** every `say` line in the pack is short by habit;
`norns validate` catches overflow.

### L13. Voice prompt files: two locations
The woven bake inlines **pack-root** `voices/<stem>.md`; the live app
resolves per-region `voices/` first. `fragments` merge from both.
**Workaround:** each voice ships in both places (the shipped
sample-world does the same).

## Testing seams

### L14. `storyteller-test` / `storyteller-benchmark` need a live brain
No model endpoint was reachable in this environment (no llama.cpp chat
server; the local `:8082` endpoint serves only the `bge-m3` embedder).
**Workaround:** the game is authored model-free (fragments, grammars,
books); playtests run offline and are deterministic. A pool weave
(`weave --pool N`) is left as an optional step for whoever has a
brain; `player.model: "optional"` lets players bring their own.

### L15. `journal.KINDS` has `rule_fired` with no server call site
The woven player is static — its rule log lives in `localStorage`
(`VEFR_WHY`), not in the studio journal. `vefr handbok` therefore
sees only live-app play.
**Workaround:** playtest notes are kept by hand in `PLAYTEST-LOG.md`;
handbok is run over live-app sessions where useful.

## Learned while building (second pass, 2026-10-01)

### L16. `picks-up` fires only for floor drops, never chest contents
`takeHere()` (walking onto an enemy's drop) fires `picks-up`; a
chest's `giveChestDrops` adds items to the bag silently - one line,
no event. So a quest item in a chest can never drive a `picks-up`
rule. (Chest opening itself fires nothing - see L4.)
**Workaround:** every evidence item that must fire a story beat rides
on an **enemy drop** (the rats ate the ledger; the mimic ate the post;
the sentinel carried the rope; the Warden carries his seal). Chests
carry treasure and books. The one item the story hands over directly
(`corwins-last-entry`) is given by a `comes-near` rule instead.

### L17. `uses-with` is unreachable for a quest tool
The Bag's Use button appears only for items with `heal` or `light`,
and using one **spends the copy** (a heal at full health is the one
mercy case that keeps it). A never-spent quest tool like the Evercan
therefore cannot be "used" at all - and if it were given `light` to
force the button, a stray use would destroy it and soft-lock the
spine.
**Workaround:** the lamps light on `comes-near` (the hero walks up to
the lamp POI carrying the Evercan). `uses-with` is left unused.

### L18. Doors open with Interact, not by stepping (docs are stale)
`rulesets.md` says "a door is stepped on, not stood on: the step
enters the other region". The live player disagrees: `move()` has no
transition call; only `doInteract`'s door target crosses (the button
says "Go through the door"). The doc line is stale against
`ecbb1ea`'s player. Flagged here per the project rule (record, do not
modify the engine); the guides' claim should be corrected by the
engine's own keepers.

### L19. Testing seams for jsdom harnesses
Three things a harness must know: (1) the woven file touches
`localStorage` at boot, so jsdom needs a real origin (`url:
https://...`) or it dies on opaque-origin SecurityError before the
wiring runs; (2) Begin's handler settles on a `setTimeout` tick -
await it; (3) the canvas needs the minimal 2D stub the engine's own
harnesses use. Beliefs in rule state are `{value, source}` objects,
not booleans. (Harness: `tools/rules_test.mjs`, which plays the real
woven file.)

### L20. One sprite pair reads alike
`hush-wisp` and `drowned-chorister` are the same Kenney ghost; the
hue shift is a no-op on near-white pixels (skin/value guards), so the
two differ by name and place only. Accepted for v1; the fix is a
tint pass in `art/tools/build_art.py`.

### L21. `vefr handbok` reads the wrong game's play
`handbok --pack <name>` writes the manual "from real play", but the
journal it reads is the engine's default session, not the pack's:
running it for this pack printed **another pack's title** and that
pack's `/api/*` call counts into `worlds/lanternwake/handbok.md`.
The woven player keeps its journal in `localStorage` anyway (L15),
so a woven-first game has no server journal to read.
**Workaround:** the generated manual was deleted rather than shipped
wrong; the honest mechanics record for this game is
`design/PLAYTEST-LOG.md`. The engine's keepers may want handbok to
scope its journal by pack (and to never print another world's name
into a pack's file - the neutrality guard's spirit).


## Supersede notes (2026-10-02 — the upstream pass)

VEFR's keepers ran a verification pass over this file's evidence
(the matrix lives in the engine repo's `docs/research/
2026-10-02-first-independent-pack.md`) and landed contract repairs.
The workarounds ABOVE STAY AS HISTORY — they were true when written
and the scars are the point — but note what superseded them:

| Was | Status now |
|---|---|
| L4 `opens` never fires | **fixed upstream**: `opens` fires through the Interact path (chest = its book id, door = the place it opens into); the orphaned `useHere` was deleted |
| L5 POI labels / distance 0 rejected | **fixed upstream**: one identity model — POI labels, book ids and enemy ids are declared things; distance is 0..9 (0 = standing on it). The phantom-item workaround below is no longer needed (it still validates — a name-only item is a legal thing — but new work should use the label directly) |
| L16 `picks-up` only from floor drops | **fixed upstream**: every player acquisition (floor, chest, trade) fires `picks-up`; a rule's `give` stays silent |
| L17 `uses-with` unreachable for quest tools | **fixed upstream**: item `keep: true` + a bare `use` (button appears, nothing spent); the Evercan could now be a `keep` tool if the pack ever rebuilds |
| L18 doors need Interact, docs stale | **fixed upstream**: docs now say Interact |
| L21 `handbok` read the wrong game's play | **fixed upstream**: pack-scoped, fails closed, cross-pack isolation pinned by a test |
| L4b/L22 *(not in this file)* | the bake/engine rule-mirrors drifted (`takes` dropped silently) and `refresh_living_tree` broke journal writes on fresh worlds — both found during the upstream pass and fixed there |

Remaining (no upstream change): L1 acts (ADR 0006), L2 one play
surface (ADR 0006), L3 the 40-rule budget (ADR 0004 proposes
scoped rules), L6 cosmetic verbs, L7 no NPC hand-over beyond
`takes` + `comes-near`, L8 one shop per region, L10 cosmetic tide,
L12 280-char say lines, L14 no live brain in that environment, L15
static journals, L20 the twin ghost sprite, and P2 dialogue state
(ADR 0005).
