@echo off
cd /d "%~dp0"

REM Tenta localizar o Python automaticamente no PATH
where python >nul 2>&1
if %errorlevel% == 0 (
    python estacionamento_rosa.py
    pause
    exit /b
)

REM Fallback: tenta o caminho padrão de instalação do Python 3.12
set "PY312=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
if exist "%PY312%" (
    "%PY312%" estacionamento_rosa.py
    pause
    exit /b
)

REM Fallback: tenta py launcher
where py >nul 2>&1
if %errorlevel% == 0 (
    py estacionamento_rosa.py
    pause
    exit /b
)

echo.
echo ERRO: Python nao encontrado.
echo Instale o Python em https://www.python.org/downloads/
echo e marque a opcao "Add Python to PATH" durante a instalacao.
echo.
pause
