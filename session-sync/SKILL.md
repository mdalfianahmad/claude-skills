---
name: session-sync
description: Sync Claude Code session transcripts between machines (macOS, Windows, Linux) through the user's own private git repo, so a session started on one machine can be resumed on another with claude --resume. Trigger when the user says "sync my sessions", "push this session", "pull my sessions", "pick up this session on my other machine/laptop", "continue this session on Windows/Mac", or asks how to move a local Claude Code session between devices. Handles the machine-specific ~/.claude/projects folder-name encoding automatically. This is a workaround for local CLI sessions only — it does not upload anything to Anthropic's cloud; for cloud-native sessions point the user to claude.ai/code, claude --cloud, or claude --teleport instead.
---

# Session Sync

Claude Code stores every local session as a JSONL transcript at
`~/.claude/projects/<encoded-project-path>/<session-id>.jsonl`. The folder name
encodes the project's **absolute path on that machine** (every non-alphanumeric
character becomes `-`), so transcripts are not portable between machines as-is.
There is no official way to push a local session to Anthropic's cloud.

This skill makes local sessions portable anyway: it syncs the transcript files
through a **private git repo owned by the user**, keyed by a stable per-project
slug, and re-encodes the folder name for whichever machine pulls them. After a
pull, `claude --resume` on the second machine lists the session with full
history.

All operations go through `scripts/session-sync.sh` (bash + git only; on
Windows run it from Git Bash, which Claude Code already requires).

## Non-negotiable safety rules

1. **The sync repo must be private.** Transcripts contain the user's code,
   file contents, and possibly secrets. Before setup, confirm the repo is
   private (`gh repo view <repo> --json isPrivate`). Refuse to sync to a
   public repo.
2. **Never sync a live session.** Pushing while a session is running captures
   a partial transcript; pulling over a running session can corrupt it. The
   script warns when a transcript was modified in the last 2 minutes — stop
   and tell the user to end the session first.
3. **Sync is manual, not continuous.** Do not wire this into a file-watcher or
   cloud-drive folder; concurrent writes from two machines are exactly the
   corruption case this design avoids.

## One-time setup (per machine)

1. Ask the user for (or help create) a **private** git repo, e.g.
   `gh repo create claude-session-sync --private`.
2. Run: `bash <skill-dir>/scripts/session-sync.sh setup <repo-url>`
3. Register each project the user wants to sync, using the **same slug on
   every machine** but that machine's local path:
   - macOS: `session-sync.sh add myapp /Users/alfian/myapp`
   - Windows (Git Bash): `session-sync.sh add myapp "C:/Users/alfian/myapp"`

Config lives at `~/.claude/session-sync.conf`; the repo clone at
`~/.claude/session-sync-repo`.

## Everyday flow

- **Leaving machine A:** end the session, then
  `session-sync.sh push <slug>`.
- **Arriving at machine B:** `session-sync.sh pull <slug>`, then
  `cd <project> && claude --resume` and pick the session.
- **Check state:** `session-sync.sh list` shows local vs repo session counts
  per project.

The project's *code* is not carried by this skill — remind the user to
commit/push the repo itself (or sync files) so machine B matches machine A's
working state; the transcript only carries the conversation.

## Troubleshooting

- **Session doesn't appear in `claude --resume`:** the encoded folder name may
  not match. Verify ground truth: start and immediately exit a throwaway
  session in that project on the affected machine, then `ls -t
  ~/.claude/projects | head -1` to see the real folder name. If it differs
  from what `session-sync.sh list` prints for that project, the registered
  path is wrong (wrong case, trailing slash, or symlinked path) — fix the
  `project` line in `~/.claude/session-sync.conf` to the exact path Claude
  Code runs in.
- **Push says "nothing new":** transcripts are compared by mtime; the repo
  already has the latest copies.
- **Merge conflicts in the sync repo:** should not happen (each machine only
  adds/overwrites whole files), but if it does, keep the newest file version.

## Honest limitations — say these up front when relevant

- Unofficial workaround: it relies on Claude Code's on-disk transcript format
  and folder-name encoding, which Anthropic may change without notice. If a
  Claude Code update breaks resume-after-pull, re-verify the encoding with the
  troubleshooting step above.
- The resumed session's conversation history is complete, but
  machine-specific references inside it (absolute paths, tool availability,
  MCP servers) reflect the original machine.
- For sessions that must be cloud-native from the start, prefer the official
  routes: claude.ai/code, `claude --cloud "task"`, or `claude --teleport`.
