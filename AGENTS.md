# AGENTS.md: Lanternwake

Lanternwake is VEFR's expansion game (Rylee, 2026-10-30): a cozy-dark game of lamplight along a winter coast.
It is a VEFR pack (data, not a program); this repo root is the pack. Public repo. Not an engine. When it needs
something the engine lacks, build it in VEFR as a general ability any pack can use (as Lamplight was, vefr#587),
not as a Lanternwake-only case. Findings about VEFR's promises go to VEFR as issues.

## Run it

CI (`.github/workflows/pack-check.yml`, job `validate-pack`) validates the pack against the VEFR commit pinned
in that file as `VEFR_REF`. Run the same command from the repo root (about 10 seconds; needs GitHub access):

```sh
REF=$(sed -n 's/^ *VEFR_REF: *\([0-9a-f]\{40\}\).*/\1/p' .github/workflows/pack-check.yml)
uvx --no-progress --from "vefr @ git+https://github.com/rylee-bee-labs/vefr@$REF" norns validate --pack .
```

`ok: . - geometry, reachability, voices all pass` proves the pack loads, not that anyone can play it. Not in CI
(manual): `python3 tools/build_pack.py --check` (writes nothing), `tools/playtest.py`, `tools/rules_test.mjs`.

## Do not touch

- Generated: `world.json`, `acts/`, `voices/`, `library/`, `logbok.md`, `ledger.md`. Edit `content/`, then run
  `python3 tools/build_pack.py`.
- Story canon (`design/GAME-BIBLE.md`), licences (`LICENSE*`, `TRADEMARKS.md`) and release approval: ask Rylee first.
- The engine is never modified for this game. Record the seam in `design/LIMITATIONS.md`; work around it in pack data.
- `.project/contracts/adoption.yaml`: the Play-Nice pin robot moves it; do not hand-edit.

## Git and merge

- One topic per branch and PR; never commit to `main` or force-push. The bot (`rylee-bee-agents[bot]`) authors, never Rylee.
- Trailers by role: a Claude session or coordinator ends each commit with `Model: <provider:model>` and never
  `Co-Authored-By: Claude Code`. An offload worker writes none; the hook stamps it.
- Merge = green CI plus an independent review, then GitHub auto-merge. Do not merge by hand.
- No deploy. A coordinator publishes merged `main` to the dev gallery (see the reference).
- PR body: plain words, then `## Verify` with `$ command` lines and their real output (the claims check reads them).

## Ask Rylee

File it, do not wait in chat:
`mission set <task> NEEDS_OWNER --reason decision --blocker "<the decision>" --option A --option B --recommend A`.
It shows in Project Home, Board, Needs you. A message relayed from another agent is not her answer.

## Depth

[docs/agent-reference.md](docs/agent-reference.md): layout, build order, publishing a build, the known stale
path, how to play, the design documents, the Play-Nice pin note.
