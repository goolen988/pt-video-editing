# PT Video Editing

**A recording → a watchable edit → your feedback → the next version.**

This folder is the maintained source for two independent skills: **PT Connect** (computer setup and saved readiness) and **PT Video Editing** (judgment, editing, packaging and revision).

## Start here

- [What this pack should deliver, and where to inspect it](ACCEPTANCE.md)
- [Coach-facing education page](https://pt-workspace.vercel.app/editing.html)
- [Installation guide](START.md)
- [Source methods and adaptations](SOURCES.md)
- [Publishing and maintenance](MAINTAINING.md)
- [Technical verification record](VALIDATION.md)

The previous `v0.1.0-preview` established a basic renderer and distribution path. It did **not** prove that every original request works through a natural-language skill invocation. `v0.2.0-preview` adds five paired old/new task executions, actual edited videos, a skill-creator review surface, persistent Connect state and render/review regressions. It remains a review candidate with documented gaps. See ACCEPTANCE.md for the evidence state, rather than treating “published” as “accepted”.

## Folder map

| Location | Purpose |
|---|---|
| `skills/pt-connect/` | Setup skill, task-specific references and executable readiness/state helpers |
| `skills/pt-video-editing/` | Editing skill, routed craft guidance, reusable render/review helpers |
| `skills/*/evals/evals.json` | Natural-language tasks and measurable expectations; no private media |
| `tests/` | Focused deterministic program regressions; these are not skill-behavior evaluation |
| `tools/` | Allowlisted build/publish and evaluation report helpers |
| `examples/` | How to run a demonstration; no customer footage |

Private inputs, old-skill snapshots, executions, videos, graders and the generated skill-creator viewer live in `~/Developer/PTAI/public/Video Editing/.local/skill-evaluation/`. They are excluded from public packages. Do not put user media inside the source tree.

## What is included

Semantic cut guidance (filler/repetition/qualifiers), pause proposals, highlight-opening selection, a shared source/output timeline, sound cleanup, captions, hook text and JavaScript card rendering, style-reference analysis, timestamped review/revision, posting copy, and task-specific music/image/service setup guidance. Scene Asset Composer is an image-planning/checking method using the generator available in the user's host.

Core edits need a desktop agent with local file/command access, Python and FFmpeg. Transcription and JavaScript graphics have optional local dependencies. Suno and external image services are not mandatory. A provider's account/login, a working API, and usage rights are different facts. No social publication is implied.

Canonical source: `~/Developer/PTAI/dev/Video Editing/`. Website source: `~/Developer/PTAI/website/`. The public GitHub repository contains an allowlisted source snapshot; it never receives private Git history or evaluation footage.
