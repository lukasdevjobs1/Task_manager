"""
Script para testar conexão Supabase e resetar senha do admin
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.supabase_only_connection import db

def test_supabase_connection():
    """Testa a conexão com Supabase"""
    print("Testando conexão com Supabase...")
    
    try:
        # Testa buscar empresas
        companies = db.get_all_companies()
        print(f"Conexão OK! Encontradas {len(companies)} empresas:")
        for company in companies:
            print(f"   - {company['name']} (ID: {company['id']})")
        
        # Testa buscar usuários
        if companies:
            company_id = companies[0]['id']
            users = db.get_all_users(company_id)
            print(f"Encontrados {len(users)} usuários na empresa {companies[0]['name']}:")
            for user in users:
                print(f"   - {user['full_name']} ({user['username']}) - {user['role']}")
        
        return True
    except Exception as e:
        print(f"Erro na conexão: {e}")
        return False

def reset_admin_password():
    """Reseta a senha do admin geral para '123456'"""
    print("\nResetando senha do admin geral...")
    
    try:
        # Busca o admin geral
        companies = db.get_all_companies()
        if not companies:
            print("Nenhuma empresa encontrada")
            return False
        
        company_id = companies[0]['id']
        users = db.get_all_users(company_id)
        
        admin_user = None
        for user in users:
            if user.get('is_super_admin') or user['username'] == 'admin.geral':
                admin_user = user
                break
        
        if not admin_user:
            print("Admin geral não encontrado")
            return False
        
        # Reseta a senha
        success, message = db.update_password(admin_user['id'], '123456', company_id)
        
        if success:
            print(f"SUCESSO: {message}")
            print(f"   Username: {admin_user['username']}")
            print(f"   Nova senha: 123456")
            return True
        else:
            print(f"ERRO: {message}")
            return False
            
    except Exception as e:
        print(f"Erro ao resetar senha: {e}")
        return False

def main():
    print("=" * 50)
    print("TESTE DE CONEXAO SUPABASE - Task Manager ISP v2.0")
    print("=" * 50)
    
    # Testa conexão
    if not test_supabase_connection():
        print("\nFalha na conexão. Verifique as credenciais do Supabase no .env")
        return
    
    # Reseta senha do admin
    if not reset_admin_password():
        print("\nFalha ao resetar senha do admin")
        return
    
    print("\n" + "=" * 50)
    print("TUDO PRONTO! O sistema web agora usa apenas Supabase")
    print("Você pode fazer login com:")
    print("   - Username: admin.geral")
    print("   - Senha: 123456")
    print("=" * 50)

if __name__ == "__main__":
    main()