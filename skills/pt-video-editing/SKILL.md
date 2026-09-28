---
name: pt-video-editing
description: Turn an existing talking-head recording into a playable edited video, then revise it from feedback. Use for requests to remove ums, repetition or awkward pauses, find a better opening, add hook text/captions/JavaScript graphics, match a reference video URL, or improve a recording when the trainer does not know what to change. Also handle descriptions, hashtags, music and scene images when they accompany an edit. A request such as “make this watchable” is enough; the user need not name editing tools.
compatibility: Desktop agent with local file and command access; Python 3.9+ and FFmpeg. Optional local speech model and Node/Playwright for graphics. External services are task-specific.
---
# PT Video Editing

Help a trainer get from a recording to a video they can actually watch and improve. The useful unit is **an editing decision demonstrated by an output**. A plan, a script that has not run, or a prompt for an image is an intermediate, not the requested finished result.

## Start with the work already supplied

Read the current project and any feedback first. Keep the source untouched and preserve previous versions. Ask only for a missing input or a choice that changes the result; infer routine settings from the source/platform. If the user asks “what should I do?”, recommend the highest-impact two or three changes and make a playable first pass. If they request only advice, give timecoded advice and offer the most useful sample without silently expanding the task.

Use `pt-connect` for a missing tool or permission. Setup should lead back to the edit; the user should not have to learn an engine, write JSON or choose agents. Read [tools.md](references/tools.md) for supported executable paths. Both the FFmpeg cut and JavaScript graphics routes are in this package; advanced third-party workflows are optional.

## Inspect before deciding

Probe the source and obtain a word-timed transcript. Validate an existing transcript against the actual speech or use `scripts/transcribe.py`. Inspect frames across the whole recording and at prospective cut/title moments. Identify burned-in text, face/action placement and recording defects. A transcript does not reveal framing; still frames do not prove sound quality. Record unavailable perception rather than inventing a review.

Use [judgment.md](references/judgment.md) to choose changes. Save a short **edit-notes.md**: source times, what you propose, why it helps, and what must remain. Important: speech like “don't”, “unless”, “if it hurts”, uncertainty and natural emphasis must survive a punchier cut.

## Route by the requested result

| Need | Read / do | Evidence to show |
|---|---|---|
| Filler words, false starts, repeated clauses, dead time | [editing.md](references/editing.md); author semantic cuts, use pause suggestions only as candidates; run `scripts/edit.py` | Original and edited MP4; cut reasons and retained meaning |
| A stronger opening from existing footage | [hook-and-overlay.md](references/hook-and-overlay.md) | A playable complete opening with a sensible next sentence |
| Captions, hook text, cards or JavaScript motion | [packaging.md](references/packaging.md) and [motion.md](references/motion.md) | Short styled excerpt on this person's footage, then complete requested cut |
| “Make it like this URL” | [reference-style.md](references/reference-style.md) | Observed reference timestamps, actual adaptation sample, specific differences |
| Music, generated image or a missing service | [services.md](references/services.md); images use [composer.md](references/composer.md) | Actual supplied/generated asset and composed excerpt, or exact setup step if unavailable |
| Description / hashtags | [post-copy.md](references/post-copy.md) | Ready-to-copy text grounded in this final version |
| A comment on an existing cut | [revision.md](references/revision.md) | New version + concise change note; previous version still playable |

Prefer a complete simple edit to an elaborate unfinished treatment. More motion, music and cuts are not automatically better. Choose the simplest available engine that produces the requested result; do not default to the included green-card look when a reference or the user's style asks for something else.

## Execute and make the judgment visible

Use one source/output time map for picture, audio, captions and overlays. Keep a versioned plan; run the render. If a request covers a full recording, a sample is a review checkpoint, not the final deliverable. Continue after routine decisions already delegated by “you decide” / “just do it”; do not require approval for each reversible operation. A materially different style can be tested on a short sample first to reduce rework.

After rendering, use `scripts/review.py` to create the source/candidate review and `scripts/serve.py` for loopback playback with seeking. Present a clickable playable video or review link. State the proposed change in one sentence so the trainer knows what to judge. They can comment naturally in chat or export timestamped feedback from the page. Do not hand over a localhost link until that server is actually running, or a path outside the host's visible filesystem without another accessible route.

## Finish the requested scope

Read [delivery.md](references/delivery.md), run media checks, and inspect the actual output. If available, watch/listen through the whole clip and review cut seams. Missing full audio/playback review remains explicit; no technical test can certify natural delivery. Repair mechanical failures before asking the trainer to judge taste.

Deliver together:
- **The requested MP4** (and a short candidate only when that was the requested scope).
- **Review entry** with source, current version and a way to comment.
- **Edit notes** explaining decisions and any limits, plus posting copy if asked.
- **Editable context**: plan, source map, transcript/captions, selected assets/provenance and rendering receipt.

Use “ready for your review” until the trainer accepts that exact version. Rendering, human acceptance and social posting are separate. Keep the user-facing reply short: what changed, what to play, what needs their judgment.
