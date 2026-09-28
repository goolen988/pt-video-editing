# Validation — 0.1.0-preview

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
