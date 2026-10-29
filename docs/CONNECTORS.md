# nalssam 환경 재현: MCP·커넥터·플러그인 안내

**날쌤팩 설치 + 본인 계정의 서비스 연결**을 함께 해야 nalssam이 쓰는 작업 흐름에 가까운 환경이 됩니다. 아래는 2026-10-16 기준 이 작업에서 확인한 날쌤팩 구성과 설치된 서비스 플러그인의 명칭·용도입니다. 서비스 플러그인의 설치 확인은 각 서비스 계정의 로그인 유효성이나 모든 기능의 동작 검증을 뜻하지 않습니다.

## 1. 먼저 설치할 것

1. [README의 한 줄 설치](../README.md#바로-설치)로 로컬 도구·스킬·Codex MCP를 준비합니다. Claude Code도 쓰면 `--claude`를 추가합니다.
2. ChatGPT/Codex에서 제공되는 **앱·플러그인 목록**([플러그인 디렉터리](https://chatgpt.com/plugins))에서 아래 서비스의 이름을 검색해 설치·활성화하고 **본인 계정**으로 연결합니다. UI 명칭과 제공 목록은 호스트·플랜·워크스페이스에 따라 다릅니다.
3. 문서·개발 작업은 GitHub·Google Drive·Notion부터, 디자인·영상 작업은 Canva·Higgsfield를 추가하는 순서가 편합니다. 모든 서비스가 모든 작업의 필수 조건은 아닙니다.
4. GitHub는 연결 앱의 Repository access에서 대상 저장소를 선택합니다. **새 저장소를 생성해도 선택 목록에는 자동 추가되지 않을 수 있습니다.**
5. Codex MCP는 `nalssam-pack doctor --verify-mcp`, Claude Code는 [별도 MCP 연결 안내](../README.md#claude-code에-문서영상-mcp도-연결하기)와 `claude mcp list`로 확인합니다.

개인 계정·쿠키·메일·문서·API 키·프로젝트 권한은 복제하거나 배포하지 않습니다. 같은 플러그인을 설치해도 각자의 데이터·요금제·권한에 따라 사용 범위는 달라집니다.

## 2. 별도로 설치·연결하는 서비스

아래 15개는 이 작업에서 **설치됨**으로 조회한 서비스 플러그인입니다. 날쌤팩 셸 설치기가 이 OAuth 연결을 대신 만들지는 않습니다.

| 아이콘 | 서비스 명칭 | 용도별 우선순위 | 설명 | 설치·연결할 것 |
|---|---|---|---|---|
| <img src="icons/github.png" width="24" height="24" alt="GitHub"> | [GitHub](https://github.com) | 핵심 · 코드/배포 | 저장소 읽기·수정, PR·이슈, Actions·릴리스. 날쌤팩 업로드에도 사용. | 앱·플러그인에서 **GitHub** 검색. GitHub 로그인 → 사용할 저장소 선택. 새 저장소를 만들면 연결 앱의 허용 목록에도 추가. |
| <img src="icons/google-drive.png" width="24" height="24" alt="Google Drive"> | [Google Drive](https://drive.google.com) | 핵심 · 문서 | Drive 파일 검색과 Docs·Sheets·Slides 문서 작업의 진입점. | 앱·플러그인에서 **Google Drive** 검색. Google 로그인 → 사용할 Drive 파일·공유 드라이브 접근 권한 설정. |
| <img src="icons/notion.png" width="24" height="24" alt="Notion"> | [Notion](https://notion.so) | 핵심 · 지식/업무 | 페이지·데이터베이스 검색, 기록·과제·프로젝트 문서 작성 및 갱신. | 앱·플러그인에서 **Notion** 검색. Notion 로그인 → 워크스페이스와 연결할 페이지·데이터베이스 선택. |
| <img src="icons/canva.png" width="24" height="24" alt="Canva"> | [Canva](https://canva.com) | 확장 · 디자인 | 발표 자료·포스터·수업 자료·SNS 디자인 생성과 편집. | 앱·플러그인에서 **Canva** 검색. Canva 계정 연결. 브랜드 기능·일괄 생성·AI 크레딧은 요금제에 따라 다름. |
| <img src="icons/higgsfield.png" width="24" height="24" alt="Higgsfield"> | [Higgsfield](https://higgsfield.ai) | 확장 · 영상/이미지 | 이미지·영상, UGC·나레이션·자막·모션 편집, 웹 제작 워크플로. | 앱·플러그인에서 **Higgsfield** 검색. Higgsfield 계정 연결과 사용 가능한 생성 크레딧 확인. |
| <img src="icons/supabase.png" width="24" height="24" alt="Supabase"> | [Supabase](https://supabase.com) | 확장 · 데이터/백엔드 | Postgres SQL·테이블·인증·스토리지·Edge Functions·로그 관리. | 앱·플러그인에서 **Supabase** 검색. Supabase 계정 및 본인 조직·프로젝트 접근 권한 설정. |
| <img src="icons/vercel.png" width="24" height="24" alt="Vercel"> | [Vercel](https://vercel.com) | 확장 · 웹 배포 | 웹앱·AI 에이전트 배포, 프로젝트·배포 상태·로그 작업. | 앱·플러그인에서 **Vercel** 검색. Vercel 계정 연결 → 대상 팀·프로젝트 선택. |
| <img src="icons/gmail.png" width="24" height="24" alt="Gmail"> | [Gmail](https://mail.google.com) | 확장 · 메일 | 메일 검색·읽기·정리와 요청에 따른 메일 업무. | 앱·플러그인에서 **Gmail** 검색. 본인 Google 메일 계정 연결. 발송은 사용자가 요청한 작업에 한해 수행. |
| <img src="icons/google-calendar.png" width="24" height="24" alt="Google Calendar"> | [Google Calendar](https://calendar.google.com) | 확장 · 일정 | 일정·가용 시간 조회, 회의 준비와 일정 관리. | 앱·플러그인에서 **Google Calendar** 검색. 본인 Google 계정 연결 → 사용할 캘린더 권한 설정. |
| <img src="icons/google-contacts.png" width="24" height="24" alt="Google Contacts"> | [Google Contacts](https://contacts.google.com) | 확장 · 연락처 | 이름·이메일 등 연락처를 찾아 일정·메일 업무의 대상을 확인. | 앱·플러그인에서 **Google Contacts** 검색. 본인 Google 연락처 계정과 접근 권한 연결. |
| <img src="icons/windsor.png" width="24" height="24" alt="Windsor.ai"> | [Windsor.ai](https://windsor.ai) | 선택 · 마케팅/지표 | 연결한 광고·분석·비즈니스 데이터 조회와 지원되는 작업 실행. | 앱·플러그인에서 **Windsor.ai** 검색. Windsor.ai 계정 및 실제 분석할 광고·분석 서비스 계정 연결. |
| <img src="icons/openai-developers.png" width="24" height="24" alt="OpenAI Developers"> | [OpenAI Developers](https://openai.com) | 선택 · AI 개발 | OpenAI API·Agents 개발 가이드와 문제 해결 워크플로. | 앱·플러그인에서 **OpenAI Developers** 검색. 플러그인 활성화. 실제 API 앱 실행 시 본인 프로젝트/API 인증이 별도로 필요. |
| <img src="icons/sites.png" width="24" height="24" alt="Sites"> | [Sites](https://chatgpt.com) | 기본 제공 여부 확인 · 웹 제작 | 대화로 웹사이트·대시보드·도구를 만들고 게시. | 앱·플러그인에서 **Sites** 검색. 환경에 기본 제공될 수 있음. 계정·워크스페이스의 제공 여부 확인. |
| <img src="icons/plugin-creator.png" width="24" height="24" alt="Plugin Creator"> | [Plugin Creator](https://chatgpt.com) | 선택 · 플러그인 제작 | 스킬·MCP·앱을 포함하는 재사용 플러그인 제작·수정. | 앱·플러그인에서 **Plugin Creator** 검색. 제공되는 환경에서 활성화. 공유·게시 권한은 계정별로 확인. |
| <img src="icons/data.png" width="24" height="24" alt="Data"> | [Data](https://chatgpt.com) | 선택 · 데이터 분석 | 데이터 품질 검사, KPI·분석 보고서·대시보드 작성 흐름. | 앱·플러그인에서 **Data** 검색. 제공되는 환경에서 플러그인 활성화 후 분석할 파일/데이터 연결. |

Google Docs·Sheets·Slides는 이 환경에서 **Google Drive**를 진입점으로 사용합니다. 별도 서비스 플러그인 3개를 추가 설치해야 한다는 뜻은 아닙니다.

**Claude에서는:** 위 ChatGPT/Codex용 플러그인을 설치했다고 Claude에도 연결되는 것은 아닙니다. Claude의 커넥터 목록 또는 서비스가 공식 제공하는 MCP를 통해 따로 인증하세요. 서비스별 Claude 지원 여부를 확인하고, 지원하지 않는 플러그인의 주소를 추측해 등록하지 마세요. [GitHub MCP](https://github.com/github/github-mcp-server), [Notion MCP](https://developers.notion.com/docs/mcp), [Supabase MCP](https://supabase.com/docs/guides/getting-started/mcp), [Vercel MCP](https://vercel.com/docs/mcp)는 각 공식 안내를 참고할 수 있습니다.

## 3. 날쌤팩이 준비하는 로컬 MCP

기본 전체 설치의 **Codex 자동 등록 대상 7개**입니다. 외부 서비스 OAuth 커넥터와 구분됩니다. 아이콘은 문서/영상 등 기능을 나타내는 기호입니다.

| 아이콘 | MCP / 서버 이름 | 설명 | 설치·추가 조건 |
|---|---|---|---|
| 🔍 | [REA](https://github.com/nalssam/rea) · `rea` | JS/Electron·바이너리·실행 동작 등의 분석 | 자동 설치·등록. 네이티브 분석은 대상에 맞는 별도 분석 엔진 필요. |
| 📄 | [HWPX New](https://github.com/ZZombie04/hwpx_new) · `hwpx-new` | HWPX 읽기·작성·공문·보고서·서식 작업 | 자동 설치·등록. Hancom 전용 변환은 지원되는 한글 환경 필요. |
| 📊 | [PPTX Maker](https://github.com/ZZombie04/pptx_maker) · `pptx-maker` | 한국어 발표 자료 생성·설계 점검 | 자동 설치·등록. PowerPoint 전용 출력은 해당 프로그램 필요. |
| 📝 | [Kordoc](https://github.com/chrisryugj/kordoc) · `kordoc` | HWP·HWPX·PDF·오피스 문서 파싱·변환·생성 | 자동 설치·등록. OCR은 첫 사용 시 모델 다운로드가 필요할 수 있음. |
| 🔄 | [MarkItDown](https://github.com/microsoft/markitdown) · `markitdown` | 문서·파일 내용을 Markdown으로 변환 | 자동 설치·등록. 형식별 의존성은 고정 목록으로 준비. |
| 🎬 | [Motion Director](https://github.com/ZZombie04/motion) · `motion` | 모션그래픽 구성·렌더·검수 | 자동 설치·등록. Chromium·ffmpeg 실행 환경 필요. |

Claude Code는 [README의 7개 등록 명령](../README.md#claude-code에-문서영상-mcp도-연결하기)을 사용합니다. 이름 충돌 시 기존 설정을 보존하고 별도 이름을 사용하세요.

Reason Network도 전체 구성의 MCP로 등록됩니다. 팀 로그인·초대 링크와 릴레이 접근은 별도이며 자동으로 가입하거나 메시지를 보내지 않습니다.

## 4. 날쌤팩의 스킬·플러그인 묶음

아래 GitHub 프로젝트들은 서비스 OAuth 커넥터가 아닙니다. 각 원본이 제공하는 스킬을 설치하며, 모든 프로젝트가 MCP 서버를 제공하는 것은 아닙니다. 개별 수동 설치보다 날쌤팩의 버전 고정 설치를 권장합니다.

| 아이콘 | 명칭 | 설명 | 설치 방식 / 추가 조건 |
|---|---|---|---|
| 🤝 | [ClaraMuz](https://github.com/Jay-Hyun/ClaraMuz) | Claude·GPT 협업과 공유 메모·인수인계 | 두 스킬 기본 설치, 네이티브 플러그인은 `--claude`. 상대 CLI·로그인 별도. |
| 🧠 | [Claude Mem](https://github.com/thedotmack/claude-mem) | 작업 기억·관찰과 문맥 재사용 | 기본 Codex 네이티브 플러그인. 관찰 모델·계정 설정 및 수집 동작은 별도 확인. |
| 🛠️ | [ECC](https://github.com/affaan-m/ECC) | 개발·검토·테스트 등 작업 가이드 | Codex 스킬. Claude 네이티브 플러그인은 --claude. |
| 🪨 | [Caveman](https://github.com/JuliusBrussee/caveman) | 간결한 응답과 작업 방식 | Codex 스킬. --claude 시 원본 플러그인 훅도 적용. |
| 🧭 | [Harness / Evolve](https://github.com/revfactory/harness) | 프로젝트 작업 구조와 개선 흐름 구성 | 스킬. Claude 네이티브 구성은 --claude. |
| 🧩 | [Wshobson Agents](https://github.com/wshobson/agents) | 분야별 개발 에이전트·워크플로·스킬 | Codex는 스킬. 원본 Claude 플러그인 묶음은 --claude. |
| ⚡ | [Superpowers](https://github.com/obra/superpowers) | 기획·디버깅·테스트·구현 작업 흐름 | 고정 커밋의 로컬 스킬. Claude 플러그인은 --claude. |
| 🎨 | [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | UI·UX 설계·스타일 검색 | 스킬 및 원본 검색 스크립트. |
| 🖌️ | [Taste](https://github.com/Leonxlnx/taste-skill) | 브랜드·프런트엔드 시각 설계 | 스킬. 일부 작업에는 브라우저 필요. |
| ✨ | [Impeccable](https://github.com/pbakaus/impeccable) | UI 검토·다듬기·디자인 품질 관리 | 스킬. 원본 실행기가 최초 사용 시 엔진을 준비할 수 있음. |
| 📽️ | [Showreel](https://github.com/revfactory/showreel) | 한국어 모션그래픽 제작 | 스킬·렌더러 준비. 나레이션 등은 ElevenLabs 계정·키 별도. |
| 🎞️ | [Cinetic](https://github.com/Leonxlnx/cinetic) | 코드 기반 런치 영상·모션 연출 | 스킬·Python/Remotion 실행 환경. Remotion 라이선스 조건 확인. |
| 🎥 | [Motion Graphics](https://github.com/Barty-Bart/motion-graphics) | 모션 B-roll·설명 영상 등 제작 기법 | 스킬. 작업별 외부 생성·미디어 도구 조건은 원본 안내 확인. |
| 👁️ | [Watch / claude-video](https://github.com/bradautomates/claude-video) | 영상 프레임·자막을 근거로 분석 | 스킬. 로컬 ffmpeg·다운로더 또는 선택한 음성/API 백엔드 필요. |
| 👾 | [Sprite Gen](https://github.com/aldegad/sprite-gen) | 게임 캐릭터 스프라이트·아틀라스 작업 | 스킬·CLI. 이미지·영상 생성 공급자 인증은 별도. |
| 🌐 | [Playwright](https://github.com/microsoft/playwright) | 브라우저 자동화·페이지 점검 | 스킬·CLI. 별도 ChatGPT 브라우저 커넥터를 설치한다는 뜻은 아님. |
| 📡 | [Agent Reach](https://github.com/Panniantong/Agent-Reach) | 웹·영상·소셜 조사 도구 연결 가이드 | 스킬·CLI. 각 채널 도구·계정 설정은 별도. |
| ☁️ | [Google Skills](https://github.com/google/skills) | Google 제품·클라우드 개발 작업 가이드 | 로컬 스킬. Google Drive 커넥터나 Cloud OAuth를 대신하지 않음. |
| 📐 | [Karpathy Skills](https://github.com/multica-ai/andrej-karpathy-skills) | 코딩 시 가정·범위·간결성을 점검하는 가이드 | 스킬. |
| 🤖 | [Codex Plugin for Claude Code](https://github.com/openai/codex-plugin-cc) | Claude Code에서 Codex에 검토·작업 위임 | Codex 관련 스킬. Claude 네이티브 플러그인은 --claude. |
| 🅰️ | [After Effects MCP](https://github.com/nalssam/aftereffects-mcp) | Adobe After Effects 프로젝트 제어 | 소스·스킬 준비. Windows/macOS의 After Effects와 패널이 필요하며 기본 자동 등록 대상에서는 제외. |

`--claude`가 설치하는 **123개 네이티브 플러그인의 정확한 이름·원본·활성 상태**는 [`pack.lock.json`의 `claude_plugins`](../pack.lock.json)에 있습니다. 위 표는 원본 묶음별 안내이며, 클라우드 서비스 플러그인 123개를 모두 OAuth로 연결한다는 뜻이 아닙니다.

Harness 100·Awesome Claude Code·Superpowers Marketplace는 참고·템플릿 모음으로 보관합니다. `lifeofpi-ux/ppt-automation`은 접근 불가로 미설치 상태입니다.

## 5. 환경별 제공 기능과 사용자 제작 플러그인

이 작업 환경에는 Pages·Sites·Cloud Environment·OpenAI Developers·Data·Plugin Creator·Work Pets와 보안/게임 제작/연수 자료 관련 스킬도 노출돼 있습니다. 일부는 호스트가 제공하는 기능이고 일부는 사용자 제작 패키지입니다. **공개 날쌤팩이 이 기능들의 사용 권한이나 비공개 플러그인 원본까지 배포하는 것은 아닙니다.**

| 아이콘 | 명칭/분야 | 설명 | 재현할 때 확인할 것 |
|---|---|---|---|
| 📚 | Pages / Sites | 문서·공간 관리 / 웹사이트 제작·게시 | 사용하는 ChatGPT/Codex 환경의 제공 여부 확인. Sites는 위 서비스 표 참고. |
| ☁️ | Cloud Environment | 관리형 실행 환경·네트워크·런타임 | 사용할 호스트에 클라우드 작업 환경이 있어야 함. 로컬 날쌤팩만으로 생성되지는 않음. |
| 🐾 | Work Pets | 작업 화면의 반려 캐릭터 관리·제작 | 해당 호스트 기능·플러그인 제공 여부 확인. |
| 🛡️ | 보안·분석·게임 제작 스킬 | 코드 보안 검토, 데이터 분석, 게임 에셋·3D 작업 등 | 원본 플러그인의 공개·설치 가능 여부와 별도 도구/계정 필요 여부 확인. |
| 🧑‍🏫 | nalssam-training-kit / AI 서논술 글쓰기 평가 | 교사 연수 자료 제작 / 글쓰기 평가 작업 지침 | 사용자 제작 플러그인은 제작자의 공유 링크·원본·권한 필요. 날쌤팩에 자동 포함되지 않음. |

## 6. 재현 완료 체크리스트

- [ ] 날쌤팩 설치 보고서에서 실패 단계와 추가 설정을 확인했다.
- [ ] 본인 Codex 또는 Claude Code 계정으로 로그인했다.
- [ ] GitHub·Google Drive·Notion 등 필요한 서비스 플러그인을 설치하고 본인 데이터 접근 범위를 정했다.
- [ ] 디자인·영상 작업에 쓰는 Canva·Higgsfield·ElevenLabs 등의 계정과 요금제/크레딧을 확인했다.
- [ ] 서비스 플러그인은 각 호스트에서 연결하고, 로컬 MCP는 해당 호스트 설정에서 확인했다.
- [ ] MCP 실제 연결 검사와 간단한 문서·브라우저·영상 작업을 확인했다.
- [ ] 비공개 플러그인과 호스트 전용 기능은 별도 공유·사용 권한을 확보했다.

## 아이콘 출처

서비스 아이콘은 공식 배포 아이콘 또는 각 서비스 도메인의 favicon을 받아 이 저장소에 보관한 것입니다. 파일별 원본 URL은 [아이콘 출처 목록](icons/SOURCES.json)에 있습니다. 프로젝트 표의 기호는 기능 구분용입니다. 서비스명·로고의 권리는 각 소유자에게 있으며, 날쌤팩과 해당 서비스의 제휴·보증을 의미하지 않습니다.
