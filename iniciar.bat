@echo off
title APRS-WX-CE - Estacion WX APRS
color 0A
echo.
echo  ================================================
echo   APRS-WX-CE - CA2JAT
echo   Estacion Meteorologica APRS para Chile
echo  ================================================
echo.
echo  Iniciando... (no cierre esta ventana, puede minimizarla)
echo.
cd /d "C:\python-wx"
python wx_chile.py
echo.
echo  El programa se detuvo. Presione una tecla para cerrar.
pause >nul
