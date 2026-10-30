# 2026-10-16 — Choices and consequences across the five-lantern journey

**2026-10-24 — Built as draft:** Lanternwake#10 confirmed the pinned VEFR build ships the "Where next?" and "Why?" panels in [rylee-bee-labs/vefr](https://github.com/rylee-bee-labs/vefr) at `72d366e731f5e4c286269928089cc35da96202f8`, the pin in `.github/workflows/pack-check.yml` (`web/player/parts/030-shell.html:205-206`; `web/player/parts/340-where-next-hints.js:70-119`; `web/player/parts/510-rules-closure-surfaces.js:26-58`; `web/player/parts/320-pack-rules.js:93-94,136-143`; `web/player/parts/445-rules-engine.js:369`). The Causeway fork uses those panels through declared route regions rather than duplicating them. Its three approved player-facing lines are draft pending Rylee's final read (the pack format has no draft marker, so the status is recorded here and in PR #36, not in the pack); the fork now lives in the pack as draft. This file remains a design proposal and is not canon.

**Status: design record. The fork is built as draft in the pack; this
file is not canon, and its player-facing lines remain draft.** It records
the first step of [lanternwake#8](https://github.com/rylee-bee-labs/lanternwake/issues/8)
under Rylee's owner ballot of 2026-10-16: gather evidence first, propose
a small content-only vertical slice with **one demonstrable
consequence**, then review before canon or wider rollout.

The original proposal predates the draft implementation recorded below.
Every count below was read out of this tree; unresolved claims are marked
UNKNOWN with the check that would settle them.

## 0. What this document is, and is not

It is:

- an inventory of the agency the pack **already** has, by rule id;
- three bounded options with their trade-offs, priced in rules;
- the smallest-first draft implementation and its evidence;
- what we would play to decide whether the prototype is any good.

It is **not**:

- new canon. The fork's three approved lines are draft pending the
  owner's final read;
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
story:** the two `comes-near` rules are tied to Toll-Yann and the ferry
lamp, each with radius one, and each checks the other flag is false.
Walking up to either trigger first sets one branch and excludes the other.
The manual jsdom harness exercises both orders (see §5 and §7).

## 2. What the pack cannot do, so nothing here is designed around air

| Seam | Consequence for a choice design | Ref |
|---|---|---|
| 40 rules flat, no chains, a rule fires at most once, no timers, no typed input, no `says` event | A choice cannot be a menu, a dialogue wheel or a timed decision. It has to be **walking somewhere or talking to someone**. | `design/LIMITATIONS.md` L3 |
| Items cannot be taken, given, equipped or spent | No "hand the rope to the Ferry", no "spend the token". Consequences must live in lines, flags and beliefs. | L7 |
| Beliefs are engine state, visible only in the why-log | Every branch needs its own `say`, or the player cannot tell the branch happened. | L9 |
| `RULE_SAY_LIMIT` 280 characters | Payoff lines must be short. A consequence is one line, not a scene. | L12 |
| **`the 40-rule budget is full.`** `world.json` carries 40 rules today; `CONTENT-PLAN.md` reserves 3 inside that 40 | Anything a choice costs must be **reclaimed**, or it does not land. See §4. | this tree |

Of the 40 rules, **7 are unconditional and `say`-only**
(`marta-welcome`, `causeway-tide`, `whale-fall`, `barrow-door`,
`sea-cave`, `ash-hints`, `sef-sings`). Each of those people or places
already speaks four phase seeds from `content/speakers.json` — so the
three retired rules cost authored lines, not characters.

**Shipped-capability check:** Lanternwake#10 confirmed that the pinned
build at `72d366e731f5e4c286269928089cc35da96202f8` in
[`rylee-bee-labs/vefr`](https://github.com/rylee-bee-labs/vefr), pinned by
`.github/workflows/pack-check.yml`, ships the player-facing **Where
next?** and **Why?** panels. The Causeway fork is legible through those
panels, and both branches speak.

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

## 4. Causeway fork — built as draft

**Option B, across the Causeway road and the ferry lamp above Saltreach.** It is the first place the player must
decide where to go next (Toll-Yann on the Causeway road, or the ferry lamp above Saltreach), it
sits before the second lamp, and both characters already exist with
seeds, fragments and sprites. Two branch rules and one payoff rule.

The built fork uses two separate radius-one triggers so either is
reachable first from the normal entrance. Toll-Yann is on the Causeway
road; the ferry lamp is above Saltreach. It is recorded as draft in
`content/root.world.json`:

```
# rule 1 — the toll-keeper first
when: comes-near toll-yann (distance 1)
if:   flag heard-ferry-first is false
then: set heard-toll-yann-first
      say the approved draft Toll-Yann line

# rule 2 — the crossing boy first
when: comes-near the unlit ferry lamp (distance 1)
if:   flag heard-toll-yann-first is false
then: set heard-ferry-first
      say the approved draft Ferrylight Oku line

# rule 3 — the one demonstrable consequence
when: comes-near the unlit ferry lamp        (i.e. inside light-the-ferry-lamp's beat)
if:   flag heard-toll-yann-first is true
      flag the-ferry-lamp-lit is true
then: say the draft Toll-Yann account of the lamp
```

Plus two flag declarations in `content/root.world.json`:
`heard-toll-yann-first`, `heard-ferry-first`.

**Budget arithmetic:**

- 3 rules spent, 3 reclaimed from unconditional say-only rules:
  `ferry-sings`, `pip-calls`, and `guildhall-ruin`. `ash-hints` remains
  live; the characters retain their phase seeds.
- 40 − 3 + 3 = **40**. Net zero against `maplab.RULE_LIMIT`.

**Deliberately left out of this draft:** the return-visit
half. A second visit to Toll-Yann needs a *second* rule instance
because rules fire once (L3), so the return payoff is the next
increment (+2 rules, and two more reclaimed lines), not this one. The
prototype's whole claim is that one consequence is legible; if it is
not, the return-visit work is the wrong thing to build on top of it.

The three approved lines in the pack remain draft pending Rylee's final
read. This design file is not canon.

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
4. **Rules-harness assertions** (jsdom, `tools/rules_test.mjs`): both
   orders set exactly one branch, only the Toll-Yann route gets the
   payoff, and the default ferry-lamp rule still lights the lamp on both
   routes. Run by hand with a woven `dist/*.html`.
5. **Duration wording.** The ~40 hours stays a **design target** from
   `CONTENT-PLAN.md` and is **not measured** (`PLAYTEST-LOG.md`, "Honest
   gaps"). No document produced from this line may state it as a
   verified duration.

## 6. What Rylee has to decide before anything lands

1. Give the three draft player-facing lines a final read before canon.
2. Keep engine limits in vefr#452 — no engine patch from this repo.

## 7. UNKNOWNs at time of writing

| Unknown | Why it is unknown here | What would settle it |
|---|---|---|
| Whether the pinned Lanternwake build exposes the #192 **Where next?** / **Why?** panels | Answered by Lanternwake#10 against the pinned VEFR source | `rylee-bee-labs/vefr` at `72d366e731f5e4c286269928089cc35da96202f8`, `.github/workflows/pack-check.yml`: `web/player/parts/030-shell.html:205-206`; `web/player/parts/340-where-next-hints.js:70-119`; `web/player/parts/510-rules-closure-surfaces.js:26-58`; `web/player/parts/320-pack-rules.js:93-94,136-143`; `web/player/parts/445-rules-engine.js:369` |
| Whether `comes-near` mutual exclusion (`flag is false` guards) behaves as read on the woven player | **OPEN:** the manual jsdom harness exists and asserts both route orders, but has never been run against a build. It requires a woven `dist/*.html` and `jsdom`; CI deliberately excludes it. | Weave a build with pinned VEFR `72d366e731f5e4c286269928089cc35da96202f8`; run `npm i jsdom`; then `node tools/rules_test.mjs <build>` |
| Whether a *silent* unchosen branch reads as intent or as a bug to a phone player | Requires human play | Exploratory phone session (§5.3) |
| Measured completionist playtime | Never measured; the 40 hours are a content-ledger target | A full playthrough. Until then: **target** |

## 8. Traceability

- Evidence in this file is read from `world.json` / `content/root.world.json`,
  `content/speakers.json`, `acts/act-1/*/contract.json`,
  `design/MAKING-OF.md`, `design/WISHLIST.md`, `design/CONTENT-PLAN.md`,
  `design/PLAYTEST-LOG.md`, `design/LIMITATIONS.md`, `AGENTS.md`.
- Local gate run for this file: `python3 tools/build_pack.py --check` —
  green (10 hand regions ok). `norns validate --pack .` could not be
  run in this sandbox (no `norns`); CI runs only `norns validate --pack .`.
- The fork is built as draft in the pack. This file remains non-canon.
