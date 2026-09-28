# JavaScript motion in an edit

Motion should direct attention to a spoken idea. Choose a short title reveal, a step card, a numeric comparison, a pointer, or a supplied screenshot/image when it answers a viewer's question. Keep the trainer visible when their expression or movement supplies the evidence. Leave a quiet hold long enough to read; never animate constantly just because code can.

## Executable options

The bundled `graphics.cjs` is a deterministic baseline renderer for timed text cards/captions. `edit.py render` invokes it when the plan contains cards or the FFmpeg build lacks subtitle support. Its input is output-time seconds and normalized rectangles. Use it when a simple clear title/card fits the request.

For a named reference style, per-word emphasis, a diagram or a different animation, author an appropriate seekable JavaScript composition using an installed engine. The entry in [tools.md](tools.md) covers HyperFrames. You may also adapt a copy of the bundled renderer inside the edit project for a small custom treatment; preserve the reusable package files. Keep actual assets local and pinned, render transparent frames or a finished composite, and inspect the resulting MP4. No missing module, remote asset or unexecuted JS may be presented as finished.

A useful motion plan has source/output time, the idea to explain, element, enter/hold/exit behavior, bounds, and why that motion helps. For graphs, use real proportions and consistent units. For images/screenshots, the method that creates the asset is separate from the code that animates and places it.

## Rendering constraints

A frame at time t must look the same whenever it is requested. Use a supplied time, not Date.now, unseeded random values or input events. Do not let independent video and audio players establish different clocks. Derive caption and graphic timing from the edited word map. Test the beginning, a key beat, a cut boundary and the ending. Re-render only what changed, then composite from the clean edit rather than stacking lossy edits onto a captioned review copy.
