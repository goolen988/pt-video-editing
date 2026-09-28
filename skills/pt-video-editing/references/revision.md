# Revise the result the user saw

Identify the version by its receipt/hash and use the comment's OUTPUT time. If the user says “the title at 00:18,” inspect that exact version and time before editing. For source edits, translate through timeline.json; a held tail maps to source_end. Retain the user's original words in feedback.json alongside your interpretation.

Copy the plan to a new revision and record a concise requested-change list. Keep all unrelated accepted choices. A subtitle-position change should not silently change the opening, transcript, colors or audio. A restored pause changes output timing; regenerate every affected subtitle/card using the new map. If an upstream cut changes, confirm downstream overlays still refer to the intended speech.

Deliver revised.mp4, a before/after review and change-note.md stating exactly what changed and what remains unresolved. Preserve original source and earlier candidate bytes. Check source integrity and previous-version hash. Do not overwrite accepted media. The review page can save progress before a final decision; exporting unfinished feedback is useful and should not be blocked.

Human feedback may concern taste, readability, meaning or a technical defect. Fix an observable defect yourself before handing the piece back; offer a short visual alternative when the choice is subjective. End with the concrete new playback entry, not “I updated the prompt.”
