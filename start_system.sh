#!/bin/bash
echo "Iniciando Task Manager ISP v2.0"

echo "Iniciando API Mobile..."
python api_mobile.py &
API_PID=$!

sleep 3

echo "Iniciando Streamlit..."
streamlit run app.py &
STREAMLIT_PID=$!

echo "Sistema iniciado!"
echo "API Mobile: http://localhost:5000"
echo "Streamlit: http://localhost:8501"

trap "kill $API_PID $STREAMLIT_PID; exit" INT
wait
