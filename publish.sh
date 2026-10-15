#!/usr/bin/env bash
# Run in an authenticated GitHub CLI on a machine permitted to create/push this repository.
set -euo pipefail
cd "$(dirname "$0")"
REPO=nalssam/nalssam-pack
TAG=v1.0.0
for tool in gh git python3; do
  command -v "$tool" >/dev/null || { echo "필수 도구: $tool" >&2; exit 1; }
done
gh auth status
python3 -m unittest discover -s tests -v
bash -n install.sh
if [[ ! -d .git ]]; then
  git init -b main
  git add .
  git -c user.name=nalssam -c user.email=nalssam@users.noreply.github.com commit -m 'feat: release Nalssam Pack v1.0.0'
fi
if ! gh repo view "$REPO" >/dev/null 2>&1; then
  gh repo create "$REPO" --public --description '날쌘팩 — 한 줄로 준비하는 Codex 작업 환경'
fi
if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "https://github.com/$REPO.git"
fi
EXPECTED="https://github.com/$REPO.git"
[[ "$(git remote get-url origin)" == "$EXPECTED" ]] || { echo 'origin 저장소를 직접 확인하세요.' >&2; exit 1; }
git push -u origin main
if gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
  echo "$TAG 릴리스가 이미 있습니다. 기존 릴리스를 덮어쓰지 않았습니다."
  exit 0
fi
if ! git rev-parse "$TAG" >/dev/null 2>&1; then
  git tag "$TAG"
fi
git push origin "$TAG"
BUILD_DIR=$(mktemp -d)
trap 'rm -rf "$BUILD_DIR"' EXIT
git archive --format=zip --prefix=nalssam-pack/ --output="$BUILD_DIR/nalssam-pack-$TAG.zip" "$TAG"
python3 - "$BUILD_DIR" "$TAG" <<'PY'
import hashlib,sys
from pathlib import Path
p=Path(sys.argv[1]);z=p/('nalssam-pack-'+sys.argv[2]+'.zip')
(p/'SHA256SUMS.txt').write_text(hashlib.sha256(z.read_bytes()).hexdigest()+'  '+z.name+'\n')
PY
gh release create "$TAG" --repo "$REPO" --title "날쌘팩 $TAG" --notes-file RELEASE_NOTES.md "$BUILD_DIR/nalssam-pack-$TAG.zip" "$BUILD_DIR/SHA256SUMS.txt"
echo "공개 완료: https://github.com/$REPO"
