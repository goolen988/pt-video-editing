# Scene Asset Composer — portable PT adaptation

Source: local scene-asset-composer (see SOURCES.md). This is a task method, not a separate SaaS/API.

1. Identify the exact beat and purpose of the image: room geometry, mood, placement, illustrative cutaway, or character continuity. Reuse a suitable existing asset before generating.
2. Assign references explicit roles: style, geometry, character, equipment placement or action surface. Check the scene can physically contain the intended action; a beautiful image with the wrong scale or missing surface does not fit.
3. Use the host's connected image-generation tool by default. If missing, PT Connect explains the supported installation/login path or requests a generated file from the user. Do not pretend a text prompt is a delivered image. Keep generation within the user's authorized scope and budget.
4. Inspect the actual output: coherent space, correct scale, identity/appearance continuity, no unwanted text/people/logos, useful crop and overlay clearance. For a concrete mismatch, make a targeted revision and compare. Do not silently swap an accepted image.
5. Save a versioned local PNG/JPEG, dimensions, SHA-256, prompt, reference roles, model/provider when observed, and real task IDs if returned. A signed download URL expires; keep the file and provenance, not bearer query strings. Unknown IDs remain null.
6. Put the selected image into the video at its planned output time, show the actual excerpt and accept feedback. A generated illustration is not proof of exercise technique, product performance or a client's outcome.

SilkGear's iCloud paths, SKU contracts, production approval states and Seedance-specific face model requirement are not imposed on PT editing. If a later task explicitly needs Seedance face references, verify that provider's current reference/model rules before using them.
