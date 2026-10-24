# 2026-10-16 — Choices and consequences across the five-lantern journey

**2026-10-24 — Built:** Lanternwake#10 confirmed the pinned VEFR build ships the "Where next?" and "Why?" panels (`web/player/parts/030-shell.html:205-206`; `340-where-next-hints.js:70-119`; `510-rules-closure-surfaces.js:26-58`; `320-pack-rules.js:93-94,136-143`; `445-rules-engine.js:369`). The Causeway fork uses those panels through declared route regions rather than duplicating them. Its three approved player-facing lines are `status: draft` pending Rylee's final read; the fork now lives in the pack.

**Status: design proposal. Nothing here is canon, code, or approved
story text.** It is the first step of [lanternwake#8](https://github.com/rylee-bee-labs/lanternwake/issues/8)
under Rylee's owner ballot of 2026-10-16: gather evidence first, propose
a small content-only vertical slice with **one demonstrable
consequence**, then review before canon or wider rollout.

No rule, flag, line, item or map was added, changed or deleted to write
this file. Every count below was read out of this tree; every claim the
reader cannot re-derive is marked UNKNOWN with the check that would
settle it.

## 0. What this document is, and is not

It is:

- an inventory of the agency the pack **already** has, by rule id;
- three bounded options with their trade-offs, priced in rules;
- one smallest-first prototype proposal, for Rylee to accept or refuse
  before anyone writes a line of story;
- what we would play to decide whether the prototype is any good.

It is **not**:

- new canon. Every suggested line is marked `PLACEHOLDER — NOT CANON`;
- a goal tracker or objective panel (see §2, last bullet);
- an engine change. The engine is never patched for this game; gaps go
  to [vefr#452](https://github.com/rylee-bee-labs/vefr/issues/452).

## 1. Evidence: the agency this pack already has

Read from `world.json` (generated from `content/root.world.json` +
`tools/build_pack.py`); `python3 tools/build_pack.py --check` is green on
this tree.

| # | Lever the player already holds | Evidence in this tree |
|---|---|---|
| 1 | **The order of the five lamps.** Nothing in the rules requires an order. | `the-beacon-lights` gates only on `all-of` of the five `*-lit` flags. The five `light-the-*-lamp` rules carry no ordering condition. Only the `point-to` hint in each lamp's `then` implies an order (`light-the-causeway-lamp` → `saltreach`, etc.). |
| 2 | **The road taken.** 15 regions, free transitions. | `acts/act-1/` — 15 `contract.json` files; the deep floors are optional, nothing gates them. |
| 3 | **Who you carry a piece of truth to.** Five evidence items each gate one belief beat. | `aisling-believes` (`has: a-halfburnt-ledger`), `drennan-believes` (`has: the-wardens-seal`), `vetch-believes` (`has: a-saltstiff-letter`), `marta-believes` (`has: the-bell-rope`). Items cannot be handed over (L7), so "telling" *is* walking up carrying the thing. |
| 4 | **Who you ask.** Ten people in Thornhollow, five at Gullwatch, each with their own belief and their own four phase seeds. | `content/speakers.json` — every speaker carries `seeds` per phase plus a `voices/<name>.fragments.md` bank. |
| 5 | **What you buy, and where.** Marta, Orra and Lise keep the three trade points; gold starts at 8. | `content/speakers.json` — `shop: true` on `marta`, `orra`, `lise`; `player.gold: 8`. One shop per region, whole catalog priced (L8) — so order of spend is a choice today, and nothing notices. |
| 6 | **Whether you fight at all.** Cozy death, no gating. | `surface: "combat"`, `verbs: ["attack", "soothe"]`; L6 — Soothe is a printed line, not a mechanic. |

**The finding that matters most:** lever 1 is already free, and nothing
in the pack spends it. The five lamps can be lit in any order today and
the game is identical either way. That is the cheapest possible place to
buy a consequence, because the mechanic needs no engine help and no new
place for the player to go.

**A second free lever, found by reading the rule shape rather than the
story:** rules are `once: true` by default (L3), and a rule's `if`
accepts `{"flag": "x", "is": false}`. Two `comes-near` rules at two POIs
in the same region, each guarded by *the other* flag being false, are
**mutually exclusive in first-approach order**: walk to A first and B's
rule never fires. Read from the schema and from the pack's own
`if`/`flag` usage; **not yet run on the woven player** (no `norns`,
no `node`, no woven `dist/` in this sandbox — see §7).

## 2. What the pack cannot do, so nothing here is designed around air

| Seam | Consequence for a choice design | Ref |
|---|---|---|
| 40 rules flat, no chains, a rule fires at most once, no timers, no typed input, no `says` event | A choice cannot be a menu, a dialogue wheel or a timed decision. It has to be **walking somewhere or talking to someone**. | `design/LIMITATIONS.md` L3 |
| Items cannot be taken, given, equipped or spent | No "hand the rope to the Ferry", no "spend the token". Consequences must live in lines, flags and beliefs. | L7 |
| Beliefs are engine state, visible only in the why-log | Every branch needs its own `say`, or the player cannot tell the branch happened. | L9 |
| `RULE_SAY_LIMIT` 280 characters | Payoff lines must be short. A consequence is one line, not a scene. | L12 |
| **`the 40-rule budget is full.`** `world.json` carries 40 rules today; `CONTENT-PLAN.md` reserves 3 inside that 40 | Anything a choice costs must be **reclaimed**, or it does not land. See §4. | this tree |

Of the 40 rules, **10 are unconditional and `say`-only**
(`marta-welcome`, `causeway-tide`, `guildhall-ruin`, `whale-fall`,
`barrow-door`, `sea-cave`, `pip-calls`, `ferry-sings`, `ash-hints`,
`sef-sings`). Each of those people or places already speaks four phase
seeds from `content/speakers.json` — so reclaiming a rule costs one
authored line, not a character.

**Shipped-capability caution (from the issue, and it binds this doc).**
VEFR's first-independent-pack findings say a player-facing **Where
next?** panel (#192) and a **Why?** panel landed in the engine after
this game's wishlist was written. Whether the *pinned* Lanternwake
build consumes them is **UNKNOWN here** — this sandbox has no `norns`
and no engine checkout, and [lanternwake#10](https://github.com/rylee-bee-labs/lanternwake/issues/10)
owns that check. Therefore: **this proposal adds no objective list, no
goal HUD and no "what I owe" panel.** If the panel is live in the pinned
build, the fork below is read *through* it for free; if it is not, the
fork is still legible because both branches speak.

## 3. Three bounded options, priced

| | Option A — *Order of the lamps* | Option B — *One of two voices* | Option C — *Who you tell first* |
|---|---|---|---|
| **What the player does** | Lights a later lamp before an earlier one, on purpose | At one fork, approaches one of two people and not the other | Carries one evidence item past one believer to reach another |
| **New mechanic needed** | None — the freedom already exists | One mutual-exclusion flag pair | None |
| **Rules spent** | 2 (two gated payoffs) | 3 (two branches + one payoff) | 2–3 |
| **Canon risk** | Low: no new place, no new truth. Two alternate narrator lines. | Medium: one line each for two existing characters — new *text*, existing *people*. | Low: existing people, existing beliefs |
| **Engine risk** | Low: `if` + `flag` on an existing `comes-near` | Medium: relies on mutual exclusion behaving on the woven player (§1, §7) | Low |
| **Offline-safe?** | Yes — say + flag only | Yes | Yes |
| **What it cannot do** | It cannot make the player *feel* the order mattered — a changed narrator line is thin, and on a phone it may be missed | It cannot express a *refusal* — no way to say "I asked someone else", so the silent branch risks reading as a bug | It cannot punish delay, and a player who carries everything gets everything anyway |
| **Fights** | `MAKING-OF.md` §5 "the mystery is read, not played" | `WISHLIST.md` B3 return visits / reactivity | `WISHLIST.md` B4 mystery as scenes |

**Rejected, and why:** an item hand-over choice (spend the token, give
the rope) is the most satisfying shape and is impossible — L7. It goes
to vefr#452 as a limit, never as a patch here.

## 4. Smallest first prototype — proposal for owner review

**Option B, at the Causeway.** It is the first place the player must
decide where to go next (Toll-Yann on the road, Ferry at the slip), it
sits before the second lamp, and both characters already exist with
seeds, fragments and sprites. Two branch rules and one payoff rule.

Shape, in pack vocabulary only (`when` / `if` / `then` as they exist in
`content/root.world.json` today):

```
# rule 1 — the toll-keeper first
when: comes-near toll-yann
if:   flag heard-ferry-first is false
then: set heard-toll-yann-first
      say {who: toll-yann, line: PLACEHOLDER — NOT CANON}

# rule 2 — the crossing boy first
when: comes-near ferry
if:   flag heard-toll-yann-first is false
then: set heard-ferry-first
      say {who: ferry, line: PLACEHOLDER — NOT CANON}

# rule 3 — the one demonstrable consequence
when: comes-near the unlit ferry lamp        (i.e. inside light-the-ferry-lamp's beat)
if:   flag heard-toll-yann-first is true
then: say PLACEHOLDER — NOT CANON              # Toll-Yann's account of the lamp instead of the default line
```

Plus two flag declarations in `content/root.world.json`:
`heard-toll-yann-first`, `heard-ferry-first`.

**Budget arithmetic, so this is not a promise the CI will break:**

- 3 rules spent, 3 reclaimed from the unconditional say-only ten
  (recommend `pip-calls`, `ferry-sings`, `ash-hints` — all three
  characters keep their four phase seeds; the reclaimed text is three
  authored lines).
- 40 − 3 + 3 = **40**. Net zero against `maplab.RULE_LIMIT`.

**Deliberately left out of v1 of the prototype:** the return-visit
half. A second visit to Toll-Yann needs a *second* rule instance
because rules fire once (L3), so the return payoff is the next
increment (+2 rules, and two more reclaimed lines), not this one. The
prototype's whole claim is that one consequence is legible; if it is
not, the return-visit work is the wrong thing to build on top of it.

**What is NOT canon in this sketch:** every line of player-facing text
above. Writing them is Rylee's call, not this document's.

## 5. How we would know whether it worked

The prototype is only worth landing if a consequence is *perceived*.
Proposed evidence, in the order we would run it:

1. **Two fresh runs, same build, no scripting.** Divergent transcripts
   at the Causeway fork; the payoff line appears in exactly one run per
   route. Reproducible by hand; recorded in `design/PLAYTEST-LOG.md`.
2. **The documented loss point.** `MAKING-OF.md` §5 records players
   getting lost after the third lamp. Watch for the stall *after* the
   fork: does the player still know the next lamp? That is the friction
   location #8 asks for, and it is observable with a notebook.
3. **Phone and desktop, exploratory, with notes** — not rules-engine
   tests. The silent branch is exactly the thing that reads as a bug on
   a small screen; that has to be watched, not asserted.
4. **Rules-harness assertions** (jsdom, `tools/rules_test.mjs`): mutual
   exclusion holds; the payoff rule fires only on the gated route.
   Needs a woven `dist/*.html`; this sandbox has neither `node` nor a
   weave, so this check is written here and not yet run (§7).
5. **Duration wording.** The ~40 hours stays a **design target** from
   `CONTENT-PLAN.md` and is **not measured** (`PLAYTEST-LOG.md`, "Honest
   gaps"). No document produced from this line may state it as a
   verified duration.

## 6. What Rylee has to decide before anything lands

1. Approve or refuse the Causeway fork as the vertical slice (§4).
2. Approve any player-facing line before it is written into
   `content/` — canon is the owner's, per the ballot.
3. Agree that reclaiming `pip-calls`, `ferry-sings`, `ash-hints` is an
   acceptable trade for three choice rules.
4. Confirm the #10 result first: if the pinned build ships a usable
   "Where next?" panel, the fork should be tuned against it rather
   than around it.
5. Keep engine limits in vefr#452 — no engine patch from this repo.

## 7. UNKNOWNs at time of writing

| Unknown | Why it is unknown here | What would settle it |
|---|---|---|
| Whether the pinned Lanternwake build exposes the #192 **Where next?** / **Why?** panels | No `norns`, no VEFR checkout in this sandbox; the pack's own AGENTS.md pins the engine at CI time only | #10, against the pinned build |
| Whether `comes-near` mutual exclusion (`flag is false` guards) behaves as read on the woven player | The schema supports it and this pack uses both shapes, but no woven file exists here and neither `node` nor a `dist/` build is available | Two jsdom assertions in `tools/rules_test.mjs` after a weave |
| Whether a *silent* unchosen branch reads as intent or as a bug to a phone player | Requires human play | Exploratory phone session (§5.3) |
| Measured completionist playtime | Never measured; the 40 hours are a content-ledger target | A full playthrough. Until then: **target** |

## 8. Traceability

- Evidence in this file is read from `world.json` / `content/root.world.json`,
  `content/speakers.json`, `acts/act-1/*/contract.json`,
  `design/MAKING-OF.md`, `design/WISHLIST.md`, `design/CONTENT-PLAN.md`,
  `design/PLAYTEST-LOG.md`, `design/LIMITATIONS.md`, `AGENTS.md`.
- Local gate run for this file: `python3 tools/build_pack.py --check` —
  green (10 hand regions ok). `norns validate --pack .` could not be
  run in this sandbox (no `norns`); CI runs it at the pinned VEFR SHA.
- This file is proposal-only: no canon, no code, no rule, no flag.
