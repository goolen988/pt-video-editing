# Setup by task

Basic editing: Python 3.9+, FFmpeg and FFprobe. Inspect installed filters for `ass` and encoders for `libx264`. On macOS with Homebrew already available, `brew install ffmpeg` is a normal route; otherwise consult https://ffmpeg.org/download.html for the user's OS. Do not install a package manager silently. Verify with a short local render.

Transcription: prefer an existing, verified word-timed transcript. Otherwise create a project virtual environment, install `faster-whisper`, then run the editing skill's `transcribe.py`. It downloads the selected model on first use. Start with a short sample, inspect the language and listen/check uncertain words. Never fabricate a transcript when the source is silent.

JavaScript graphics: Node 20+; in the user's project run `npm install --save-dev playwright@1.58.2` and `npx playwright install chromium`. Run the editing skill's `graphics.cjs` using `NODE_PATH=<project>/node_modules`. Browser installation is optional for clean cuts/plain captions. Retain package-lock.json.

Reference download: use an already supplied file first. For a public supported URL, install/use yt-dlp in an isolated environment, inspect available formats, download and record the URL. Browser login/download is a separate host capability; the user handles login. If access fails, ask for an exported file rather than guessing the reference style from a thumbnail.

External music and image services: read the editing skill's services reference. A website login, an API credential and commercial-use entitlement are separate states. Do not call an unofficial service a vendor's official API.

Save task capability receipts, installed versions, verification artifacts and any unresolved requirements to `.pt-connect.json`; never store tokens or passwords. Re-run task checks after a host or dependency change.

If FFmpeg lacks libass (common in some builds), the renderer automatically draws captions with the JavaScript/Playwright path. Install that optional dependency for burned-in captions, or render a clean cut with `captions: false` and retain SRT. Do not silently omit requested subtitles.
