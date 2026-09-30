@echo off
setlocal
set "PROJECT=%~dp0homelab-rack-Bambu-Studio-6-plates.3mf"
set "BAMBU=C:\Program Files\Bambu Studio\bambu-studio.exe"

if not exist "%PROJECT%" (
  echo Project not found: "%PROJECT%"
  pause
  exit /b 1
)

if exist "%BAMBU%" (
  start "" "%BAMBU%" "%PROJECT%"
) else (
  start "" "%PROJECT%"
)
