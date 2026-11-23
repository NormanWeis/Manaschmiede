@echo off
cd /d "%~dp0"
title Commander-Datenbank - dieses Fenster offen lassen
echo Beende eventuell noch laufende aeltere Versionen der Datenbank ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -ne $PID -and $_.CommandLine -match 'commander_db(_v[0-9]+)?[.]py.+serve' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
timeout /t 1 /nobreak >nul
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 commander_db_v53.py serve 
) else (
  python commander_db_v53.py serve 
)
echo.
echo Das Programm wurde beendet. Zum Schliessen eine beliebige Taste druecken.
pause >nul
