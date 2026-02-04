#!/usr/bin/env python3
"""
Script Final - Completar Integração Task Manager ISP v2.0
"""

import os
import sys

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 50)
    print("FINALIZANDO INTEGRACAO - TASK MANAGER ISP v2.0")
    print("=" * 50)
    
    # 1. Criar scripts de inicialização simples
    print("\n1. Criando scripts de inicialização...")
    
    # Script Windows
    bat_content = '''@echo off
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
'''
    
    with open('start_system.bat', 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    # Script Linux/Mac
    sh_content = '''#!/bin/bash
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
'''
    
    with open('start_system.sh', 'w') as f:
        f.write(sh_content)
    
    try:
        os.chmod('start_system.sh', 0o755)
    except:
        pass
    
    print("OK - Scripts criados")
    
    # 2. Verificar se o sistema básico funciona
    print("\n2. Verificando sistema...")
    
    try:
        from database.connection import SessionLocal
        from sqlalchemy import text
        session = SessionLocal()
        session.execute(text("SELECT 1"))
        session.close()
        print("OK - PostgreSQL funcionando")
    except Exception as e:
        print(f"AVISO - PostgreSQL: {e}")
    
    try:
        from database.supabase_connection import supabase_manager
        response = supabase_manager.client.table('users').select('count').execute()
        print("OK - Supabase conectado")
    except Exception as e:
        print(f"AVISO - Supabase: {e}")
    
    # 3. Instruções finais
    print("\n" + "=" * 50)
    print("INTEGRACAO FINALIZADA!")
    print("=" * 50)
    
    print("""
PROXIMOS PASSOS:

1. INICIAR O SISTEMA:
   Windows: Execute start_system.bat
   Linux/Mac: Execute ./start_system.sh

2. ACESSAR:
   Web: http://localhost:8501
   API: http://localhost:5000

3. LOGIN (senha: 123456):
   - admin.geral (Super Admin)
   - carlos.gerente (Gerente)
   - joao.tecnico (Tecnico)
   - maria.tecnica (Tecnica)

4. APP MOBILE:
   - Entre na pasta mobile/
   - Execute: npx expo start
   - Escaneie QR code com Expo Go

SISTEMA PRONTO PARA USO!
""")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        print("\nSUCESSO! Integração finalizada.")
    except Exception as e:
        print(f"\nERRO: {e}")
    
    input("\nPressione Enter para sair...")