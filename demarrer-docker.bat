@echo off
REM ============================================================================
REM  HelpMeDraft - demarrage de la pile Docker + journal de diagnostic
REM
REM  Double-cliquer ce fichier. Il ecrit TOUT dans docker-demarrage.log, que
REM  Claude peut relire directement : pas de copier-coller depuis la console.
REM
REM  « down -v » supprime le volume de la base. C'est VOULU : les scripts de
REM  /docker-entrypoint-initdb.d ne sont rejoues qu'au premier demarrage d'un
REM  volume neuf. Sans cela, une base initialisee lors d'un essai precedent
REM  garderait son etat, droits SGBD non appliques compris.
REM ============================================================================

cd /d "%~dp0"
set LOG=docker-demarrage.log

echo ============================================================ > "%LOG%"
echo  HelpMeDraft - demarrage du %DATE% a %TIME%                  >> "%LOG%"
echo ============================================================ >> "%LOG%"
echo. >> "%LOG%"

echo [1/5] Verification de Docker...
echo ---------- [1/5] docker version ---------- >> "%LOG%"
docker version >> "%LOG%" 2>&1
if errorlevel 1 (
    echo. >> "%LOG%"
    echo ERREUR : Docker ne repond pas. Docker Desktop est-il lance ? >> "%LOG%"
    echo ERREUR : Docker ne repond pas. Lance Docker Desktop, puis relance ce script.
    echo.
    pause
    exit /b 1
)

echo [2/5] Arret de la pile et suppression du volume de base...
echo. >> "%LOG%"
echo ---------- [2/5] docker compose down -v ---------- >> "%LOG%"
docker compose down -v >> "%LOG%" 2>&1

echo [3/5] Construction des images et demarrage (plusieurs minutes)...
echo. >> "%LOG%"
echo ---------- [3/5] docker compose up --build -d ---------- >> "%LOG%"
docker compose up --build -d >> "%LOG%" 2>&1
set RESULTAT=%ERRORLEVEL%

echo [4/5] Attente de l'initialisation de la base (45 s)...
REM MySQL cree le schema et applique les droits a ce moment : les journaux
REM utiles n'existent pas encore si on les lit tout de suite.
timeout /t 45 /nobreak >nul

echo. >> "%LOG%"
echo ---------- [4/5] etat des conteneurs ---------- >> "%LOG%"
docker compose ps >> "%LOG%" 2>&1

echo [5/5] Collecte des journaux...
echo. >> "%LOG%"
echo ---------- [5/5] journaux complets ---------- >> "%LOG%"
docker compose logs --no-color --timestamps >> "%LOG%" 2>&1

echo. >> "%LOG%"
echo ---------- code de retour du up : %RESULTAT% ---------- >> "%LOG%"

echo.
echo ============================================================
if "%RESULTAT%"=="0" (
    echo  Pile demarree. Interface : http://localhost:8080
    echo  API                     : http://localhost:5000
) else (
    echo  ECHEC au demarrage. Tout est dans docker-demarrage.log
)
echo  Journal : docker-demarrage.log
echo ============================================================
echo.
pause
