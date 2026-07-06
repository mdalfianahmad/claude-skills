#!/usr/bin/env bash
# render.sh DOCX OUTDIR
# Converts DOCX -> PDF (LibreOffice) and rasterizes every page to JPEG for QA.
# Verifies Scheherazade New actually embedded — if not, the Arabic fell back to a
# substitute (ornament becomes a box) and the render must not be trusted.
#
# IMPORTANT — how soffice is invoked (learned the hard way):
#   * ALWAYS go through the office helper's run_soffice(), which sets
#     SAL_USE_VCLPLUGIN=svp and an AF_UNIX LD_PRELOAD shim. Calling the raw
#     `soffice` binary directly hangs/dies on startup in this sandbox.
#   * Run it FOREGROUND with an internal timeout. Backgrounding (nohup/&) was
#     unreliable here — jobs vanished without output. Foreground + timeout works
#     (a cold start + convert completes in a few seconds).
set -euo pipefail

DOCX="${1:?usage: render.sh DOCX OUTDIR}"
OUTDIR="${2:?usage: render.sh DOCX OUTDIR}"
mkdir -p "$OUTDIR"

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OFFICE_DIR="/mnt/skills/public/docx/scripts/office"
PDF="$OUTDIR/$(basename "${DOCX%.docx}").pdf"

# 1. ensure font present (idempotent)
bash "$SKILL_DIR/setup_fonts.sh" >/dev/null

# 2. convert via the helper's run_soffice (reliable path), foreground + timeout
python3 - "$DOCX" "$OUTDIR" << 'PY'
import sys
sys.path.insert(0, "/mnt/skills/public/docx/scripts/office")
from soffice import run_soffice
docx, outdir = sys.argv[1], sys.argv[2]
r = run_soffice(["--headless", "--convert-to", "pdf", "--outdir", outdir, docx],
                capture_output=True, text=True, timeout=240)
if r.returncode != 0:
    sys.stderr.write("soffice failed: " + (r.stderr or "")[:300] + "\n")
    sys.exit(1)
PY

[ -f "$PDF" ] || PDF="$(ls -t "$OUTDIR"/*.pdf | head -1)"

# 3. verify font embedding
if pdffonts "$PDF" 2>/dev/null | grep -qi "ScheherazadeNew"; then
  echo "FONT OK: Scheherazade New embedded."
else
  echo "FONT ERROR: Scheherazade New NOT embedded — Arabic used a substitute." >&2
  echo "The ornament likely rendered as a box. Do not trust this render." >&2
  pdffonts "$PDF" >&2
  exit 1
fi

# 4. rasterize pages for visual QA
pdftoppm -jpeg -r 96 "$PDF" "$OUTDIR/page" >/dev/null
PAGES=$(pdfinfo "$PDF" | awk '/^Pages:/{print $2}')
echo "PDF: $PDF"
echo "Pages: $PAGES"
echo "Images: $OUTDIR/page-*.jpg"
echo "Next: python3 $SKILL_DIR/measure_fill.py \"$PDF\""
