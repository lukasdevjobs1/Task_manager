"""
Script de Teste - Sistema de Gerenciamento de Tarefas ISP v2.0
Verifica se todos os componentes estão funcionando corretamente
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configurações
API_BASE_URL = "http://localhost:5000/api"
WEB_URL = "http://localhost:8501"

def test_api_connection():
    """Testa conexão com a API"""
    print("🔍 Testando conexão com API...")
    try:
        response = requests.get(f"{API_BASE_URL}/test", timeout=5)
        if response.status_code == 200:
            print("✅ API respondendo corretamente")
            return True
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão com API: {e}")
        return False

def test_login():
    """Testa login via API"""
    print("🔍 Testando login...")
    try:
        data = {
            "username": "joao.tecnico",
            "password": "123456"
        }
        response = requests.post(f"{API_BASE_URL}/login", json=data, timeout=5)
        result = response.json()
        
        if result.get('success'):
            print("✅ Login funcionando corretamente")
            print(f"   Usuário: {result['user']['full_name']}")
            return result['user']
        else:
            print(f"❌ Erro no login: {result.get('message')}")
            return None
    except Exception as e:
        print(f"❌ Erro no teste de login: {e}")
        return None

def test_tasks(user):
    """Testa carregamento de tarefas"""
    print("🔍 Testando carregamento de tarefas...")
    try:
        response = requests.get(f"{API_BASE_URL}/tasks/{user['id']}", timeout=5)
        result = response.json()
        
        if result.get('success'):
            tasks = result.get('tasks', [])
            print(f"✅ Tarefas carregadas: {len(tasks)} encontradas")
            return tasks
        else:
            print(f"❌ Erro ao carregar tarefas: {result.get('message')}")
            return []
    except Exception as e:
        print(f"❌ Erro no teste de tarefas: {e}")
        return []

def test_database_connection():
    """Testa conexão com banco de dados"""
    print("🔍 Testando conexão com banco...")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from database.supabase_only_connection import db
        
        # Tenta buscar usuários
        users = db.get_all_users(1)  # Company ID 1
        print(f"✅ Banco conectado: {len(users)} usuários encontrados")
        return True
    except Exception as e:
        print(f"❌ Erro de conexão com banco: {e}")
        return False

def test_web_access():
    """Testa acesso ao sistema web"""
    print("🔍 Testando acesso ao sistema web...")
    try:
        response = requests.get(WEB_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Sistema web acessível")
            return True
        else:
            print(f"❌ Sistema web retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de acesso ao sistema web: {e}")
        print("   Certifique-se de que o Streamlit está rodando")
        return False

def main():
    """Executa todos os testes"""
    print("=" * 50)
    print("🧪 TESTE COMPLETO DO SISTEMA")
    print("=" * 50)
    print()
    
    # Contador de testes
    tests_passed = 0
    total_tests = 5
    
    # Teste 1: Conexão com API
    if test_api_connection():
        tests_passed += 1
    print()
    
    # Teste 2: Conexão com banco
    if test_database_connection():
        tests_passed += 1
    print()
    
    # Teste 3: Login
    user = test_login()
    if user:
        tests_passed += 1
    print()
    
    # Teste 4: Tarefas (se login funcionou)
    if user:
        tasks = test_tasks(user)
        if isinstance(tasks, list):
            tests_passed += 1
    else:
        print("⏭️  Pulando teste de tarefas (login falhou)")
    print()
    
    # Teste 5: Sistema web
    if test_web_access():
        tests_passed += 1
    print()
    
    # Resultado final
    print("=" * 50)
    print("📊 RESULTADO DOS TESTES")
    print("=" * 50)
    print(f"Testes aprovados: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema funcionando corretamente")
    elif tests_passed >= 3:
        print("⚠️  SISTEMA PARCIALMENTE FUNCIONAL")
        print("🔧 Alguns componentes precisam de atenção")
    else:
        print("❌ SISTEMA COM PROBLEMAS")
        print("🚨 Verifique as configurações e dependências")
    
    print()
    print("💡 Dicas:")
    print("- Certifique-se de que a API está rodando (python api_mobile.py)")
    print("- Certifique-se de que o Streamlit está rodando (streamlit run app.py)")
    print("- Verifique as configurações no arquivo .env")
    print("- Use start_complete_system.bat para iniciar tudo automaticamente")

if __name__ == "__main__":
    main()