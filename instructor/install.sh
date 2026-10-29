#!/usr/bin/env bash
# macOS / Linux / WSL. Keep managed Python local; leave system packages and shell profiles alone.
set -euo pipefail
PYTHON=''
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null && "$candidate" -c 'import sys; assert sys.version_info >= (3,11)' 2>/dev/null; then
    PYTHON="$candidate"; break
  fi
done
if [[ -z "$PYTHON" && "$(uname -s)" == Darwin ]]; then
  # A new Mac may have no usable Python. Pin and verify uv before it installs a dedicated runtime.
  UV_VERSION=0.12.23
  PYTHON_VERSION=3.12.12
  case "$(uname -m)" in
    arm64|aarch64)
      UV_TARGET=aarch64-apple-darwin
      UV_SHA256=50487ae565ccd96e499056b4674d438f4c53170202617b4c759defe0c6a1b544 ;;
    x86_64|amd64)
      UV_TARGET=x86_64-apple-darwin
      UV_SHA256=960da44cb4b73685206ddd250b19e0a117fa41095710c1038f081f5cb613efb4 ;;
    *) echo "지원하지 않는 Mac CPU입니다: $(uname -m)" >&2; exit 1 ;;
  esac
  for required in curl tar shasum; do
    command -v "$required" >/dev/null || { echo "필수 도구가 없습니다: $required" >&2; exit 1; }
  done
  BOOTSTRAP_ROOT="${NALSSAM_INSTRUCTOR_BOOTSTRAP_DIR:-$HOME/.local/share/nalssam-instructor/bootstrap}"
  mkdir -p "$BOOTSTRAP_ROOT"
  BOOTSTRAP_TEMP=$(mktemp -d "$BOOTSTRAP_ROOT/.uv-download-XXXXXXXX")
  trap 'rm -rf "$BOOTSTRAP_TEMP"' EXIT
  echo '공군 교관 에디션 전용 Python을 사용자 폴더에 준비합니다. 시스템 Python은 변경하지 않습니다.'
  curl -fsSL "https://github.com/astral-sh/uv/releases/download/$UV_VERSION/uv-$UV_TARGET.tar.gz" -o "$BOOTSTRAP_TEMP/uv.tar.gz"
  ACTUAL_SHA256=$(shasum -a 256 "$BOOTSTRAP_TEMP/uv.tar.gz")
  ACTUAL_SHA256=${ACTUAL_SHA256%% *}
  if [[ "$ACTUAL_SHA256" != "$UV_SHA256" ]]; then
    echo 'uv 다운로드 체크섬이 일치하지 않아 설치를 중단했습니다.' >&2
    exit 1
  fi
  tar -xzf "$BOOTSTRAP_TEMP/uv.tar.gz" -C "$BOOTSTRAP_TEMP"
  UV_BIN="$BOOTSTRAP_TEMP/uv-$UV_TARGET/uv"
  [[ "$("$UV_BIN" --version)" == "uv $UV_VERSION"* ]] || { echo 'uv 버전 확인에 실패했습니다.' >&2; exit 1; }
  export UV_PYTHON_INSTALL_DIR="$BOOTSTRAP_ROOT/python"
  export UV_CACHE_DIR="$BOOTSTRAP_ROOT/cache"
  "$UV_BIN" python install --no-config --no-bin --no-progress "$PYTHON_VERSION"
  PYTHON=$("$UV_BIN" python find --no-config --managed-python --no-python-downloads "$PYTHON_VERSION")
  "$PYTHON" -c 'import sys; assert sys.version_info >= (3,11)'
  rm -rf "$BOOTSTRAP_TEMP"
  trap - EXIT
fi
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
curl -fsSL https://raw.githubusercontent.com/nalssam/nalssam-pack/instructor-v0.1.1/instructor/bootstrap.py -o "$TEMP/bootstrap.py"
"$PYTHON" "$TEMP/bootstrap.py" "$@"
