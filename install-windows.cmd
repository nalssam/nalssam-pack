@echo off
chcp 65001 >nul
wsl.exe --exec bash -lc "curl -fsSL https://raw.githubusercontent.com/nalssam/nalssam-pack/v1.0.0/install.sh -o /tmp/nalssam-pack-install.sh && bash /tmp/nalssam-pack-install.sh"
if errorlevel 1 (
  echo 설치 실패: WSL2 Ubuntu 설치 여부와 오류 내용을 확인하세요.
  pause
)
