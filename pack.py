#!/usr/bin/env python3
"""Nalssam Pack: pinned, user-scoped Codex environment installer (Python 3.11+)."""
from __future__ import annotations
import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import platform
import re
import selectors
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCK = json.loads((HERE / 'pack.lock.json').read_text())
DEFAULT_ROOT = Path.home() / '.local/share/nalssam-pack'
PY_TOOLS = {
    'microsoft/markitdown': [('markitdown', 'packages/markitdown', '[all]'), ('markitdown-mcp', 'packages/markitdown-mcp', '')],
    'ZZombie04/hwpx_new': [('hwpx-new', '.', '')],
    'ZZombie04/pptx_maker': [('pptx-maker', '.', '[images]')],
    'aldegad/sprite-gen': [('sprite-gen', '.', '')],
    'Panniantong/Agent-Reach': [('agent-reach', '.', '')],
}
EXCLUDED = {'.git', 'node_modules', 'tests', 'examples', '__pycache__'}

def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)

def run(args, *, cwd=None, env=None):
    # No shell parsing, inherited proxies/CA/auth remain intact. Do not log env values.
    merged = os.environ.copy()
    if env:
        merged.update({str(k): str(v) for k, v in env.items()})
    out = subprocess.run([str(a) for a in args], cwd=cwd, env=merged,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if out.returncode:
        raise RuntimeError(f'{Path(str(args[0])).name} 실패 (종료 코드 {out.returncode})\n{out.stdout[-2500:]}')
    return out.stdout.strip()

class Pack:
    def __init__(self, args):
        self.args = args
        self.root = Path(args.root).expanduser().resolve()
        self.state_path = self.root / 'state.json'
        self.state = json.loads(self.state_path.read_text()) if self.state_path.exists() else {
            'version': LOCK['version'], 'sources': {}, 'skills': {}, 'mcp': {}, 'wrappers': {}, 'plugins': {}}
        self.report = {'version': LOCK['version'], 'time': dt.datetime.now(dt.timezone.utc).isoformat(),
                       'profile': getattr(args, 'profile', 'full'), 'steps': [], 'pending': []}
        self.bin = self.root / 'bin'
        self.logs = self.root / 'logs'
        self.node = shutil.which('node')
        self.uv = shutil.which('uv')
        self.codex = shutil.which('codex')
        self.claude = shutil.which('claude')

    @property
    def skill_dirs(self):
        dirs = [Path.home() / '.agents/skills']
        if getattr(self.args, 'claude', False):
            dirs.append(Path(os.environ.get('CLAUDE_CONFIG_DIR', str(Path.home() / '.claude'))) / 'skills')
        return dirs

    def save(self):
        atomic_json(self.state_path, self.state)
        atomic_json(self.root / 'report.json', self.report)

    def step(self, name, action):
        print(f'  → {name}', flush=True)
        start = time.monotonic()
        try:
            detail = action()
            row = {'name': name, 'status': 'ok', 'seconds': round(time.monotonic() - start, 2), 'detail': detail}
            print(f'    완료 ({row["seconds"]}초)', flush=True)
        except Exception as exc:
            row = {'name': name, 'status': 'failed', 'error': str(exc)}
            print(f'    실패: {exc}', flush=True)
        self.report['steps'].append(row)
        self.save()
        return row['status'] == 'ok'

    def prerequisites(self):
        if not shutil.which('git'):
            raise RuntimeError('Git이 필요합니다. macOS: xcode-select --install / Ubuntu: apt install git')
        if platform.system() not in ('Darwin', 'Linux'):
            raise RuntimeError('Windows에서는 WSL2 Ubuntu 안에서 실행하세요. 네이티브 Windows는 지원하지 않습니다.')
        if not self.uv:
            raise RuntimeError('uv가 필요합니다. install.sh로 실행하면 사용자 폴더에 준비합니다.')
        Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))).mkdir(parents=True, exist_ok=True)
        # Use the locked Node version, but never replace the user's Node installation.
        good = self.node and run([self.node, '--version']) == 'v' + LOCK['node_version']
        managed = self.root / 'runtime/node'
        if not good:
            if (managed / 'bin/node').exists():
                self.node = str(managed / 'bin/node')
            else:
                system = {'Linux': 'linux', 'Darwin': 'darwin'}[platform.system()]
                arch = {'x86_64': 'x64', 'AMD64': 'x64', 'aarch64': 'arm64', 'arm64': 'arm64'}.get(platform.machine())
                if not arch:
                    raise RuntimeError('지원하지 않는 CPU: ' + platform.machine())
                version = LOCK['node_version']
                filename = f'node-v{version}-{system}-{arch}.tar.gz'
                base = f'https://nodejs.org/dist/v{version}/'
                with tempfile.TemporaryDirectory() as temp:
                    archive = Path(temp) / filename
                    checks = run(['curl', '-fsSL', base + 'SHASUMS256.txt'])
                    expected = next((line.split()[0] for line in checks.splitlines() if line.split()[-1] == filename), None)
                    if not expected:
                        raise RuntimeError('Node 체크섬 목록에 배포 파일이 없습니다.')
                    run(['curl', '-fsSL', base + filename, '-o', archive])
                    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
                        raise RuntimeError('Node 다운로드 체크섬 불일치')
                    with tarfile.open(archive) as tar:
                        tar.extractall(temp, filter='data')
                    managed.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(Path(temp) / filename[:-7]), managed)
                self.node = str(managed / 'bin/node')
        if run([self.node, '--version']) != 'v' + LOCK['node_version']:
            raise RuntimeError('관리 Node 버전이 lock과 다릅니다.')
        self.env = {'PATH': str(Path(self.node).parent) + os.pathsep + str(self.bin) + os.pathsep + os.environ.get('PATH', '')}
        self.npm = str(Path(self.node).with_name('npm'))
        self.bin.mkdir(parents=True, exist_ok=True)
        return {'node': run([self.node, '--version']), 'python': sys.version.split()[0], 'uv': run([self.uv, '--version'])}

    def checkout(self, source):
        repo, sha = source['repo'], source['commit']
        dest = self.root / 'sources' / source['id']
        if (dest / '.git').exists():
            head = run(['git', '-C', dest, 'rev-parse', 'HEAD'])
            if head != sha:
                raise RuntimeError(f'{repo}: 기존 체크아웃 커밋이 다릅니다. 별도 --root로 설치하세요.')
        else:
            if dest.exists():
                raise RuntimeError(f'기존 폴더를 덮어쓰지 않습니다: {dest}')
            dest.parent.mkdir(parents=True, exist_ok=True)
            cache = Path(self.args.source_cache).expanduser() / source['id'] if self.args.source_cache else None
            with tempfile.TemporaryDirectory(prefix='.fetch-', dir=dest.parent) as staging:
                work = Path(staging) / 'checkout'
                if cache and (cache / '.git').exists():
                    run(['git', 'clone', '--no-hardlinks', '--no-checkout', cache, work])
                else:
                    run(['git', 'init', '-q', work])
                    run(['git', '-C', work, 'remote', 'add', 'origin', f'https://github.com/{repo}.git'])
                    run(['git', '-C', work, 'fetch', '--depth', '1', 'origin', sha])
                run(['git', '-C', work, 'checkout', '--detach', sha])
                work.rename(dest)
        self.state['sources'][repo] = {'path': str(dest), 'commit': sha}
        return {'repo': repo, 'commit': sha}

    def source(self, repo):
        return Path(self.state['sources'][repo]['path'])

    def link_skills(self, source):
        root = self.source(source['repo'])
        count, conflicts = 0, []
        for pattern in source['skills']:
            base = root / pattern
            if not base.exists():
                raise RuntimeError(f'스킬 원본 경로 없음: {source["repo"]}/{pattern}')
            files = [base / 'SKILL.md'] if (base / 'SKILL.md').is_file() else sorted(base.rglob('SKILL.md'))
            for file in files:
                if any(part in EXCLUDED for part in file.relative_to(base).parts):
                    continue
                text = file.read_text(errors='replace')
                match = re.search(r'^name:\s*[\'\"]?([a-zA-Z0-9_.-]+)[\'\"]?\s*$', text, re.M)
                name = match.group(1) if match else file.parent.name
                for directory in self.skill_dirs:
                    directory.mkdir(parents=True, exist_ok=True)
                    target = directory / name
                    if target.exists() or target.is_symlink():
                        if target.is_symlink() and target.resolve() == file.parent.resolve():
                            count += 1
                            continue
                        target = directory / (source['id'].lower() + '-' + name)
                        if target.exists() or target.is_symlink():
                            if target.is_symlink() and target.resolve() == file.parent.resolve():
                                count += 1
                                continue
                            conflicts.append(str(target))
                            continue
                    target.symlink_to(file.parent, target_is_directory=True)
                    self.state['skills'][str(target)] = str(file.parent)
                    count += 1
        if conflicts:
            self.report['pending'].append({'source': source['repo'], 'skill_conflicts_preserved': conflicts})
        return {'registered': count, 'conflicts': len(conflicts)}

    def wrapper(self, name, command, extra_env=None):
        target = self.bin / name
        if (target.exists() or target.is_symlink()) and str(target) not in self.state['wrappers']:
            raise RuntimeError(f'알 수 없는 기존 실행 파일 보존: {target}')
        exports = {'PATH': self.env['PATH']}
        exports.update(extra_env or {})
        content = '#!/bin/sh\n' + ''.join(f'export {k}={shlex.quote(str(v))}\n' for k, v in exports.items())
        env_file = shlex.quote(str(self.root / 'env.sh'))
        content += f'[ ! -f {env_file} ] || . {env_file}\n'
        content += 'exec ' + ' '.join(shlex.quote(str(x)) for x in command) + ' "$@"\n'
        target.write_text(content)
        target.chmod(0o755)
        self.state['wrappers'][str(target)] = hashlib.sha256(content.encode()).hexdigest()
        return str(target)

    def npm_tools(self):
        dest = self.root / 'runtime/npm'
        dest.mkdir(parents=True, exist_ok=True)
        for name in ['package.json', 'package-lock.json']:
            shutil.copy2(HERE / 'locks/npm/tools' / name, dest / name)
        run([self.npm, 'ci', '--no-audit', '--no-fund'], cwd=dest, env=self.env)
        for name in ['kordoc', 'kordoc-mcp', 'playwright-cli', 'mcporter']:
            self.wrapper(name, [dest / 'node_modules/.bin' / name])
        if not self.codex:
            self.codex = self.wrapper('codex', [dest / 'node_modules/.bin/codex'])
        if getattr(self.args, 'claude', False) and not self.claude:
            self.claude = self.wrapper('claude', [dest / 'node_modules/.bin/claude'])
        return {'runtime': str(dest), 'codex': self.codex}

    def python_tool(self, name, relative, extras, source):
        venv = self.root / 'venvs' / name
        py = venv / 'bin/python'
        if not py.exists():
            run([self.uv, 'venv', '--python', LOCK['python_version'], venv])
        run([self.uv, 'pip', 'install', '--python', py, '--constraint', HERE / 'locks/python' / (name + '.txt'), str(source / relative) + extras])
        commands = {'markitdown': ['markitdown'], 'markitdown-mcp': ['markitdown-mcp'],
                    'hwpx-new': ['hwpx-new', 'hwpx-new-mcp'], 'pptx-maker': ['pptx-maker', 'pptx-maker-mcp'],
                    'sprite-gen': ['sprite-gen'], 'agent-reach': ['agent-reach']}[name]
        for command in commands:
            self.wrapper(command, [venv / 'bin' / command])
        return {'environment': str(venv)}

    def build_source(self, repo):
        source = self.source(repo)
        if repo == 'nalssam/rea':
            run([self.npm, 'ci', '--no-audit', '--no-fund'], cwd=source, env=self.env)
            run([self.npm, 'run', 'build:cached'], cwd=source, env=self.env)
            self.wrapper('rea', [self.node, source / 'scripts/rea.mjs'])
        elif repo == 'ZZombie04/motion':
            run([self.npm, 'ci', '--no-audit', '--no-fund'], cwd=source, env=self.env)
            self.wrapper('motion', [self.node, source / 'bin/motion.mjs'])
        elif repo == 'revfactory/showreel':
            target = source / 'scripts'
            shutil.copy2(HERE / 'locks/npm/showreel/package-lock.json', target / 'package-lock.json')
            run([self.npm, 'ci', '--no-audit', '--no-fund'], cwd=target, env=self.env)
            venv = self.root / 'venvs/showreel'
            if not (venv / 'bin/python').exists():
                run([self.uv, 'venv', '--python', LOCK['python_version'], venv])
            run([self.uv, 'pip', 'install', '--python', venv / 'bin/python', '-r', HERE / 'locks/python/showreel.txt'])
        return {'built': repo}

    def reason_network(self):
        """Install the locked official binary without joining a team or changing agent hooks."""
        release = LOCK['reason_network']
        system = {'Linux': 'unknown-linux-musl', 'Darwin': 'apple-darwin'}[platform.system()]
        arch = {'x86_64': 'x86_64', 'AMD64': 'x86_64', 'aarch64': 'aarch64', 'arm64': 'aarch64'}.get(platform.machine())
        target = f'{arch}-{system}'
        expected = release['sha256'].get(target)
        if not expected:
            raise RuntimeError('Reason Network 지원 대상이 아닙니다: ' + target)
        version = release['version']
        dest = self.root / 'runtime/reason-network' / version
        binary = dest / 'reason-network'
        dest.mkdir(parents=True, exist_ok=True)
        # Always verify the archive, including when refreshing an existing installation.
        with tempfile.TemporaryDirectory(dir=dest) as temporary:
            temp = Path(temporary)
            archive = temp / 'release.tar.gz'
            url = f'https://github.com/reason-machines/reason-network/releases/download/v{version}/reason-network-{target}.tar.gz'
            run(['curl', '-fsSL', url, '-o', archive], env=self.env)
            if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
                raise RuntimeError('Reason Network 다운로드 체크섬 불일치')
            with tarfile.open(archive) as tar:
                tar.extractall(temp / 'unpacked', filter='data')
            candidate = temp / 'unpacked/reason-network'
            actual = run([candidate, '--version'], env=self.env)
            if actual != 'reason-network ' + version:
                raise RuntimeError('Reason Network 버전 불일치: ' + actual)
            candidate.replace(binary)
        state = self.root / 'data/reason-network'
        command = self.wrapper('reason-network', [binary], {'REASON_NETWORK_HOME': str(state)})
        self.report['pending'].append({'service': 'Reason Network', 'reason': 'CLI·MCP 준비. 팀 로그인/초대·외부 연결은 별도. 자동 팀 생성·가입·메시지 전송·훅 등록은 하지 않습니다.'})
        return {'command': command, 'version': version, 'state': str(state)}

    def media(self):
        # Never use sudo. An installed Chromium/ffmpeg is reused. Missing Linux shared
        # libraries remain explicit pending requirements instead of fake readiness.
        ffmpeg = shutil.which('ffmpeg')
        browser = next((shutil.which(n) for n in ['chromium', 'google-chrome', 'google-chrome-stable', 'chromium-browser'] if shutil.which(n)), None)
        if not browser and platform.system() == 'Darwin':
            candidate = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
            browser = str(candidate) if candidate.exists() else None
        if not ffmpeg:
            self.report['pending'].append({'requirement': 'ffmpeg + ffprobe', 'fix': 'macOS: brew install ffmpeg / Ubuntu: sudo apt install ffmpeg'})
        if not browser:
            playwright = self.root / 'runtime/npm/node_modules/.bin/playwright'
            run([playwright, 'install', 'chromium'], env=self.env)
            code = "const {chromium}=require('playwright');process.stdout.write(chromium.executablePath())"
            browser = run([self.node, '-e', code], cwd=self.root / 'runtime/npm', env=self.env)
        self.media_env = {'MOTION_CHROME': browser, 'REMOTION_BROWSER': browser, 'CHROMIUM_PATH': browser, 'REEL_CHROME_PATH': browser}
        self.state['media_env'] = self.media_env
        return {'browser': browser, 'ffmpeg': ffmpeg, 'ffprobe': shutil.which('ffprobe')}

    def cinetic(self):
        venv = self.root / 'venvs/cinetic'
        if not (venv / 'bin/python').exists():
            run([self.uv, 'venv', '--python', LOCK['python_version'], venv])
        run([self.uv, 'pip', 'install', '--python', venv / 'bin/python', '-r', HERE / 'locks/python/cinetic.txt'])
        dest = self.root / 'runtime/cinetic'
        if not dest.exists():
            run(['bash', self.source('Leonxlnx/cinetic') / 'skills/cinetic/scripts/new-film.sh', dest, '--no-install', '--browser', self.media_env['CHROMIUM_PATH']], env=self.env)
        for name in ['package.json', 'package-lock.json']:
            shutil.copy2(HERE / 'locks/npm/cinetic' / name, dest / name)
        run([self.npm, 'ci', '--no-audit', '--no-fund'], cwd=dest, env=self.env)
        return {'python': str(venv / 'bin/python'), 'node_modules': str(dest / 'node_modules')}

    def mcp(self, name, command):
        if not self.codex:
            raise RuntimeError('Codex CLI를 찾을 수 없습니다.')
        existing = subprocess.run([self.codex, 'mcp', 'get', name, '--json'], capture_output=True, text=True, env={**os.environ, **self.env})
        actual = name
        if existing.returncode == 0 and name not in self.state['mcp']:
            actual = 'nalssam-' + name
            other = subprocess.run([self.codex, 'mcp', 'get', actual, '--json'], capture_output=True, text=True, env={**os.environ, **self.env})
            if other.returncode == 0 and actual not in self.state['mcp']:
                raise RuntimeError(f'기존 MCP 설정 보존: {name}, {actual}. 이름 충돌을 먼저 해결하세요.')
        if actual in self.state['mcp']:
            # Refuse to overwrite a registration edited by the user after installation.
            old = subprocess.run([self.codex, 'mcp', 'get', actual, '--json'], capture_output=True, text=True, env={**os.environ, **self.env})
            if old.returncode == 0:
                transport = json.loads(old.stdout).get('transport', {})
                previous = self.state['mcp'][actual]
                if transport.get('command') != previous[0] or transport.get('args', []) != previous[1:]:
                    raise RuntimeError(f'사용자가 바꾼 MCP 설정 보존: {actual}')
        run([self.codex, 'mcp', 'add', actual, '--', *command], env=self.env)
        self.state['mcp'][actual] = [str(c) for c in command]
        return {'registered': actual, 'command': [str(c) for c in command]}

    def memory_plugin(self):
        # One pinned local marketplace; do not copy other platforms' hook files into Codex.
        root = self.root / 'marketplace'
        root.mkdir(parents=True, exist_ok=True)
        plugin = root / 'claude-mem'
        source = self.source('thedotmack/claude-mem')
        if not plugin.exists():
            plugin.symlink_to(source, target_is_directory=True)
        folder = root / '.agents/plugins'
        folder.mkdir(parents=True, exist_ok=True)
        data = {'name': 'nalssam-pack-local', 'interface': {'displayName': '날쌤팩'},
                'plugins': [{'name': 'claude-mem', 'source': {'source': 'local', 'path': './claude-mem/plugin'},
                             'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'},
                             'category': 'Productivity'}]}
        atomic_json(folder / 'marketplace.json', data)
        run([self.codex, 'plugin', 'marketplace', 'add', root, '--json'], env=self.env)
        run([self.codex, 'plugin', 'add', 'claude-mem@nalssam-pack-local', '--json'], env=self.env)
        self.state['plugins']['claude-mem@nalssam-pack-local'] = True
        # The native plugin owns the memory skills. Remove only links created by this pack.
        for link, target in list(self.state['skills'].items()):
            if Path(target).is_relative_to(source):
                path = Path(link)
                if path.is_symlink() and path.resolve() == Path(target).resolve():
                    path.unlink()
                    del self.state['skills'][link]
        self.report['pending'].append({'service': 'claude-mem', 'status': 'plugin installed; observer model/account configuration and collection are not verified'})
        return {'plugin': 'claude-mem@nalssam-pack-local'}

    def claude_plugins(self, selected):
        if not self.claude:
            raise RuntimeError('Claude Code CLI 설치가 필요합니다.')
        root = self.root / 'claude-marketplace'
        folder = root / '.claude-plugin'
        folder.mkdir(parents=True, exist_ok=True)
        chosen = [p for p in LOCK.get('claude_plugins', []) if p['source'] in selected]
        entries = []
        for item in chosen:
            target = root / item['name']
            source = self.source(item['source']) / item['path']
            if not target.exists():
                target.symlink_to(source, target_is_directory=True)
            entries.append({'name': item['name'], 'source': './' + item['name']})
        atomic_json(folder / 'marketplace.json', {'name': 'nalssam-pack', 'owner': {'name': 'nalssam'}, 'plugins': entries})
        run([self.claude, 'plugin', 'marketplace', 'add', root, '--json'], env=self.env)
        # CLI config mutations are sequential. No network marketplace references remain.
        completed = []
        for item in chosen:
            name = item['name'] + '@nalssam-pack'
            result = run([self.claude, 'plugin', 'install', name, '--json'], env=self.env)
            self.state.setdefault('claude_plugins', {})[name] = True
            if not item['enabled']:
                run([self.claude, 'plugin', 'disable', name], env=self.env)
            self.save()
            completed.append(name)
        # Remove duplicate standalone skills only when a loaded plugin contains
        # byte-identical SKILL.md content. Disabled plugins keep their skill fallback.
        bodies = set()
        for item in chosen:
            if item['enabled']:
                base = self.source(item['source']) / item['path']
                for file in base.rglob('SKILL.md'):
                    if not any(p in EXCLUDED for p in file.relative_to(base).parts):
                        bodies.add(hashlib.sha256(file.read_bytes()).hexdigest())
        claude_dir = Path(os.environ.get('CLAUDE_CONFIG_DIR', str(Path.home() / '.claude'))) / 'skills'
        for link, target in list(self.state['skills'].items()):
            path = Path(link)
            file = Path(target) / 'SKILL.md'
            if path.parent == claude_dir and path.is_symlink() and file.is_file() and hashlib.sha256(file.read_bytes()).hexdigest() in bodies:
                path.unlink()
                del self.state['skills'][link]
        return {'installed': len(completed)}

    def shell_environment(self):
        extra = self.state.get('media_env', {})
        paths = [str(self.bin)]
        if (self.root / 'venvs/cinetic/bin').exists():
            paths.append(str(self.root / 'venvs/cinetic/bin'))
        elif (self.root / 'venvs/showreel/bin').exists():
            paths.append(str(self.root / 'venvs/showreel/bin'))
        if self.node:
            paths.append(str(Path(self.node).parent))
        self.root.mkdir(parents=True, exist_ok=True)
        text = '# Generated by 날쌤팩. No credentials are stored here.\n'
        text += 'export PATH=' + shlex.quote(':'.join(paths)) + ':"$PATH"\n'
        text += ''.join(f'export {k}={shlex.quote(str(v))}\n' for k, v in extra.items())
        (self.root / 'env.sh').write_text(text)
        init = '\n# 날쌤팩\n[ ! -f ' + shlex.quote(str(self.root / 'env.sh')) + ' ] || . ' + shlex.quote(str(self.root / 'env.sh')) + '\n'
        for filename in ['.bashrc', '.zshrc', '.profile']:
            path = Path.home() / filename
            old = path.read_text() if path.exists() else ''
            if init not in old:
                self.backup(path)
                path.write_text(old + init)
                self.state.setdefault('shell_entries', {})[str(path)] = init
        command = self.wrapper('nalssam-pack', [sys.executable, HERE / 'pack.py', '--root', self.root])
        return {'command': command, 'activate': '. ' + shlex.quote(str(self.root / 'env.sh'))}

    def verify_mcp(self):
        checks = []
        for name, command in self.state['mcp'].items():
            result = check_mcp(name, command)
            checks.append(result)
            print(f'    {name}: ' + (f'{result["tools"]}개 도구 연결 확인' if result['ok'] else '연결 실패'), flush=True)
        self.state['last_mcp_checks'] = checks
        failed = [check['name'] for check in checks if not check['ok']]
        if failed:
            raise RuntimeError('MCP 초기화/도구 목록 실패: ' + ', '.join(failed))
        return checks

    def backup(self, path):
        if path.exists():
            stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            dest = self.root / 'backups' / (path.name + '.' + stamp)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)

    def install(self):
        self.root.mkdir(parents=True, exist_ok=True)
        selected = [s for s in LOCK['sources'] if (not self.args.only or s['repo'] in self.args.only or s['id'] in self.args.only)
                    and (s['kind'] != 'claude-plugin-dependency' or self.args.claude)]
        if self.args.only and not selected:
            raise RuntimeError('--only에 일치하는 저장소가 없습니다.')
        if not self.step('기본 도구 확인', self.prerequisites):
            return 1
        self.state['sources']['nalssam/nalssam-pack'] = {'path': str(HERE), 'version': LOCK['version']}
        self.step('날쌤팩 관리 스킬', lambda: self.link_skills({'repo': 'nalssam/nalssam-pack', 'id': 'nalssam--nalssam-pack', 'skills': ['skills/nalssam-pack']}))
        full = self.args.profile == 'full'
        if full:
            self.step('잠긴 npm 도구 설치', self.npm_tools)
        for source in selected:
            if not source['available']:
                self.report['pending'].append({'source': source['repo'], 'reason': source.get('note')})
                continue
            if not self.step('소스 ' + source['repo'], lambda s=source: self.checkout(s)):
                continue
            self.step('스킬 ' + source['repo'], lambda s=source: self.link_skills(s))
            if full:
                for name, relative, extras in PY_TOOLS.get(source['repo'], []):
                    self.step('Python ' + name, lambda n=name, r=relative, e=extras, s=source: self.python_tool(n, r, e, self.source(s['repo'])))
                if source['repo'] == 'reason-machines/reason-network':
                    self.step('Reason Network 실행 환경', self.reason_network)
                if source['repo'] in ['nalssam/rea', 'ZZombie04/motion', 'revfactory/showreel']:
                    self.step('빌드 ' + source['repo'], lambda repo=source['repo']: self.build_source(repo))
        media_ok = full and self.step('영상 실행 환경', self.media)
        if full and 'Leonxlnx/cinetic' in {s['repo'] for s in selected} and media_ok:
            self.step('Cinetic 실행 환경', self.cinetic)
        if full:
            mappings = {'rea': ['rea', 'mcp'], 'hwpx-new': ['hwpx-new-mcp'], 'pptx-maker': ['pptx-maker-mcp'],
                        'markitdown': ['markitdown-mcp'], 'kordoc': ['kordoc-mcp'],
                        'motion': ['motion', '__mcp__'], 'reason-network': ['reason-network', 'mcp']}
            # Motion CLI's MCP server is a separate entry point.
            if 'ZZombie04/motion' in self.state['sources'] and (self.bin / 'motion').exists():
                self.wrapper('motion-mcp', [self.node, self.source('ZZombie04/motion') / 'mcp/server.mjs'])
                mappings['motion'] = ['motion-mcp']
            cfg = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'config.toml'
            self.backup(cfg)
            for name, cmd in mappings.items():
                if (self.bin / cmd[0]).exists():
                    command = [str(self.bin / cmd[0]), *cmd[1:]]
                    self.step('MCP ' + name, lambda n=name, c=command: self.mcp(n, c))
            if 'thedotmack/claude-mem' in {s['repo'] for s in selected} and 'thedotmack/claude-mem' in self.state['sources']:
                self.step('Codex 메모리 플러그인', self.memory_plugin)
            if self.args.claude:
                selected_repos = {s['repo'] for s in selected if s['repo'] in self.state['sources']}
                self.step('Claude Code 네이티브 플러그인', lambda: self.claude_plugins(selected_repos))
            if 'nalssam/aftereffects-mcp' in self.state['sources']:
                self.report['pending'].append({'service': 'After Effects MCP', 'reason': 'Adobe After Effects 2022+와 패널 설치 필요. Linux에서는 실제 제어 불가; 소스·스킬만 준비.'})
        self.step('셸 실행 환경', self.shell_environment)
        if full:
            self.step('MCP 실제 연결 검증', self.verify_mcp)
        self.report['pending'].append({'accounts': 'ChatGPT/Codex 로그인, ElevenLabs·Gemini·Google Cloud 등 계정/API 키는 공유하거나 복사하지 않습니다.'})
        failed = sum(row['status'] == 'failed' for row in self.report['steps'])
        self.report['status'] = 'partial' if failed else ('installed_with_pending' if self.report['pending'] else 'installed')
        self.save()
        print(f'\n날쌤팩 설치 종료: 실패 {failed}개 / 스킬 링크 {len(self.state["skills"])}개 / MCP {len(self.state["mcp"])}개')
        print('설치 기록:', self.root / 'report.json')
        print('새 터미널 또는 Codex 새 세션에서 사용하세요. 처음이면 codex login을 실행하세요.')
        return 1 if failed else 0

    def doctor(self):
        if not self.state_path.exists():
            raise RuntimeError('설치 기록이 없습니다. 먼저 install을 실행하세요.')
        rows = []
        for name in ['git', 'node', 'ffmpeg', 'ffprobe', 'codex']:
            path = self.bin / name if (self.bin / name).exists() else shutil.which(name)
            rows.append({'name': name, 'available': bool(path), 'path': str(path) if path else None})
        broken = [p for p, t in self.state['skills'].items() if not Path(p).is_symlink() or Path(p).resolve() != Path(t).resolve() or not Path(t).exists()]
        mcp = []
        if self.args.verify_mcp:
            for name, cmd in self.state['mcp'].items():
                mcp.append(check_mcp(name, cmd))
        result = {'tools': rows, 'skills': len(self.state['skills']), 'broken_or_changed_skills': broken, 'mcp': mcp,
                  'pending': json.loads((self.root / 'report.json').read_text()).get('pending', []) if (self.root / 'report.json').exists() else []}
        atomic_json(self.root / 'doctor.json', result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        full = (json.loads((self.root / 'report.json').read_text()).get('profile') == 'full') if (self.root / 'report.json').exists() else True
        missing = full and any(not row['available'] for row in rows)
        return int(bool(broken) or bool(missing) or any(not item['ok'] for item in mcp))

    def uninstall(self):
        # Only remove things whose current identity still matches our receipt.
        changed = []
        for link, target in list(self.state['skills'].items()):
            path = Path(link)
            if path.is_symlink() and path.resolve() == Path(target).resolve():
                path.unlink()
                del self.state['skills'][link]
            elif path.exists() or path.is_symlink():
                changed.append(link)
        if self.codex:
            for name, command in list(self.state['mcp'].items()):
                raw = subprocess.run([self.codex, 'mcp', 'get', name, '--json'], capture_output=True, text=True)
                if raw.returncode:
                    continue
                transport = json.loads(raw.stdout).get('transport', {})
                if transport.get('command') == command[0] and transport.get('args', []) == command[1:]:
                    run([self.codex, 'mcp', 'remove', name])
                    del self.state['mcp'][name]
                else:
                    changed.append('MCP ' + name)
            for plugin in list(self.state['plugins']):
                run([self.codex, 'plugin', 'remove', plugin])
                del self.state['plugins'][plugin]
        claude = self.claude or str(self.root / 'runtime/npm/node_modules/.bin/claude')
        for plugin in list(self.state.get('claude_plugins', {})):
            run([claude, 'plugin', 'uninstall', plugin])
            del self.state['claude_plugins'][plugin]
        for filename, entry in self.state.get('shell_entries', {}).items():
            path = Path(filename)
            if path.exists():
                path.write_text(path.read_text().replace(entry, ''))
        for filename, digest in list(self.state['wrappers'].items()):
            path = Path(filename)
            if path.is_file() and not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest() == digest:
                path.unlink()
                del self.state['wrappers'][filename]
            elif path.exists() or path.is_symlink():
                changed.append(filename)
        self.save()
        print('연결 해제 완료. 다운로드·가상환경·백업은 보존했습니다:', self.root)
        if changed:
            print('변경되어 보존한 항목:', ', '.join(changed))
        return 0


def check_mcp(name, command):
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    select = selectors.DefaultSelector()
    select.register(process.stdout, selectors.EVENT_READ)
    buffer = b''
    def send(message):
        process.stdin.write((json.dumps(message) + '\n').encode())
        process.stdin.flush()
    try:
        send({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'nalssam-pack-doctor', 'version': LOCK['version']}}})
        until = time.monotonic() + 40
        while time.monotonic() < until:
            if not select.select(1):
                continue
            part = os.read(process.stdout.fileno(), 65536)
            if not part:
                break
            buffer += part
            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n', 1)
                try:
                    value = json.loads(line)
                except (ValueError, UnicodeError):
                    continue
                if value.get('error'):
                    return {'name': name, 'ok': False, 'error': value['error']}
                if value.get('id') == 1:
                    send({'jsonrpc': '2.0', 'method': 'notifications/initialized'})
                    send({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}})
                elif value.get('id') == 2:
                    return {'name': name, 'ok': True, 'tools': len(value.get('result', {}).get('tools', []))}
        return {'name': name, 'ok': False, 'error': 'timeout or early exit'}
    except (OSError, ValueError) as exc:
        return {'name': name, 'ok': False, 'error': str(exc)}
    finally:
        select.close()
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def main(argv=None):
    parser = argparse.ArgumentParser(description='날쌤팩 — 한 번에 준비하는 Codex 작업 환경')
    parser.add_argument('command', nargs='?', choices=['install', 'plan', 'doctor', 'uninstall'], default='install')
    parser.add_argument('--root', default=str(DEFAULT_ROOT), help='설치 전용 디렉터리')
    parser.add_argument('--profile', choices=['full', 'skills'], default='full')
    parser.add_argument('--only', action='append', help='선택할 owner/repository (반복 가능)')
    parser.add_argument('--source-cache', help='검증용: 이미 보유한 owner--repository 체크아웃에서 복제')
    parser.add_argument('--claude', action='store_true', help='Claude Code 스킬·네이티브 플러그인도 설치')
    parser.add_argument('--verify-mcp', action='store_true', help='doctor: 실제 MCP 초기화·도구 목록 요청')
    args = parser.parse_args(argv)
    if args.command == 'plan':
        selected = [s for s in LOCK['sources'] if not args.only or s['repo'] in args.only or s['id'] in args.only]
        print(json.dumps({'profile': args.profile, 'root': str(Path(args.root).expanduser()), 'sources': selected}, ensure_ascii=False, indent=2))
        return 0
    root = Path(args.root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    # A second installer must not corrupt the receipt or the shared config.
    import fcntl
    with (root / 'install.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('같은 설치 폴더에서 다른 날쌤팩 작업이 진행 중입니다.', file=sys.stderr)
            return 1
        app = Pack(args)
        try:
            return getattr(app, args.command)()
        except Exception as exc:
            print('날쌤팩:', exc, file=sys.stderr)
            return 1

if __name__ == '__main__':
    sys.exit(main())
