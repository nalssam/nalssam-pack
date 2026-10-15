@echo off
chcp 65001 >nul
setlocal
set "NALSSAM_PACK_WINDOWS_DIR=%~dp0"
set "WSLENV=NALSSAM_PACK_WINDOWS_DIR/p:%WSLENV%"
wsl.exe --exec bash -lc "cd -- \"$NALSSAM_PACK_WINDOWS_DIR\" && exec bash ./install.sh"
if errorlevel 1 (
  echo 설치 실패: WSL2 Ubuntu 설치 여부와 오류 내용을 확인하세요.
  pause
)
endlocal
