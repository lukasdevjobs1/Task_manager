"""
Teste rápido de conexão com Supabase
"""
from supabase import create_client

SUPABASE_URL = "https://ntatkxgsykdnsfrqxwnz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YXRreGdzeWtkbnNmcnF4d256Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjIwNzEsImV4cCI6MjA4NDAzODA3MX0.wmv7xL8z-1D5OYmOzDr-RUzFAgFBbWxMrJk7TMSFv4M"

try:
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Verificar empresas
    companies = client.table('companies').select('*').execute()
    print(f"Empresas: {len(companies.data)}")
    for c in companies.data:
        print(f"   - {c['name']} (ID: {c['id']})")
    
    # Verificar usuários
    users = client.table('users').select('*').execute()
    print(f"\nUsuarios: {len(users.data)}")
    for u in users.data:
        print(f"   - {u['username']} | {u['full_name']} | Role: {u['role']}")
    
    # Verificar tarefas
    tasks = client.table('task_assignments').select('*').execute()
    print(f"\nTarefas: {len(tasks.data)}")
    for t in tasks.data:
        print(f"   - {t['title']} | Status: {t['status']}")
    
    print("\nCONEXAO OK! Use qualquer username acima com qualquer senha.")
    
except Exception as e:
    print(f"Erro: {e}")
