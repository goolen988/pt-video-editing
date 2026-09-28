# Execution routes

Basic cut/captions: Python 3.9 and FFmpeg/FFprobe with libx264 (libass preferred). Scripts are self-contained except optional dependencies. `transcribe.py` uses faster-whisper in a project venv. `graphics.cjs` uses Node 20+ and `playwright@1.58.2` with Chromium installed; set NODE_PATH to that project's node_modules. No service account is required.

For advanced custom animation, reframing, PiP or an existing HyperFrames project, use the official HyperFrames tooling: https://github.com/heygen-com/hyperframes and https://hyperframes.heygen.com/ . Install its skills with `npx skills add heygen-com/hyperframes` into the chosen project/host; inspect available options first. Read the installed entrypoint, then route to talking-head-recut for overlay-only work or general-video for custom montage. Version-pin the project and retain its lockfile. `npx hyperframes --help` gives the installed CLI contract. Validate/check, inspect frames, render, and inspect the output. Do not assume a CLI command's presence means that its renderer or browser has been tested.

Advanced third-party workflows are installed on demand, not copied into this distribution. No automatic refresh of a working project's engine during a local revision; if upgrading, retain the old version and verify renders before switching. The public package's core does not rely on a developer's global Skills folder or private project checkout.

Supplied B-roll/images can be composed using the host's installed video tooling or HyperFrames; retain every input and align to the clean edit timeline. Background music can be supplied as `music` in the plan, with `music_gain` (default 0.08). This simple mixer loops and fades the bed, then limits peaks; listen for masking and lower it when necessary. Advanced speech-driven ducking uses the chosen engine's supported audio mixer.

If FFmpeg lacks libass (common in some builds), the renderer automatically draws captions with the JavaScript/Playwright path. Install that optional dependency for burned-in captions, or render a clean cut with `captions: false` and retain SRT. Do not silently omit requested subtitles.
