# Windows native installer. Existing Python is preferred; missing Python is installed through winget.
param(
    [string]$Root,
    [string]$Workspace,
    [ValidateSet('codex','claude','both','manual')][string]$Agent = 'codex',
    [string]$Answers,
    [switch]$NoPythonInstall
)
$ErrorActionPreference = 'Stop'
$Python = $null
$PythonArgs = @()
foreach ($Candidate in @('py','python','python3')) {
    $Command = Get-Command $Candidate -ErrorAction SilentlyContinue
    if (-not $Command) { continue }
    $Prefix = @()
    if ($Candidate -eq 'py') { $Prefix = @('-3') }
    & $Command.Source @Prefix -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)' 2>$null
    if ($LASTEXITCODE -eq 0) { $Python = $Command.Source; $PythonArgs = $Prefix; break }
}
if (-not $Python -and -not $NoPythonInstall) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw 'Python 3.11 이상을 python.org에서 설치한 뒤 다시 실행하세요. winget을 찾지 못했습니다.'
    }
    Write-Host '공식 Windows 패키지 관리자로 Python 3.12를 사용자 범위에 설치합니다.'
    winget install --id Python.Python.3.12 --exact --scope user --silent --accept-package-agreements --accept-source-agreements --disable-interactivity
    if ($LASTEXITCODE -ne 0) { throw 'Python 설치가 완료되지 않았습니다. 위 오류를 확인하세요.' }
    $Installed = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
    if (Test-Path $Installed) { $Python = $Installed }
}
if (-not $Python) { throw 'Python 3.11 이상을 설치한 후 이 설치기를 다시 실행하세요.' }
$Temporary = Join-Path ([IO.Path]::GetTempPath()) ([Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $Temporary | Out-Null
try {
    $Bootstrap = Join-Path $PSScriptRoot 'bootstrap.py'
    $Arguments = @()
    if ($PSScriptRoot -and (Test-Path $Bootstrap) -and (Test-Path (Join-Path $PSScriptRoot 'bundle.json'))) {
        $Arguments += @('--source', $PSScriptRoot)
    } else {
        $Bootstrap = Join-Path $Temporary 'bootstrap.py'
        Invoke-WebRequest -UseBasicParsing -Uri 'https://raw.githubusercontent.com/nalssam/nalssam-pack/instructor-v0.1.1/instructor/bootstrap.py' -OutFile $Bootstrap
    }
    if ($Root) { $Arguments += @('--root', $Root) }
    if ($Workspace) { $Arguments += @('--workspace', $Workspace) }
    if ($Answers) { $Arguments += @('--answers', $Answers) }
    $Arguments += @('--agent', $Agent)
    & $Python @PythonArgs $Bootstrap @Arguments
    if ($LASTEXITCODE -ne 0) { throw "공군 교관 에디션 설치 실패: 종료 코드 $LASTEXITCODE" }
} finally {
    Remove-Item -LiteralPath $Temporary -Recurse -Force
}
