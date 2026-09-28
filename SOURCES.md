# Sources and adaptation

Canonical development: `~/Developer/PTAI/dev/Video Editing/`. Public release snapshots are built from that source with an allowlist. Original private source paths below are provenance for maintainers, not runtime dependencies. Exact reviewed hashes are in `sources.json`.

- `~/.claude/skills/talking-head-cut/SKILL.md` — editing, packaging, audio and geometry methods.
- `~/.claude/skills/talking-head-cut/scripts/tighten_pauses.py` — pause proposal and EDL remapping adapted into edit.py.
- `~/.claude/skills/talking-head-cut/scripts/words.py` — portable word transcription adapted into transcribe.py.
- `~/.claude/skills/talking-head-cut/scripts/audio_clean.sh` — conservative audio filter rationale.
- `~/.claude/skills/talking-head-recut/SKILL.md` — graphic packaging route; upstream optional.
- `~/.agents/skills/embedded-captions/SKILL.md` — readable captions and timing constraints.
- `~/.claude/skills/mmm-video/video-subtitle-design/SKILL.md` — semantic grouping and mobile readability.
- `~/.claude/skills/mmm-video/video-understanding/SKILL.md` — reference inspection and media selection.
- `~/.claude/skills/mmm-video/video-hook-writer/SKILL.md` — opening judgment source; account-specific branches not copied.
- `~/.claude/skills/mmm-video/tiktok-description-writer/SKILL.md` — post-copy source; unsupported causal/account claims excluded.
- `~/.claude/skills/mmm-video/tiktok-hashtag-writer/SKILL.md` — post-copy source; account-specific tag rules excluded.
- `~/.claude/skills/video-finalize-deliver/SKILL.md` — delivery states and synchronized media lineage.
- `~/.claude/skills/scene-asset-composer/SKILL.md` — asset provenance and image inspection.
- `~/.claude/skills/scene-asset-composer/legacy-non-tech.md` — PT-adapted scene fit and reference roles.
- `~/Obsidian/Personal vault/4 Insights/视频判断总原则.md` — cross-format judgment source.
- `~/Obsidian/Personal vault/4 Insights/Talking Head 评分标准.md` — PT-adapted judgment and safe-zone experience.
- `~/Developer/PTAI/PT Dev/PT-Workspace-Pack/docs/ONBOARDING.md` — connect setup adaptation.
- `~/.agents/skills/hyperframes/SKILL.md` — optional advanced JS workflow discovery.

The shared source methods were adapted for portable PT use: no personal accounts, footage, absolute home paths, SilkGear archives, finance persona, fixed cartoon opening or unsupported performance promises. New scripts implement the portable time map, validation, rendering and review.

Optional advanced engine: [HyperFrames](https://github.com/heygen-com/hyperframes), installed separately from its upstream. [FFmpeg](https://ffmpeg.org/), [faster-whisper](https://github.com/SYSTRAN/faster-whisper), and [Playwright](https://github.com/microsoft/playwright) are external dependencies, not bundled binaries. Suno guidance cites its official help pages inside the services reference.

## Rework additions

- `~/.claude/skills/silkgear-video/references/text-overlay.md`: hook title placement, one-title discipline, natural-resolution type, full-window face clearance. Adapted to trainer footage; product-specific overlays are not imposed.
- `~/.claude/skills/mmm-video/broll-design/SKILL.md`: choose visuals by what they explain/prove, separate asset generation from composition. Historic fixed density ratios and account-specific performance claims are not imposed.
- Explicit skill-creator workflow: freeze baseline, define realistic prompts, execute paired runs, grade artifacts, aggregate metrics and generate its review viewer. The viewer and private evidence are not runtime dependencies.

## What actually ships

| Original capability | Included form | Limit |
|---|---|---|
| Talking-head cut, pause compression, word transcription, audio cleanup | Adapted execution helpers plus `editing.md` / `judgment.md` | Semantic decisions remain agent-owned; not an automatic universal filler classifier |
| Hook writing and text overlay | `hook-and-overlay.md`, packaging rules and executable title/card renderer | No imposed finance persona or cartoon opening |
| Embedded captions and subtitle design | Readability/timing/placement guidance and a basic caption renderer | The complete upstream style catalog/matting engine is not vendored |
| Talking-head repurpose / JS animation | `motion.md`, bundled JS renderer, advanced engine setup route | Advanced HyperFrames operations require that separately installed engine |
| Description and hashtag writing | PT-adapted `post-copy.md` | Historical account-specific growth claims excluded |
| Scene Asset Composer | Portable scene-fit/reference/provenance method | Uses an actually available host image generator; no fake standalone Composer API |
| Video understanding / reference analysis | `reference-style.md`, source/media evidence and timed adaptation | Reference access can depend on platform/login/provider setup |
| Delivery | `delivery.md`, decode/layout checks, source map and review/revision scripts | Technical checks do not establish human taste approval |

The hash manifest distinguishes currently available reviewed sources from historical paths and changed upstream files. A source listed here is provenance, not proof that its entire original workflow is bundled or behaviorally validated.
