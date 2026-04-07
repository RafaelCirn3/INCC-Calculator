@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

title INCC Calculator - Autostart
color 0A

REM Resolução silenciosa de Python e validação
call :resolver_python || goto :fatal
call :resolver_venv
call :validar_arquivos || goto :fatal

REM Fluxo automático único
call :diagnostico
call :preparar_ambiente || goto :fatal
call :executar_migracoes || goto :fatal
call :executar_check || goto :fatal
call :popular_incc_se_necessario
call :iniciar_servidor || goto :fatal

goto :fim

:resolver_python
set "PY_CMD="
python --version >nul 2>&1
if not errorlevel 1 set "PY_CMD=python"
if not defined PY_CMD (
    py -3 --version >nul 2>&1
    if not errorlevel 1 set "PY_CMD=py -3"
)

if not defined PY_CMD (
    echo [ERRO] Python nao encontrado.
    echo Instale Python 3 e tente novamente.
    exit /b 1
)

for /f "tokens=*" %%v in ('%PY_CMD% --version 2^>^&1') do set "PY_VER=%%v"
exit /b 0

:resolver_venv
set "VENV_DIR=.venv"
if exist "env\Scripts\python.exe" set "VENV_DIR=env"
if exist "venv\Scripts\python.exe" set "VENV_DIR=venv"
if exist ".venv\Scripts\python.exe" set "VENV_DIR=.venv"
set "VENV_PY=%CD%\%VENV_DIR%\Scripts\python.exe"
exit /b 0

:validar_arquivos
if not exist "manage.py" (
    echo [ERRO] Arquivo manage.py nao encontrado em %CD%.
    exit /b 1
)
if not exist "requirements.txt" (
    echo [ERRO] Arquivo requirements.txt nao encontrado em %CD%.
    exit /b 1
)
exit /b 0

:diagnostico
echo.
echo ========== DIAGNOSTICO DO PROJETO ==========
if exist "%VENV_PY%" (
    echo [OK] Ambiente virtual encontrado em "%VENV_DIR%"
) else (
    echo [SETUP] Ambiente virtual nao existe, sera criado.
)

if exist "db.sqlite3" (
    echo [OK] Banco de dados existe
) else (
    echo [SETUP] Banco de dados sera criado na migracao.
)

echo ============================================
echo.
exit /b 0

:preparar_ambiente
echo [1/5] Preparando ambiente...
if not exist "%VENV_PY%" (
    echo.Criando ambiente virtual em "%VENV_DIR%"...
    call %PY_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERRO] Falha ao criar ambiente virtual.
        exit /b 1
    )
)

echo.Atualizando pip/setuptools/wheel...
"%VENV_PY%" -m pip install --upgrade pip setuptools wheel >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Falha ao atualizar ferramentas do pip.
    exit /b 1
)

echo.Instalando dependencias do projeto...
"%VENV_PY%" -m pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    exit /b 1
)

echo [OK] Ambiente pronto.
exit /b 0

:executar_migracoes
echo [2/5] Aplicando migracoes...
"%VENV_PY%" manage.py makemigrations >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Falha no makemigrations.
    exit /b 1
)

"%VENV_PY%" manage.py migrate >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Falha no migrate.
    exit /b 1
)

echo [OK] Migracoes aplicadas com sucesso.
exit /b 0

:executar_check
echo [3/5] Validando projeto...
"%VENV_PY%" manage.py check >nul 2>&1
if errorlevel 1 (
    echo [ERRO] O comando manage.py check retornou falha.
    exit /b 1
)

echo [OK] Validacao concluida sem erros.
exit /b 0

:popular_incc_se_necessario
echo [4/5] Verificando dados INCC...
"%VENV_PY%" manage.py shell -c "from app.models import INCCIndex; exit(0 if INCCIndex.objects.exists() else 1)" >nul 2>&1

if errorlevel 1 (
    echo.Populando base de dados INCC pela primeira vez...
    "%VENV_PY%" manage.py load_incc >nul 2>&1
    if errorlevel 1 (
        echo [AVISO] Falha ao popular INCC, pode ser feito manualmente depois.
    ) else (
        echo [OK] Base INCC carregada com sucesso.
    )
) else (
    echo [OK] Base INCC ja populada. Pulando...
)
exit /b 0

:iniciar_servidor
echo [5/5] Iniciando servidor...
echo.
echo ===== SERVIDOR PRONTO =====
echo Acesse em: http://127.0.0.1:8000
echo ============================
echo.
start "INCC - Django Server" cmd /k "cd /d \"%CD%\" && \"%VENV_PY%\" manage.py runserver"
if errorlevel 1 (
    echo [ERRO] Nao foi possivel iniciar a janela do servidor.
    exit /b 1
)
timeout /t 2 >nul
exit /b 0

:fatal
echo.
echo [ERRO CRITICO] Falha na inicializacao.
echo Verifique os requisitos:
echo - Python 3.x instalado
echo - manage.py e requirements.txt presentes
echo.
pause
exit /b 1

:fim
echo Projeto pronto! Use Ctrl+C para parar o servidor.
exit /b 0
