"""Offline checks for bootstrap validation and complete local-bundle installation."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("instructor_bootstrap", SOURCE / "bootstrap.py")
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)


class BootstrapManifestTest(unittest.TestCase):
    def manifest(self):
        return {"version": "0.1.0", "files": {
            "harness.py": "a" * 64,
            "defaults.json": "b" * 64,
            "templates/lesson-plan.md": "c" * 64,
        }}

    def test_bad_paths_missing_required_and_case_collisions_rejected(self):
        for path in ["../escape.py", "/absolute", "templates/../escape.md", "templates/./lesson.md", "templates\\outside.md", "C:/escape.py", "secrets.json"]:
            with self.subTest(path=path):
                manifest = self.manifest()
                manifest["files"][path] = "e" * 64
                with self.assertRaises(ValueError):
                    bootstrap.validate_manifest(manifest)
        missing = self.manifest()
        del missing["files"]["harness.py"]
        with self.assertRaises(ValueError):
            bootstrap.validate_manifest(missing)
        collision = self.manifest()
        collision["files"]["templates/Lesson-Plan.md"] = "d" * 64
        with self.assertRaises(ValueError):
            bootstrap.validate_manifest(collision)

    def test_malformed_manifest_is_a_validation_error(self):
        for bad in [None, [], "manifest", {"files": []}, {"files": {}}]:
            with self.subTest(manifest=bad):
                with self.assertRaises(ValueError):
                    bootstrap.validate_manifest(bad)

    def test_local_bootstrap_installs_verified_bundle_with_unicode_space_paths(self):
        with tempfile.TemporaryDirectory(prefix="instructor-bootstrap-") as temporary:
            base = Path(temporary)
            source = base / "오프라인 배포본"
            source.mkdir()
            shutil.copy2(SOURCE / "harness.py", source / "harness.py")
            defaults = {"role": "교관", "courses": "일반 교수법", "audience": "성인 학습자", "session_minutes": 50,
                        "tasks": ["강의안"], "tone": "간결한 한국어", "agent": "manual"}
            (source / "defaults.json").write_text(json.dumps(defaults, ensure_ascii=False), encoding="utf-8")
            template = source / "templates/lesson-plan.md"
            template.parent.mkdir()
            template.write_text("# 공개 수업 계획", encoding="utf-8")
            skills = source / "skills/instructor-start/SKILL.md"
            skills.parent.mkdir(parents=True)
            skills.write_text("---\nname: instructor-start\ndescription: Start.\n---\n설정을 시작합니다.\n", encoding="utf-8")
            manifest = {"version": "0.1.0", "files": {
                path.relative_to(source).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in source.rglob("*") if path.is_file()
            }}
            (source / "bundle.json").write_text(json.dumps(manifest), encoding="utf-8")
            root = base / "설치 도구"
            workspace = base / "교관 작업실"
            result = subprocess.run([
                sys.executable, str(SOURCE / "bootstrap.py"), "--source", str(source),
                "--root", str(root), "--workspace", str(workspace), "--agent", "manual", "--non-interactive",
            ], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((root / "bundle/harness.py").exists())
            profile = json.loads((workspace / ".harness/profile.json").read_text(encoding="utf-8"))
            self.assertEqual(profile["role"], "교관")
            self.assertEqual(profile["workspace"], str(workspace.resolve()))
            self.assertEqual((workspace / "templates/lesson-plan.md").read_text(encoding="utf-8"), "# 공개 수업 계획")


if __name__ == "__main__":
    unittest.main()
