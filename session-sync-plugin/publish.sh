#!/usr/bin/env bash
#
# publish.sh — assemble the session-sync plugin tree and push it to its
# public GitHub repo.
#
# The skill's single source of truth is ../session-sync in this repo; this
# script copies it into skills/session-sync/ of the plugin repo at publish
# time, so the plugin can never drift from the skill.
#
# plugin.json intentionally has no "version" field: Claude Code then treats
# every commit as a new version, so users get updates on every publish
# (via /plugin marketplace update) without manual version bumps.
#
# Usage:
#   ./publish.sh <public-repo-url>    # clone, assemble, commit, push
#   ./publish.sh --dry-run [dir]      # assemble only (default: temp dir), no git
#
# Requires rsync (present on macOS/Linux). Run from the maintainer machine.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_src="$here/../session-sync"

die() { echo "error: $*" >&2; exit 1; }

[ -f "$skill_src/SKILL.md" ] || die "skill source not found at $skill_src"

assemble() {
  local dest="$1"
  mkdir -p "$dest/.claude-plugin" "$dest/skills"
  cp "$here/.claude-plugin/plugin.json" "$here/.claude-plugin/marketplace.json" \
    "$dest/.claude-plugin/"
  cp "$here/README.md" "$here/LICENSE" "$dest/"
  rm -rf "$dest/skills/session-sync"
  rsync -a --exclude='.*' "$skill_src/" "$dest/skills/session-sync/"
}

case "${1:-}" in
  --dry-run)
    dest="${2:-$(mktemp -d)/session-sync-plugin}"
    assemble "$dest"
    echo "assembled at: $dest"
    ;;
  "")
    die "usage: publish.sh <public-repo-url> | publish.sh --dry-run [dir]"
    ;;
  *)
    url="$1"
    work="$(mktemp -d)"
    git clone --depth 1 "$url" "$work/repo"
    # Never publish into a transcript sync repo: those are PRIVATE and hold
    # sessions/<slug>/*.jsonl. The plugin repo must be a different, public repo.
    [ -d "$work/repo/sessions" ] && die \
      "target has a sessions/ dir — looks like a private transcript sync repo, refusing"
    assemble "$work/repo"
    git -C "$work/repo" add -A
    if git -C "$work/repo" diff --cached --quiet; then
      echo "nothing to publish — plugin repo already up to date"
      exit 0
    fi
    git -C "$work/repo" -c commit.gpgsign=false commit -m "publish session-sync plugin"
    git -C "$work/repo" push origin HEAD
    echo "published to $url"
    ;;
esac
