# Validation — 0.2.0-preview review candidate

This version is a skill-creator rework, not a claim of trainer acceptance. Behavioral results and requirement-by-requirement evidence are recorded in ACCEPTANCE.md.

## Checks in this rework

- The maintained runtime files match the evaluated snapshots byte-for-byte (4 Connect files and 18 Editing files; source-only eval specs excluded).
- Both skills passed the invoked skill-creator `quick_validate.py`.
- **16/16 automated regression checks passed**, including the actual Playwright/Chromium media test (`PT_VIDEO_EDITING_BROWSER_TEST=1`). Coverage includes host-bound setup state and resume, real A/V render, failed-render cleanup/retry, partial-word and frame-grid mapping, face/safe bounds, actual overlay pixels, version/source-bound comments and feedback export.
- Both preview ZIPs built and installed in separate clean project directories. The newly installed editing ZIP also passed all five real media/browser regression tests from its installed location. The package builder excludes evaluation recordings, local states and private history.
- The exact skill-creator `generate_review.py` produced the evaluation viewer. The thin wrapper preserves its Outputs/Benchmark/feedback UI, adds inline MP4 playback, loads task metadata from nested run directories, safely embeds HTML outputs and makes static comment persistence/download reliable. An actual Chromium check confirmed MP4 playback, feedback surviving reload, and a ten-result feedback JSON download without page errors. Automated feedback is a test fixture, not user acceptance.
- The education page returned HTTP 200 at its existing public URL on 2026-09-28. This rework does not replace its prior browser evidence below with a claim of a new design test.

## Evaluation boundaries

Five realistic tasks each have one revised and one frozen-old-skill execution. The executor is independent Codex agents. An actual Claude Code probe returned weekly-limit HTTP 429, so this is **not Claude behavioral validation**. Explicitly supplying a skill does not measure automatic trigger accuracy. Source speech, reference media and all rendered cases remain private local fixtures.

Reported wall-clock includes host/queue interruption and cannot establish speed improvement. Token telemetry is unavailable and is not estimated. A renderer callback correction occurred during the first round and was logged. One old-version executor made a limited memory registry lookup before isolation was reinforced. This is a practical small-sample comparison, not a controlled claim of general superiority.

Human full listening, natural delivery and aesthetic acceptance remain pending. Suno account operation, paid image generation and arbitrary supplied-provider APIs are conditional routes, not verified universal connectors. The provided guidance explains setup and available alternatives; no such paid service was used during this rework. Platform margins are editable layout assumptions, not a universal guarantee about changing app UI.

# Historical validation — 0.1.0-preview

Validated on macOS with Python 3.9, FFmpeg 8.1/libx264, Node 25 and Playwright 1.58.2 Chromium on 2026-09-28.

- Core unit checks (8 passed): source/output word remapping, 100-segment frame-grid accumulation, partial-word rejection, invalid ranges, face collisions, overlapping text, safe bounds, upgrade backup and user-media preservation, symlink-target refusal.
- Actual frame-grid regression: 30 non-frame-aligned source spans produced exactly 120 frames / 4.000 seconds at 30 FPS, matching the source/output map.
- Actual synthetic media pipeline: reordered two segments, burned captions and JavaScript cards, cleaned audio, decoded full MP4; requested 0.3 seconds of restored pause (3.333-second output after whole-frame quantization), remapped subsequent words and preserved v001.
- Real talking-head local smoke: reordered a 4.77-second excerpt, rendered captions and a timed card, decoded the output and visually inspected a rendered frame. Re-transcribed the result with local faster-whisper small.en; speech order matched the edit. Private footage is not distributed.
- Browser interactions: actual video playback, output-to-source seek, timestamped comment entry, reload persistence, decision selection and downloaded feedback JSON. Education-page copy/fallback and 390/320-pixel layouts passed without horizontal overflow or page errors. Existing homepage interactions and mobile checks also passed. The deployed education page was rechecked at https://pt-workspace.vercel.app/editing.html .
- A ZIP was extracted into a fresh project, installed for Claude, and its installed renderer produced the actual captioned/animated MP4 using only declared external dependencies. Both Codex and Claude project-scoped installation paths were exercised.
- Both Skill frontmatter validators passed. Release tooling separately verifies each ZIP by installing into a new temporary project and downloads published assets to compare hashes.

## Explicit limits

This is a public preview, not a claim of independent coach acceptance or production validation of every route. Full human listening/naturalness review of the real excerpt is not established by these checks. Frame inspection and ASR are not full playback judgment. Automated layout checks use supplied face boxes; no automatic face/prop detector is bundled. Other operating systems are not end-to-end tested. Suno, image-provider generation, arbitrary reference URL access and advanced HyperFrames workflows are guided optional routes, not end-to-end tested service connectors in this release. No paid generation or social posting was performed.

Actual user tasks must follow the skill's full playback/listening and revision review before being called accepted. Review comments stay browser-local until exported to the agent.
