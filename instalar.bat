@echo off
title APRS-WX-CE Instalador
color 0A
echo.
echo  ================================================
echo   APRS-WX-CE - Instalador para Windows
echo   Estacion Meteorologica APRS para Chile
echo   by CA2JAT - Valle de Elqui
echo  ================================================
echo.

echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python no esta instalado.
    echo.
    echo  Instale Python desde https://www.python.org/downloads/
    echo  IMPORTANTE: marque la casilla "Add Python to PATH"
    echo  durante la instalacion.
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)
python --version
echo  Python encontrado OK

echo.
echo [2/4] Creando carpeta C:\python-wx ...
if not exist "C:\python-wx" mkdir "C:\python-wx"
echo  Carpeta lista OK

echo.
echo [3/4] Copiando archivos...
if not exist "wx_chile.py" (
    echo  ERROR: no se encuentra wx_chile.py
    echo  Ejecute instalar.bat desde la carpeta descargada.
    pause
    exit /b 1
)
copy /Y wx_chile.py "C:\python-wx\wx_chile.py" >nul
copy /Y iniciar.bat "C:\python-wx\iniciar.bat" >nul
echo  Archivos copiados OK

echo.
echo [4/4] Instalando dependencias (puede tardar unos minutos)...
python -m pip install requests pytz
if errorlevel 1 (
    echo.
    echo  ERROR instalando dependencias.
    echo  Intente manualmente: python -m pip install requests pytz
    pause
    exit /b 1
)
echo  Dependencias instaladas OK

echo.
echo  Creando inicio automatico con Windows...
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
copy /Y iniciar.bat "%STARTUP%\APRS-WX-CE.bat" >nul
echo  Inicio automatico OK

echo.
echo  ================================================
echo   Instalacion completada
echo  ================================================
echo.
echo  SIGUIENTE PASO:
echo  Edite C:\python-wx\wx_chile.py con el Bloc de notas
echo  y configure indicativo, ubicacion, token DMC y
echo  API key de OpenWeatherMap.
echo  Cambie tambien la ruta ESTADO_FILE a:
echo    C:/python-wx/estado_dia.json
echo.
echo  Luego ejecute C:\python-wx\iniciar.bat
echo.
pause
