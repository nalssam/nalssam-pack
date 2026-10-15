날쌘팩의 첫 배포 패키지입니다.

- 추천 저장소의 스킬과 문서·영상 CLI/MCP를 Codex용으로 구성합니다.
- Git 커밋·npm·Python 의존성을 고정합니다.
- 기존 설정 백업, 충돌 보존, 재설치, 실제 MCP 연결 진단, 영수증 기반 제거를 지원합니다.
- Mac 실행 파일, Windows WSL2 실행 파일, 터미널 설치기를 포함합니다.
- Claude Code 네이티브 플러그인 122개는 `--claude` 옵션입니다.

Linux 격리 HOME에서 전체 설치·재설치·제거, MCP 6개 연결, PPTX 생성 및 문서 변환을 확인했습니다. macOS·WSL2 전체 설치와 외부 계정 연동은 아직 별도 검증이 필요합니다.

ZIP을 풀고 macOS에서는 `날쌘팩설치.command`, Linux에서는 `bash install.sh`를 실행하세요. Windows는 WSL2 Ubuntu가 필요합니다.
