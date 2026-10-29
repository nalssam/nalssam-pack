#!/usr/bin/env python3
"""Fetch only the published instructor bundle, verify it, and install locally."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import urllib.request

CHANNEL = 'https://raw.githubusercontent.com/nalssam/nalssam-pack/instructor-channel/channel.json'
BASE = 'https://raw.githubusercontent.com/nalssam/nalssam-pack/{ref}/instructor/'
MAX_FILE = 2 * 1024 * 1024


def fetch(url):
    with urllib.request.urlopen(url, timeout=40) as response:
        if not response.url.startswith('https://raw.githubusercontent.com/'):
            raise ValueError('허용되지 않은 다운로드 경로입니다.')
        body = response.read(MAX_FILE + 1)
    if len(body) > MAX_FILE:
        raise ValueError('다운로드 파일이 제한 크기를 초과했습니다.')
    return body


def validate_manifest(manifest):
    if not isinstance(manifest, dict):
        raise ValueError('배포 목록은 JSON 객체여야 합니다.')
    files = manifest.get('files', {})
    if not isinstance(files, dict) or not 2 <= len(files) <= 100:
        raise ValueError('올바른 배포 목록이 아닙니다.')
    seen = set()
    for name, digest in files.items():
        if not isinstance(name, str):
            raise ValueError('배포 파일 이름은 문자열이어야 합니다.')
        path = PurePosixPath(name)
        if (path.is_absolute() or '..' in path.parts or '\\' in name
                or str(path) != name or ':' in name or '\x00' in name
                or not (name in ('harness.py', 'defaults.json')
                        or (name.startswith(('skills/', 'templates/'))
                            and not any(p.startswith('.') for p in path.parts)
                            and path.suffix.lower() in ('.md', '.json', '.txt', '.csv')))
                or not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest)):
            raise ValueError('배포 목록에 허용되지 않은 경로/체크섬이 있습니다.')
        if name.casefold() in seen:
            raise ValueError('대소문자가 겹치는 배포 파일입니다.')
        seen.add(name.casefold())
    if not {'harness.py', 'defaults.json'} <= files.keys():
        raise ValueError('필수 파일이 없습니다.')
    return files


def main(argv=None):
    parser = argparse.ArgumentParser(description='공군 교관 에디션 설치')
    parser.add_argument('--root', type=Path)
    parser.add_argument('--workspace', type=Path)
    parser.add_argument('--agent', choices=['codex', 'claude', 'both', 'manual'], default='codex')
    parser.add_argument('--answers', type=Path)
    parser.add_argument('--non-interactive', action='store_true', help='기본 설치는 항상 비대화형으로 진행합니다.')
    parser.add_argument('--source', type=Path, help='검증할 로컬 배포 폴더 (오프라인 ZIP 설치)')
    parser.add_argument('--ref', help='배포할 정확한 Git 커밋 SHA (생략 시 연수 채널)')
    args = parser.parse_args(argv)
    root = args.root or (Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'NalssamInstructor'
                         if os.name == 'nt' else Path.home() / '.local/share/nalssam-instructor')
    workspace = args.workspace or Path.home() / 'Documents/NalssamInstructor'
    with tempfile.TemporaryDirectory(prefix='nalssam-instructor-') as temp:
        stage = Path(temp)
        if args.source:
            source = args.source.resolve()
            manifest_bytes = (source / 'bundle.json').read_bytes()
            read = lambda name: (source / name).read_bytes()
        else:
            ref = args.ref
            if not ref:
                channel = json.loads(fetch(CHANNEL))
                ref = channel.get('ref', '')
            if not re.fullmatch('[0-9a-f]{40}', ref):
                raise ValueError('동기화 채널에 고정된 Git 커밋이 필요합니다.')
            base = BASE.format(ref=ref)
            manifest_bytes = fetch(base + 'bundle.json')
            read = lambda name: fetch(base + name)
            print('고정 배포 커밋:', ref, flush=True)
        manifest = json.loads(manifest_bytes)
        files = validate_manifest(manifest)
        total = 0
        for name, digest in files.items():
            if args.source and not (source / name).resolve().is_relative_to(source):
                raise ValueError('배포 폴더 밖을 가리키는 파일입니다.')
            body = read(name)
            total += len(body)
            if len(body) > MAX_FILE or total > 10 * MAX_FILE:
                raise ValueError('배포 크기 제한 초과')
            if hashlib.sha256(body).hexdigest() != digest:
                raise ValueError('체크섬 불일치: ' + name)
            dest = stage / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(body)
        (stage / 'bundle.json').write_bytes(manifest_bytes)
        command = [sys.executable, str(stage / 'harness.py'), 'install', '--root', str(root),
                   '--workspace', str(workspace), '--agent', args.agent, '--non-interactive']
        if args.answers:
            command += ['--answers', str(args.answers.resolve())]
        return subprocess.call(command)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print('설치 중단:', exc, file=sys.stderr)
        raise SystemExit(1)
