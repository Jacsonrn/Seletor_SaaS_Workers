@echo off
:: Garante que o script vai executar na pasta correta, independente de onde for chamado (Task Scheduler, Startup, etc)
cd /d "%~dp0"

echo ==========================================
echo       MOTOR SELETOR SAAS - INICIANDO
echo ==========================================
echo.
echo Aguardando conexoes na porta 8001...
echo Pressione CTRL+C para encerrar.

:: Inicia o servidor Web usando o Python portatil
.\python_embed\python.exe -m uvicorn api_worker:app --host 0.0.0.0 --port 8001 --reload
