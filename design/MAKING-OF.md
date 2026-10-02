# MAKING-OF — the transcript of one game, written down

How LANTERNWAKE came to exist on October 1–2, 2026: one agent as
lead developer and creative director, VEFR as the engine, Kenney as
the art library, MiMo-v2.6-Flash as implementation partner. This is
the honest account — including the parts where the tooling lied to
me and the moments where the game is genuinely not fun.

Companion files: `WISHLIST.md` (what I'd want changed),
`LIMITATIONS.md` (engine seams, evidence-first), `PLAYTEST-LOG.md`
(the verification record), `ART.md`, `GAME-BIBLE.md`, `CONTENT-PLAN.md`.

---

## 1. What "a game on VEFR" actually means

The first lesson arrived before any code: a VEFR game is **a pack**,
not a program. The engine is finished; the creator's whole job lives
in data — maps, contracts, voices, fragments, books, items, rules.
"Learn VEFR through the resources provided to ordinary creators" meant
reading `GETTING_STARTED.md`, the journey map, `world-creation.md`,
`rulesets.md`, and the sample pack, then doing exactly what those
docs say: scaffold a pack under `worlds/`, validate constantly, weave
one file.

The second lesson: the engine's own documentation is a map of a
**living seam** between "what the docs promise" and "what the code
does today". I learned the pack contract faster by probing the code
than by reading the guides — and where the two disagreed, the code
won (see the doors story below). The project rule — *do not modify
the engine, record limitations instead* — turned out to be the most
educational constraint in the whole task. Every gap became a design
input instead of a patch.

## 2. The session, stop by stop

The studio's own journey turned out to be a good transcript skeleton.

**Desk (say what the game is).** The brief asked for ~40 hours of
meaningful play on an engine whose verbs are walk, talk, read, fight,
collect. The honest design move was to stop pretending the game would
be a systems game and lean into what VEFR uniquely does: a place that
reacts, voices that speak with no model, and a rumor engine. The
premise — a lamplighter re-lighting a winter coast while uncovering
why the bell drowned — was chosen because it makes the engine's
strongest systems *diegetic*: fog is the Hush, the light items are
the trade, the phases are the watches of one long night, and the
rules engine becomes "the world notices".

**Map room (the first place).** Maps were generated from a small
layout DSL in `tools/build_pack.py` — deterministic, re-editable,
and self-checking. My own flood-fill checker caught seven real
geometry breaks (a cat walled in by furniture, a door opening into a
grave, an island cut off from its own road) before the engine ever
saw the maps. Lesson: **write the checker before the content**; the
engine's validator is a gate, not a designer.

**Folks (the first people).** 27 characters, each a voice prompt, a
fragment bank and four watch-lines. This is where delegation began:
I wrote the exemplars (Marta the innkeeper, Moss the cat) and the
spec, and handed the other 25 to MiMo-v2.6-Flash. The returned work
was genuinely good — Grandmother Ash's "Truth is like reed smoke.
You breathe it or you lose it." went in unedited. Lesson: **one
exemplar is worth a page of instructions**, and the worker should
never be the one who decides if it passed.

**Library (books).** 50 documents, placed by hand in a plan table
(exact tiles, speakers, unlock conditions), written by three parallel
workers, verified by an acceptance script. I placed; they wrote. The
split held perfectly — placement needs the map, prose doesn't.

**Vault (things).** 25 items and their icons. Here the engine's
first real trap appeared: items can be **given** to the hero but
never taken away, and the Bag's Use button only exists for items
that heal or light — and using one *spends* it. My whole quest spine
had been built on "use the Evercan at the lamp". The fix changed the
game for the better: the Evercan is an heirloom that lights lamps
because you **walk up to them carrying it**. Never-spent tools are
now canon ("the ever-full can").

**Walk it (play).** Three verifications, in escalating strictness:
the engine validator, a jsdom harness that fires the game's own
rules engine at the real woven file, and a Playwright journey that
plays the game with keystrokes. The browser playtest found the
biggest doc/code disagreement in the project (doors), and the jsdom
harness proved the spine — lamps, once-only, the Beacon's five-lamp
condition, belief correction — without walking there. Lesson: **the
test that plays the game is the test that finds the game's bugs**;
the other two find the data's.

**Weave.** One 848 KB HTML file that plays with no server, no
model, no network. Watching Quill say two *different* things on two
playtest runs — from an offline fragment bank, no model — was the
moment the thing felt alive.

## 3. What I learned about the engine

1. **The seams are the design.** The 40-rule cap forced the story
   spine to be six lamps, five evidence beats and five corrections —
   a tighter game than the one I would have written with unlimited
   scripting.
2. **Offline-first is real.** Fragments + grammars + books carry a
   complete game. The model layer is decoration, not dependency. That
   is a genuinely unusual property for an AI-adjacent engine and it
   should be the headline of the pitch.
3. **The validator is a design partner.** It refuses unreachable
   people and unspeakable rules in plain sentences. It caught a dozen
   mistakes my own checker didn't.
4. **The docs drift in exactly one direction** — toward the older,
   gentler behavior ("doors are stepped on"; the `opens` call site
   that exists but is orphaned). Anyone making a pack should read the
   player code around their own mechanic before trusting a guide
   line. This is recorded, with evidence, in `LIMITATIONS.md`.
5. **Acts are the future, not the present.** Multi-act games can't
   ship yet; chapters have to live inside one act. (Recorded as L1.)

## 4. What I learned about making it

- **Verification stack beats verification ritual.** validate +
  rules-harness + playtest each caught different bugs. No one of them
  would have been enough.
- **The image tool in my own harness served stale renders.** Tiles
  were misidentified until I switched to ASCII pixel probes and pixel
  statistics. A mock room at real tile size — the studio's own art
  rule — caught four wrong tiles that looked plausible alone.
- **Delegation works when placement is separated from prose.** Five
  offload packets (27 voices, 50 books), zero content rewrites, one
  checker bug of mine that three workers all correctly diagnosed.
- **Generators pay for themselves.** The pack rebuilds from
  `content/` + `tools/` in one command; layout bugs were fixed once,
  in one place.

## 5. Was anything actually fun?

The question deserves a straight answer, so here is the honest
ledger, having played it through twice and watched it run:

**Yes, genuinely fun:**

- **Lighting the first lamp.** Walking up to the dark lamp with the
  can and having the narrator name the wick, a token fall in the bag,
  and the next region get a direction — that is a real beat, and the
  rule that does it fired correctly in every test, every time.
- **The world lying to you.** The whisper that came back in my first
  playtest was a barrow-keeper's rhyme flagged "A lie, or close
  enough." I laughed out loud. The truth-flag on whispers is the
  best small feature in the engine.
- **The writing.** Osric's fragments ("You may hate me and I will
  agree. It is the agreeing I am tired of."), Ferrylight's bell song,
  the Master who asks your name and gives none back. The players who
  like this game will like it because of sentences like these.
- **The cat.** "Mrrp." as a shipped, once-only, rule-fired beat that
  bookends the game. Small delight, exactly sized.
- **Being surprised by my own content.** Quill said different things
  on consecutive runs because the fragment composer re-splices. I
  wrote the banks and still got a new line.

**Not fun yet, honestly:**

- **Combat is busy-work.** Bump-mashing rats with 8 hp and no
  decisions: no positioning pressure that matters, no tool choice, no
  reason to fight anything you can walk around. The cozy death means
  there are no stakes, and the verbs beyond `attack` are words. For
  40 hours this needs either far fewer fights or fights that are
  puzzles.
- **Being lost.** There is no quest tracker and the journal records
  verbs, not goals. After the third lamp a player will not remember
  where the fifth lamp's POI is. The `point-to` hints help once per
  lamp; that is not a log.
- **The empty middle of the walk.** The fog is atmospheric and the
  towns are dense, but the between-places stretches are travel time
  with sparse content. The ring road is the right shape; the density
  is uneven.
- **The mystery is read, not played.** Holding an item and walking to
  a person *works* as delivery, but the fun of the Warden's story is
  the text, not the interaction. The moment of correction is a line,
  not a scene.

**The verdict I'd give a publisher:** it is a finished, beautiful
first act with a content engine behind it and one real weakness —
the verbs. The fun is discovery, voice and reactivity; the systems
are deliberately thin (the engine's law: failure bends the story).
At 40 hours it needs the world to change *shape* more often, not just
its lines.

## 6. What I'd do differently

1. Prototype one lamp-lighting beat before writing 50 books — the
   `uses-with` trap would have surfaced on day one and the spine
   design would have spent less time being rewritten.
2. Playtest in a browser from hour two, not at the end. The doors
   discovery changed how the playtest reads, and would have changed
   how the maps feel.
3. Trust the ASCII probe over the pretty picture, always.
4. Give every region one "thing that changes when you return" —
   reactivity beats density for keeping a walk from feeling empty.
