"""Exercise the portable instructor installer without a network or global config writes."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
DEFAULTS = {
    "role": "교관",
    "courses": "일반 교수법",
    "audience": "성인 학습자",
    "session_minutes": 50,
    "tasks": ["강의안", "평가문항"],
    "tone": "명확하고 간결한 한국어",
    "agent": "manual",
}


class HarnessIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="instructor-harness-tests-")
        self.base = Path(self.temp.name)
        self.root = self.base / "installed tool"
        self.workspace = self.base / "교관 작업실"
        self.source = self.base / "bundle source"
        self.source.mkdir()
        shutil.copy2(SOURCE / "harness.py", self.source / "harness.py")
        (self.source / "defaults.json").write_text(json.dumps(DEFAULTS), encoding="utf-8")
        self.write_asset("skills/instructor-start/SKILL.md", "---\nname: instructor-start\ndescription: Setup.\n---\n설정 질문을 시작합니다.\n")
        self.write_asset("templates/lesson-plan.md", "# 수업 계획\n원본 템플릿\n")
        self.manifest(self.source)

    def tearDown(self):
        self.temp.cleanup()

    def write_asset(self, relative, content, source=None):
        file = (source or self.source) / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content, encoding="utf-8")
        return file

    def manifest(self, source, version="0.1.0"):
        files = {}
        for path in sorted(source.rglob("*")):
            if path.is_file() and path.name != "bundle.json":
                files[path.relative_to(source).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        value = {"version": version, "files": files}
        (source / "bundle.json").write_text(json.dumps(value, indent=2), encoding="utf-8")
        return value

    def run_cli(self, command, *args, expected=0, script=None):
        result = subprocess.run(
            [sys.executable, str(script or self.source / "harness.py"), command, "--root", str(self.root), *map(str, args)],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=20,
        )
        self.assertEqual(result.returncode, expected, result.stdout)
        return result

    def install(self, agent="manual"):
        return self.run_cli("install", "--workspace", self.workspace, "--agent", agent, "--non-interactive")

    def profile(self):
        return json.loads((self.workspace / ".harness/profile.json").read_text(encoding="utf-8"))

    def answers(self, value):
        path = self.base / "answers.json"
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return path

    def test_install_is_durable_and_scoped_to_selected_workspace(self):
        self.install(agent="codex")
        self.assertTrue((self.root / "bundle/harness.py").is_file())
        self.assertTrue((self.workspace / "AGENTS.md").is_file())
        self.assertTrue((self.workspace / ".agents/skills/instructor-start/SKILL.md").is_file())
        self.assertTrue((self.workspace / "templates/lesson-plan.md").is_file())
        self.assertEqual(self.profile()["agent"], "codex")
        shutil.rmtree(self.source)
        self.run_cli("doctor", script=self.root / "bundle/harness.py")

    def test_configure_persists_answers_and_preserves_preexisting_instructions(self):
        self.workspace.mkdir()
        (self.workspace / "AGENTS.md").write_text("사용자의 기존 규칙\n", encoding="utf-8")
        self.install()
        self.run_cli("configure", "--answers", self.answers({"role": "교수설계 교관", "courses": "공개 교육자료 작성", "session_minutes": 75, "tasks": ["실습 설계"]}))
        profile = self.profile()
        self.assertEqual(profile["role"], "교수설계 교관")
        self.assertEqual(profile["session_minutes"], 75)
        self.assertEqual(profile["tasks"], ["실습 설계"])
        self.assertEqual((self.workspace / "AGENTS.md").read_text(encoding="utf-8"), "사용자의 기존 규칙\n")
        self.assertTrue((self.workspace / ".harness/AGENTS.generated.md").is_file())

    def test_reinstall_does_not_reset_profile_or_overwrite_user_edits(self):
        self.install()
        self.run_cli("configure", "--answers", self.answers({"role": "맞춤 교관", "session_minutes": 90}))
        template = self.workspace / "templates/lesson-plan.md"
        template.write_text("내가 수정한 강의안\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(self.source / "harness.py"), "install", "--root", str(self.root), "--workspace", str(self.workspace), "--agent", "manual", "--non-interactive"], capture_output=True, text=True, timeout=20)
        self.assertIn(result.returncode, (0, 2), result.stdout + result.stderr)
        self.assertEqual(template.read_text(encoding="utf-8"), "내가 수정한 강의안\n")
        self.assertEqual(self.profile()["role"], "맞춤 교관")
        self.assertEqual(self.profile()["session_minutes"], 90)

    def test_custom_root_launcher_finds_its_installation_without_root_flag(self):
        self.install()
        launcher = self.root / ("bin/instructor.cmd" if os.name == "nt" else "bin/instructor")
        def run_launcher(*arguments):
            command = (["cmd", "/c", str(launcher)] if os.name == "nt" else [str(launcher)]) + list(map(str, arguments))
            result = subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return result
        report = json.loads(run_launcher("doctor", "--json").stdout)
        self.assertTrue(report["ready"])
        self.assertEqual(report["workspace"], str(self.workspace.resolve()))
        run_launcher("configure", "--answers", self.answers({"role": "실제 실행기 설정"}))
        self.assertEqual(self.profile()["role"], "실제 실행기 설정")

    def test_doctor_distinguishes_modified_runtime_from_user_templates(self):
        self.install()
        template = self.workspace / "templates/lesson-plan.md"
        template.write_text("사용자 편집", encoding="utf-8")
        report = json.loads(self.run_cli("doctor", "--json").stdout)
        self.assertTrue(report["ready"])
        runtime = self.root / "bundle/harness.py"
        runtime.write_text(runtime.read_text(encoding="utf-8") + "\n# local modification\n", encoding="utf-8")
        report = json.loads(self.run_cli("doctor", "--json", expected=2).stdout)
        self.assertFalse(report["ready"])
        self.assertIn(str(runtime), report["modified"])

    def test_configure_preserves_edited_template_while_changing_profile(self):
        self.install()
        template = self.workspace / "templates/lesson-plan.md"
        template.write_text("개인 편집본", encoding="utf-8")
        self.run_cli("configure", "--answers", self.answers({"role": "수정된 업무 설정"}))
        self.assertEqual(self.profile()["role"], "수정된 업무 설정")
        self.assertEqual(template.read_text(encoding="utf-8"), "개인 편집본")

    def test_invalid_configuration_does_not_change_saved_profile(self):
        self.install()
        path = self.workspace / ".harness/profile.json"
        before = path.read_bytes()
        for invalid in [{"session_minutes": 0}, {"agent": "unknown"}, {"api_key": "not-a-configuration-field"}]:
            with self.subTest(answers=invalid):
                self.run_cli("configure", "--answers", self.answers(invalid), expected=2)
                self.assertEqual(path.read_bytes(), before)

    @unittest.skipIf(sys.platform == "win32", "Creating symlinks requires a separate Windows permission.")
    def test_sync_refuses_symlinked_source_and_workspace_files(self):
        self.install()
        outside = self.base / "outside.txt"
        outside.write_text("기존 파일", encoding="utf-8")
        template = self.workspace / "templates/lesson-plan.md"
        template.unlink()
        template.symlink_to(outside)
        self.run_cli("sync", "--source", self.source, expected=2)
        self.assertEqual(outside.read_text(encoding="utf-8"), "기존 파일")
        template.unlink()
        template.write_text("복원된 사용자 파일", encoding="utf-8")
        source_template = self.source / "templates/lesson-plan.md"
        source_template.unlink()
        source_template.symlink_to(outside)
        self.manifest(self.source)
        self.run_cli("sync", "--source", self.source, expected=2)
        self.assertEqual(outside.read_text(encoding="utf-8"), "기존 파일")

    def test_export_excludes_course_files_state_and_machine_paths(self):
        self.install()
        (self.workspace / "personal-notes.txt").write_text("PRIVATE_SENTINEL", encoding="utf-8")
        output = self.base / "shared-profile.json"
        self.run_cli("export", "--output", output)
        text = output.read_text(encoding="utf-8")
        value = json.loads(text)
        self.assertNotIn("PRIVATE_SENTINEL", text)
        self.assertNotIn(str(self.workspace), text)
        self.assertNotIn(str(self.root), text)
        self.assertNotIn("workspace", value)
        self.assertNotIn("network.db", text)
        self.assertEqual(value["role"], self.profile()["role"])

    def test_sync_updates_unmodified_assets_without_replacing_profile(self):
        self.install()
        self.run_cli("configure", "--answers", self.answers({"role": "내 설정"}))
        updated = self.base / "updated bundle"
        shutil.copytree(self.source, updated)
        self.write_asset("templates/lesson-plan.md", "# 새 공통 템플릿\n", updated)
        self.manifest(updated, "0.1.1")
        self.run_cli("sync", "--source", updated)
        self.assertEqual((self.workspace / "templates/lesson-plan.md").read_text(encoding="utf-8"), "# 새 공통 템플릿\n")
        self.assertEqual(self.profile()["role"], "내 설정")

    def test_sync_preserves_modified_assets(self):
        self.install()
        path = self.workspace / "templates/lesson-plan.md"
        path.write_text("개인 편집본\n", encoding="utf-8")
        updated = self.base / "updated bundle"
        shutil.copytree(self.source, updated)
        self.write_asset("templates/lesson-plan.md", "배포 수정본\n", updated)
        self.manifest(updated, "0.1.1")
        result = subprocess.run([sys.executable, str(self.source / "harness.py"), "sync", "--root", str(self.root), "--source", str(updated)], capture_output=True, text=True, timeout=20)
        self.assertIn(result.returncode, (0, 2), result.stdout + result.stderr)
        self.assertEqual(path.read_text(encoding="utf-8"), "개인 편집본\n")

    def test_sync_rejects_corrupt_archive_members_and_unsafe_manifest_paths(self):
        self.install()
        template = self.workspace / "templates/lesson-plan.md"
        original = template.read_bytes()
        self.write_asset("templates/lesson-plan.md", "고정 해시와 다른 내용\n")
        self.run_cli("sync", "--source", self.source, expected=2)
        self.assertEqual(template.read_bytes(), original)
        for bad_path in ["../escape.txt", "/tmp/escape.txt", "private-key.txt"]:
            with self.subTest(path=bad_path):
                manifest = self.manifest(self.source)
                manifest["files"][bad_path] = "a" * 64
                (self.source / "bundle.json").write_text(json.dumps(manifest), encoding="utf-8")
                self.run_cli("sync", "--source", self.source, expected=2)
                self.assertEqual(template.read_bytes(), original)
        self.assertFalse((self.base / "escape.txt").exists())

    def test_uninstall_preserves_local_profile_materials_and_modified_assets(self):
        self.install(agent="both")
        material = self.workspace / "my-handout.md"
        material.write_text("내 연수 자료\n", encoding="utf-8")
        template = self.workspace / "templates/lesson-plan.md"
        template.write_text("내 수정본\n", encoding="utf-8")
        self.run_cli("uninstall")
        self.assertTrue((self.workspace / ".harness/profile.json").exists())
        self.assertEqual(material.read_text(encoding="utf-8"), "내 연수 자료\n")
        self.assertEqual(template.read_text(encoding="utf-8"), "내 수정본\n")
        self.assertFalse((self.workspace / ".agents/skills/instructor-start/SKILL.md").exists())
        self.assertFalse((self.workspace / ".claude/skills/instructor-start/SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
