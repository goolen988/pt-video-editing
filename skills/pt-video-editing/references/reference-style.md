# Adapt a reference

Obtain the video, recording its URL and retrieval date. Use an available authorized downloader or browser export; if unavailable, ask for the file. A thumbnail, description or transcript does not prove editing style.

Probe duration/aspect/fps; inspect the beginning, middle, ending and transitions; extract denser frames around motion details; listen to the actual audio when available. Create a short `reference-style.md` with observed timestamps and separate:
- Rhythm: shot lengths, meaningful pauses, where changes happen.
- Type: size, placement, line length, emphasis and timing.
- Composition: crop, speaker size, PiP and usable space.
- Motion: entrance, hold, exit; its purpose.
- Sound: music level, accents and relation to speech (unknown if not listened to).

Then map each useful element to the user's available footage. State what can be reproduced and what needs extra material. Preserve the user's words/identity; do not download the reference's soundtrack and assume it is cleared. Render a representative 8–15 second sample, show it, then apply feedback to the full cut. If the source contains burned-in text or incompatible framing, explain the practical limit and show the closest workable treatment.

For extraction, use `ffmpeg -ss <seconds> -i <reference> -frames:v 1 <frame.png>` and a short audio/video excerpt. These are analysis evidence, not proof of full playback. Save observed facts separately from inferred style choices.
