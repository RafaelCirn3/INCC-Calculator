@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

title INCC Calculator - Docker Desktop
color 0A

set "IMAGE_NAME=incc-calculator"
set "COMPOSE_FILE=docker-compose.yml"

call :validar_arquivos || goto :fatal
call :validar_docker || goto :fatal

echo.
echo [1/2] Iniciando com Docker Compose...
docker compose -f %COMPOSE_FILE% up -d --build
if errorlevel 1 goto :fatal_run

timeout /t 3 >nul
start "" http://localhost:8000

echo.
echo Projeto em execucao no Docker Desktop.
echo Acesse em: http://localhost:8000
echo O servico foi criado via Docker Compose.
echo.
pause
exit /b 0

:validar_arquivos
if not exist "Dockerfile" (
    echo [ERRO] Arquivo Dockerfile nao encontrado em %CD%.
    exit /b 1
)
if not exist "manage.py" (
    echo [ERRO] Arquivo manage.py nao encontrado em %CD%.
    exit /b 1
)
if not exist "requirements.txt" (
    echo [ERRO] Arquivo requirements.txt nao encontrado em %CD%.
    exit /b 1
)
if not exist "%COMPOSE_FILE%" (
    echo [ERRO] Arquivo %COMPOSE_FILE% nao encontrado em %CD%.
    exit /b 1
)
exit /b 0

:validar_docker
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Docker nao esta pronto.
    echo Abra o Docker Desktop e tente novamente.
    exit /b 1
)
exit /b 0

:fatal_run
echo.
echo [ERRO] O projeto nao foi iniciado pelo Docker Compose.
pause
exit /b 1

:fatal
echo.
echo [ERRO] Falha na inicializacao.
pause
exit /b 1
