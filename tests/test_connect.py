import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/pt-connect/scripts/state.py"
EVALUATION_ROOT = ROOT.parents[1] / "public/Video Editing/.local/skill-evaluation/pt-connect-workspace"


class ConnectState(unittest.TestCase):
    def setUp(self):
        EVALUATION_ROOT.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="test-connect-", dir=str(EVALUATION_ROOT))
        self.workspace = Path(self.temporary.name)
        (self.workspace / "artifacts").mkdir()

    def tearDown(self):
        self.temporary.cleanup()

    def invoke(self, command, *args, success=True):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), command, "--workspace", str(self.workspace), *args],
            capture_output=True,
            text=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def test_first_setup_resume_preserves_receipts_and_scopes_them_to_host(self):
        empty = self.invoke("status", "--host-id", "host-a")
        self.assertFalse(empty["state_exists"])
        self.assertFalse((self.workspace / ".pt-connect.json").exists())

        first_check = self.invoke("check", "--host-id", "host-a")
        self.assertTrue(all(first_check["host_check"]["access"].values()))
        self.assertNotIn("verified", json.dumps(first_check["host_check"]["tools"]))

        self.invoke("record-explanation", "--host-id", "host-a", "--topic", "first-setup", "--language", "zh-CN")
        self.invoke("record-explanation", "--host-id", "host-a", "--topic", "first-setup", "--language", "zh-CN")
        self.invoke("record-explanation", "--host-id", "host-a", "--topic", "first-setup", "--language", "en")
        self.invoke("record-login", "--host-id", "host-a", "--service", "browser-login", "--status", "pending")
        artifact = self.workspace / "artifacts" / "smoke.txt"
        artifact.write_bytes(b"actual local smoke output\n")
        passed = self.invoke(
            "record-smoke", "--host-id", "host-a", "--capability", "ffmpeg-render",
            "--result", "passed", "--artifact", str(artifact),
        )
        receipt = passed["smokes_for_selected_host"][-1]
        self.assertEqual(receipt["artifact"]["path"], "artifacts/smoke.txt")
        self.assertEqual(receipt["artifact"]["sha256"], hashlib.sha256(artifact.read_bytes()).hexdigest())

        resumed = self.invoke("check", "--host-id", "host-a")
        self.assertEqual(set(resumed["completed_explanations"]["first-setup"]), {"zh-CN", "en"})
        self.assertEqual(resumed["user_language"], "en")
        self.assertEqual(len(resumed["host_check_history"]), 2)
        self.assertEqual(resumed["services_for_selected_host"]["browser-login"]["status"], "pending")
        self.assertEqual(len(resumed["smokes_for_selected_host"]), 1)
        state_file = self.workspace / ".pt-connect.json"
        self.assertEqual(os.stat(state_file).st_mode & 0o777, 0o600)
        saved = json.loads(state_file.read_text(encoding="utf-8"))
        self.assertNotIn("password", json.dumps(saved).lower())
        self.assertNotIn("token", json.dumps(saved).lower())

        second_host = self.invoke("check", "--host-id", "host-b")
        self.assertEqual(second_host["known_hosts"], ["host-a", "host-b"])
        self.assertTrue(all(second_host["host_check"]["access"].values()))
        self.assertEqual(second_host["services_for_selected_host"], {})
        self.assertEqual(second_host["smokes_for_selected_host"], [])
        host_a = self.invoke("status", "--host-id", "host-a")
        self.assertEqual(len(host_a["smokes_for_selected_host"]), 1)
        self.assertEqual(len(host_a["host_check_history"]), 2)

    def test_smoke_requires_a_real_project_artifact_and_keeps_history(self):
        self.invoke("record-smoke", "--host-id", "host-a", "--capability", "transcription", "--result", "passed", success=False)
        outside = EVALUATION_ROOT / "outside-smoke.txt"
        outside.write_text("not in the project", encoding="utf-8")
        try:
            self.invoke(
                "record-smoke", "--host-id", "host-a", "--capability", "transcription",
                "--result", "passed", "--artifact", str(outside), success=False,
            )
        finally:
            outside.unlink(missing_ok=True)

        artifact = self.workspace / "artifacts" / "transcript.json"
        artifact.write_text('{"words": ["checked"]}', encoding="utf-8")
        self.invoke(
            "record-smoke", "--host-id", "host-a", "--capability", "transcription",
            "--result", "passed", "--artifact", str(artifact),
        )
        failed = self.invoke(
            "record-smoke", "--host-id", "host-a", "--capability", "transcription", "--result", "failed",
        )
        history = failed["smokes_for_selected_host"]
        self.assertEqual([item["result"] for item in history], ["passed", "failed"])
        self.assertIsNone(history[-1]["artifact"])

    def test_status_does_not_initialize_state_and_symlink_state_is_refused(self):
        status = self.invoke("status", "--host-id", "host-a")
        self.assertFalse(status["state_exists"])
        self.assertFalse((self.workspace / ".pt-connect.json").exists())

        target = self.workspace / "kept.json"
        target.write_text('{"preserve": true}', encoding="utf-8")
        (self.workspace / ".pt-connect.json").symlink_to(target)
        result = self.invoke("check", "--host-id", "host-a", success=False)
        self.assertIn("must not be a symlink", result.stderr)
        self.assertEqual(target.read_text(encoding="utf-8"), '{"preserve": true}')


if __name__ == "__main__":
    unittest.main()
