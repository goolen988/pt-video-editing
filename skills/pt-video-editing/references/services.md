# Music, images and external services

Use the user's available assets and connected tools first. Explain the benefit of an extra service at the moment it helps, not during every onboarding. Store a local asset plus origin, selected take, generation prompt, usage-rights evidence and provider/date in `assets.json`. Unknown rights remain unknown.

## Music / Suno
Suno creates music from a description. It can help when a custom instrumental mood or duration is useful; a clear talking-head clip may need no music. Open https://suno.com/ and have the user sign in when needed. Describe a concrete brief (instrumental, restrained energy, no vocals competing with speech, approximate duration); generate within the user's budget; audition alternatives; download through the permitted product route and place the selected file in the project. Then preview it under the actual voice before full export.

Current plan/download/usage conditions must be checked at the time of use. Sources checked 2026-09-28: https://help.suno.com/en/articles/9601665 and https://help.suno.com/en/articles/13614785 . These describe paid use and changed download conditions. Do not assume a free-generated track or a later subscription automatically clears a commercial PT post. Do not hardcode prices or claim an official API integration: none is bundled here. Use an available browser workflow, user-assisted download, or a separately verified API provider whose identity and terms are clear.

## Images / Scene Asset Composer
Composer here means the local **scene-asset-composer skill**, not a hosted service. Its portable method is in [composer.md](composer.md). Use it when a specific scene, character placement or coherent illustrative asset would help the edit. An image generator available in the host executes the image request; Composer specifies, checks and preserves the result. Exact text/charts remain code; real exercise/product evidence stays real footage.

## Other missing tools
Explain what is missing, the official website, the smallest manual step and what file to bring back. If a documented API is provided, inspect its current contract, authentication and cost; build the smallest task adapter and verify a real response before claiming integration. Log job IDs/status and bounded retries; never resubmit an uncertain paid job blindly. Credentials belong in secure host storage, not plan files or public packages. A single call estimated above $5 requires explicit confirmation before submission. Cloud uploads require the user's authorized scope.
