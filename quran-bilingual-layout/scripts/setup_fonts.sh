#!/usr/bin/env bash
# Install "Scheherazade New" so LibreOffice renders the Arabic correctly.
# Idempotent: safe to run every session. The Arabic WILL silently fall back to a
# substitute font (boxes/tofu for the U+06DD ornament) if this font is missing,
# so this must run and succeed before any render.
#
# NOTE: the docx asks for the family "Scheherazade New" (with "New"). The older
# "Scheherazade" (no New) is a DIFFERENT family name and will NOT satisfy the cs
# font lookup — install the New TTFs specifically.
set -uo pipefail   # not -e: we handle failures explicitly so a transient
                   # fontconfig miss does not abort the caller.

# fontconfig in this sandbox sometimes returns an empty list on the first call
# of a fresh process. So treat the font as present if EITHER fontconfig sees it
# OR the TTF files are on disk (the definitive check). Prime the cache first.
have_files() { [ -s "$HOME/.fonts/ScheherazadeNew-Regular.ttf" ] \
            && [ -s "$HOME/.fonts/ScheherazadeNew-Bold.ttf" ]; }
have_fc()    { fc-list 2>/dev/null | grep -qi "scheherazade new"; }
check()      { have_files || have_fc; }

fc-cache -f >/dev/null 2>&1 || true
if check; then
  echo "Scheherazade New already installed."
  exit 0
fi

mkdir -p "$HOME/.fonts"
BASE="https://github.com/google/fonts/raw/main/ofl/scheherazadenew"
for w in Regular Bold; do
  f="$HOME/.fonts/ScheherazadeNew-$w.ttf"
  if [ ! -s "$f" ]; then
    echo "Downloading ScheherazadeNew-$w.ttf ..."
    curl -fsSL "$BASE/ScheherazadeNew-$w.ttf" -o "$f" || {
      echo "WARN: download of $w failed; will retry cache rebuild anyway." >&2
    }
  fi
done

# Rebuild cache up to twice — fontconfig sometimes needs a second pass to see
# newly dropped files in this environment.
for _ in 1 2 3; do
  fc-cache -f >/dev/null 2>&1 || true
  check && { echo "Scheherazade New installed OK."; exit 0; }
  sleep 1
done

echo "ERROR: Scheherazade New still not visible to fontconfig." >&2
echo "Without it, Arabic renders with a substitute and the ornament breaks." >&2
echo "Files present in ~/.fonts:" >&2
ls -la "$HOME/.fonts" >&2 || true
exit 1
