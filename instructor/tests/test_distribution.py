"""Exercise the actual workshop ZIP, including both desktop entry points."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile


SOURCE = Path(__file__).resolve().parents[1]


class DistributionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="instructor-distribution-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.base = Path(cls.temporary.name)
        cls.archive = cls.base / "공군 교관 에디션.zip"
        result = subprocess.run([
            sys.executable, str(SOURCE / "build_bundle.py"), "--check", "--zip", str(cls.archive),
        ], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)

    def test_packaged_runtime_checksums_and_release_version_match(self):
        checksum = self.archive.with_suffix(".zip.sha256").read_text(encoding="utf-8").split()[0]
        self.assertEqual(hashlib.sha256(self.archive.read_bytes()).hexdigest(), checksum)
        with zipfile.ZipFile(self.archive) as archive:
            self.assertIsNone(archive.testzip())
            prefix = "nalssam-instructor/"
            manifest = json.loads(archive.read(prefix + "bundle.json"))
            for name, expected in manifest["files"].items():
                self.assertEqual(hashlib.sha256(archive.read(prefix + name)).hexdigest(), expected, name)
            runtime = ast.parse(archive.read(prefix + "harness.py").decode("utf-8"))
            versions = [ast.literal_eval(node.value) for node in runtime.body
                        if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == "VERSION"
                                for target in node.targets)]
            self.assertEqual(versions, [manifest["version"]])
            self.assertEqual(manifest["version"], "0.1.1")

    def test_both_desktop_entry_points_are_shippable(self):
        with zipfile.ZipFile(self.archive) as archive:
            prefix = "nalssam-instructor/"
            mac = archive.getinfo(prefix + "공군교관설치.command")
            self.assertTrue(stat.S_IMODE(mac.external_attr >> 16) & stat.S_IXUSR,
                            "Mac double-click launcher must retain execute permission in the ZIP")
            self.assertTrue(archive.read(prefix + "공군교관설치.cmd"))
            self.assertTrue(archive.read(prefix + "install.ps1").startswith(b"\xef\xbb\xbf"),
                            "Windows PowerShell 5.1 needs UTF-8 BOM for Korean script text")
            guide = archive.read(prefix + "README.md").decode("utf-8")
            self.assertIn("공군 교관 에디션", guide)
            self.assertIn("공군교관설치.command", guide)
            self.assertIn("공군교관설치.cmd", guide)

    def test_extracted_zip_installs_offline_with_korean_space_paths(self):
        extracted = self.base / "한글 이름 배포 폴더"
        with zipfile.ZipFile(self.archive) as archive:
            archive.extractall(extracted)
        source = extracted / "nalssam-instructor"
        root = self.base / "교관 도구 설치"
        workspace = self.base / "공개 수업 작업실"
        installed = subprocess.run([
            sys.executable, str(source / "bootstrap.py"), "--source", str(source),
            "--root", str(root), "--workspace", str(workspace), "--agent", "both",
            "--non-interactive",
        ], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30)
        self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
        report = subprocess.run([
            sys.executable, str(root / "bundle/harness.py"), "doctor", "--json",
        ], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=20)
        self.assertEqual(report.returncode, 0, report.stdout + report.stderr)
        data = json.loads(report.stdout)
        self.assertEqual(data["version"], "0.1.1")
        self.assertTrue(data["ready"])
        self.assertEqual(data["missing"], [])
        self.assertEqual(data["modified"], [])
        for host in (".agents", ".claude"):
            self.assertTrue((workspace / host / "skills/instructor-start/SKILL.md").is_file())
        self.assertIn("공군 교관 에디션", (workspace / "AGENTS.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
