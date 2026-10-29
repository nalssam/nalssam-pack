# 날쌤 교관 워크벤치

**한 번 설치하고, AI가 묻는 질문에 답하면서 나만의 수업 작업실을 만드세요.**

공군 교육사령부 교관 대상 연수를 위해 준비한 **날쌤의 독립 제작 교육 도구**입니다. 기관의 공식 시스템이나 승인 제품을 뜻하지 않습니다. 공개·가상 사례로 교수설계와 교육자료 제작을 연습하도록 구성했습니다.

## 1. 설치

**Windows 권장: [연수용 ZIP 내려받기](https://raw.githubusercontent.com/nalssam/nalssam-pack/instructor-channel/nalssam-instructor-v0.1.0.zip)** → 압축 풀기 → **`교관워크벤치설치.cmd` 더블클릭**.

기존 Python 3.11 이상을 사용합니다. Windows에 Python이 없으면 공식 `winget`으로 사용자 범위의 Python 3.12를 설치합니다. `winget`이 없는 PC는 [python.org](https://www.python.org/downloads/)에서 먼저 설치하세요. Windows 설치기의 실제 Windows 실행은 아직 검증 전입니다.

Windows PowerShell에서 바로 설치하려면:

```powershell
$f = Join-Path $env:TEMP 'nalssam-instructor-install.ps1'; Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/nalssam/nalssam-pack/instructor-v0.1.0/instructor/install.ps1' -OutFile $f; powershell.exe -NoProfile -ExecutionPolicy Bypass -File $f
```

macOS·Linux·WSL은 **Python 3.11 이상**이 있는 터미널에서:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/nalssam/nalssam-pack/instructor-v0.1.0/instructor/install.sh)"
```

이 설치기는 **업무 설정·스킬·양식·관리 명령**을 준비합니다. 기본 설치에는 별도 Python 패키지가 필요하지 않습니다. Codex 또는 Claude Code 앱 설치·로그인은 각자 진행하세요. HWPX·PPTX 파일을 실제 생성하는 날쌤팩 도구와 AI 서비스 요금·계정은 별도입니다.

설치 폴더와 작업실을 직접 지정할 수도 있습니다:

```bash
bash instructor/install.sh --root "$HOME/.local/share/nalssam-instructor" --workspace "$HOME/Documents/NalssamInstructor" --agent both
```

Windows ZIP에서는 `install.ps1 -Root 'D:\교관도구' -Workspace 'D:\수업작업실' -Agent both`처럼 지정합니다.

## 2. 시작: 역프롬프트로 나에게 맞추기

Codex 또는 Claude Code에서 설치 결과에 표시된 **작업실 폴더**를 열고 다음 문장을 붙여 넣으세요:

> 교관 워크벤치를 시작해줘. `.harness/profile.json`과 `.harness/AGENTS.generated.md`를 읽고, 내 업무에 필요한 조건을 하나씩 역프롬프트로 물어봐. 답변을 요약해 확인받고 설정에 반영한 뒤, 공개·가상 주제로 첫 강의안 하나를 함께 만들어줘.

AI는 역할, 주제, 학습 대상, 차시 시간, 우선 산출물, 문체, 사용하는 AI 도구, 작업실 위치를 확인합니다. 이미 답한 것은 반복해서 묻지 않습니다. 답변은 로컬 설정에 저장되고, 다음 작업부터 그대로 적용됩니다. 일반 채팅만 사용하는 경우에는 생성된 시작 안내와 스킬 내용을 함께 붙여 넣을 수 있으며, 로컬 파일 저장은 직접 해야 합니다.

## 3. 들어 있는 것

| 구성 | 하는 일 |
|---|---|
| `instructor-start` | 질문으로 요구를 구체화하고 업무 환경 설정 |
| `lesson-design` | 목표→활동→평가가 연결되는 수업 설계 |
| `assessment` | 평가문항·루브릭·피드백 검토 |
| `materials` | 강의 슬라이드·학습자 실습지·교관 진행 메모 구성 |
| 양식 5종 | 수업 설계, 평가표, 교관 진행 메모, 학습자 실습지, 수업 개선 기록 |
| 관리 명령 | 설치, 설정, 상태 점검, 공통 양식 동기화, 설정 내보내기·가져오기, 제거 |

선택한 앱에 맞춰 **해당 작업실 내부**의 `.agents/skills`와 `.claude/skills`에 스킬을 둡니다. 기존 `AGENTS.md`·`CLAUDE.md`는 보존하고 `.harness/AGENTS.generated.md`를 별도로 제공합니다. 이 경우 시작 문장을 통해 생성된 지침을 읽게 하세요. 전역 설정을 덮어쓰지 않습니다.

## 4. 동기화와 설정 이전

**동기화는 공통 스킬·양식을 내려받는 기능입니다. 개인 자료를 GitHub에 올리는 기능은 없습니다.**

설치 폴더의 `bin/instructor`(Windows는 `bin/instructor.cmd`)를 `도구`라고 부르면:

```text
도구 doctor --json
도구 configure
도구 sync
도구 export --output 내설정.json
도구 import --answers 내설정.json
도구 uninstall
```

`도구`는 실제 설치 경로로 바꾸세요. Windows 예: `& "$env:LOCALAPPDATA\NalssamInstructor\bin\instructor.cmd" doctor --json`. macOS 예: `~/.local/share/nalssam-instructor/bin/instructor doctor --json`.

연수 배포 채널은 **정확한 Git 커밋**을 지정합니다. 내려받은 모든 파일의 SHA-256을 검사합니다. 수정된 공통 파일이 있으면 동기화를 중단하고 보존하므로, 원래 양식을 복사해 다른 이름으로 작성하세요. 인터넷이 없는 경우에는 검증된 ZIP의 `instructor` 번들 폴더를 지정해 `도구 sync --source 폴더`로 갱신할 수 있습니다.

업무 설정만 옮기려면 `export` 후 다른 PC의 `import`를 사용하세요. 작업실 경로·작성 자료·계정·API 키는 내보내지 않습니다. 설정에는 담당 과목 등 직접 입력한 정보가 들어가므로 공유 전에 열어보세요. `uninstall`은 설치 기록과 일치하는 파일만 제거하며 작성 자료와 개인 프로필은 보존합니다.

## 5. 연수에서 바로 해보기 (20분)

1. **설치·점검 3분**: 설치하고 `START-HERE.md`를 확인합니다.
2. **나만의 설정 5분**: 시작 문장을 입력하고 AI의 질문에 답합니다.
3. **첫 산출물 8분**: 예시 주제 “성인 학습자에게 명확하게 설명하는 방법”으로 50분 수업 설계와 평가표를 만듭니다.
4. **검토 2분**: 수업 목표와 평가 항목이 연결되는지, 제공하지 않은 사실이 만들어졌는지 확인합니다.
5. **동기화 2분**: 작성본을 별도 파일에 저장한 뒤 `sync`, `doctor`를 실행합니다.

교관·학습자의 개인정보나 비공개 기관 자료 대신 공개 자료·가상 예시를 사용하세요. 외부 AI에 제공할 수 있는 범위는 소속 기관 지침을 따릅니다. 설치기가 자료를 자동 전송하거나 다른 에이전트에 메시지를 보내지는 않습니다.

## 유지보수·개발

이 에디션은 기존 날쌤팩의 전체 49개 원본/런타임 설치와 분리된 경량 작업실입니다. [전체 날쌤팩 구성](../README.md)이 필요하면 별도로 설치할 수 있습니다. ClaraMuz·Reason Network는 선택 도구이며 이 기본 설치에서 팀 가입·메시지 동기화를 실행하지 않습니다.

```bash
python3 instructor/build_bundle.py
python3 -m unittest discover -s instructor/tests -v
python3 instructor/build_bundle.py --check --zip /tmp/nalssam-instructor-v0.1.0.zip
```

배포 코드: `instructor-v0.1.0` 태그. 업데이트 채널·연수용 ZIP: `instructor-channel` 브랜치. 채널 변경은 새 코드 커밋과 테스트를 확인한 뒤 진행합니다. 전체 팩의 기존 `v1.0.1` 릴리스는 교체하지 않습니다.

Linux 설치·설정·동기화·보존·제거와 MCP 등 기존 팩의 회귀 검사를 실행합니다. **Windows/macOS 실제 실행과 AI 계정 로그인·문서 출력은 별도 검증 대상**입니다. 자동으로 군용 운영망에 연결하거나 기관의 승인 절차를 대신하지 않습니다.
