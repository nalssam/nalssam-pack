#!/usr/bin/env python3
"""Local instructor workspace installer. Standard library only; no document upload."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import sys
import tempfile
import urllib.error
import urllib.request

VERSION = '0.1.1'
REPOSITORY = 'nalssam/nalssam-pack'
MARKER = 'nalssam-instructor-harness'
_HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = (_HERE.parent if _HERE.name == 'bundle' else
                Path(os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData/Local'))) / 'NalssamInstructor'
                if os.name == 'nt' else Path.home() / '.local' / 'share' / 'nalssam-instructor')
MAX_FILE = 2 * 1024 * 1024
MAX_TOTAL = 16 * 1024 * 1024
MAX_FILES = 150
PROFILE_KEYS = {'role', 'courses', 'audience', 'session_minutes', 'tasks', 'tone', 'agent', 'workspace'}
DEFAULTS = {'role': '교관', 'courses': '일반 교수법', 'audience': '성인 학습자',
            'session_minutes': 50, 'tasks': ['강의안', '실습자료', '평가문항'],
            'tone': '명확하고 간결한 한국어', 'agent': 'codex', 'workspace': ''}


class HarnessError(Exception):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def checked_directory(path):
    """Do not follow a pre-existing symlink supplied as a managed directory."""
    path = Path(path).expanduser().absolute()
    if path.is_symlink():
        raise HarnessError(f'심볼릭 링크 폴더는 사용하지 않습니다: {path}')
    return path.resolve()


def no_symlink(path, boundary):
    path = Path(path)
    boundary = Path(boundary)
    if not path.is_relative_to(boundary):
        raise HarnessError(f'관리 폴더 밖의 경로입니다: {path}')
    current = path
    while current != boundary.parent:
        if current.is_symlink():
            raise HarnessError(f'기존 심볼릭 링크를 보존했습니다: {current}')
        if current == boundary:
            break
        current = current.parent


def atomic_write(path, body, boundary):
    no_symlink(path, boundary)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.instructor-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(body)
        os.replace(name, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(name)


def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise HarnessError(f'JSON을 읽지 못했습니다: {path}: {exc}') from exc


def safe_relative(value):
    if not isinstance(value, str) or '\\' in value or '\x00' in value:
        raise HarnessError('번들 경로 형식이 올바르지 않습니다.')
    p = PurePosixPath(value)
    if p.is_absolute() or str(p) != value or not p.parts or any(x in ('', '.', '..') for x in p.parts):
        raise HarnessError(f'허용되지 않은 번들 경로: {value}')
    if ':' in value:
        raise HarnessError(f'허용되지 않은 번들 경로: {value}')
    if value not in ('harness.py', 'defaults.json'):
        if len(p.parts) < 2 or p.parts[0] not in ('skills', 'templates') or any(x.startswith('.') for x in p.parts):
            raise HarnessError(f'허용되지 않은 번들 파일: {value}')
        if p.suffix.lower() not in ('.md', '.json', '.txt', '.csv'):
            raise HarnessError(f'허용되지 않은 번들 파일 형식: {value}')
    return value


def validate_manifest(manifest):
    if not isinstance(manifest, dict) or not isinstance(manifest.get('files'), dict):
        raise HarnessError('bundle.json의 files 객체가 필요합니다.')
    version = manifest.get('version')
    if not isinstance(version, str) or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?', version):
        raise HarnessError('번들 버전 형식이 올바르지 않습니다.')
    files = manifest['files']
    if not 1 <= len(files) <= MAX_FILES or not {'harness.py', 'defaults.json'}.issubset(files):
        raise HarnessError('번들 파일 개수 또는 필수 파일이 올바르지 않습니다.')
    folded = set()
    for name, checksum in files.items():
        safe_relative(name)
        if name.casefold() in folded:
            raise HarnessError('대소문자가 겹치는 번들 경로가 있습니다.')
        folded.add(name.casefold())
        if not isinstance(checksum, str) or not re.fullmatch('[0-9a-f]{64}', checksum):
            raise HarnessError(f'올바르지 않은 SHA-256: {name}')
    return manifest


def read_bundle(source):
    source = checked_directory(source)
    manifest_path = source / 'bundle.json'
    no_symlink(manifest_path, source)
    if manifest_path.stat().st_size > MAX_FILE:
        raise HarnessError('번들 manifest가 너무 큽니다.')
    manifest = validate_manifest(read_json(manifest_path))
    contents = {}
    total = 0
    for name, checksum in manifest['files'].items():
        path = source / name
        no_symlink(path, source)
        if not path.is_file() or path.stat().st_size > MAX_FILE:
            raise HarnessError(f'파일이 없거나 너무 큽니다: {name}')
        body = path.read_bytes()
        total += len(body)
        if total > MAX_TOTAL or digest(body) != checksum:
            raise HarnessError(f'번들 체크섬/크기 검증 실패: {name}')
        contents[name] = body
    return manifest, contents


def download(url):
    """HTTPS with inherited proxy and normal certificate validation, bounded response size."""
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            final = response.geturl()
            if not final.startswith('https://raw.githubusercontent.com/'):
                raise HarnessError('공식 GitHub 원본 이외의 리디렉션은 허용하지 않습니다.')
            body = response.read(MAX_FILE + 1)
    except (urllib.error.URLError, OSError) as exc:
        raise HarnessError(f'공식 배포 파일 다운로드 실패: {exc}') from exc
    if len(body) > MAX_FILE:
        raise HarnessError('다운로드 파일이 너무 큽니다.')
    return body


def remote_bundle(ref):
    if not re.fullmatch('[0-9a-f]{40}', ref or ''):
        raise HarnessError('--ref에는 GitHub의 전체 40자리 커밋 SHA를 입력하세요.')
    base = f'https://raw.githubusercontent.com/{REPOSITORY}/{ref}/instructor/'
    try:
        manifest = validate_manifest(json.loads(download(base + 'bundle.json')))
    except ValueError as exc:
        raise HarnessError('원격 bundle.json 형식이 올바르지 않습니다.') from exc
    contents = {}
    total = 0
    for name, checksum in manifest['files'].items():
        body = download(base + name)
        total += len(body)
        if total > MAX_TOTAL or digest(body) != checksum:
            raise HarnessError(f'원격 번들 체크섬/크기 검증 실패: {name}')
        contents[name] = body
    return manifest, contents


def state_path(root):
    return root / 'state.json'


def load_state(root, required=True):
    path = state_path(root)
    no_symlink(path, root)
    if not path.exists():
        if required:
            raise HarnessError('설치 기록이 없습니다. install을 먼저 실행하세요.')
        return None
    state = read_json(path)
    if not isinstance(state, dict) or state.get('kind') != MARKER or not isinstance(state.get('managed'), dict):
        raise HarnessError('다른 프로그램의 state.json을 보존했습니다. 별도 --root를 사용하세요.')
    workspace = checked_directory(state.get('workspace', ''))
    for name, checksum in state['managed'].items():
        path = Path(name)
        if not path.is_absolute() or not (path.is_relative_to(root) or path.is_relative_to(workspace)):
            raise HarnessError('설치 기록의 관리 파일 경로가 올바르지 않습니다.')
        if not isinstance(checksum, str) or not re.fullmatch('[0-9a-f]{64}', checksum):
            raise HarnessError('설치 기록의 체크섬이 올바르지 않습니다.')
    return state


def string(value, name, maximum=200):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum or '\x00' in value:
        raise HarnessError(f'{name}: 비어 있지 않은 {maximum}자 이하 문자열을 입력하세요.')
    if '\n' in value or '\r' in value:
        raise HarnessError(f'{name}: 한 줄로 입력하세요.')
    return value.strip()


def validate_profile(profile):
    if set(profile) - PROFILE_KEYS:
        raise HarnessError('알 수 없는 설정 항목: ' + ', '.join(sorted(set(profile) - PROFILE_KEYS)))
    result = {}
    for name in ('role', 'courses', 'audience', 'tone'):
        result[name] = string(profile.get(name), name)
    minutes = profile.get('session_minutes')
    if type(minutes) is not int or not 10 <= minutes <= 480:
        raise HarnessError('session_minutes는 10~480 사이의 정수여야 합니다.')
    result['session_minutes'] = minutes
    tasks = profile.get('tasks')
    if isinstance(tasks, str):
        tasks = [x.strip() for x in tasks.split(',') if x.strip()]
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 12:
        raise HarnessError('tasks는 1~12개 항목의 목록이어야 합니다.')
    result['tasks'] = [string(x, 'tasks 항목', 100) for x in tasks]
    if profile.get('agent') not in ('codex', 'claude', 'both', 'manual'):
        raise HarnessError('agent는 codex, claude, both, manual 중 하나여야 합니다.')
    result['agent'] = profile['agent']
    result['workspace'] = str(checked_directory(string(profile.get('workspace'), 'workspace', 1024)))
    return result


def ask_profile(profile):
    questions = [('role', '담당 역할'), ('courses', '담당 과목/주제'), ('audience', '학습 대상'),
                 ('session_minutes', '한 차시 시간(분)'), ('tasks', '우선 만들 산출물(쉼표로 구분)'),
                 ('tone', '문체'), ('agent', 'AI 도구(codex/claude/both/manual)')]
    print('공군 교관 에디션 설정 — 이름·계정·보안자료 대신 일반 업무 특성만 입력하세요.')
    for key, label in questions:
        old = ', '.join(profile[key]) if isinstance(profile[key], list) else str(profile[key])
        value = input(f'{label} [{old}]: ').strip()
        if value:
            if key == 'session_minutes':
                try:
                    value = int(value)
                except ValueError as exc:
                    raise HarnessError('차시 시간은 정수로 입력하세요.') from exc
            profile[key] = value
    return profile


def answers(path):
    value = read_json(Path(path).expanduser())
    if not isinstance(value, dict):
        raise HarnessError('응답 파일은 JSON 객체여야 합니다.')
    if set(value) - PROFILE_KEYS:
        raise HarnessError('알 수 없는 응답 항목: ' + ', '.join(sorted(set(value) - PROFILE_KEYS)))
    return value


def generated_files(root, workspace, profile, contents):
    """Only common templates/skills and generated instructions; never read participant documents."""
    command = f'"{sys.executable}" "{root / "bundle/harness.py"}" configure --root "{root}"'
    guidance = f'''# 공군 교관 에디션

이 작업실의 설정은 `.harness/profile.json`에 있습니다. 먼저 읽고 아래 기준을 따르세요.

- 역할: {profile['role']}
- 주제: {profile['courses']}
- 대상: {profile['audience']}
- 차시: {profile['session_minutes']}분
- 우선 산출물: {', '.join(profile['tasks'])}
- 문체: {profile['tone']}

사용자가 "시작", "내 환경 설정", "역프롬프트"라고 하면 역할·대상·차시·산출물·자료 범위를 짧게 확인하세요.
이미 설정한 내용을 되묻지 말고, 빠진 조건만 한 번에 1~3개 질문하세요. 답을 요약한 뒤 사용자의 의도에 맞는 업무 프롬프트를 작성하세요.
설정 변경은 응답을 로컬 JSON으로 저장하고 아래 명령에 `--answers 파일경로`를 붙여 반영하세요.

```text
{command}
```

공통 스킬 원본: `{root / 'bundle/skills'}`. `instructor-start` 스킬을 먼저 읽으세요.
교육 설계는 목표→활동→평가의 연결을 확인하고, 제공되지 않은 사실·평가 결과는 만들지 마세요.
작업 자료는 이 로컬 작업실에 둡니다. 동기화는 공통 스킬·서식만 갱신하며 개인 설정·작성 문서를 업로드하지 않습니다.
'''
    start = f'''# 시작하기

1. 이 폴더를 Codex 또는 Claude Code에서 여세요. AI 로그인은 각 앱에서 진행합니다.
2. 다음 문장을 입력하세요.

> 공군 교관 에디션을 시작해줘. `.harness/profile.json`과 `.harness/AGENTS.generated.md`를 읽고, 내 업무에 필요한 조건을 역프롬프트로 물어봐. 답변에 맞춰 설정하고 첫 강의안 하나를 함께 만들어줘.

3. 직접 설정하려면 아래 명령을 실행하세요.

```text
{command}
```

상태 점검: `"{sys.executable}" "{root / 'bundle/harness.py'}" doctor --root "{root}"`
전체 날쌤팩의 문서·PPT 도구는 선택 설치입니다. 이 기본 작업실은 Python 표준 라이브러리만 사용합니다.
'''
    files = {workspace / '.harness/profile.json': json_bytes(profile),
             workspace / '.harness/AGENTS.generated.md': guidance.encode(),
             workspace / 'AGENTS.md': guidance.encode(),
             workspace / 'CLAUDE.md': b'# Instructor workspace\n\nRead `.harness/AGENTS.generated.md` and `.harness/profile.json` before work.\n',
             workspace / 'START-HERE.md': start.encode(),
             workspace / '.harness/.gitignore': b'profile.json\n'}
    for name, body in contents.items():
        rel = PurePosixPath(name)
        if rel.parts[0] == 'templates':
            files[workspace / name] = body
        if rel.parts[0] == 'skills':
            if profile['agent'] in ('codex', 'both'):
                files[workspace / '.agents' / name] = body
            if profile['agent'] in ('claude', 'both'):
                files[workspace / '.claude' / name] = body
    return files


def planned_conflicts(files, state, root, workspace, optional=()):
    managed = state.get('managed', {}) if state else {}
    conflicts = []
    skipped = []
    for path, body in files.items():
        boundary = root if path.is_relative_to(root) else workspace
        no_symlink(path, boundary)
        if not path.exists():
            continue
        if not path.is_file():
            conflicts.append(str(path))
            continue
        current = digest(path.read_bytes())
        owned = managed.get(str(path))
        if owned and current != owned:
            conflicts.append(str(path))
        elif not owned:
            if path in optional:
                skipped.append(path)
            else:
                conflicts.append(str(path))
    if conflicts:
        raise HarnessError('사용자가 만든/수정한 파일을 보존했습니다. 별도 설치 경로를 선택하거나 변경본을 백업하세요:\n' + '\n'.join(conflicts))
    return skipped


def apply(files, state, root, workspace):
    optional = {workspace / 'AGENTS.md', workspace / 'CLAUDE.md', workspace / 'START-HERE.md'}
    skipped = planned_conflicts(files, state, root, workspace, optional)
    managed = dict(state.get('managed', {}))
    for path, body in files.items():
        if path in skipped:
            continue
        boundary = root if path.is_relative_to(root) else workspace
        # Recheck immediately before replacement instead of overwriting a concurrent edit.
        planned_conflicts({path: body}, {'managed': managed}, root, workspace)
        atomic_write(path, body, boundary)
        managed[str(path)] = digest(body)
    state['managed'] = managed
    return skipped


def save_state(root, state):
    atomic_write(state_path(root), json_bytes(state), root)


def install(args):
    root = checked_directory(args.root)
    source = checked_directory(args.source or Path(__file__).parent)
    manifest, contents = read_bundle(source)
    old = load_state(root, required=False)
    workspace = checked_directory(args.workspace or (old['workspace'] if old else root / 'workspace'))
    if root == workspace:
        raise HarnessError('--root와 --workspace는 서로 다른 폴더로 지정하세요.')
    profile = dict(DEFAULTS)
    defaults = json.loads(contents['defaults.json'])
    profile.update({k: v for k, v in defaults.items() if k in PROFILE_KEYS})
    if old:
        no_symlink(Path(old['workspace']) / '.harness/profile.json', Path(old['workspace']))
        profile.update(read_json(Path(old['workspace']) / '.harness/profile.json'))
        if workspace != Path(old['workspace']):
            raise HarnessError('기존 작업실 위치는 바꾸지 않습니다. 새 --root로 설치하세요.')
    profile['workspace'] = str(workspace)
    if args.answers:
        supplied = answers(args.answers)
        if supplied.get('workspace') and checked_directory(supplied['workspace']) != workspace:
            raise HarnessError('응답의 workspace와 설치 작업실 위치가 다릅니다.')
        profile.update(supplied)
        profile['workspace'] = str(workspace)
    if args.agent:
        profile['agent'] = args.agent
    if not args.answers and not args.non_interactive and sys.stdin.isatty():
        profile = ask_profile(profile)
    profile = validate_profile(profile)
    files = {root / 'bundle' / name: body for name, body in contents.items()}
    files[root / 'bundle/bundle.json'] = json_bytes(manifest)
    files.update(generated_files(root, workspace, profile, contents))
    # Native launchers point at retained runtime, never the temporary download folder.
    if os.name == 'nt':
        python_cmd = sys.executable.replace('%', '%%')
        script_cmd = str(root / 'bundle/harness.py').replace('%', '%%')
        launcher = f'@echo off\r\n@setlocal DisableDelayedExpansion\r\n@chcp 65001 >nul\r\n"{python_cmd}" "{script_cmd}" %*\r\n'
        files[root / 'bin/instructor.cmd'] = launcher.encode()
    else:
        launcher = f'#!/bin/sh\nexec {shlex.quote(sys.executable)} {shlex.quote(str(root / "bundle/harness.py"))} "$@"\n'
        files[root / 'bin/instructor'] = launcher.encode()
    state = old or {'kind': MARKER, 'managed': {}}
    if old:
        profile_path = workspace / '.harness/profile.json'
        no_symlink(profile_path, workspace)
        state['managed'][str(profile_path)] = digest(profile_path.read_bytes())
    skipped = apply(files, state, root, workspace)
    state.update(version=manifest['version'], workspace=str(workspace), root=str(root), source_ref=None)
    save_state(root, state)
    if os.name != 'nt':
        (root / 'bin/instructor').chmod(0o755)
    print(f'설치 완료: {workspace}\n시작 안내: {workspace / "START-HERE.md"}\n설정: {workspace / ".harness/profile.json"}')
    if skipped:
        print('기존 사용자 안내 파일 보존: ' + ', '.join(str(p) for p in skipped))
    print('AI 앱에서 이 작업실 폴더를 열고 "공군 교관 에디션을 시작해줘"라고 입력하세요.')
    return 0


def configure(args):
    root = checked_directory(args.root)
    state = load_state(root)
    workspace = Path(state['workspace'])
    profile_path = workspace / '.harness/profile.json'
    # Profile is explicitly editable; its digest may change between configure runs.
    no_symlink(profile_path, workspace)
    profile = read_json(profile_path)
    if args.answers:
        supplied = answers(args.answers)
        if supplied.get('workspace') and checked_directory(supplied['workspace']) != workspace:
            raise HarnessError('설정으로 작업실 위치를 이동할 수 없습니다.')
        profile.update(supplied)
    elif sys.stdin.isatty():
        profile = ask_profile(profile)
    else:
        raise HarnessError('대화형 터미널 또는 --answers 응답.json이 필요합니다.')
    profile['workspace'] = str(workspace)
    profile = validate_profile(profile)
    manifest, contents = read_bundle(root / 'bundle')
    generated = generated_files(root, workspace, profile, contents)
    files = {path: body for path, body in generated.items()
             if path.relative_to(workspace).parts[0] not in ('templates', '.agents', '.claude')}
    # Changing AI apps registers missing local skills, without refreshing edited assets.
    for path, body in generated.items():
        if path.relative_to(workspace).parts[0] in ('.agents', '.claude'):
            if not path.exists() and not path.is_symlink():
                files[path] = body
    state['managed'][str(profile_path)] = digest(profile_path.read_bytes())
    skipped = apply(files, state, root, workspace)
    save_state(root, state)
    print('업무 설정 반영 완료: ' + str(profile_path))
    if skipped:
        print('사용자 안내 파일은 보존했습니다. .harness/AGENTS.generated.md에서 새 설정을 확인하세요.')
    return 0


def sync(args):
    root = checked_directory(args.root)
    state = load_state(root)
    workspace = Path(state['workspace'])
    if args.source:
        manifest, contents = read_bundle(args.source)
    else:
        if not args.ref:
            try:
                channel = json.loads(download(f'https://raw.githubusercontent.com/{REPOSITORY}/instructor-channel/channel.json'))
            except ValueError as exc:
                raise HarnessError('업데이트 채널 JSON 형식이 올바르지 않습니다.') from exc
            if not isinstance(channel, dict) or not isinstance(channel.get('version'), str):
                raise HarnessError('업데이트 채널 형식이 올바르지 않습니다.')
            args.ref = channel.get('ref')
        manifest, contents = remote_bundle(args.ref)
    no_symlink(workspace / '.harness/profile.json', workspace)
    profile = validate_profile(read_json(workspace / '.harness/profile.json'))
    files = {root / 'bundle' / name: body for name, body in contents.items()}
    files[root / 'bundle/bundle.json'] = json_bytes(manifest)
    generated = generated_files(root, workspace, profile, contents)
    generated.pop(workspace / '.harness/profile.json')
    files.update(generated)
    # Do not delete files removed upstream: user additions remain local.
    skipped = apply(files, state, root, workspace)
    state.update(version=manifest['version'], source_ref=args.ref or 'local')
    save_state(root, state)
    print(f'공통 스킬·서식 동기화 완료: {manifest["version"]}. 개인 설정·작성 문서는 업로드하지 않았습니다.')
    if skipped:
        print('기존 사용자 안내 파일은 보존했습니다.')
    return 0


def doctor(args):
    root = checked_directory(args.root)
    state = load_state(root)
    workspace = Path(state['workspace'])
    changed = []
    missing = []
    for name, checksum in state['managed'].items():
        path = Path(name)
        try:
            no_symlink(path, root if path.is_relative_to(root) else workspace)
            if not path.is_file():
                missing.append(name)
            elif digest(path.read_bytes()) != checksum:
                changed.append(name)
        except (HarnessError, OSError):
            changed.append(name)
    runtime_modified = [p for p in changed if Path(p).is_relative_to(root / 'bundle')]
    result = {'installed': True, 'version': state['version'], 'workspace': str(workspace),
              'python': sys.version.split()[0], 'codex_available': shutil.which('codex') is not None,
              'claude_available': shutil.which('claude') is not None,
              'missing': missing, 'modified': changed,
              'ready': not missing and not runtime_modified, 'ai_login_verified': False}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f'워크벤치 {state["version"]}: {workspace}\n누락 {len(missing)}개 / 사용자 수정 {len(changed)}개')
        print('AI CLI 로그인과 외부 API 연결은 이 검사에서 확인하지 않습니다.')
    return 2 if missing or runtime_modified else 0


def export_profile(args):
    root = checked_directory(args.root)
    state = load_state(root)
    no_symlink(Path(state['workspace']) / '.harness/profile.json', Path(state['workspace']))
    profile = validate_profile(read_json(Path(state['workspace']) / '.harness/profile.json'))
    # Workspace location is machine-local; importing always retains destination workspace.
    profile.pop('workspace')
    dest = Path(args.output).expanduser().absolute()
    if dest.exists() or dest.is_symlink():
        raise HarnessError('기존 내보내기 파일을 덮어쓰지 않습니다: ' + str(dest))
    atomic_write(dest, json_bytes(profile), dest.parent)
    print('업무 설정만 내보냈습니다(작성 자료·계정·키 제외): ' + str(dest))
    return 0


def uninstall(args):
    root = checked_directory(args.root)
    state = load_state(root)
    workspace = Path(state['workspace'])
    preserved = []
    remaining = {}
    for name, checksum in state['managed'].items():
        path = Path(name)
        if path == workspace / '.harness/profile.json':
            preserved.append(name)
            continue
        boundary = root if path.is_relative_to(root) else workspace
        try:
            no_symlink(path, boundary)
            if path.is_file() and digest(path.read_bytes()) == checksum:
                path.unlink()
            elif path.exists():
                preserved.append(name)
                remaining[name] = checksum
        except (HarnessError, OSError):
            preserved.append(name)
            remaining[name] = checksum
    state['managed'] = remaining
    if remaining:
        save_state(root, state)
    else:
        state_path(root).unlink()
    print('변경되지 않은 설치 파일을 제거했습니다. 작성 자료와 사용자 변경 파일은 보존했습니다.')
    if preserved:
        print('보존: ' + ', '.join(preserved))
    return 0


def parser():
    p = argparse.ArgumentParser(description='공군 교관 에디션 — 설치·역프롬프트 설정·공통 서식 동기화')
    p.add_argument('--version', action='version', version=VERSION)
    sub = p.add_subparsers(dest='command', required=True)
    for command in ('install', 'configure', 'doctor', 'status', 'sync', 'export', 'import', 'uninstall'):
        q = sub.add_parser(command)
        q.add_argument('--root', default=str(DEFAULT_ROOT), help='설치 폴더')
        if command == 'install':
            q.add_argument('--source', help='bundle.json이 있는 로컬 배포 폴더')
            q.add_argument('--workspace', help='교관 작업실 위치(기본: 설치폴더/workspace)')
            q.add_argument('--agent', choices=['codex', 'claude', 'both', 'manual'])
            q.add_argument('--answers', help='역프롬프트 응답 JSON 파일')
            q.add_argument('--non-interactive', action='store_true', help='기본값 또는 응답 파일로 설치')
        if command in ('configure', 'import'):
            q.add_argument('--answers', required=command == 'import', help='로컬 응답 JSON 파일')
        if command in ('doctor', 'status'):
            q.add_argument('--json', action='store_true')
        if command == 'sync':
            group = q.add_mutually_exclusive_group()
            group.add_argument('--source', help='로컬 공통 번들 폴더')
            group.add_argument('--ref', help='공식 GitHub 저장소의 40자리 커밋 SHA')
        if command == 'export':
            q.add_argument('--output', required=True, help='새 설정 JSON 파일 경로')
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    commands = {'install': install, 'configure': configure, 'import': configure, 'sync': sync,
                'doctor': doctor, 'status': doctor, 'export': export_profile, 'uninstall': uninstall}
    try:
        return commands[args.command](args)
    except (HarnessError, OSError, ValueError, TypeError) as exc:
        print('공군 교관 에디션: ' + str(exc), file=sys.stderr)
        return 2
    except (EOFError, KeyboardInterrupt):
        print('\n설정을 취소했습니다. 기존 사용자 자료는 보존했습니다.', file=sys.stderr)
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
