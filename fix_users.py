"""
Script para corrigir usuários e criar admin geral correto
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.supabase_only_connection import db

def fix_users():
    """Corrige os usuários no sistema"""
    print("Corrigindo usuários no sistema...")
    
    try:
        # Busca todas as empresas
        companies = db.get_all_companies()
        print(f"Empresas encontradas: {len(companies)}")
        
        for company in companies:
            print(f"\nEmpresa: {company['name']} (ID: {company['id']})")
            users = db.get_all_users(company['id'])
            
            for user in users:
                print(f"  - {user['full_name']} ({user['username']}) - Role: {user['role']} - Super Admin: {user.get('is_super_admin', False)}")
        
        # Criar admin geral se não existir
        admin_geral_exists = False
        for company in companies:
            users = db.get_all_users(company['id'])
            for user in users:
                if user['username'] == 'admin.geral':
                    admin_geral_exists = True
                    break
        
        if not admin_geral_exists:
            print("\nCriando admin geral...")
            # Usar primeira empresa para criar admin geral
            company_id = companies[0]['id']
            success, message = db.create_user(
                username='admin.geral',
                password='123456',
                full_name='Admin Geral do Sistema',
                team='administracao',
                company_id=company_id,
                role='admin'
            )
            
            if success:
                print(f"Admin geral criado: {message}")
                # Marcar como super admin
                users = db.get_all_users(company_id)
                for user in users:
                    if user['username'] == 'admin.geral':
                        # Atualizar para super admin
                        db.client.table('users').update({
                            'is_super_admin': True
                        }).eq('id', user['id']).execute()
                        print("Marcado como super admin")
                        break
            else:
                print(f"Erro ao criar admin geral: {message}")
        
        # Verificar se lucas.gc existe na empresa GCNET
        gcnet_company = None
        for company in companies:
            if 'GCNET' in company['name'].upper():
                gcnet_company = company
                break
        
        if gcnet_company:
            print(f"\nVerificando usuários da {gcnet_company['name']}...")
            users = db.get_all_users(gcnet_company['id'])
            
            lucas_exists = False
            for user in users:
                if user['username'] == 'lucas.gc':
                    lucas_exists = True
                    print(f"  - Lucas encontrado: {user['full_name']} - Role: {user['role']}")
                    
                    # Garantir que lucas.gc é admin (gerente)
                    if user['role'] != 'admin':
                        db.client.table('users').update({
                            'role': 'admin'
                        }).eq('id', user['id']).execute()
                        print("    -> Atualizado para admin (gerente)")
                    break
            
            if not lucas_exists:
                print("Criando usuário lucas.gc como gerente da GCNET...")
                success, message = db.create_user(
                    username='lucas.gc',
                    password='123456',
                    full_name='Lucas - Gerente GCNET',
                    team='gerencia',
                    company_id=gcnet_company['id'],
                    role='admin'
                )
                
                if success:
                    print(f"Lucas criado: {message}")
                else:
                    print(f"Erro ao criar Lucas: {message}")
        
        return True
        
    except Exception as e:
        print(f"Erro: {e}")
        return False

def main():
    print("=" * 60)
    print("CORRIGINDO USUARIOS - Task Manager ISP v2.0")
    print("=" * 60)
    
    if fix_users():
        print("\n" + "=" * 60)
        print("USUARIOS CORRIGIDOS!")
        print("Credenciais de acesso:")
        print("  ADMIN GERAL (você):")
        print("    - Username: admin.geral")
        print("    - Senha: 123456")
        print("  GERENTE GCNET:")
        print("    - Username: lucas.gc") 
        print("    - Senha: 123456")
        print("=" * 60)
    else:
        print("\nFalha ao corrigir usuários")

if __name__ == "__main__":
    main()