#!/usr/bin/env bash
#
# package.sh — zip a skill folder into an upload-ready .zip
#
# The resulting archive:
#   * has SKILL.md at the archive root (no nested top-level folder)
#   * contains no __MACOSX entries and no dot-files (.DS_Store, ._* forks, etc.)
#   * omits CHANGELOG.md (repo bookkeeping, not part of the skill payload)
#   * leaves SKILL.md frontmatter untouched
#
# Usage:
#   ./package.sh <skill-folder>          # -> dist/<skill-folder>.zip
#   ./package.sh <skill-folder> <out>    # -> <out> (path to a .zip)
#   ./package.sh --all                   # zip every skill folder into dist/
#
set -euo pipefail

# Prevent macOS from stashing AppleDouble (._*) / __MACOSX resource forks in zips.
export COPYFILE_DISABLE=1

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Files/patterns never included in a packaged skill.
zip_excludes=(
  '*/.*'          # dot-files in any subdirectory
  '.*'            # dot-files at the root
  '__MACOSX*'     # macOS resource-fork directory
  'CHANGELOG.md'  # repo-only bookkeeping
)

package_one() {
  local folder="$1" out="${2:-}"
  local name
  name="$(basename "$folder")"

  if [[ ! -d "$repo_root/$name" ]]; then
    echo "error: skill folder not found: $name" >&2
    return 1
  fi
  if [[ ! -f "$repo_root/$name/SKILL.md" ]]; then
    echo "error: $name has no SKILL.md — not a skill folder" >&2
    return 1
  fi
  # Sanity: SKILL.md must open with YAML frontmatter.
  if [[ "$(head -n1 "$repo_root/$name/SKILL.md")" != "---" ]]; then
    echo "error: $name/SKILL.md is missing its frontmatter (--- on line 1)" >&2
    return 1
  fi

  if [[ -z "$out" ]]; then
    mkdir -p "$repo_root/dist"
    out="$repo_root/dist/$name.zip"
  fi
  # Normalize to an absolute path so the trailing `cd` doesn't matter.
  case "$out" in
    /*) : ;;
    *)  out="$PWD/$out" ;;
  esac

  rm -f "$out"

  # Zip from *inside* the folder so paths are relative to the skill root
  # (SKILL.md, scripts/..., references/...) with no wrapping directory.
  ( cd "$repo_root/$name" && zip -r -X -q "$out" . -x "${zip_excludes[@]}" )

  echo "packaged $name -> $out"
}

main() {
  if [[ $# -eq 0 ]]; then
    echo "usage: ./package.sh <skill-folder> [output.zip]" >&2
    echo "       ./package.sh --all" >&2
    exit 1
  fi

  if [[ "$1" == "--all" ]]; then
    for dir in "$repo_root"/*/; do
      [[ -f "${dir}SKILL.md" ]] || continue
      package_one "$(basename "$dir")"
    done
    return
  fi

  package_one "$1" "${2:-}"
}

main "$@"
