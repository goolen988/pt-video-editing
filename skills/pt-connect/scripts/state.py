#!/usr/bin/env python3
"""Maintain project-local, credential-free PT Connect setup receipts."""
import argparse
import datetime
import hashlib
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path


SCHEMA_VERSION = 1
STATE_NAME = ".pt-connect.json"
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
LANGUAGE = re.compile(r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$")


def now():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def project_root(value):
    root = Path(value).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("workspace must be an existing directory")
    return root


def host_id(value):
    value = value or platform.node() or socket.gethostname() or platform.system()
    value = value.strip()
    if not value or len(value) > 128 or any(ord(char) < 32 for char in value):
        raise ValueError("host id must be 1-128 printable characters")
    return value


def checked_key(value, label):
    value = value.strip()
    if not SLUG.fullmatch(value):
        raise ValueError("{} must be a short lowercase id (letters, digits, dot, underscore, hyphen)".format(label))
    return value


def empty_state():
    timestamp = now()
    return {
        "schema_version": SCHEMA_VERSION,
        "created_at": timestamp,
        "updated_at": timestamp,
        "user_language": None,
        "hosts": {},
        "explanations": {},
        "services": {},
        "smokes": [],
    }


def state_path(root):
    path = root / STATE_NAME
    if path.is_symlink():
        raise ValueError("{} must not be a symlink".format(STATE_NAME))
    return path


def load_state(root):
    path = state_path(root)
    if not path.exists():
        return empty_state(), False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("cannot read {}: {}".format(STATE_NAME, error))
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported or invalid {} schema; preserve the file and inspect it before repair".format(STATE_NAME))
    allowed_fields = {"schema_version", "created_at", "updated_at", "user_language", "hosts", "explanations", "services", "smokes"}
    if set(data) - allowed_fields:
        raise ValueError("unrecognized fields in {}; preserve the file and inspect it before repair".format(STATE_NAME))
    expected = {"hosts": dict, "explanations": dict, "services": dict, "smokes": list}
    for key, kind in expected.items():
        if key not in data:
            data[key] = kind()
        if not isinstance(data[key], kind):
            raise ValueError("invalid {} field in {}".format(key, STATE_NAME))
    data.setdefault("created_at", now())
    data.setdefault("user_language", None)
    data.setdefault("updated_at", data["created_at"])
    return data, True


def save_state(root, data):
    path = state_path(root)
    data["updated_at"] = now()
    temporary = None
    try:
        fd, name = tempfile.mkstemp(prefix=".pt-connect-", suffix=".tmp", dir=str(root))
        temporary = Path(name)
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(str(temporary), str(path))
        temporary = None
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except OSError:
                pass


def tool_inventory():
    inventory = {}
    for tool in ("python3", "ffmpeg", "ffprobe", "node", "yt-dlp"):
        executable = shutil.which(tool)
        entry = {"present": bool(executable)}
        if executable:
            flag = "-version" if tool in ("ffmpeg", "ffprobe") else "--version"
            try:
                result = subprocess.run(
                    [executable, flag], capture_output=True, text=True, timeout=8
                )
                lines = (result.stdout or result.stderr).splitlines()
                entry["version"] = lines[0][:240] if lines else "UNKNOWN"
            except (OSError, subprocess.TimeoutExpired):
                entry["version"] = "UNKNOWN"
        inventory[tool] = entry
    return inventory


def check_access(root):
    access = {"workspace_exists": root.is_dir(), "workspace_read": False, "workspace_write": False, "command_execution": False}
    try:
        with os.scandir(str(root)) as entries:
            next(entries, None)
        access["workspace_read"] = True
    except OSError:
        pass
    try:
        with tempfile.TemporaryDirectory(prefix=".pt-connect-probe-", dir=str(root)) as probe:
            test_file = Path(probe) / "probe"
            test_file.write_text("ok", encoding="utf-8")
            access["workspace_write"] = test_file.read_text(encoding="utf-8") == "ok"
    except OSError:
        pass
    try:
        result = subprocess.run(
            [sys.executable, "-c", "print('pt-connect-command-check')"],
            capture_output=True, text=True, timeout=8,
        )
        access["command_execution"] = result.returncode == 0 and "pt-connect-command-check" in result.stdout
    except (OSError, subprocess.TimeoutExpired):
        pass
    return access


def view(root, selected_host, state_exists, state, operation):
    host_entry = state["hosts"].get(selected_host, {})
    checks = host_entry.get("checks", []) if isinstance(host_entry, dict) else []
    host = checks[-1] if checks else None
    return {
        "operation": operation,
        "state_exists": state_exists,
        "state_file": str(root / STATE_NAME),
        "selected_host": selected_host,
        "user_language": state.get("user_language"),
        "host_check": host,
        "host_check_history": checks,
        "known_hosts": sorted(state["hosts"].keys()),
        "completed_explanations": state["explanations"],
        "services_for_selected_host": state["services"].get(selected_host, {}),
        "smokes_for_selected_host": [item for item in state["smokes"] if item.get("host_id") == selected_host],
    }


def record_check(root, selected_host):
    state, _ = load_state(root)
    host = state["hosts"].setdefault(selected_host, {"checks": []})
    if not isinstance(host, dict) or not isinstance(host.setdefault("checks", []), list):
        raise ValueError("invalid host check history in {}".format(STATE_NAME))
    host["checks"].append({
        "checked_at": now(),
        "platform": platform.platform(),
        "access": check_access(root),
        # Tool presence/version is discovery only; task capability needs a real smoke below.
        "tools": tool_inventory(),
    })
    save_state(root, state)
    return view(root, selected_host, True, state, "check")


def record_explanation(root, selected_host, topic, language):
    topic = checked_key(topic, "topic")
    if not LANGUAGE.fullmatch(language):
        raise ValueError("language must be a language tag such as en or zh-CN")
    state, _ = load_state(root)
    state["user_language"] = language
    topics = state["explanations"].setdefault(topic, {})
    # Repeating a receipt does not remove any prior topic/language completion.
    topics.setdefault(language, now())
    save_state(root, state)
    return view(root, selected_host, True, state, "record-explanation")


def record_login(root, selected_host, service, status):
    service = checked_key(service, "service")
    if status not in ("pending", "verified", "not-required"):
        raise ValueError("status must be pending, verified, or not-required")
    state, _ = load_state(root)
    host_services = state["services"].setdefault(selected_host, {})
    host_services[service] = {"status": status, "updated_at": now()}
    save_state(root, state)
    return view(root, selected_host, True, state, "record-login")


def artifact_receipt(root, raw_path):
    path = Path(raw_path).expanduser().resolve(strict=True)
    if not path.is_file():
        raise ValueError("smoke artifact must be an existing file")
    try:
        relative = path.relative_to(root)
    except ValueError:
        raise ValueError("smoke artifact must be inside the project workspace")
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
    return {"path": relative.as_posix(), "sha256": digest.hexdigest(), "size_bytes": size}


def record_smoke(root, selected_host, capability, result, artifact):
    capability = checked_key(capability, "capability")
    if result not in ("passed", "failed"):
        raise ValueError("result must be passed or failed")
    if result == "passed" and not artifact:
        raise ValueError("a passed smoke requires an actual artifact inside the workspace")
    receipt = artifact_receipt(root, artifact) if artifact else None
    state, _ = load_state(root)
    state["smokes"].append({
        "host_id": selected_host,
        "capability": capability,
        "result": result,
        "checked_at": now(),
        "artifact": receipt,
    })
    save_state(root, state)
    return view(root, selected_host, True, state, "record-smoke")


def main():
    parser = argparse.ArgumentParser(description="Read or update credential-free PT Connect setup receipts in a project.")
    parser.add_argument("command", choices=("status", "check", "record-explanation", "record-login", "record-smoke"))
    parser.add_argument("--workspace", required=True, help="existing authorized project directory")
    parser.add_argument("--host-id", help="stable local host label; defaults to this machine's host name")
    parser.add_argument("--topic", help="explanation topic id")
    parser.add_argument("--language", help="language used for an explanation that was actually delivered")
    parser.add_argument("--service", help="short service id for host-specific login state")
    parser.add_argument("--status", help="service status: pending, verified, or not-required")
    parser.add_argument("--capability", help="capability tested by a real local operation")
    parser.add_argument("--result", help="smoke result: passed or failed")
    parser.add_argument("--artifact", help="actual smoke output file inside the workspace")
    args = parser.parse_args()
    try:
        root = project_root(args.workspace)
        selected_host = host_id(args.host_id)
        if args.command == "status":
            state, exists = load_state(root)
            result = view(root, selected_host, exists, state, "status")
        elif args.command == "check":
            result = record_check(root, selected_host)
        elif args.command == "record-explanation":
            if not args.topic or not args.language:
                raise ValueError("record-explanation requires --topic and --language")
            result = record_explanation(root, selected_host, args.topic, args.language)
        elif args.command == "record-login":
            if not args.service or not args.status:
                raise ValueError("record-login requires --service and --status")
            result = record_login(root, selected_host, args.service, args.status)
        else:
            if not args.capability or not args.result:
                raise ValueError("record-smoke requires --capability and --result")
            result = record_smoke(root, selected_host, args.capability, args.result, args.artifact)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as error:
        print("pt-connect: {}".format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
