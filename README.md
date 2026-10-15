<div align="center">

# 날쌘팩 · nalssam-pack

**한 줄로 준비하는 나만의 Codex 작업실.**

한국어 문서 · PPT · 모션그래픽 · 영상 · 브라우저 · 개발 스킬과 MCP를 한 번에.

</div>

## 바로 설치

**macOS · Linux · Windows의 WSL2 Ubuntu** 터미널 또는 명령 실행이 가능한 Codex 작업 환경에서:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/nalssam/nalssam-pack/v1.0.0/install.sh)"
```

첫 설치에는 다운로드와 빌드 시간이 필요합니다. 설치가 끝나면 **새 터미널과 Codex 새 세션**을 여세요. Codex에 아직 로그인하지 않았다면 `codex login`을 실행합니다. 기존 Codex CLI는 유지하고, 없으면 날쌘팩 전용 경로에 설치합니다.

Codex에 한 문장으로 맡길 수도 있습니다:

> https://github.com/nalssam/nalssam-pack 의 README를 읽고 날쌘팩을 설치한 다음 MCP 연결을 진단해 줘.

일반 ChatGPT 웹 채팅은 내 컴퓨터의 설치 명령을 실행하지 않습니다. **Codex 앱·CLI·작업 환경처럼 파일과 터미널을 사용할 수 있는 환경**에서 실행하세요. 클라우드 환경에 설치하면 그 환경에만 적용됩니다.

## 버튼처럼 실행

[최신 릴리스](https://github.com/nalssam/nalssam-pack/releases/latest)의 ZIP을 받아 압축을 풉니다.

- **Mac:** `날쌘팩설치.command` 실행. 최초 실행 시 macOS의 다운로드 파일 확인 절차가 나타날 수 있습니다.
- **Windows:** WSL2 Ubuntu를 먼저 설치한 뒤 `install-windows.cmd` 실행. 도구는 WSL 안에 설치됩니다. 네이티브 Windows 설치기는 아닙니다.
- **Linux:** 폴더에서 `bash install.sh` 실행.

## 무엇이 들어 있나요?

| 분야 | 구성 |
|---|---|
| 한글·문서 | HWPX New, Kordoc, MarkItDown, PPTX Maker |
| 영상·모션 | Motion Director, Showreel, Cinetic, motion-graphics, claude-video, Sprite Gen |
| UI·디자인 | UI UX Pro Max, Taste, Impeccable |
| 개발·조사 | REA, Playwright, Agent Reach, Google Skills, Karpathy Skills |
| 작업 방식·기억 | ECC, Caveman, Harness, Wshobson Agents, Superpowers, Claude Mem |
| 참고 모음 | Harness 100, Awesome Claude Code, Superpowers Marketplace |
| 원본 보관·호스트별 기능 | After Effects MCP, Codex Plugin for Claude Code |

사용자가 추천한 **29개 원본 저장소**와 추가 의존 저장소를 `pack.lock.json`에 기록했습니다. 접근 불가인 `lifeofpi-ux/ppt-automation`은 실패를 숨기지 않고 미설치로 표시합니다. 참고 모음은 소스로 보관하며, 목록에 나오는 모든 외부 링크를 무제한으로 설치하지 않습니다.

기본값은 **Codex 전체 구성**입니다. 원본에서 실제 제공하는 스킬을 연결하고 문서·영상 CLI와 MCP, Codex용 Claude Mem 플러그인을 설치합니다. Claude Code 전용 훅을 Codex 설정으로 바꾸어 넣지 않습니다. Claude Code에서 사용하던 네이티브 플러그인 122개도 원한다면 `--claude` 옵션을 쓰세요.

### 버전을 고정합니다

- 저장소는 브랜치 최신값 대신 **40자리 Git 커밋**으로 받습니다.
- Node `24.19.0`, 관리 Python `3.12.12`, Codex(없는 경우) `0.159.2` 기준입니다.
- npm은 lockfile과 `npm ci`, Python은 고정된 의존성 제약 파일을 사용합니다.
- 설치 대상 폴더에 전용 런타임·가상환경을 만들고 시스템 Python/Node를 교체하지 않습니다.
- OS별 실행 파일·미디어 라이브러리·기존 Codex 버전은 다를 수 있습니다. 완전히 동일한 OS 이미지나 계정 권한을 복제하는 기능은 아닙니다.

## 설치 옵션

처음 실행할 때는 한 줄 뒤에 옵션을 붙입니다.

```bash
# 스킬·원본만 설치: 영상·문서 런타임 다운로드와 MCP 등록 생략
bash -c "$(curl -fsSL https://raw.githubusercontent.com/nalssam/nalssam-pack/v1.0.0/install.sh)" -- --profile skills

# Codex + Claude Code 스킬 및 네이티브 플러그인
bash -c "$(curl -fsSL https://raw.githubusercontent.com/nalssam/nalssam-pack/v1.0.0/install.sh)" -- --claude

# 설치 전에 목록만 보기 (부트스트랩 Python 준비는 진행)
bash -c "$(curl -fsSL https://raw.githubusercontent.com/nalssam/nalssam-pack/v1.0.0/install.sh)" -- plan
```

이미 설치했다면:

```bash
nalssam-pack plan
nalssam-pack install                        # 다시 실행해 누락·실패 단계 재시도
nalssam-pack install --only ZZombie04/motion # 특정 저장소만
nalssam-pack doctor --verify-mcp            # 실제 MCP 연결·도구 목록 검사
nalssam-pack uninstall                      # 날쌘팩이 만든 연결만 해제
```

기본 설치 경로는 `~/.local/share/nalssam-pack`입니다. `NALSSAM_PACK_ROOT=/원하는/경로 bash install.sh` 또는 `--root`로 바꿀 수 있습니다. PATH에 명령이 없다면 `. ~/.local/share/nalssam-pack/env.sh`를 실행하세요.

## 기존 환경을 보존합니다

- 기존 스킬과 이름이 겹치면 원본을 보존하고 별도 이름으로 연결합니다.
- 기존 MCP와 겹치면 `nalssam-` 접두사로 구분합니다. 설치 이후 사용자가 수정한 MCP는 덮어쓰지 않습니다.
- Codex 설정과 셸 시작 파일의 기존 내용은 보존하고 백업합니다.
- 설치 영수증 `state.json`에 날쌘팩이 만든 연결만 기록합니다.
- 제거 시 현재 값이 영수증과 일치하는 연결만 해제합니다. **소스·캐시·가상환경·백업은 남깁니다.**
- 동시에 같은 폴더에서 두 설치기가 상태를 덮어쓰지 않도록 잠급니다.

Claude Code 옵션은 네이티브 플러그인을 설치하므로 해당 플러그인의 훅과 동작 방식도 적용됩니다. 기본 Codex 설치와 구분해서 선택하세요.

## 설치와 실제 사용 준비는 다릅니다

| 항목 | 추가로 필요한 것 |
|---|---|
| Codex | 본인의 ChatGPT 계정 로그인 또는 지원되는 API 인증 |
| Showreel 나레이션·일부 음악 | ElevenLabs 키와 해당 요금제 |
| claude-video 음성 인식·Gemini | 선택한 백엔드 또는 본인 API 키. 프레임 분석은 로컬 도구로 가능 |
| Google Cloud·외부 서비스 MCP | 본인 프로젝트·계정·서비스별 설정 |
| Claude Mem | 설치 후 관찰 모델·계정 설정 및 동작 점검. 메모리 수집 성공을 설치 성공으로 대신하지 않음 |
| After Effects | macOS/Windows의 Adobe After Effects 2022+와 연결 패널. Linux에서는 소스·스킬만 준비 |
| REA 네이티브 분석 | 분석 대상에 맞는 Ghidra/IDA 등 별도 엔진 |
| PPTX의 PowerPoint 전용 내보내기 | 지원되는 PowerPoint 환경. PPTX 자체 생성은 PowerPoint 없이 가능 |
| 영상 렌더 | ffmpeg·ffprobe, Chromium 실행에 필요한 OS 라이브러리 |

설치기는 `sudo`를 자동 실행하지 않습니다. ffmpeg가 없으면 macOS는 `brew install ffmpeg`, Ubuntu/WSL은 `sudo apt install ffmpeg`로 준비하세요. Chromium이 없으면 관리 브라우저 다운로드를 시도하지만, Linux의 필수 공유 라이브러리는 OS에서 설치해야 할 수 있습니다. Git·curl·tar가 먼저 필요합니다. Python은 uv를 통해 사용자 범위에 준비합니다.

**계정·쿠키·API 키·유료 라이선스는 배포 파일에 포함하지 않습니다.** 따라서 "설치 완료"와 "외부 서비스 연결 완료"를 구분해 보고합니다.

## 확인할 파일

- `pack.lock.json`: 저장소 커밋, 옵션 플러그인 목록
- `locks/`: npm·Python 의존성 버전
- 설치 경로의 `report.json`: 단계별 성공·실패·추가 설정
- 설치 경로의 `doctor.json`: MCP 실제 연결 검사 결과
- 설치 경로의 `state.json`: 제거·재설치에 쓰는 영수증
- 설치 경로의 `backups/`: 기존 설정 백업

중간에 실패하면 오류 원인을 해결한 뒤 같은 명령을 다시 실행하세요. 실패한 소스 다운로드는 완성된 체크아웃으로 등록하지 않습니다. 일부 실패가 있으면 종료 코드는 1이고 `report.json`에 남습니다.

## 개발·검증

```bash
python3 -m unittest discover -s tests -v
bash -n install.sh
python3 pack.py plan
```

지원 대상은 macOS와 Linux/WSL2입니다. 실제 검증 범위는 [검증 기록](VERIFICATION.md)에 적습니다.

## 라이선스

날쌘팩 설치 코드는 MIT입니다. 포함 도구는 원본 저장소에서 다운로드하며 각각의 라이선스를 따릅니다. Remotion·Adobe·외부 API의 별도 사용 조건도 그대로 적용됩니다. 원본 코드·이미지·사용자 계정 정보를 한 ZIP에 재배포하지 않습니다.

## 공개 배포하기

ZIP 자체는 공개 주소 없이도 `bash install.sh`로 설치할 수 있습니다. 새 공개 저장소 생성 권한이 있는 GitHub CLI 환경에서 패키지를 배포하려면:

```bash
bash publish.sh
```

이 명령은 `nalssam/nalssam-pack` 공개 저장소, `v1.0.0` 태그와 ZIP 릴리스를 만듭니다. 이미 있는 릴리스를 덮어쓰지 않습니다. 저장소를 만든 뒤에도 현재 GitHub 앱 연결에 새 저장소 접근 권한을 추가해야 업로드할 수 있는 경우가 있습니다.
