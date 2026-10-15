"""Regression tests: user configuration preservation, receipt ownership and retry behavior."""
import argparse
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('nalssam_pack', BASE / 'pack.py')
pack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pack)

class InstallerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)
        self.patch = patch.dict(os.environ, {'HOME': str(self.home), 'CODEX_HOME': str(self.home / '.codex')})
        self.patch.start()
        self.args = argparse.Namespace(root=str(self.home / 'pack'), profile='skills', only=None, claude=False, source_cache=None, verify_mcp=False)
        self.app = pack.Pack(self.args)
        self.app.env = {'PATH': os.environ.get('PATH', '')}
        self.app.bin.mkdir(parents=True)

    def tearDown(self):
        self.patch.stop()
        self.temp.cleanup()

    def source(self, repo='demo/repo', name='demo'):
        root = self.home / 'source'
        root.mkdir(exist_ok=True)
        (root / 'SKILL.md').write_text(f'---\nname: {name}\ndescription: Demo.\n---\nDemo')
        self.app.state['sources'][repo] = {'path': str(root), 'commit': 'a' * 40}
        return {'repo': repo, 'id': repo.replace('/', '--'), 'skills': ['.']}, root

    def test_existing_skill_is_preserved_and_reinstall_is_idempotent(self):
        source, _ = self.source()
        user = self.home / '.agents/skills/demo'
        user.mkdir(parents=True)
        (user / 'SKILL.md').write_text('user-owned')
        self.app.link_skills(source)
        receipt = dict(self.app.state['skills'])
        self.app.link_skills(source)
        self.assertEqual(receipt, self.app.state['skills'])
        self.assertEqual((user / 'SKILL.md').read_text(), 'user-owned')
        self.assertTrue((user.parent / 'demo--repo-demo').is_symlink())

    def test_uninstall_preserves_changed_skill_and_wrapper(self):
        source, _ = self.source()
        self.app.link_skills(source)
        link = next(iter(self.app.state['skills']))
        Path(link).unlink()
        Path(link).mkdir()
        (Path(link) / 'user.txt').write_text('keep')
        wrapper = Path(self.app.wrapper('example', ['/bin/echo', 'hello']))
        wrapper.write_text('user replacement')
        self.app.codex = None
        with contextlib.redirect_stdout(io.StringIO()):
            self.app.uninstall()
        self.assertTrue((Path(link) / 'user.txt').exists())
        self.assertEqual(wrapper.read_text(), 'user replacement')

    def test_shell_setup_has_backup_and_exact_reversible_entry(self):
        rc = self.home / '.bashrc'
        rc.write_text('# existing\nexport KEEP=yes\n')
        self.app.shell_environment()
        first = rc.read_text()
        self.app.shell_environment()
        self.assertEqual(rc.read_text(), first)
        self.assertTrue(list((self.app.root / 'backups').glob('.bashrc.*')))
        self.app.codex = None
        with contextlib.redirect_stdout(io.StringIO()):
            self.app.uninstall()
        self.assertEqual(rc.read_text(), '# existing\nexport KEEP=yes\n')

    def test_wrapper_preserves_spaces_and_literal_shell_characters(self):
        value = 'spaces $(touch unsafe) `touch unsafe`'
        command = self.app.wrapper('quote-test', ['/bin/echo', value])
        result = subprocess.check_output([command], text=True).strip()
        self.assertEqual(result, value)
        self.assertFalse((self.home / 'unsafe').exists())

    def test_failed_checkout_leaves_no_poisoned_destination(self):
        source = {'repo': 'demo/missing', 'id': 'demo--missing', 'commit': 'a' * 40}
        def fake(args, **kwargs):
            if 'fetch' in args:
                raise RuntimeError('network denied')
            return ''
        with patch.object(pack, 'run', side_effect=fake):
            with self.assertRaises(RuntimeError):
                self.app.checkout(source)
        self.assertFalse((self.app.root / 'sources/demo--missing').exists())
        self.assertEqual(list((self.app.root / 'sources').iterdir()), [])

    def test_mcp_collision_reuses_owned_prefixed_registration(self):
        self.app.codex = '/fake/codex'
        own = ['/pack/server', 'mcp']
        self.app.state['mcp']['nalssam-demo'] = own
        def response(args, **kwargs):
            return subprocess.CompletedProcess(args, 0, json.dumps({'transport': {'command': own[0], 'args': own[1:]}}), '')
        with patch.object(pack.subprocess, 'run', side_effect=response), patch.object(pack, 'run', return_value='ok') as execute:
            result = self.app.mcp('demo', own)
        self.assertEqual(result['registered'], 'nalssam-demo')
        self.assertIn('nalssam-demo', execute.call_args.args[0])

    def test_changed_mcp_registration_is_not_overwritten(self):
        self.app.codex = '/fake/codex'
        self.app.state['mcp']['demo'] = ['/original', 'mcp']
        changed = subprocess.CompletedProcess([], 0, json.dumps({'transport': {'command': '/user', 'args': []}}), '')
        with patch.object(pack.subprocess, 'run', return_value=changed), patch.object(pack, 'run') as execute:
            with self.assertRaisesRegex(RuntimeError, '사용자가 바꾼'):
                self.app.mcp('demo', ['/new', 'mcp'])
            execute.assert_not_called()

    def test_manifest_has_commits_and_no_local_machine_paths(self):
        data = (BASE / 'pack.lock.json').read_text()
        self.assertNotIn('/workspace/', data)
        self.assertNotIn('/home/agent/', data)
        for source in pack.LOCK['sources']:
            if source['available']:
                self.assertRegex(source['commit'], r'^[0-9a-f]{40}$')
        self.assertEqual(len(pack.LOCK['claude_plugins']), 122)

if __name__ == '__main__':
    unittest.main()
