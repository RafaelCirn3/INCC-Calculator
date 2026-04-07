@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

title INCC Launcher
color 0A

call :resolver_python || goto :fatal
call :resolver_venv
call :validar_arquivos || goto :fatal

:menu
cls
call :cabecalho
echo [1] Preparar ambiente (venv + dependencias)
echo [2] Banco de dados (makemigrations + migrate)
echo [3] Verificar projeto (manage.py check)
echo [4] Popular INCC (load_incc)
echo [5] Iniciar servidor
echo [6] Executar fluxo completo
echo [0] Sair
echo.
choice /c 1234560 /n /m "Escolha uma opcao: "

if errorlevel 7 goto :fim
if errorlevel 6 goto :acao_fluxo_completo
if errorlevel 5 goto :acao_iniciar_servidor
if errorlevel 4 goto :acao_popular_incc
if errorlevel 3 goto :acao_check
if errorlevel 2 goto :acao_migrate
if errorlevel 1 goto :acao_preparar
goto :menu

:acao_preparar
call :preparar_ambiente
call :retorno_menu
goto :menu

:acao_migrate
call :executar_migracoes
call :retorno_menu
goto :menu

:acao_check
call :executar_check
call :retorno_menu
goto :menu

:acao_popular_incc
call :popular_incc
call :retorno_menu
goto :menu

:acao_iniciar_servidor
call :iniciar_servidor
call :retorno_menu
goto :menu

:acao_fluxo_completo
call :preparar_ambiente || goto :fluxo_erro
call :executar_migracoes || goto :fluxo_erro
call :executar_check || goto :fluxo_erro
echo.
choice /c SN /n /m "Deseja popular os indices INCC agora? [S/N]: "
if errorlevel 2 goto :iniciar_apos_fluxo
call :popular_incc || goto :fluxo_erro

:iniciar_apos_fluxo
call :iniciar_servidor || goto :fluxo_erro
echo.
echo Fluxo completo executado com sucesso.
call :retorno_menu
goto :menu

:fluxo_erro
echo.
echo [ERRO] Fluxo completo interrompido.
call :retorno_menu
goto :menu

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

:cabecalho
echo ==============================================================
echo                 INCC CALCULATOR - LAUNCHER
echo ==============================================================
echo Diretorio: %CD%
echo Python: %PY_VER%
echo Ambiente virtual: %VENV_DIR%
echo ==============================================================
echo.
exit /b 0

:preparar_ambiente
echo.
echo [1/4] Preparando ambiente...
if not exist "%VENV_PY%" (
    echo Criando ambiente virtual em "%VENV_DIR%"...
    call %PY_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERRO] Falha ao criar ambiente virtual.
        exit /b 1
    )
)

echo Atualizando pip/setuptools/wheel...
"%VENV_PY%" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [ERRO] Falha ao atualizar ferramentas do pip.
    exit /b 1
)

echo Instalando dependencias do projeto...
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias.
    exit /b 1
)

echo Ambiente pronto.
exit /b 0

:executar_migracoes
echo.
echo [2/4] Aplicando migracoes...
"%VENV_PY%" manage.py makemigrations
if errorlevel 1 (
    echo [ERRO] Falha no makemigrations.
    exit /b 1
)

"%VENV_PY%" manage.py migrate
if errorlevel 1 (
    echo [ERRO] Falha no migrate.
    exit /b 1
)

echo Migracoes aplicadas com sucesso.
exit /b 0

:executar_check
echo.
echo [3/4] Validando projeto...
"%VENV_PY%" manage.py check
if errorlevel 1 (
    echo [ERRO] O comando manage.py check retornou falha.
    exit /b 1
)

echo Validacao concluida sem erros.
exit /b 0

:popular_incc
echo.
echo [4/4] Populando dados INCC...
"%VENV_PY%" manage.py load_incc
if errorlevel 1 (
    echo [ERRO] Falha ao executar load_incc.
    exit /b 1
)

echo Base INCC atualizada.
exit /b 0

:iniciar_servidor
echo.
echo Iniciando servidor Django em nova janela...
start "INCC - Django Server" cmd /k "cd /d \"%CD%\" && \"%VENV_PY%\" manage.py runserver"
if errorlevel 1 (
    echo [ERRO] Nao foi possivel iniciar a janela do servidor.
    exit /b 1
)

echo Servidor iniciado em http://127.0.0.1:8000
exit /b 0

:retorno_menu
echo.
pause
exit /b 0

:fatal
echo.
echo Falha critica. Encerrando launcher.
pause
exit /b 1

:fim
echo.
echo Encerrando launcher.
exit /b 0
