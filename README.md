# PT Video Editing

Bring a recording. Ask for the edit. Watch the result and tell your agent what to change.

Two independently installable skillsets for a desktop agent with local file and command access:

- **PT Connect** checks the computer, installs only the tools a task needs, and saves setup status.
- **PT Video Editing** combines editing judgment, local execution, playable review and timestamped revisions.

Start in your desktop agent:

> Read https://raw.githubusercontent.com/goolen988/pt-video-editing/main/START.md and help me edit my talking-head video.

[What you can ask](https://pt-workspace.vercel.app/editing.html) · [Releases](https://github.com/goolen988/pt-video-editing/releases) · [Sources](SOURCES.md)

## Included

Word-timed edit decisions; pause suggestions; manual/agent-authored filler and repetition removal; highlight reordering; synchronized picture/audio/caption remapping; plain readable captions; JavaScript animated cards; conservative audio cleanup; optional supplied music; local before/after review with exported feedback; decode and duration checks. Reference-style and external-service work is agent-guided, not a promise of an automatic connector to every website.

The agent chooses semantic edits. A script cannot decide whether a hesitation is meaningful. All renders remain review candidates until the user accepts that version. No social posting is included.

## Compatibility

Reference environment: macOS, Python 3.9+, FFmpeg/FFprobe with libx264 (libass preferred). Optional: faster-whisper for local transcription; Node 20+ and Playwright Chromium for JavaScript graphics; yt-dlp for supported reference URLs. Linux and Windows require a fresh capability check; they have not been end-to-end qualified for this preview. No paid service is required for the core edit. First-time model/browser downloads need internet and disk space.

## Maintainers

This repository contains the public source snapshot. The canonical development source is `~/Developer/PTAI/dev/Video Editing/`. Changes are made there, tested, and published through `python3 tools/publish.py --publish`. The private developer tree is never uploaded. See [MAINTAINING.md](MAINTAINING.md).

If FFmpeg lacks libass (common in some builds), the renderer automatically draws captions with the JavaScript/Playwright path. Install that optional dependency for burned-in captions, or render a clean cut with `captions: false` and retain SRT. Do not silently omit requested subtitles.
