# Aphrael on Hermes

## Runtime

`distribution.yaml` pins the exact Hermes release and declares the Aphrael files that a profile update may replace. `SETUP_APHRAEL.ps1` uses the official Hermes installer, then runs `scripts/aphrael_profile.py` to install or update the `aphrael`, `aphrael-worker`, `aphrael-reviewer`, and `aphrael-dispatcher` profiles.

The setup process creates `%USERPROFILE%\AphraelWorkspace\output` as the only writable agent workspace and `%USERPROFILE%\.hermes\aphrael-board` as the dedicated Kanban store. It keeps a backup of distribution-owned profile files before update and restores those files if an update is interrupted. It does not replace memory, session, OAuth, or other user-owned state.

## Authorization and launch

Run the device-flow command in the README once, then launch with `START_APHRAEL.ps1`. Hermes shows the authorization URL and short device code; enter it only in the official OpenAI authorization page. Aphrael does not access Hermes' auth store.

Use `START_APHRAEL.ps1 -Surface Check` after an update. It verifies profile isolation, the dedicated board, manual approval settings, no fallback provider, the installed plugin, and the fail-closed shell hook.

## Operational controls

The default profile can converse and delegate. The worker profile is limited to work execution; the reviewer profile can independently verify a predeclared file outcome. A Kanban task being marked complete is only task-state evidence; it does not itself establish that an external file or action succeeded.

The guardrail policy is stored privately per profile. It denies unlisted tools, private paths, reparse points and hardlinks, network/device paths, and shell commands except a small fixed read-only set. The policy also blocks automatic cron, single-query, and unattended approvals. A user can stop a conversation or task through Hermes at any time.

## Updating

Run `SETUP_APHRAEL.ps1` again from a newer checked-out distribution. The script uses the Hermes profile update command and preserves unowned profile state. If setup reports an interrupted update, rerun it; the recovery marker restores the owned-file backup before a new update starts.
