@echo off
cd /d "%~dp0"

echo Iniciando o ambiente do Django...

REM Verifica se a venv existe
IF NOT EXIST "env" (
    echo Criando ambiente virtual...
    python -m venv env
)

REM Ativa o ambiente virtual
call env\Scripts\activate.bat

echo Instalando dependências...
pip install -r requirements.txt

echo Iniciando servidor Django...

REM Abre o servidor em nova janela e continua rodando
start "" cmd /k "call env\Scripts\activate.bat && python manage.py runserver"

echo Projeto iniciado em http://127.0.0.1:8000
echo Esta janela sera fechada...
timeout /t 2 > nul
exit
