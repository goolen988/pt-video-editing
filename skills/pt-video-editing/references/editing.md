# One time map

Keep source media unchanged. Author `plan-v001.json` in a new edit project. `source` and `words` are relative to the plan's directory (absolute paths also work locally). Word data is an array of `{w,s,e}` in source seconds. All segment start/end values are source seconds; sequence order is output order. Captions and graphic cards are authored in output seconds.

Example:
```json
{"version":"v001","source":"source.mp4","words":"words.json","segments":[{"start":8.0,"end":12.0,"reason":"Lead with the complete payoff"},{"start":0.0,"end":7.6,"reason":"Context without the false start"}],"clean_audio":true,"captions":true,"caption_y":0.71,"cards":[{"start":0.2,"end":3.5,"text":"A clearer starting point","x":0.15,"y":0.21,"w":0.70,"h":0.12}],"face_boxes":[]}
```

First run `python3 scripts/edit.py suggest source.mp4 words.json suggestions.json`. This proposes silence compression only. Agent separately identifies semantic filler/repetition edits and records reasons in the EDL. Inspect/listen to uncertain boundaries. The renderer rejects partial-word cuts against the supplied transcript; repair timestamps after inspecting speech rather than disabling the check.

Run `python3 scripts/edit.py render plan-v001.json renders/v001`. It validates all ranges, hashes the source, cuts picture and audio together, remaps words, writes a lossless clean MKV, SRT and ASS, then MP4. If cards are present, install the optional JavaScript renderer first. The renderer refuses an existing output directory. Name the next revision explicitly.

The saved `timeline.json` records every output interval and its source interval. Keep it with receipts. Substituting an enhanced source later requires applying exactly the same EDL, including its audio; validate the replacement's offsets. Never reuse the pre-edit transcript against the edited movie.

The built-in renderer preserves source dimensions (pads an odd edge to even) and uses a constant output frame rate derived from the source. Set `fps` explicitly if needed. It does not infer a crop or synthesize missing frames. For reframing or advanced composites, use the retained clean edit and the tools path. Do not label upscaled or duplicated frames as recovered detail or true motion interpolation.

Frame-grid rule: each output segment is rounded up to a whole number of output frames while retaining the exact requested source range. The final source image is held and audio is padded for less than one frame when necessary. The output map, word offsets and render all use that same quantized duration; source-seek clamps this tiny tail to source_end. Audition seams, especially with many very short cuts.
