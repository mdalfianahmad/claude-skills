# Changelog

## 2026-07-07

- initial version: push/pull Claude Code session transcripts through a private
  git repo with cross-machine path re-encoding (setup/add/push/pull/list)
- add push-all / pull-all / push-auto commands and a SessionEnd hook recipe
  for hands-free pushing; document that first push syncs all pre-existing
  sessions
- add harvest-cowork: collect desktop-app Cowork (local agent mode)
  transcripts — which live outside ~/.claude/projects — into a registered
  'cowork' project; push-all harvests automatically when configured

## 2026-07-08

- pull now localizes transcripts: machine-specific absolute paths recorded
  inside pulled session files (cwd fields, path mentions) are rewritten to
  the local machine's registered project path, so cross-OS resume works
  instead of "session not found"; mtimes reset to repo copy so localization
  never re-triggers a push
- package for public sharing as a Claude Code plugin: new sibling dir
  session-sync-plugin/ holds plugin.json + marketplace.json (repo doubles as
  its own marketplace), public README, MIT LICENSE, and publish.sh, which
  assembles the installable tree by copying this skill in at publish time so
  the plugin can never drift from the skill source
