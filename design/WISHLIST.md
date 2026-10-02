# WISHLIST — problems hit, and what I wish existed

Two lists: what the **engine** should grow (for VEFR's keepers —
each already evidenced in `LIMITATIONS.md` by number), and what
**Lanternwake itself** still wants. Ordered by how much each would
change the game.

## A. Engine wishes (impact order)

1. **A goal/journal surface for players.** Nothing tracks what the
   hero has decided to do; the journal logs verbs. One "what I owe"
   list — even just the `point-to` hints kept in a panel — would cut
   the biggest real play problem (getting lost) in half. *This is the
   single highest-value feature on this list.*
2. **Quest-tool support** (L7, L17): items that can be *spent* or
   *handed over* on purpose — a `takes`/`gives` action pair, or an
   item flag like `"keep": true` that enables Use without spending.
   Today a delivery quest and a consumed resource are both
   impossible; the game canonized "the ever-full can" to survive it.
3. **More events for the rules engine** (L3, L4): `opens` actually
   firing (its call site is orphaned), plus `defeats` (an enemy
   dies), `buys`/`sells`, `reads` (a book closed), `phase-changes`.
   With those six added, a 40-hour game's reactivity triples inside
   the same 40-rule budget.
4. **Acts that advance** (L1) and **more than one play surface per
   game** (L2). A cooking chapter *between* two walking chapters is
   the game this engine almost has; right now each game must choose
   one loop.
5. **Dialogue state** — seed lines keyed not only to phase but to
   flags ("marta: once the Beacon is lit"), or simply a second seed
   table read when a named flag is set. Characters currently have one
   voice per watch forever; the rules `say` beats carry all the
   change.
6. **A rule budget that scales or nests** (L3): 40 flat rules with
   no chains is fine for a spine and thin for a world. A per-region
   allowance, or `once: per-visit`, would let side content breathe.
7. **A hero-facing "why?" panel** (the design doc already proposes
   it): the `VEFR_WHY` log exists in the player but nothing shows it.
   Players would love "why did the fog lift?" — it would also market
   the rules engine, which is the engine's best-kept secret.
8. **Fix the docs where they drifted** (L13, L18): "doors are stepped
   on" (they need Interact), and the orphaned `opens` call site named
   in ROADMAP as if live. Both cost me real design time.
9. **`handbok` scoped by pack** (L21): it printed another game's
   title and numbers into this pack's manual. Neutrality guard
   spirit: no other world's name should appear in a pack's file.
10. **Rule event payloads that match the runtime** (L5): the validator
    rejects POI labels and distance 0 that the runtime actually sends.
    Either accept POI labels as things or fire person-shaped events.

## B. What the game itself still wants

1. **A reason to fight** — enemies guard nothing today (chest access
   isn't gated). Either give the cozy combat a purpose (a toll, a
   pressure, a reward you can't walk to) or shrink it to set-pieces:
   the Warden, the mimic, and one or two ambushes.
2. **Movement toys** — the light system is the game's best mechanic
   and it barely matters outside fog. Torches that *open* dark rooms
   containing something, a lantern radius progression, tide-timed
   crossings (the flood is cosmetic; the engine forbids timers, so
   this would need a rules event on phase change).
3. **Return visits that change** — one flag-driven second line per
   townsperson, one altered scene per region after the lamp lights.
   Reactivity, not more map.
4. **The mystery as scenes** — the five corrections are single
   lines. Two-beat conversations (accuse → confess) would make the
   Warden's arc land as drama rather than as a log entry.
5. **An ending with weight** — the Beacon lighting is one paragraph.
   A walk back through the lit coast (the engine's phases make this
   free: first-light + every lamp flag) and a closing letter from
   Marta (the `stefna` voice already exists) would end the game like
   the game ends its chapters.
6. **More small delights of the Moss class** — the cat-sized beats
   are the cheapest joy in the whole build and there are only four.

## C. Tooling wishes

1. A `vefr pack new` scaffold that emits the generator-friendly shape
   (content/ + tools/) instead of a flat pack to hand-edit.
2. `norns validate --play` : one command that runs a pack's own
   playtest harness if it has one.
3. An art import verb (`vefr art import --pack ... --from kenney`)
   with the identify-by-looking step built in as labelled contact
   sheets — the whole art pipeline was mine to write (fine!) but
   every pack will write it again.
