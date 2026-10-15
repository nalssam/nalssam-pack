#!/usr/bin/env bash
# 날쌘팩: macOS / Linux / Windows WSL2. No sudo, no credentials copied.
set -euo pipefail
PACK_VERSION="v1.0.0"
UV_VERSION="0.12.23"
PYTHON_VERSION="3.12.12"
REPOSITORY="nalssam/nalssam-pack"
DATA_ROOT="${NALSSAM_PACK_ROOT:-$HOME/.local/share/nalssam-pack}"

for cmd in curl tar; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "필수 도구가 없습니다: $cmd" >&2; exit 1; }
done
case "$(uname -s)" in
  Linux|Darwin) ;;
  *) echo 'Windows에서는 WSL2 Ubuntu에서 실행하세요.' >&2; exit 1 ;;
esac

# A downloaded install.sh has no sibling pack.py. Fetch a versioned archive.
SCRIPT_DIR=""
if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]}" ]]; then
  SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
fi
if [[ -z "$SCRIPT_DIR" || ! -f "$SCRIPT_DIR/pack.py" ]]; then
  mkdir -p "$DATA_ROOT"
  TEMP_DIR=$(mktemp -d)
  trap 'rm -rf "$TEMP_DIR"' EXIT
  curl -fsSL "https://github.com/$REPOSITORY/archive/refs/tags/$PACK_VERSION.tar.gz" -o "$TEMP_DIR/pack.tar.gz"
  tar -xzf "$TEMP_DIR/pack.tar.gz" -C "$TEMP_DIR"
  SOURCE="$TEMP_DIR/nalssam-pack-${PACK_VERSION#v}"
  DEST="$DATA_ROOT/installer-$PACK_VERSION"
  if [[ ! -f "$DEST/pack.py" ]]; then
    [[ ! -e "$DEST" ]] || { echo "기존 폴더 보존: $DEST" >&2; exit 1; }
    cp -R "$SOURCE" "$DEST"
  fi
  SCRIPT_DIR="$DEST"
fi

# uv itself lives in the pack, not in the system Python installation.
if ! command -v uv >/dev/null 2>&1; then
  mkdir -p "$DATA_ROOT/bootstrap/bin"
  curl -fsSL "https://astral.sh/uv/$UV_VERSION/install.sh" -o "$DATA_ROOT/bootstrap/uv-install.sh"
  UV_INSTALL_DIR="$DATA_ROOT/bootstrap/bin" UV_NO_MODIFY_PATH=1 sh "$DATA_ROOT/bootstrap/uv-install.sh"
  export PATH="$DATA_ROOT/bootstrap/bin:$PATH"
fi
if ! command -v git >/dev/null 2>&1; then
  echo 'Git이 필요합니다. macOS: xcode-select --install / Ubuntu·WSL: sudo apt install git' >&2
  exit 1
fi
uv python install "$PYTHON_VERSION"
# Keep options intact when invoked through: bash -c "$(curl ...)" -- --profile skills
uv run --python "$PYTHON_VERSION" --no-project python "$SCRIPT_DIR/pack.py" --root "$DATA_ROOT" "$@"
