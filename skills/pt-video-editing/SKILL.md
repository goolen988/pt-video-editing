---
name: pt-video-editing
description: Edit an existing talking-head recording, remove filler words or repetition, tighten pauses, move a highlight to the opening, add captions or animated cards, match a reference video's style, and revise a playable cut from natural-language feedback.
---
# PT Video Editing

Deliver an actual playable edit with retained sources and revision context. Users need not name a skill, engine or prompt formula. "Make it better" calls for one grounded recommendation; "just do it" authorizes routine reversible local editing, not paid subscriptions or posting.

## Begin from the recording

Resume an existing project before asking intake questions. Read its plan, feedback and review state. For a new task, identify source, intended platform and the user's requested change; infer non-critical defaults and say them briefly. Use `pt-connect` only for a missing capability; [tools.md](references/tools.md) also gives the minimum setup when this skill is installed alone.

Probe the entire source, inspect representative frames and the actual speech, and check for existing burned-in text. Obtain word timings with `scripts/transcribe.py` or validate an existing transcript. Read [judgment.md](references/judgment.md) before deciding what to cut or highlight. A transcript alone cannot establish visual or audio quality.

## Choose the smallest useful path

- Filler words / false starts / repetition / pauses / highlight opening: [editing.md](references/editing.md), then execute the EDL with `scripts/edit.py`.
- Captions / hook text / numbers / cards: [packaging.md](references/packaging.md). Render a representative short sample on the user's footage before expensive whole-video styling, unless the user already chose the treatment.
- Reference URL / "like this video": [reference-style.md](references/reference-style.md). Inspect the reference; translate its style into achievable edits using this user's recording.
- Music / generated image / missing service: [services.md](references/services.md). Obtain a real local asset and provenance; then compose it. No required music subscription.
- Posting copy: [post-copy.md](references/post-copy.md), grounded in the final cut.

## Show, listen, revise

Every material recommendation should have a watchable result: an opening candidate, before/after excerpt, rough cut, or style sample. Continue routine work when authorized; do not force approval for every cut. Make the review page with `scripts/review.py`, serve on localhost, and show its link or embed the MP4 in the host. A file on disk that nobody can play is not a review handoff.

Feedback such as "00:18 card covers my face" refers to the named rendered version and its output time, not the raw source time. Save the feedback with version/hash. Duplicate the plan into a new revision, modify only relevant decisions, render again, and preserve the prior candidate. Use the saved output/source timeline map when translating feedback to source ranges. Timestamped feedback from the page is browser-local until exported; ask the user to provide the exported JSON if the agent cannot read it.

## Finish

Run `scripts/edit.py check <render>` plus [delivery.md](references/delivery.md). Watch/listen through the result using the host's available media capabilities; review every seam. If actual playback/listening is unavailable, explicitly record that gap; decode success is not aesthetic acceptance. Deliver MP4, clean edit, captions, posting copy if requested, review link and retained editable plan. Save source hash, cut map, tool versions and a short change note. User acceptance applies only to the reviewed version. Publishing a video to social platforms is outside this skill's default scope.
