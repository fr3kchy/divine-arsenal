#!/usr/bin/env python3
"""Read-only health diagnostics for a Hermes profile."""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
SKILLS_DIR = HERMES_HOME / "skills"
CRON_DIR = HERMES_HOME / "cron"
VOICE_DIR = HERMES_HOME / "voice"
REPORT_DIR = HERMES_HOME / "self-improve" / "reports"
SCORE = {"pass": 0, "fail": 0, "warn": 0, "fixes_applied": 0}


def find_issues(root_dir, name):
    issues = []
    if not root_dir.exists():
        return [f"{name} directory not found: {root_dir}"], 0
    files_found = 0
    for f in root_dir.rglob("*"):
        if not f.is_file() or f.name == ".gitkeep" or f.suffix == ".pyc":
            continue
        files_found += 1
        try:
            content = f.read_text(errors="replace")
            if "TODO" in content:
                issues.append(f"{f.relative_to(HERMES_HOME)} has TODO marker")
            if "FIXME" in content:
                issues.append(f"{f.relative_to(HERMES_HOME)} has FIXME marker")
        except OSError as exc:
            issues.append(f"{f.relative_to(HERMES_HOME)}: {exc}")
    if files_found == 0:
        issues.append(f"{name} directory is empty")
    return issues, files_found


def check_skills():
    issues = []
    if not SKILLS_DIR.exists():
        SCORE["warn"] += 1
        return ["Skills directory not found"]
    count = 0
    for skill_file in SKILLS_DIR.rglob("SKILL.md"):
        count += 1
        try:
            content = skill_file.read_text(encoding="utf-8")
            if not content.startswith("---"):
                issues.append(f"{skill_file.relative_to(HERMES_HOME)} missing frontmatter")
            in_code = False
            for line in content.splitlines():
                if line.strip().startswith("```"):
                    in_code = not in_code
                elif not in_code and any(token in line for token in ("TODO:", "FIXME:", "// TODO")):
                    if not any(word in line.lower() for word in ("todos", "stale", "check")):
                        issues.append(f"{skill_file.relative_to(HERMES_HOME)} has TODO/FIXME")
                        break
        except (OSError, UnicodeError) as exc:
            issues.append(f"{skill_file}: {exc}")
    if count == 0:
        issues.append("No skill files found")
    SCORE["warn"] += len(issues)
    SCORE["pass"] += count
    return issues


def check_memory():
    import yaml
    issues = []
    try:
        config_path = HERMES_HOME / "config.yaml"
        config = yaml.safe_load(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
        settings = (config or {}).get("memory", {}) or {}
        stores = (("MEMORY.md", "memory_enabled", "memory_char_limit", 2200),
                  ("USER.md", "user_profile_enabled", "user_char_limit", 1375))
        observed = 0
        for filename, enabled_key, limit_key, default_limit in stores:
            if settings.get(enabled_key, True) is False:
                continue
            path = HERMES_HOME / "memories" / filename
            if not path.exists():
                continue
            observed += 1
            limit = int(settings.get(limit_key, default_limit))
            if limit <= 0:
                raise ValueError(f"{limit_key} must be positive")
            used = len(path.read_text(encoding="utf-8").strip())
            if used > limit:
                issues.append(f"{filename}: {used}/{limit} characters; review before new writes")
        if not observed:
            issues.append("No enabled built-in memory files found; usage unverified")
    except (OSError, UnicodeError, ValueError, TypeError, AttributeError, yaml.YAMLError) as exc:
        issues.append(f"Memory check unavailable: {type(exc).__name__}")
    SCORE["warn" if issues else "pass"] += 1
    return issues


def check_cron():
    path = CRON_DIR / "executions.db"
    if not path.exists():
        SCORE["warn"] += 1
        return ["Cron execution history unavailable; not verified healthy"]
    try:
        conn = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=2)
        try:
            rows = conn.execute("SELECT job_id, status, claimed_at FROM executions ORDER BY claimed_at DESC LIMIT 30").fetchall()
        finally:
            conn.close()
    except sqlite3.Error as exc:
        SCORE["warn"] += 1
        return [f"Cron execution history unreadable: {type(exc).__name__}"]
    if not rows:
        SCORE["warn"] += 1
        return ["No cron execution attempts recorded; schedule unverified"]
    failures = [f"Cron {job}: {status} at {at}" for job, status, at in rows if status == "failed"]
    unknown = [f"Cron {job}: unknown outcome at {at}" for job, status, at in rows if status == "unknown"]
    if failures:
        SCORE["fail"] += 1
    if unknown:
        SCORE["warn"] += 1
    if not failures and not unknown:
        if any(status == "completed" for _, status, _ in rows):
            SCORE["pass"] += 1
        else:
            SCORE["warn"] += 1
            unknown.append("Cron attempts exist but none has completed in the inspected window")
    return failures + unknown


def check_voice():
    voice_file = VOICE_DIR / "voice.py"
    if not voice_file.exists():
        SCORE["fail"] += 1
        return [f"Voice module not found at {voice_file}"]
    try:
        sys.path.insert(0, str(VOICE_DIR))
        from voice import list_voices
        count = len(list_voices())
        if count >= 20:
            SCORE["pass"] += 1
            return []
        SCORE["warn"] += 1
        return [f"Only {count} voices available (expected 20+)"]
    except Exception as exc:
        SCORE["fail"] += 1
        return [f"Voice import failed: {type(exc).__name__}"]


def check_npu():
    try:
        sys.path.insert(0, str(VOICE_DIR))
        from npu_orch import probe
        accel = probe()
    except Exception as exc:
        SCORE["warn"] += 1
        return [f"Accelerator check unavailable: {type(exc).__name__}"]
    issues = []
    for key, label in (("rocm", "ROCm iGPU"), ("vitisai", "VitisAI NPU")):
        if accel.get(key):
            SCORE["pass"] += 1
        else:
            SCORE["warn"] += 1
            issues.append(f"{label} not detected")
    return issues


def check_divine_arsenal():
    path = Path.home() / "repos" / "divine-arsenal"
    if not path.exists():
        SCORE["warn"] += 1
        return ["divine-arsenal repo not found"]
    SCORE["pass"] += 1
    return []


def compute_scorecard():
    health = "degraded" if SCORE["fail"] else ("warning" if SCORE["warn"] else "healthy")
    return {"timestamp": datetime.now(timezone.utc).isoformat(), "score": dict(SCORE),
            "health": health, "scope": "local diagnostics; counters are not an availability percentage"}


def generate_speech_report(scorecard, issues):
    return ". ".join([f"Self improvement audit complete. System health is {scorecard['health']}", *issues[:5]])


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only checks; writes a diagnostic report only")
    parser.add_argument("--extended", action="store_true", help="Also probe voice, accelerators, and Divine Arsenal")
    parser.add_argument("--speak", action="store_true", help="Opt into local spoken summary")
    args = parser.parse_args(argv)
    SCORE.update({"pass": 0, "fail": 0, "warn": 0, "fixes_applied": 0})
    checks = [("skills", check_skills), ("memory", check_memory), ("cron", check_cron)]
    if args.extended:
        checks.extend([("voice", check_voice), ("accelerators", check_npu), ("divine_arsenal", check_divine_arsenal)])
    findings = {}
    for name, check in checks:
        try:
            findings[name] = check()
        except Exception as exc:
            SCORE["fail"] += 1
            findings[name] = [f"{name} check failed: {type(exc).__name__}"]
    scorecard = compute_scorecard()
    scorecard["issues"] = findings
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"audit-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}.json"
    report_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
    print(json.dumps(scorecard, indent=2))
    print(f"Report saved: {report_path}")
    if args.speak:
        try:
            sys.path.insert(0, str(VOICE_DIR))
            from voice import speak
            speak(generate_speech_report(scorecard, [x for xs in findings.values() for x in xs]), voice="af_bella", speed=1.33)
        except Exception as exc:
            print(f"Speech unavailable: {type(exc).__name__}; diagnostic report preserved", file=sys.stderr)
    return 1 if SCORE["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
