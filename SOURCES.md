# Sources and adaptation

Canonical development: `~/Developer/PTAI/PT Dev/editing-kit/`. Public release snapshots are built from that source with an allowlist. Original private source paths below are provenance for maintainers, not runtime dependencies. Exact reviewed hashes are in `sources.json`.

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
