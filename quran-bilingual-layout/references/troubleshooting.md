# Troubleshooting — environment failures and how the scripts handle them

Hard-won notes from building and running this skill. Most of these are about the
render environment, not the document logic.

## soffice (LibreOffice) hangs, dies, or produces no output

Symptoms seen: `soffice --version` never returns; conversions hang forever;
background render jobs vanish without writing a PDF or any log.

Root cause: the raw `soffice` binary does not start cleanly in this sandbox. It
needs two things the helper supplies:
- `SAL_USE_VCLPLUGIN=svp` (headless graphics backend), and
- an `AF_UNIX` socket `LD_PRELOAD` shim.

Fixes baked into `render.sh`:
- ALWAYS invoke via the office helper's `run_soffice()` (it sets the env). Never
  call the raw `soffice` binary directly.
- Run FOREGROUND with an internal `timeout=` argument. Do NOT background it with
  `nohup`/`&` — backgrounded jobs were unreliable here and produced no output.
- A correct cold start + convert of the full surah completes in a few seconds.

If you still get "source file could not be loaded", the input path is wrong or
the docx was cleaned up — rebuild it and retry.

## Arabic renders as empty boxes (tofu), or pdffonts shows a substitute

Cause: Scheherazade New not embedded. Either the font is missing, or the Arabic
runs lack `w:cs="Scheherazade New"` (see encoding-spec.md — `cs` is the slot that
matters for rtl text). `render.sh` runs `pdffonts` and FAILS LOUDLY if the font
is not embedded; do not trust a render that failed this check.

## fontconfig intermittently reports the font missing

Symptom: `fc-list | grep scheherazade` returns nothing on the first call of a
fresh process, even though the TTFs are installed — then succeeds on a later
call. fontconfig in this sandbox is flaky on cold cache.

Fix in `setup_fonts.sh`: the presence check accepts EITHER fontconfig seeing the
font OR the TTF files existing on disk (`have_files`), primes `fc-cache` before
checking, and retries the cache rebuild up to 3 times. The on-disk check is the
definitive one; fc-list is treated as advisory.

## Bash commands return -1 / empty output mid-session

The execution tool can time out or return nothing when a command (especially a
soffice cold start) runs long, or when the sandbox is under load. This is not a
bug in the skill. Mitigations: use the foreground+timeout soffice path above;
keep individual commands short; if a step returns nothing, re-run it rather than
assuming it failed silently. Basic commands (`echo`, `python3 -c`) returning
instantly while only soffice fails is the signature of this.

## A fresh sandbox is missing Pillow

`measure_fill.py` needs Pillow. Install once per session:
`pip install Pillow --break-system-packages`.
