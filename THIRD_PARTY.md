# Third-party components

No third-party binaries, models, fonts, generated customer media or upstream Skill directories are bundled. Dependencies are installed separately under their own terms: FFmpeg (license depends on build), faster-whisper (MIT), Playwright (Apache-2.0), HyperFrames (Apache-2.0; optional). Browser/model downloads have their respective licenses. Preserve their notices when redistributing those dependencies. The installed renderer uses system fonts rather than shipping font files.

Internal methods were adapted from the local sources in SOURCES.md; account-specific examples and customer assets are excluded. Suno and image services are not bundled connectors, and their current account/usage terms must be checked when used.
