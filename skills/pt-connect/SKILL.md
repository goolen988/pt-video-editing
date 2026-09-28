---
name: pt-connect
description: Set up or repair local computer access and task-specific tools for PT video editing. Use when a trainer needs to connect their desktop agent, install editing dependencies, or resume a previously configured workspace.
---
# PT Connect

Make setup understandable and persistent. Handle commands yourself. A successful Python check does not prove the host can see the desktop, hear audio or control a browser.

1. Locate the user's authorized project. Check local read/write/command access with `scripts/doctor.py --workspace <project>`; inspect its structured result. It uses a temporary file and removes it. It reports optional tools separately and stores no credentials.
2. Read `<project>/.pt-connect.json` if present. Recheck cheap tool checks; skip already completed explanations. Ask only for missing information, such as the project folder or an interactive login.
3. Read [setup.md](references/setup.md) for the requested task. Install only needed dependencies using the host's normal permission flow. Never make an external account mandatory for basic trimming.
4. Run doctor again. Run a small real operation for the needed capability; record its artifact and result in the state. Do not mark browser access, transcription, rendering or provider authentication verified from an executable's presence alone.
5. State simply: what is ready, what needs the user's login, and the next useful task. Store setup under the project, not in global model memory. Credentials stay in provider-supported secure storage.

For a host limitation, offer the specific local-session path or a narrowly scoped manual step. Do not silently upload recordings to a cloud workaround. Estimated single paid calls over $5 require explicit approval before submission.
