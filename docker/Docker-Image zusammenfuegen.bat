@echo off
rem Fuegt die beiden Teile des Manaschmiede-Docker-Images wieder zu einer Datei zusammen.
cd /d "%~dp0"
if not exist "manaschmiede-32-docker-image.tar.gz.teil0" (echo Teil 0 fehlt. & pause & exit /b 1)
if not exist "manaschmiede-32-docker-image.tar.gz.teil1" (echo Teil 1 fehlt. & pause & exit /b 1)
copy /b "manaschmiede-32-docker-image.tar.gz.teil0"+"manaschmiede-32-docker-image.tar.gz.teil1" "manaschmiede-32-docker-image.tar.gz" >nul
echo Pruefe Pruefsumme ...
certutil -hashfile "manaschmiede-32-docker-image.tar.gz" SHA256 | findstr /i "d265b368c24d4873502bf3d05fd8ba7a76c0921c69c2f29b2790c2927bc7ab3c" >nul && (echo OK: Datei ist vollstaendig.) || (echo ACHTUNG: Pruefsumme stimmt nicht - Teile bitte neu kopieren.)
echo.
echo Fertig: manaschmiede-32-docker-image.tar.gz
pause
