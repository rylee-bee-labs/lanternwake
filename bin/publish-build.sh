#!/usr/bin/env bash
# Weave the current pack into one offline HTML file and post it to the dev gallery.
#   usage: bin/publish-build.sh            (build is named for the checked-out HEAD's short sha)
#          bin/publish-build.sh --dry-run  weave and record only; nothing is posted to the gallery
# Needs this machine's ssh key accepted by the gallery stage host (added 2026-10-02).
# VEFR_DIR picks the VEFR checkout that weaves it (default ~/code/Rylee-Bee/vefr). ~/.agents/bin/publish-build
# sets it to VEFR's origin/main, so a coordinator's build is exactly what merged (Rylee, 2026-10-09).
# The pack's own VEFR pin (VEFR_REF in .github/workflows/pack-check.yml, the engine its gate validates against)
# is the floor: the VEFR checkout must contain that commit, so a stale checkout cannot weave this game (studio#192).
# This repository IS the pack root. Modelled on cottage-of-the-breeze's bin/publish-build.sh.
set -euo pipefail
DRY=0
case "${1:-}" in
  "") ;;
  --dry-run) DRY=1 ;;
  *) echo "usage: bin/publish-build.sh [--dry-run]" >&2; exit 2 ;;
esac
ROOT="$(git rev-parse --show-toplevel)"
PACK="$ROOT"
SHA="$(git -C "$ROOT" rev-parse --short HEAD)"
VEFR="${VEFR_DIR:-$HOME/code/Rylee-Bee/vefr}"
PIN="$(sed -n 's/^ *VEFR_REF: *\([0-9a-f]\{40\}\).*/\1/p' "$ROOT/.github/workflows/pack-check.yml" | head -n 1)"
[ -n "$PIN" ] || { echo "publish-build: no VEFR_REF found in .github/workflows/pack-check.yml" >&2; exit 1; }
if ! { git -C "$VEFR" cat-file -e "$PIN^{commit}" 2>/dev/null && git -C "$VEFR" merge-base --is-ancestor "$PIN" HEAD; }; then
  echo "publish-build: the VEFR checkout at $VEFR ($(git -C "$VEFR" rev-parse --short HEAD)) does not include this pack's pin ${PIN:0:7}; fetch or update it" >&2
  exit 1
fi
OUT="$(mktemp -d)"
trap 'rm -rf "$OUT"' EXIT
chmod 755 "$OUT"   # mktemp makes 0700; the gallery copies the mode and nginx then cannot read it
( cd "$VEFR" && uv run python -c "
import sys; from pathlib import Path; from vefr import cli
Path(sys.argv[2], 'index.html').write_text(cli.weave_html(Path(sys.argv[1])))" "$PACK" "$OUT" )
[ -s "$OUT/index.html" ] || { echo "publish-build: the weave wrote no index.html" >&2; exit 1; }
# Reproducibility (cottage #75): record exactly which engine and pack revisions made this file.
VEFR_SHA="$(git -C "$VEFR" rev-parse --short HEAD)"
VEFR_DIRTY="$(git -C "$VEFR" status --porcelain --untracked-files=no | wc -l)"
PACK_DIRTY="$(git -C "$ROOT" status --porcelain --untracked-files=no | wc -l)"
printf 'lanternwake %s (uncommitted changes: %s)\nvefr %s (uncommitted changes: %s)\nvefr pin of this pack: %s\n' \
  "$SHA" "$PACK_DIRTY" "$VEFR_SHA" "$VEFR_DIRTY" "${PIN:0:7}" > "$OUT/build-info.txt"
echo "build: lanternwake $SHA, vefr $VEFR_SHA (pack pin ${PIN:0:7}), index.html $(wc -c < "$OUT/index.html") bytes"
if [ "$DRY" = 1 ]; then
  echo "dry run: nothing was posted to the gallery"
  exit 0
fi
GALLERY_BY=claude ~/.agents/bin/gallery build lanternwake "$OUT" --sha "$SHA"
