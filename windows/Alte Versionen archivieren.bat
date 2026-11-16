@echo off
rem Verschiebt alte Versionen der Commander-DB in den Unterordner "Alte Versionen".
rem Behalten werden: commander_db_v32.py, das ZIP-Paket Manaschmiede-v32, cards.db und die Startdateien.
cd /d "%~dp0"
if not exist "Alte Versionen" mkdir "Alte Versionen"
set n=0
if exist "commander_db.py" (move /y "commander_db.py" "Alte Versionen\" >nul & set /a n+=1)
for /L %%v in (2,1,31) do if exist "commander_db_v%%v.py" (move /y "commander_db_v%%v.py" "Alte Versionen\" >nul & set /a n+=1)
for /L %%v in (1,1,31) do if exist "Commander-DB-v%%v-Server-und-Android.zip" (move /y "Commander-DB-v%%v-Server-und-Android.zip" "Alte Versionen\" >nul & set /a n+=1)
echo.
echo Fertig: %n% Dateien nach "Alte Versionen" verschoben.
echo Aktuell bleibt: commander_db_v32.py (Start mit "Commander-DB starten.bat").
echo.
pause
