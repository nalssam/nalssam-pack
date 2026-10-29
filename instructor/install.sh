#!/usr/bin/env bash
# macOS / Linux / WSL. Uses the system Python; does not alter system packages.
set -euo pipefail
PYTHON=''
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null && "$candidate" -c 'import sys; assert sys.version_info >= (3,11)' 2>/dev/null; then
    PYTHON="$candidate"; break
  fi
done
if [[ -z "$PYTHON" ]]; then
  echo 'Python 3.11 이상이 필요합니다. python.org 또는 OS 패키지 관리자로 설치한 뒤 다시 실행하세요.' >&2
  exit 1
fi
SOURCE=''
if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]}" ]]; then
  SOURCE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
fi
if [[ -n "$SOURCE" && -f "$SOURCE/bootstrap.py" && -f "$SOURCE/bundle.json" ]]; then
  exec "$PYTHON" "$SOURCE/bootstrap.py" --source "$SOURCE" "$@"
fi
command -v curl >/dev/null || { echo 'curl이 필요합니다.' >&2; exit 1; }
TEMP=$(mktemp -d)
trap 'rm -rf "$TEMP"' EXIT
curl -fsSL https://raw.githubusercontent.com/nalssam/nalssam-pack/instructor-v0.1.0/instructor/bootstrap.py -o "$TEMP/bootstrap.py"
"$PYTHON" "$TEMP/bootstrap.py" "$@"
