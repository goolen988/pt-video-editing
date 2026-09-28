# Start PT Video Editing

For the agent: speak plain English by default, or the user's language. Do not ask the user to write commands or understand engines.

1. Check that this session can read/write an authorized local project folder and execute commands. If not, explain the missing capability and help the user open a suitable desktop session. Do not claim a browser-only chat has local permissions.
2. Read the latest GitHub release at https://api.github.com/repos/goolen988/pt-video-editing/releases/latest . Download `release.json` and the requested `pt-connect-<version>.zip` and/or `pt-video-editing-<version>.zip` assets from that same release. Compare SHA-256 to `release.json`; this is integrity checking, not independent signing. Do not run code before inspection and verification.
3. Extract to a temporary staging folder, rejecting absolute or parent-traversal archive paths. Each package includes `install.py`, its skill folder and VERSION. Inspect `install.py`, then run `python3 install.py --project <authorized-project> --host codex --skill pt-connect` (or `--host claude`, `--skill pt-video-editing`). Install both only if needed. Existing skill versions are backed up; footage and user projects are not replaced.
4. Read the installed SKILL.md. PT Connect checks only capabilities needed for the first task. Save projects in a separate `edits/<project-name>/` directory, not inside installed skills.
5. Ask for the recording if missing; otherwise start by inspecting it. Offer one useful first edit and show the result. No elaborate prompt is required.

Return to the same saved project for future chats. Another host/session must verify its own permissions. Core setup does not establish Suno, image-generation or browser-control access.

Update by downloading a fixed newer release, verifying and staging it, then running the installer. Never unpack over an edit project. Preserve the previous skill backup for rollback. Read its SKILL.md or reinstall a prior verified release to restore it; no user-data migration is performed by this preview.
