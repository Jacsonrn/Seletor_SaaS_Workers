@echo off
setlocal enabledelayedexpansion

REM Garante que o script vai executar na pasta correta, independente de onde for chamado (Task Scheduler, Startup, etc)
cd /d "%~dp0"

echo ==========================================
echo       MOTOR SELETOR SAAS - INICIANDO
echo ==========================================
echo Verificando dependencias do sistema...

where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] Git nao detectado. Iniciando instalacao automatica invisivel...
    curl -L -o Git-Installer.exe https://github.com/git-for-windows/git/releases/download/v2.46.0.windows.1/Git-2.46.0-64-bit.exe
    if exist Git-Installer.exe (
        echo [INFO] Instalando Git silenciosamente. Pode levar 1-2 minutos...
        Git-Installer.exe /VERYSILENT /NORESTART /NOCANCEL /SP- /SUPPRESSMSGBOXES
        del Git-Installer.exe
        set "PATH=!PATH!;C:\Program Files\Git\cmd"
        echo [OK] Git instalado e configurado!
    ) else (
        echo [ERRO] Falha ao baixar o Git. Verifique a internet do laboratorio.
    )
) else (
    echo [OK] Git detectado.
)

echo.
echo Aguardando conexoes na porta 8001...
echo Pressione CTRL+C para encerrar.

REM Inicia o servidor Web usando o Python portatil
.\python_embed\python.exe -m uvicorn api_worker:app --host 0.0.0.0 --port 8001

echo.
echo [ERRO] O Motor parou inesperadamente!
pause
