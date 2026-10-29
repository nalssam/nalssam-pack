#!/bin/bash
# Double-click this file after extracting the workshop ZIP on macOS.
set -u
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd) || exit 1
cd "$SCRIPT_DIR" || exit 1
bash "$SCRIPT_DIR/install.sh" "$@"
STATUS=$?
if [[ "$STATUS" -eq 0 ]]; then
  printf '\n공군 교관 에디션 설치가 완료되었습니다. 표시된 작업실 폴더를 AI 앱에서 여세요.\n'
else
  printf '\n설치가 완료되지 않았습니다(종료 코드 %s). 위 오류를 확인한 뒤 다시 실행하세요.\n' "$STATUS" >&2
fi
if [[ -t 0 ]]; then
  printf '\n이 창을 닫으려면 Enter 키를 누르세요. '
  read -r _ || true
fi
exit "$STATUS"
