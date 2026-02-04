@echo off
echo Iniciando Task Manager ISP v2.0
echo.

echo Iniciando API Mobile...
start "API Mobile" cmd /k "python api_mobile.py"

timeout /t 3 /nobreak > nul

echo Iniciando Streamlit...
start "Streamlit" cmd /k "streamlit run app.py"

echo.
echo Sistema iniciado!
echo API Mobile: http://localhost:5000
echo Streamlit: http://localhost:8501
echo.
pause
