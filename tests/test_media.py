"""Media regressions for edit timing, render recovery, safe overlays and review context.

The normal publish test run covers timeline, recovery, A/V and review receipt checks.
Set PT_VIDEO_EDITING_BROWSER_TEST=1 to include the Playwright/Chromium pixel and
review-page export test. It uses only a generated four-second fixture.
"""

import hashlib
import importlib.util
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/pt-video-editing/scripts"
EDIT_SCRIPT = SCRIPTS / "edit.py"
REVIEW_SCRIPT = SCRIPTS / "review.py"
SERVE_SCRIPT = SCRIPTS / "serve.py"
BROWSER_TEST_ENV = "PT_VIDEO_EDITING_BROWSER_TEST"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


edit = load_module("pt_video_editing_edit", EDIT_SCRIPT)
review = load_module("pt_video_editing_review", REVIEW_SCRIPT)


def run(args, **kwargs):
    return subprocess.run([str(arg) for arg in args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)


def file_sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def frame_rgb(path, at):
    return run(["ffmpeg", "-nostdin", "-v", "error", "-ss", at, "-i", path,
                "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]).stdout


def audio_f32(path, at, duration):
    return run(["ffmpeg", "-nostdin", "-v", "error", "-ss", at, "-i", path,
                "-t", duration, "-vn", "-ac", "1", "-ar", "48000",
                "-f", "f32le", "-acodec", "pcm_f32le", "-"]).stdout


def goertzel_power(samples, frequency, sample_rate=48000):
    count = len(samples) // 4
    data = struct.unpack("<" + "f" * count, samples[:count * 4])
    coefficient = 2 * math.cos(2 * math.pi * frequency / sample_rate)
    previous = previous2 = 0.0
    for sample in data:
        current = sample + coefficient * previous - previous2
        previous2, previous = previous, current
    return previous * previous + previous2 * previous2 - coefficient * previous * previous2


class TimelineMediaTests(unittest.TestCase):
    def test_edge_tolerance_does_not_map_a_word_outside_the_segment(self):
        mapped, _, _ = edit.timeline(
            [{"start": 0.0, "end": 1.0}],
            [{"w": "next", "s": 1.005, "e": 1.20}], 2.0, 24,
        )
        self.assertEqual(mapped, [])

    def test_cut_well_inside_a_word_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "cut crosses word"):
            edit.timeline(
                [{"start": 0.0, "end": 0.60}],
                [{"w": "spoken", "s": 0.40, "e": 0.80}], 2.0, 24,
            )


class ReviewContextTests(unittest.TestCase):
    def test_feedback_is_bound_to_revision_and_wrong_source_is_refused(self):
        with tempfile.TemporaryDirectory(prefix="pt-edit-review-") as temporary:
            root = Path(temporary)
            source = root / "source.mp4"
            candidate = root / "candidate.mp4"
            plan = root / "plan.json"
            timeline_path = root / "timeline.json"
            output = root / "render"
            output.mkdir()
            source.write_bytes(b"synthetic source identity")
            candidate.write_bytes(b"synthetic candidate identity")
            plan.write_text('{"version":"test-v1"}\n', encoding="utf-8")
            timeline = [
                {"source_start": 2.0, "source_end": 3.0,
                 "output_start": 0.0, "output_end": 1.0, "reason": "Hook"},
                {"source_start": 0.0, "source_end": 1.0,
                 "output_start": 1.0, "output_end": 2.0, "reason": "Context"},
            ]
            timeline_path.write_text(json.dumps(timeline), encoding="utf-8")
            (output / "candidate.mp4").write_bytes(candidate.read_bytes())
            (output / "plan.json").write_bytes(plan.read_bytes())
            (output / "timeline.json").write_bytes(timeline_path.read_bytes())
            receipt = {
                "status": "REVIEW_CANDIDATE", "version": "test-v1",
                "source_sha256": file_sha(source), "output_sha256": file_sha(candidate),
                "input_plan_sha256": file_sha(plan), "saved_plan_sha256": file_sha(plan),
                "timeline_sha256": file_sha(timeline_path),
                "expected_duration": 2.0, "actual_duration": 2.0,
            }
            (output / "receipt.json").write_text(json.dumps(receipt), encoding="utf-8")

            page = review.build_review(output, source)
            page_text = page.read_text(encoding="utf-8")
            self.assertIn("pt-video-editing-feedback/v2", page_text)
            self.assertIn(receipt["output_sha256"], page_text)
            self.assertIn(receipt["source_sha256"], page_text)
            self.assertIn(receipt["timeline_sha256"], page_text)
            self.assertEqual(review.source_context_at(timeline, 0.5)["source_time_seconds"], 2.5)
            self.assertEqual(review.source_context_at(timeline, 1.5)["source_time_seconds"], 0.5)

            old_receipt = dict(receipt)
            old_receipt.pop("timeline_sha256")
            (output / "receipt.json").write_text(json.dumps(old_receipt), encoding="utf-8")
            self.assertEqual(len(review.load_context(output, source)[3]), 2)

            wrong_source = root / "wrong-source.mp4"
            wrong_source.write_bytes(b"different source")
            with self.assertRaisesRegex(ValueError, "source video hash does not match"):
                review.load_context(output, wrong_source)


class RenderRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            raise unittest.SkipTest("ffmpeg and ffprobe are required for synthetic media tests")
        cls.temp = tempfile.TemporaryDirectory(prefix="pt-edit-media-")
        cls.root = Path(cls.temp.name)
        cls.source = cls.root / "synthetic-source.mkv"
        cls.words = cls.root / "words.json"
        cls.words.write_text("[]\n", encoding="utf-8")
        inputs = ["ffmpeg", "-nostdin", "-y", "-v", "error",
                  "-f", "lavfi", "-i", "testsrc2=size=320x480:rate=24:duration=4"]
        for frequency in (440, 880, 660, 990):
            inputs.extend(["-f", "lavfi", "-i",
                           f"sine=frequency={frequency}:sample_rate=48000:duration=1"])
        inputs.extend([
            "-filter_complex", "[1:a][2:a][3:a][4:a]concat=n=4:v=0:a=1[a]",
            "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "ultrafast",
            "-crf", "12", "-c:a", "pcm_s16le", "-shortest", cls.source,
        ])
        run(inputs)

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "temp", None):
            cls.temp.cleanup()

    def write_plan(self, path, output, music=None):
        plan = {
            "version": "synthetic-v001",
            "source": str(self.source),
            "words": str(self.words),
            "segments": [
                {"start": 2.0, "end": 3.0, "reason": "Move highlighted line first"},
                {"start": 0.0, "end": 1.0, "reason": "Keep opening context"},
            ],
            "fps": 24,
            "captions": False,
        }
        if music:
            plan["music"] = music
        path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
        return plan

    def render(self, plan_path, output):
        return subprocess.run(
            [sys.executable, str(EDIT_SCRIPT), "render", str(plan_path), str(output)],
            capture_output=True, text=True,
        )

    def test_failed_render_cleans_staging_then_same_path_renders_synced_av(self):
        output = self.root / "retry-output"
        plan_path = self.root / "plan.json"
        self.write_plan(plan_path, output, music="missing-music.wav")
        failed = self.render(plan_path, output)
        self.assertNotEqual(failed.returncode, 0)
        self.assertIn("No such file", failed.stderr)
        self.assertFalse(output.exists())
        self.assertEqual(list(self.root.glob(".retry-output.rendering-*")), [])

        self.write_plan(plan_path, output)
        rendered = self.render(plan_path, output)
        self.assertEqual(rendered.returncode, 0, rendered.stderr)
        receipt = json.loads((output / "receipt.json").read_text(encoding="utf-8"))
        self.assertAlmostEqual(receipt["expected_duration"], 2.0, places=3)

        source_frame = frame_rgb(self.source, "2.5")
        output_frame = frame_rgb(output / "clean.mkv", "0.5")
        mean_error = sum(abs(a - b) for a, b in zip(source_frame, output_frame)) / len(source_frame)
        self.assertLess(mean_error, 12.0)
        first_audio = audio_f32(output / "candidate.mp4", "0.2", "0.5")
        second_audio = audio_f32(output / "candidate.mp4", "1.2", "0.5")
        self.assertGreater(goertzel_power(first_audio, 660), goertzel_power(first_audio, 440) * 20)
        self.assertGreater(goertzel_power(second_audio, 440), goertzel_power(second_audio, 660) * 20)


    # Opt-in rendered-pixel and browser-export regression; needs local Playwright/Chromium.
    def browser_or_skip(self):
        if os.environ.get(BROWSER_TEST_ENV) != "1":
            self.skipTest(f"set {BROWSER_TEST_ENV}=1 to run Playwright/Chromium tests")
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is unavailable; install the local Playwright test dependency")
        loaded = subprocess.run([node, "-e", "require('playwright')"], capture_output=True, text=True)
        if loaded.returncode:
            self.skipTest("Playwright is unavailable; install it locally and configure NODE_PATH")
        try:
            probe = subprocess.run([
                node, "-e",
                "require('playwright').chromium.launch().then(b=>b.close()).catch(e=>{console.error(e);process.exit(1)})",
            ], capture_output=True, text=True, timeout=15)
        except subprocess.TimeoutExpired:
            self.skipTest("Playwright Chromium did not launch within 15 seconds")
        if probe.returncode:
            self.skipTest("Playwright Chromium cannot launch here: " + probe.stderr[-400:])
        return node

    def test_rendered_overlays_stay_safe_and_review_export_maps_source_time(self):
        node = self.browser_or_skip()
        output = self.root / "browser-output"
        plan_path = self.root / "browser-plan.json"
        plan = self.write_plan(plan_path, output)
        plan.update({
            "captions": True,
            "caption_y": 0.72,
            "caption_groups": [{"start": 0.15, "end": 1.85,
                                "text": "这是字幕安全区横向边界检查"}],
            "safe_rect": [0.20, 0.10, 0.60, 0.70],
            "cards": [{"start": 0.0, "end": 0.8, "text": "Short hook",
                       "x": 0.25, "y": 0.18, "w": 0.50, "h": 0.14}],
        })
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        rendered = self.render(plan_path, output)
        self.assertEqual(rendered.returncode, 0, rendered.stderr)

        clean = frame_rgb(output / "clean.mkv", "0.5")
        candidate = frame_rgb(output / "candidate.mp4", "0.5")
        width = 320
        changed = []
        for offset in range(0, len(candidate), 3):
            delta = max(abs(candidate[offset + channel] - clean[offset + channel]) for channel in range(3))
            if delta > 90:
                pixel = offset // 3
                changed.append((pixel % width, pixel // width))
        self.assertTrue(changed, "no rendered overlay pixels were found")
        self.assertTrue(all(62 <= x <= 258 and 46 <= y <= 386 for x, y in changed),
                        "rendered subtitle/card pixels escaped the configured safe rectangle")

        page = review.build_review(output, self.source)
        server = subprocess.Popen(
            [sys.executable, str(SERVE_SCRIPT), str(output), "--port", "0"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        helper = self.root / "review-browser.cjs"
        helper.write_text(r"""
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({acceptDownloads:true});
  await page.goto(process.argv[2]);
  await page.waitForFunction(()=>document.querySelector('#saved').textContent==='Timeline map loaded.');
  await page.waitForFunction(()=>document.querySelector('#edit').readyState>=1);
  await page.evaluate(()=>{document.querySelector('#edit').currentTime=.5});
  await page.waitForFunction(()=>Math.abs(document.querySelector('#edit').currentTime-.5)<.04);
  await page.fill('#comment','Move this card down');
  await page.click('#add');
  await page.selectOption('#decision','changes_requested');
  const [download]=await Promise.all([page.waitForEvent('download'),page.click('#export')]);
  await download.saveAs(process.argv[3]);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
""", encoding="utf-8")
        try:
            url = server.stdout.readline().strip()
            self.assertIn("http://127.0.0.1:", url, "local review server did not start")
            feedback_path = self.root / "feedback.json"
            result = subprocess.run([node, helper, url, feedback_path], capture_output=True,
                                    text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            feedback = json.loads(feedback_path.read_text(encoding="utf-8"))
            self.assertEqual(feedback["schema"], "pt-video-editing-feedback/v2")
            self.assertEqual(feedback["status"], "changes_requested")
            self.assertEqual(feedback["comments"][0]["output_time_seconds"], 0.5)
            self.assertEqual(feedback["comments"][0]["source_context"]["source_time_seconds"], 2.5)
            self.assertEqual(feedback["comments"][0]["source_context"]["segment_index"], 0)
        finally:
            server.terminate()
            try:
                server.wait(timeout=3)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=3)
            if server.stdout:
                server.stdout.close()
            if server.stderr:
                server.stderr.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
