#!/usr/bin/env python3
"""Refresh/check runtime checksums and create a reviewable workshop ZIP."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--zip', type=Path)
    args = parser.parse_args()
    paths = [HERE / 'harness.py', HERE / 'defaults.json']
    paths += sorted((HERE / 'skills').rglob('*.md')) + sorted((HERE / 'templates').rglob('*.md'))
    manifest = {'version': '0.1.1', 'files': {p.relative_to(HERE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    target = HERE / 'bundle.json'
    if args.check:
        if json.loads(target.read_text(encoding='utf-8')) != manifest:
            raise SystemExit('배포 목록이 오래되었습니다. python instructor/build_bundle.py 실행 필요')
    else:
        target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if args.zip:
        args.zip.parent.mkdir(parents=True, exist_ok=True)
        distribution = [HERE / n for n in ['bundle.json', 'bootstrap.py', 'install.sh', 'install.ps1', '공군교관설치.cmd', '공군교관설치.command', 'README.md']]
        distribution += paths
        with zipfile.ZipFile(args.zip, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in distribution:
                entry = zipfile.ZipInfo.from_file(path, 'nalssam-instructor/' + path.relative_to(HERE).as_posix())
                if path.suffix in ('.command', '.sh'):
                    # Preserve Mac double-click execution even when the ZIP is built on Windows.
                    entry.create_system = 3
                    entry.external_attr = 0o100755 << 16
                archive.writestr(entry, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
        digest = hashlib.sha256(args.zip.read_bytes()).hexdigest()
        args.zip.with_suffix(args.zip.suffix + '.sha256').write_text(digest + '  ' + args.zip.name + '\n')
        print(args.zip, digest)
    print('runtime manifest:', len(paths), 'files')


if __name__ == '__main__':
    main()
