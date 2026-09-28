# Maintain and publish

Canonical source: `~/Developer/PTAI/dev/Video Editing/`. Website: `~/Developer/PTAI/website/public/editing.html`, `editing.css`, `editing.js`. Change the canonical source; public snapshots are generated. Source methods and reviewed hashes are in sources.json; review changes to those upstream local Skills before porting them here. A hash alone does not mean a new upstream method has been integrated.

1. Edit the skill, reference or script here. For behavior changes run unit tests and the real media integration test. Review real talking-head footage for aesthetic changes. Update VALIDATION.md with what was actually checked.
2. Bump VERSION for every published change. Released tags are immutable. Update source hashes only after reviewing and porting the corresponding method changes.
3. From this directory run `python3 tools/publish.py --publish`. This tests, builds two ZIPs, checks clean installs, creates the public repository if absent, pushes the allowlisted source snapshot, uploads a draft release, downloads and checks both archives, then publishes it. `gh auth login` is the maintainer prerequisite; never put tokens in source. Omit --publish to build only.
4. The website uses the stable START.md and GitHub Releases links, so future releases require no download-link edit. When education content changes, run website checks and deploy the existing website Vercel project (`npx vercel --prod --yes --scope goolen98-3170s-projects` from `~/Developer/PTAI/website/`). The skill publisher does not deploy unrelated website changes.

If a draft release upload fails, inspect it and resume deliberately or remove that unpublished draft/tag before retrying. Do not overwrite published assets. A successful push is not a verified release; the download check must pass. No customer recordings, `.validation`, `.build`, private Git history, environment files or state are included.

Installer rollback: prior installed skills are retained under the target project's `.pt-skill-backups/`. Restore the selected folder or reinstall a prior verified ZIP. All video projects remain separate and untouched. Existing user edits are never auto-migrated.

Local review: `python3 skills/pt-video-editing/scripts/serve.py <render-folder>`. It listens only on loopback and supports seeking via HTTP Range. Close it when the review is no longer needed.

## Behavioral evaluation and acceptance

Skill layout follows progressive disclosure: `SKILL.md` routes natural-language requests, `references/` supplies the relevant craft, and `scripts/` performs repeatable operations. `evals/evals.json` describes realistic user tasks; it is source-only and excluded from installation ZIPs. `tests/` covers deterministic regressions. Private evaluation inputs and rendered customer footage stay outside this source tree.

For changes to user behavior, snapshot the prior skill before editing. Run the same prompts and fixtures with both versions in `<skill-name>-workspace/iteration-N/eval-*/{with_skill,old_skill}/run-1/`. Keep the prompt, outputs, execution log, timing and evidence-based `grading.json`. Never turn missing token telemetry into zero usage. Explicit skill invocation tests execution, not automatic triggering.

Use the invoked skill-creator's `scripts.aggregate_benchmark` and its `eval-viewer/generate_review.py`. This repository's `tools/render_evaluation_review.py` invokes that generator and adds inline MP4 playback to its existing Outputs/Benchmark/feedback interface. An optional private `--inputs-map` can attach clearly labeled original/reference clips to the viewer without changing execution outputs. It requires the external skill-creator directory and Python 3.10 or later; it is a maintainer utility, not a runtime dependency of either installed skill.

Run `python3 -m unittest discover -s tests -v`. Browser/media regressions are opt-in: set `PT_VIDEO_EDITING_BROWSER_TEST=1` and make Playwright resolvable to Node. A skipped browser test is not a passing browser check. Render private real footage separately, inspect final frames and audio, and ask the user to review the generated viewer. Update ACCEPTANCE.md and VALIDATION.md with observed outcomes and unresolved limits. A preview release can carry a review candidate; it never establishes human acceptance.
