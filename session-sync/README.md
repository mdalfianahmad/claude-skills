# session-sync

Move Claude Code CLI sessions between machines (macOS ↔ Windows ↔ Linux) by
syncing the transcript JSONL files through your own **private** git repo.
Start a session on one machine, `push`, then `pull` on another machine and
`claude --resume` — the conversation continues with full history.

There is no official way to do this (local sessions are machine-local, and
they can't be uploaded to Anthropic's cloud), so this skill works around it by
handling the machine-specific `~/.claude/projects` folder-name encoding.

## Setup

```bash
# once: create a PRIVATE repo to hold transcripts
gh repo create claude-session-sync --private

# on every machine
bash session-sync/scripts/session-sync.sh setup git@github.com:you/claude-session-sync.git

# register each project — same slug everywhere, local path per machine
bash session-sync/scripts/session-sync.sh add myapp /Users/you/myapp        # macOS
bash session-sync/scripts/session-sync.sh add myapp "C:/Users/you/myapp"    # Windows (Git Bash)
```

## Use

```bash
session-sync.sh push myapp   # after ending a session on machine A
session-sync.sh pull myapp   # on machine B, then: cd myapp && claude --resume
session-sync.sh push-all     # push every registered project (incl. all pre-existing sessions)
session-sync.sh pull-all     # pull every registered project
session-sync.sh list         # local vs synced session counts
```

To automate pushes, add a `SessionEnd` hook running `session-sync.sh
push-auto` (see SKILL.md) — it pushes the project a session just ended in and
is a silent no-op everywhere else. Pulling stays manual by design.

## Caveats

- The sync repo holds full conversation transcripts (your code, file contents,
  possibly secrets). Keep it private.
- Never push/pull while a session is running on either machine.
- Unofficial: depends on Claude Code's on-disk format, which may change.
- Syncs conversations only — keep the project's code in sync via git as usual.
