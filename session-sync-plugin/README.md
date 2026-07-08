# Session Sync — resume Claude Code sessions on any machine

Claude Code stores every local session as a JSONL transcript under
`~/.claude/projects/<encoded-project-path>/`. The folder name encodes the
project's **absolute path on that machine**, so transcripts are not portable
between machines as-is, and there is no official way to push a local session
to Anthropic's cloud.

This plugin makes local sessions portable anyway. It syncs transcripts through
a **private git repo that you own**, keyed by a stable per-project slug, and
re-encodes folder names and internal paths for whichever machine pulls them —
including across operating systems (a session started on macOS resumes on
Windows, and vice versa). After a pull, `claude --resume` lists the session
with its full history.

Works on macOS, Linux, and Windows (via Git Bash, which Claude Code already
requires). Everything machine-specific lives in your own
`~/.claude/session-sync.conf` — nothing about your projects or paths is baked
into the plugin.

## ⚠️ Before you start

- **Your sync repo must be PRIVATE.** Transcripts contain your prompts, code,
  file contents, and possibly secrets. Never point this at a public repo.
- **Never sync a live session.** End the session first; the script warns if a
  transcript changed in the last 2 minutes.
- This is an **unofficial workaround** that relies on Claude Code's on-disk
  transcript format, which Anthropic may change without notice.

## Install (as a Claude Code plugin)

```
/plugin marketplace add mdalfianahmad/claude-code-session-sync
/plugin install session-sync@session-sync-marketplace
```

Then just ask Claude Code things like *"sync my sessions"* or *"I want to
pick this session up on my laptop"* — the bundled skill walks through setup
and daily use. Updates: `/plugin marketplace update session-sync-marketplace`.

## Install (standalone, no plugin)

The sync itself is a plain bash script with no AI involvement — you can use it
directly:

```bash
curl -fsSL https://raw.githubusercontent.com/mdalfianahmad/claude-code-session-sync/main/skills/session-sync/scripts/session-sync.sh \
  -o ~/.claude/scripts/session-sync.sh --create-dirs
```

## Quick start

```bash
# one-time, per machine (repo must be PRIVATE)
gh repo create my-claude-sessions --private
session-sync.sh setup https://github.com/<you>/my-claude-sessions.git

# register each project — SAME slug on every machine, that machine's local path
session-sync.sh add myapp /Users/you/myapp          # macOS
session-sync.sh add myapp "C:/Users/you/myapp"      # Windows (Git Bash)

# leaving machine A            # arriving at machine B
session-sync.sh push myapp     session-sync.sh pull myapp
                               cd ~/myapp && claude --resume
```

Other commands: `push-all` / `pull-all` (every registered project), `list`
(local vs repo counts), `push-auto` (for a SessionEnd hook — hands-free push),
`harvest-cowork` (collect Claude desktop-app Cowork sessions, which live
outside `~/.claude/projects`). See
[skills/session-sync/SKILL.md](skills/session-sync/SKILL.md) for the full
guide, the opt-in auto-push hook recipe, and troubleshooting.

## What it does NOT do

- It does not sync your project's *code* — commit/push that yourself so the
  second machine matches the first.
- It does not upload sessions to Anthropic's cloud. For cloud-native sessions
  use claude.ai/code, `claude --cloud`, or `claude --teleport` instead.
- It does not run continuously. Pushing is manual or via the opt-in
  session-end hook; pulling is always deliberate, to avoid two machines
  writing the same transcript at once.

## License

MIT
