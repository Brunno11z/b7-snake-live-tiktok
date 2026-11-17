@echo off
chcp 65001 > nul
title B7 GAMES • Instalador de Dependências
cls
echo ========================================================
echo  🐍 B7 GAMES • COBRINHA 2.5D INTERATIVA TIKTOK LIVE
echo ========================================================
echo.
echo [1/3] Verificando instalação do Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python não foi encontrado no seu PATH!
    echo Por favor, instale o Python 3.10, 3.11 ou 3.12 em https://www.python.org/downloads/
    echo Lembre-se de marcar a caixa "Add python.exe to PATH" durante a instalação.
    pause
    exit /b
)
echo Python detectado com sucesso!
echo.
echo [2/3] Atualizando gerenciador pip...
python -m pip install --upgrade pip
echo.
echo [3/3] Instalando bibliotecas para TikTok Live & EulerStream API...
python -m pip install websockets aiohttp requests websocket-client TikTokLive
echo.
echo ========================================================
echo  ✓ Instalação concluída com sucesso!
echo  Agora você pode dar um duplo clique em INICIAR.bat
echo ========================================================
pause
