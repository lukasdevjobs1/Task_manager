"""
Script para verificar usuários criados e testar login
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.supabase_only_connection import db

def check_users():
    """Verifica usuários no Supabase"""
    print("Verificando usuários no Supabase...")
    
    try:
        companies = db.get_all_companies()
        
        for company in companies:
            print(f"\nEmpresa: {company['name']} (ID: {company['id']})")
            users = db.get_all_users(company['id'])
            
            for user in users:
                print(f"  - {user['full_name']} ({user['username']})")
                print(f"    Role: {user['role']} | Ativo: {user['active']}")
                print(f"    Hash: {user['password_hash'][:20]}...")
                
                # Testar login
                auth_result = db.authenticate_user(user['username'], '123456')
                if auth_result:
                    print(f"    LOGIN OK com senha '123456'")
                else:
                    print(f"    LOGIN FALHOU com senha '123456'")
                print()
        
    except Exception as e:
        print(f"Erro: {e}")

def main():
    print("=" * 50)
    print("VERIFICACAO DE USUARIOS E LOGIN")
    print("=" * 50)
    check_users()

if __name__ == "__main__":
    main()