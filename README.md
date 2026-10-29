<div align="center">

# 날쌤팩 · nalssam-pack

**한 줄로 준비하는 나만의 Codex · Claude Code 작업실.**

한국어 문서 · PPT · 모션그래픽 · 영상 · 브라우저 · 개발 스킬과 MCP를 한 번에.

</div>

## 교관 연수용 에디션

**[공군 교관 에디션 →](instructor/README.md)** — Mac·Windows 더블클릭 설치, 역프롬프트 맞춤 설정, 교수설계·평가·실습자료 스킬과 양식, 공통 설정 내려받기 동기화를 제공합니다. 기존 전체 팩과 구분되는 Python 표준 라이브러리 기반 작업실입니다.

## 바로 설치

**macOS · Linux · Windows의 WSL2 Ubuntu** 터미널 또는 명령 실행이 가능한 Codex 작업 환경에서:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/nalssam/nalssam-pack/v1.0.1/install.sh)"
```

첫 설치에는 다운로드와 빌드 시간이 필요합니다. 설치가 끝나면 **새 터미널과 Codex 새 세션**을 여세요. Codex에 아직 로그인하지 않았다면 `codex login`을 실행합니다. 기존 Codex CLI는 유지하고, 없으면 날쌤팩 전용 경로에 설치합니다.

Codex에 한 문장으로 맡길 수도 있습니다:

> https://github.com/nalssam/nalssam-pack 의 README를 읽고 날쌤팩을 설치한 다음 MCP 연결을 진단해 줘.

일반 ChatGPT 웹 채팅은 내 컴퓨터의 설치 명령을 실행하지 않습니다. **Codex 앱·CLI·작업 환경처럼 파일과 터미널을 사용할 수 있는 환경**에서 실행하세요. 클라우드 환경에 설치하면 그 환경에만 적용됩니다.

## Claude Code에서 설치

**Claude Code**에서도 날쌤팩을 사용할 수 있습니다. macOS·Linux·Windows WSL2 Ubuntu 터미널에서 다음 명령을 실행하세요.

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/nalssam/nalssam-pack/v1.0.1/install.sh)" -- --claude
```

`--claude`는 **기본 Codex 구성에 Claude Code 지원을 추가하는 옵션**입니다. Claude 전용 설치 모드는 아닙니다. Claude Code CLI가 없으면 날쌤팩 전용 경로에 준비하고, Claude용 스킬과 네이티브 플러그인 123개를 설치합니다. 플러그인에 포함된 훅과 서비스별 추가 설정도 적용됩니다.

이미 날쌤팩이 설치돼 있다면 다시 다운로드하지 않고 실행할 수 있습니다.

```bash
nalssam-pack install --claude
```

Claude Code 안에서 설치를 맡기려면 다음 문장을 입력하세요.

> https://github.com/nalssam/nalssam-pack 의 README를 읽고 `--claude` 옵션으로 날쌤팩을 설치해 줘. 설치 결과에서 실패한 단계와 추가 계정 설정이 필요한 항목을 구분해서 알려줘.

설치 후에는 **새 터미널에서 Claude Code를 다시 시작**하세요. 처음 사용하는 경우 `claude`를 실행해 본인의 Claude 계정으로 로그인합니다. 기존 Claude 인증 정보를 다른 사람에게 복사할 필요는 없습니다.

```bash
claude
# Claude Code 안에서 /plugin 으로 설치된 플러그인 확인
```

터미널에서 목록을 확인하려면:

```bash
claude plugin list
claude mcp list
```

### Claude Code에 문서·영상 MCP도 연결하기

현재 v1.0.1의 `--claude` 옵션은 Claude용 **스킬·네이티브 플러그인**을 설치합니다. 날쌤팩 공통 MCP 7개의 자동 등록과 `nalssam-pack doctor --verify-mcp` 검사는 **Codex 기준**입니다. Claude Code에서도 이 MCP들을 쓰려면 설치 후 아래 명령으로 별도 등록하세요. 플러그인 자체가 제공하는 MCP와는 구분됩니다.

기본 설치 경로 기준입니다. `--root`로 경로를 바꿨다면 아래 경로도 함께 바꾸세요.

```bash
claude mcp add --scope user nalssam-rea -- "$HOME/.local/share/nalssam-pack/bin/rea" mcp
claude mcp add --scope user nalssam-hwpx -- "$HOME/.local/share/nalssam-pack/bin/hwpx-new-mcp"
claude mcp add --scope user nalssam-pptx -- "$HOME/.local/share/nalssam-pack/bin/pptx-maker-mcp"
claude mcp add --scope user nalssam-markitdown -- "$HOME/.local/share/nalssam-pack/bin/markitdown-mcp"
claude mcp add --scope user nalssam-kordoc -- "$HOME/.local/share/nalssam-pack/bin/kordoc-mcp"
claude mcp add --scope user nalssam-motion -- "$HOME/.local/share/nalssam-pack/bin/motion-mcp"
claude mcp add --scope user nalssam-reason-network -- "$HOME/.local/share/nalssam-pack/bin/reason-network" mcp
claude mcp list
```

같은 이름의 서버가 이미 있다면 기존 설정을 보존하고 다른 이름으로 등록하세요. 이 방식으로 수동 등록한 Claude MCP는 날쌤팩 제거 영수증에 포함되지 않습니다. 해제할 때는 해당 이름을 지정해 `claude mcp remove --scope user 서버이름`을 실행하세요.

**Claude 웹 채팅이나 일반 Claude Desktop 채팅에 위 문장을 붙여 넣는 것만으로 PC에 설치되지는 않습니다.** 위 안내는 터미널 명령을 실행할 수 있는 Claude Code 기준입니다. Claude Desktop의 로컬 MCP 연결은 해당 앱 설정에서 별도로 구성해야 합니다.

## 버튼처럼 실행

[최신 릴리스](https://github.com/nalssam/nalssam-pack/releases/latest)의 ZIP을 받아 압축을 풉니다.

- **Mac:** `날쌤팩설치.command` 실행. 최초 실행 시 macOS의 다운로드 파일 확인 절차가 나타날 수 있습니다.
- **Windows:** WSL2 Ubuntu를 먼저 설치한 뒤 `install-windows.cmd` 실행. 도구는 WSL 안에 설치됩니다. 네이티브 Windows 설치기는 아닙니다.
- **Linux:** 폴더에서 `bash install.sh` 실행.

## nalssam 환경으로 맞추기

**날쌤팩 설치만으로 개인 서비스 계정까지 연결되지는 않습니다.** 같은 작업 흐름을 만들려면 아래 세 부분을 준비하세요.

| 구분 | 준비 방법 |
|---|---|
| 로컬 스킬·CLI·MCP | 위 한 줄 설치. 공통 MCP 7개는 Codex에 자동 등록. |
| Claude Code 플러그인 | `--claude`로 스킬·네이티브 플러그인 추가. 공통 MCP는 Claude에 별도 등록. |
| ChatGPT/Codex 서비스 커넥터 | 아래 서비스명을 [앱·플러그인 목록](https://chatgpt.com/plugins)에서 검색하고 본인 계정으로 연결. |

### 서비스 아이콘·명칭·설명

2026-10-16 기준 이 작업에서 설치됨으로 확인한 서비스 플러그인입니다. **설치됨은 계정 로그인·프로젝트 권한·모든 기능의 정상 동작까지 검증됐다는 뜻은 아닙니다.** 우선순위는 작업 목적에 따른 안내이며, 모든 서비스가 필수는 아닙니다.

| 아이콘 | 설치할 서비스 | 설명 | 준비할 계정·권한 |
|---|---|---|---|
| <img src="docs/icons/github.png" width="24" height="24" alt="GitHub"> | **[GitHub](https://github.com)**<br>핵심 · 코드/배포 | 저장소 읽기·수정, PR·이슈, Actions·릴리스. 날쌤팩 업로드에도 사용. | GitHub 로그인 → 사용할 저장소 선택. 새 저장소를 만들면 연결 앱의 허용 목록에도 추가. |
| <img src="docs/icons/google-drive.png" width="24" height="24" alt="Google Drive"> | **[Google Drive](https://drive.google.com)**<br>핵심 · 문서 | Drive 파일 검색과 Docs·Sheets·Slides 문서 작업의 진입점. | Google 로그인 → 사용할 Drive 파일·공유 드라이브 접근 권한 설정. |
| <img src="docs/icons/notion.png" width="24" height="24" alt="Notion"> | **[Notion](https://notion.so)**<br>핵심 · 지식/업무 | 페이지·데이터베이스 검색, 기록·과제·프로젝트 문서 작성 및 갱신. | Notion 로그인 → 워크스페이스와 연결할 페이지·데이터베이스 선택. |
| <img src="docs/icons/canva.png" width="24" height="24" alt="Canva"> | **[Canva](https://canva.com)**<br>확장 · 디자인 | 발표 자료·포스터·수업 자료·SNS 디자인 생성과 편집. | Canva 계정 연결. 브랜드 기능·일괄 생성·AI 크레딧은 요금제에 따라 다름. |
| <img src="docs/icons/higgsfield.png" width="24" height="24" alt="Higgsfield"> | **[Higgsfield](https://higgsfield.ai)**<br>확장 · 영상/이미지 | 이미지·영상, UGC·나레이션·자막·모션 편집, 웹 제작 워크플로. | Higgsfield 계정 연결과 사용 가능한 생성 크레딧 확인. |
| <img src="docs/icons/supabase.png" width="24" height="24" alt="Supabase"> | **[Supabase](https://supabase.com)**<br>확장 · 데이터/백엔드 | Postgres SQL·테이블·인증·스토리지·Edge Functions·로그 관리. | Supabase 계정 및 본인 조직·프로젝트 접근 권한 설정. |
| <img src="docs/icons/vercel.png" width="24" height="24" alt="Vercel"> | **[Vercel](https://vercel.com)**<br>확장 · 웹 배포 | 웹앱·AI 에이전트 배포, 프로젝트·배포 상태·로그 작업. | Vercel 계정 연결 → 대상 팀·프로젝트 선택. |
| <img src="docs/icons/gmail.png" width="24" height="24" alt="Gmail"> | **[Gmail](https://mail.google.com)**<br>확장 · 메일 | 메일 검색·읽기·정리와 요청에 따른 메일 업무. | 본인 Google 메일 계정 연결. 발송은 사용자가 요청한 작업에 한해 수행. |
| <img src="docs/icons/google-calendar.png" width="24" height="24" alt="Google Calendar"> | **[Google Calendar](https://calendar.google.com)**<br>확장 · 일정 | 일정·가용 시간 조회, 회의 준비와 일정 관리. | 본인 Google 계정 연결 → 사용할 캘린더 권한 설정. |
| <img src="docs/icons/google-contacts.png" width="24" height="24" alt="Google Contacts"> | **[Google Contacts](https://contacts.google.com)**<br>확장 · 연락처 | 이름·이메일 등 연락처를 찾아 일정·메일 업무의 대상을 확인. | 본인 Google 연락처 계정과 접근 권한 연결. |
| <img src="docs/icons/windsor.png" width="24" height="24" alt="Windsor.ai"> | **[Windsor.ai](https://windsor.ai)**<br>선택 · 마케팅/지표 | 연결한 광고·분석·비즈니스 데이터 조회와 지원되는 작업 실행. | Windsor.ai 계정 및 실제 분석할 광고·분석 서비스 계정 연결. |
| <img src="docs/icons/openai-developers.png" width="24" height="24" alt="OpenAI Developers"> | **[OpenAI Developers](https://openai.com)**<br>선택 · AI 개발 | OpenAI API·Agents 개발 가이드와 문제 해결 워크플로. | 플러그인 활성화. 실제 API 앱 실행 시 본인 프로젝트/API 인증이 별도로 필요. |
| <img src="docs/icons/sites.png" width="24" height="24" alt="Sites"> | **[Sites](https://chatgpt.com)**<br>기본 제공 여부 확인 · 웹 제작 | 대화로 웹사이트·대시보드·도구를 만들고 게시. | 환경에 기본 제공될 수 있음. 계정·워크스페이스의 제공 여부 확인. |
| <img src="docs/icons/plugin-creator.png" width="24" height="24" alt="Plugin Creator"> | **[Plugin Creator](https://chatgpt.com)**<br>선택 · 플러그인 제작 | 스킬·MCP·앱을 포함하는 재사용 플러그인 제작·수정. | 제공되는 환경에서 활성화. 공유·게시 권한은 계정별로 확인. |
| <img src="docs/icons/data.png" width="24" height="24" alt="Data"> | **[Data](https://chatgpt.com)**<br>선택 · 데이터 분석 | 데이터 품질 검사, KPI·분석 보고서·대시보드 작성 흐름. | 제공되는 환경에서 플러그인 활성화 후 분석할 파일/데이터 연결. |

Google Docs·Sheets·Slides는 **Google Drive**를 통해 사용합니다. GitHub에서 **새 저장소를 만들면 연결 앱의 허용 저장소 목록에도 추가**하세요. 위 서비스의 ChatGPT/Codex용 플러그인은 Claude로 자동 이전되지 않으므로, Claude에서는 각 서비스가 지원하는 커넥터·공식 MCP를 따로 연결합니다.

### 자동 설치되는 로컬 MCP

| 아이콘 | 이름 | 설명 |
|---|---|---|
| 🔍 | REA | 애플리케이션·바이너리·동작 분석 |
| 📄 | HWPX New | 한글 HWPX·공문·보고서 작성 |
| 📊 | PPTX Maker | 한국어 발표 자료 생성·점검 |
| 📝 | Kordoc | 한글·PDF·오피스 문서 파싱·변환 |
| 🔄 | MarkItDown | 파일·문서 → Markdown 변환 |
| 🎬 | Motion Director | 모션그래픽 제작·렌더·검수 |
| 🌐 | Reason Network | 팀 에이전트 목록·메시지·승인 요청(팀 연결 별도) |

[**전체 구성표와 연결 순서 보기 →**](docs/CONNECTORS.md) — Claude Mem·ECC·Caveman·Harness·Superpowers·디자인/영상 스킬의 설치 방식, Claude 공식 MCP 안내, 호스트 전용·비공개 플러그인의 재현 조건까지 정리했습니다.

개인 계정·메일·문서·쿠키·API 키·유료 라이선스는 배포하거나 복사하지 않습니다. 아이콘은 각 서비스 favicon이며 상표권은 각 소유자에게 있습니다.

## 무엇이 들어 있나요?

| 분야 | 구성 |
|---|---|
| 한글·문서 | HWPX New, Kordoc, MarkItDown, PPTX Maker |
| 영상·모션 | Motion Director, Showreel, Cinetic, motion-graphics, claude-video, Sprite Gen |
| UI·디자인 | UI UX Pro Max, Taste, Impeccable |
| 개발·조사 | REA, Playwright, Agent Reach, Google Skills, Karpathy Skills |
| 작업 방식·기억 | ECC, Caveman, Harness, Wshobson Agents, Superpowers, Claude Mem, ClaraMuz |
| 에이전트 간 통신 | Reason Network (팀 디렉터리·메시지 MCP) |
| 참고 모음 | Harness 100, Awesome Claude Code, Superpowers Marketplace |
| 원본 보관·호스트별 기능 | After Effects MCP, Codex Plugin for Claude Code |

사용자가 추천한 **31개 원본 저장소**와 추가 의존 저장소를 `pack.lock.json`에 기록했습니다. 접근 불가인 `lifeofpi-ux/ppt-automation`은 실패를 숨기지 않고 미설치로 표시합니다. 참고 모음은 소스로 보관하며, 목록에 나오는 모든 외부 링크를 무제한으로 설치하지 않습니다.

기본값은 **Codex 전체 구성**입니다. 원본에서 실제 제공하는 스킬을 연결하고 문서·영상 CLI와 MCP, Codex용 Claude Mem 플러그인을 설치합니다. Claude Code 전용 훅을 Codex 설정으로 바꾸어 넣지 않습니다. Claude Code에서 사용하던 네이티브 플러그인 123개도 원한다면 `--claude` 옵션을 쓰세요.

### ClaraMuz · Reason Network

- **ClaraMuz**: `clara-muz-team`·`ai-memory` 스킬을 설치합니다. `--claude`에서는 네이티브 플러그인도 설치합니다. 상대 AI의 CLI·로그인은 별도이며 공유 메모 자동 읽기 규칙은 임의로 추가하지 않습니다.
- **Reason Network**: 전체 구성에서 공식 CLI 0.12.11과 MCP를 설치합니다(총 7개 로컬 MCP). OS·CPU별 SHA-256을 고정하고 팩 전용 데이터 폴더를 사용합니다. `--profile skills`는 소스만 보관합니다. 팀 로그인·초대와 네트워크 접근은 별도이며 자동 팀 가입·메시지 전송·에이전트 훅 등록은 하지 않습니다. 훅이 필요하면 설치 후 `reason-network setup --no-service`를 직접 실행하세요.
- 이 변경은 개발 중인 소스 구성입니다. 기존 `v1.0.1` 릴리스 설치 명령에는 새 릴리스 발행 전까지 포함되지 않습니다.

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
bash -c "$(curl -fsSL https://raw.githubusercontent.com/nalssam/nalssam-pack/v1.0.1/install.sh)" -- --profile skills

# Codex + Claude Code 스킬 및 네이티브 플러그인
bash -c "$(curl -fsSL https://raw.githubusercontent.com/nalssam/nalssam-pack/v1.0.1/install.sh)" -- --claude

# 설치 전에 목록만 보기 (부트스트랩 Python 준비는 진행)
bash -c "$(curl -fsSL https://raw.githubusercontent.com/nalssam/nalssam-pack/v1.0.1/install.sh)" -- plan
```

이미 설치했다면:

```bash
nalssam-pack plan
nalssam-pack install                        # 다시 실행해 누락·실패 단계 재시도
nalssam-pack install --only ZZombie04/motion # 특정 저장소만
nalssam-pack doctor --verify-mcp            # 실제 MCP 연결·도구 목록 검사
nalssam-pack uninstall                      # 날쌤팩이 만든 연결만 해제
```

기본 설치 경로는 `~/.local/share/nalssam-pack`입니다. `NALSSAM_PACK_ROOT=/원하는/경로 bash install.sh` 또는 `--root`로 바꿀 수 있습니다. PATH에 명령이 없다면 `. ~/.local/share/nalssam-pack/env.sh`를 실행하세요.

## 기존 환경을 보존합니다

- 기존 스킬과 이름이 겹치면 원본을 보존하고 별도 이름으로 연결합니다.
- 기존 MCP와 겹치면 `nalssam-` 접두사로 구분합니다. 설치 이후 사용자가 수정한 MCP는 덮어쓰지 않습니다.
- Codex 설정과 셸 시작 파일의 기존 내용은 보존하고 백업합니다.
- 설치 영수증 `state.json`에 날쌤팩이 만든 연결만 기록합니다.
- 제거 시 현재 값이 영수증과 일치하는 연결만 해제합니다. **소스·캐시·가상환경·백업은 남깁니다.**
- 동시에 같은 폴더에서 두 설치기가 상태를 덮어쓰지 않도록 잠급니다.

Claude Code 옵션은 네이티브 플러그인을 설치하므로 해당 플러그인의 훅과 동작 방식도 적용됩니다. 기본 Codex 설치와 구분해서 선택하세요.

## 설치와 실제 사용 준비는 다릅니다

| 항목 | 추가로 필요한 것 |
|---|---|
| Codex | 본인의 ChatGPT 계정 로그인 또는 지원되는 API 인증 |
| Claude Code | 본인의 Claude 계정 또는 지원되는 Anthropic 인증 |
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

날쌤팩 설치 코드는 MIT입니다. 포함 도구는 원본 저장소에서 다운로드하며 각각의 라이선스를 따릅니다. Remotion·Adobe·외부 API의 별도 사용 조건도 그대로 적용됩니다. 원본 코드·이미지·사용자 계정 정보를 한 ZIP에 재배포하지 않습니다.

## 공개 배포하기

ZIP 자체는 공개 주소 없이도 `bash install.sh`로 설치할 수 있습니다. 새 공개 저장소 생성 권한이 있는 GitHub CLI 환경에서 패키지를 배포하려면:

```bash
bash publish.sh
```

이 명령은 `nalssam/nalssam-pack` 공개 저장소, `v1.0.1` 태그와 ZIP 릴리스를 만듭니다. 이미 있는 릴리스를 덮어쓰지 않습니다. 저장소를 만든 뒤에도 현재 GitHub 앱 연결에 새 저장소 접근 권한을 추가해야 업로드할 수 있는 경우가 있습니다.
