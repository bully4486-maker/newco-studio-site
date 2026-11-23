#!/usr/bin/env bash
# Pack renderer for simple box reuse (source + README + tests + preview if present).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
NAME="newco-social-renderer-${STAMP}.zip"
ART_DIR="/opt/cursor/artifacts"
if [[ -d "$ART_DIR" ]]; then
  OUT="$ART_DIR/$NAME"
else
  mkdir -p "$ROOT/archive"
  OUT="$ROOT/archive/$NAME"
fi
cd "$ROOT"
zip -r "$OUT" \
  README.md requirements.txt cli.py \
  lib templates samples fixtures tests scripts \
  vendor_assets \
  -x 'out/*' '.cache/*' '**/__pycache__/*' '**/*.pyc' '.pytest_cache/*' 'archive/*' \
  'vendor_assets/counter_book_ref/*.png'
# Include preview PNGs if already rendered
if [[ -d out ]]; then
  zip -r "$OUT" out -i '*.png' -x '*_stills/*' || true
fi
echo "WROTE $OUT"
ls -lh "$OUT"
