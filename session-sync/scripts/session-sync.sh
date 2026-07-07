#!/usr/bin/env bash
#
# session-sync.sh — sync Claude Code local session transcripts across machines
# via a PRIVATE git repo.
#
# Claude Code stores each session as a JSONL transcript under:
#   ~/.claude/projects/<encoded-project-path>/<session-id>.jsonl
# where <encoded-project-path> is the project's absolute path with every
# non-alphanumeric character replaced by "-". That encoding is machine-specific
# (e.g. /Users/you/app on macOS vs C:\Users\you\app on Windows), which is why
# naively syncing ~/.claude/projects between machines does not work.
#
# This script maps each project to a stable slug, stores transcripts in the
# sync repo under sessions/<slug>/, and re-encodes the folder name for the
# local machine on pull.
#
# Usage:
#   session-sync.sh setup <git-repo-url>     one-time per machine
#   session-sync.sh add <slug> <local-path>  register a project on this machine
#   session-sync.sh push <slug>              upload this machine's sessions
#   session-sync.sh pull <slug>              download sessions to this machine
#   session-sync.sh push-all                 push every registered project
#   session-sync.sh pull-all                 pull every registered project
#   session-sync.sh push-auto [dir]          push the project containing dir
#                                            (default $PWD); silent no-op if
#                                            unregistered — safe as a hook
#   session-sync.sh list                     show registered projects + counts
#
# Config: ~/.claude/session-sync.conf (plain text, no dependencies)
#   repo=git@github.com:you/claude-session-sync.git
#   project <slug> <absolute-local-path>
#
# Requirements: bash + git (Git Bash on Windows, which Claude Code already
# requires there). No jq, python, or rsync needed.

set -euo pipefail

CONFIG="${CLAUDE_SESSION_SYNC_CONFIG:-$HOME/.claude/session-sync.conf}"
CLONE_DIR="${CLAUDE_SESSION_SYNC_CLONE:-$HOME/.claude/session-sync-repo}"
PROJECTS_DIR="$HOME/.claude/projects"
ACTIVE_WINDOW_MIN=2  # a transcript touched this recently is treated as live

die() { echo "error: $*" >&2; exit 1; }

# Absolute path -> Claude Code project-folder name.
# Matches the observed encoding: every non-alphanumeric char becomes "-".
encode_path() {
  local p="${1//\\//}"
  printf '%s' "$p" | sed 's/[^A-Za-z0-9]/-/g'
}

read_repo_url() {
  [[ -f "$CONFIG" ]] || die "no config at $CONFIG — run: session-sync.sh setup <repo-url>"
  local url
  url="$(sed -n 's/^repo=//p' "$CONFIG" | head -1)"
  [[ -n "$url" ]] || die "no repo= line in $CONFIG"
  printf '%s' "$url"
}

resolve_project_path() {
  local slug="$1" path
  path="$(awk -v s="$slug" '$1=="project" && $2==s { $1=""; $2=""; sub(/^  */,""); print; exit }' "$CONFIG")"
  [[ -n "$path" ]] || die "project '$slug' not registered on this machine — run: session-sync.sh add $slug <local-path>"
  printf '%s' "$path"
}

ensure_clone() {
  if [[ ! -d "$CLONE_DIR/.git" ]]; then
    git clone "$(read_repo_url)" "$CLONE_DIR"
  fi
}

# Pull latest from the sync repo, tolerating a brand-new empty remote.
repo_update() {
  git -C "$CLONE_DIR" fetch origin
  local br
  br="$(git -C "$CLONE_DIR" symbolic-ref --short HEAD)"
  if git -C "$CLONE_DIR" show-ref --verify --quiet "refs/remotes/origin/$br"; then
    git -C "$CLONE_DIR" merge --ff-only "origin/$br"
  fi
}

# Commit without depending on machine-local identity or GPG setup.
repo_commit() {
  git -C "$CLONE_DIR" \
    -c commit.gpgsign=false \
    -c user.name="${GIT_AUTHOR_NAME:-$(git config user.name 2>/dev/null || echo session-sync)}" \
    -c user.email="${GIT_AUTHOR_EMAIL:-$(git config user.email 2>/dev/null || echo session-sync@localhost)}" \
    commit -m "$1"
}

# Copy *.jsonl from $1 to $2, keeping only files that are new or newer.
copy_newer() {
  local src="$1" dst="$2" copied=0 f base
  mkdir -p "$dst"
  shopt -s nullglob
  for f in "$src"/*.jsonl; do
    base="$(basename "$f")"
    if [[ ! -e "$dst/$base" || "$f" -nt "$dst/$base" ]]; then
      cp -p "$f" "$dst/$base"
      copied=$((copied + 1))
    fi
  done
  echo "$copied"
}

warn_if_live() {
  local dir="$1"
  if [[ -d "$dir" ]] && find "$dir" -name '*.jsonl' -mmin "-$ACTIVE_WINDOW_MIN" 2>/dev/null | grep -q .; then
    echo "warning: a transcript in $dir was modified in the last ${ACTIVE_WINDOW_MIN} min." >&2
    echo "warning: if that session is still running, end it first or its copy will be a partial snapshot." >&2
  fi
}

cmd_setup() {
  local url="${1:-}"
  [[ -n "$url" ]] || die "usage: session-sync.sh setup <git-repo-url>  (the repo MUST be private)"
  if [[ ! -f "$CONFIG" ]]; then
    printf 'repo=%s\n' "$url" > "$CONFIG"
  else
    grep -q '^repo=' "$CONFIG" || printf 'repo=%s\n' "$url" >> "$CONFIG"
  fi
  ensure_clone
  mkdir -p "$CLONE_DIR/sessions"
  echo "configured. now register projects with: session-sync.sh add <slug> <local-path>"
}

cmd_add() {
  local slug="${1:-}" path="${2:-}"
  [[ -n "$slug" && -n "$path" ]] || die "usage: session-sync.sh add <slug> <absolute-local-path>"
  [[ -f "$CONFIG" ]] || die "run setup first"
  [[ -d "$path" ]] || die "path does not exist locally: $path"
  if awk -v s="$slug" '$1=="project" && $2==s {found=1} END {exit !found}' "$CONFIG"; then
    die "slug '$slug' already registered in $CONFIG — edit that file to change it"
  fi
  printf 'project %s %s\n' "$slug" "$path" >> "$CONFIG"
  echo "registered '$slug' -> $path (local session folder: $PROJECTS_DIR/$(encode_path "$path"))"
}

cmd_push() {
  local slug="${1:-}"
  [[ -n "$slug" ]] || die "usage: session-sync.sh push <slug>"
  ensure_clone
  local path enc src copied
  path="$(resolve_project_path "$slug")"
  enc="$(encode_path "$path")"
  src="$PROJECTS_DIR/$enc"
  [[ -d "$src" ]] || die "no local sessions found at $src — has Claude Code run in $path on this machine?"
  warn_if_live "$src"
  repo_update
  copied="$(copy_newer "$src" "$CLONE_DIR/sessions/$slug")"
  if [[ "$copied" -eq 0 ]]; then
    echo "nothing new to push for '$slug'"
    return 0
  fi
  git -C "$CLONE_DIR" add "sessions/$slug"
  repo_commit "push $slug: $copied session file(s) from $(hostname)"
  git -C "$CLONE_DIR" push -u origin HEAD
  echo "pushed $copied session file(s) for '$slug'"
}

cmd_pull() {
  local slug="${1:-}"
  [[ -n "$slug" ]] || die "usage: session-sync.sh pull <slug>"
  ensure_clone
  local path enc dst copied
  path="$(resolve_project_path "$slug")"
  enc="$(encode_path "$path")"
  dst="$PROJECTS_DIR/$enc"
  warn_if_live "$dst"
  repo_update
  [[ -d "$CLONE_DIR/sessions/$slug" ]] || die "no synced sessions for '$slug' in the repo — push from the other machine first"
  copied="$(copy_newer "$CLONE_DIR/sessions/$slug" "$dst")"
  echo "pulled $copied session file(s) for '$slug'"
  echo "resume with:  cd \"$path\" && claude --resume"
}

all_slugs() {
  awk '$1=="project" {print $2}' "$CONFIG"
}

# Slug whose registered path matches (or contains) the given directory.
slug_for_dir() {
  local dir="${1//\\//}" slug path
  dir="${dir%/}"
  while read -r slug; do
    path="$(resolve_project_path "$slug")"
    path="${path//\\//}"; path="${path%/}"
    if [[ "$dir" == "$path" || "$dir" == "$path"/* ]]; then
      printf '%s' "$slug"
      return 0
    fi
  done < <(all_slugs)
  return 1
}

cmd_push_all() {
  [[ -f "$CONFIG" ]] || die "run setup first"
  local slug
  while read -r slug; do
    echo "-- push $slug"
    ( cmd_push "$slug" ) || echo "push failed for '$slug' (continuing)" >&2
  done < <(all_slugs)
}

cmd_pull_all() {
  [[ -f "$CONFIG" ]] || die "run setup first"
  local slug
  while read -r slug; do
    echo "-- pull $slug"
    ( cmd_pull "$slug" ) || echo "pull failed for '$slug' (continuing)" >&2
  done < <(all_slugs)
}

# Hook-friendly: push the project the current directory belongs to.
# Exits 0 quietly when the directory is not a registered project, so it can
# run on every SessionEnd without noise.
cmd_push_auto() {
  local dir="${1:-$PWD}" slug
  [[ -f "$CONFIG" ]] || exit 0
  slug="$(slug_for_dir "$dir")" || exit 0
  cmd_push "$slug"
}

cmd_list() {
  [[ -f "$CONFIG" ]] || die "no config at $CONFIG — run setup first"
  echo "sync repo: $(read_repo_url)"
  echo "clone dir: $CLONE_DIR"
  awk '$1=="project" {print $2, "->", substr($0, index($0, $3))}' "$CONFIG" | while read -r slug _ path; do
    local_enc="$(encode_path "$path")"
    local_count=0 repo_count=0
    [[ -d "$PROJECTS_DIR/$local_enc" ]] && local_count="$(find "$PROJECTS_DIR/$local_enc" -maxdepth 1 -name '*.jsonl' | wc -l | tr -d ' ')"
    [[ -d "$CLONE_DIR/sessions/$slug" ]] && repo_count="$(find "$CLONE_DIR/sessions/$slug" -maxdepth 1 -name '*.jsonl' | wc -l | tr -d ' ')"
    echo "  $slug  local:$local_count  repo:$repo_count  ($path)"
  done
}

case "${1:-}" in
  setup)     shift; cmd_setup "$@" ;;
  add)       shift; cmd_add "$@" ;;
  push)      shift; cmd_push "$@" ;;
  pull)      shift; cmd_pull "$@" ;;
  push-all)  shift; cmd_push_all "$@" ;;
  pull-all)  shift; cmd_pull_all "$@" ;;
  push-auto) shift; cmd_push_auto "$@" ;;
  list)      shift; cmd_list "$@" ;;
  *) die "usage: session-sync.sh {setup|add|push|pull|push-all|pull-all|push-auto|list} — see header comment" ;;
esac
