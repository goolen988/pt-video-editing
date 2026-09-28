# Delivery review

Automated: complete decode, output duration vs EDL, video/audio presence, valid source hash, valid word remap, subtitle/card bounds, supplied face-box clearance. `edit.py check` reports measured media data but never marks user acceptance.

Agent visual/audio: watch/listen through the entire edit; inspect every seam on both sides, no clipped syllables or changed meaning, no click/pop, no desync, no unreadable or duplicate captions, no card hiding eyes/mouth/exercise evidence, no text escaping phone-player margins. Use the actual output, not just plans or extracted stills. If host playback/audio access is absent, disclose the exact unverified checks and keep status `REVIEW_CANDIDATE`.

Provide reviewable MP4, lossless clean edit, captions, source map, plan and change note. Preserve earlier versions. Use source dimensions by default; only change fps/resolution for an actual delivery need. Export a lightweight review copy if needed, but generate each deliverable from the clean intermediate to avoid stacked lossy encodes. Final acceptance and social upload are separate actions.
