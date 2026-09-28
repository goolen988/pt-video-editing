# Maintain and publish

Canonical source: `~/Developer/PTAI/PT Dev/editing-kit/`. Website: adjacent `pt-site/public/editing.html`, `editing.css`, `editing.js`. Change the canonical source; public snapshots are generated. Source methods and reviewed hashes are in sources.json; review changes to those upstream local Skills before porting them here. A hash alone does not mean a new upstream method has been integrated.

1. Edit the skill, reference or script here. For behavior changes run unit tests and the real media integration test. Review real talking-head footage for aesthetic changes. Update VALIDATION.md with what was actually checked.
2. Bump VERSION for every published change. Released tags are immutable. Update source hashes only after reviewing and porting the corresponding method changes.
3. From this directory run `python3 tools/publish.py --publish`. This tests, builds two ZIPs, checks clean installs, creates the public repository if absent, pushes the allowlisted source snapshot, uploads a draft release, downloads and checks both archives, then publishes it. `gh auth login` is the maintainer prerequisite; never put tokens in source. Omit --publish to build only.
4. The website uses the stable START.md and GitHub Releases links, so future releases require no download-link edit. When education content changes, run website checks and deploy the existing pt-site Vercel project (`npx vercel --prod --yes --scope goolen98-3170s-projects` from pt-site). The skill publisher does not deploy unrelated website changes.

If a draft release upload fails, inspect it and resume deliberately or remove that unpublished draft/tag before retrying. Do not overwrite published assets. A successful push is not a verified release; the download check must pass. No customer recordings, `.validation`, `.build`, private Git history, environment files or state are included.

Installer rollback: prior installed skills are retained under the target project's `.pt-skill-backups/`. Restore the selected folder or reinstall a prior verified ZIP. All video projects remain separate and untouched. Existing user edits are never auto-migrated.

Local review: `python3 skills/pt-video-editing/scripts/serve.py <render-folder>`. It listens only on loopback and supports seeking via HTTP Range. Close it when the review is no longer needed.
