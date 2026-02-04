"""
Conexão EXCLUSIVA com Supabase - Substitui PostgreSQL local
Sistema de Gerenciamento de Tarefas ISP v2.0
"""
from supabase import create_client, Client
from typing import Optional, Dict, List, Any
from datetime import datetime
import bcrypt
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY

# Cliente Supabase com service key para bypass RLS
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY or SUPABASE_KEY)

class SupabaseDatabase:
    """Classe principal para todas as operações de banco via Supabase"""
    
    def __init__(self):
        self.client = supabase
    
    # === AUTENTICAÇÃO ===
    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Autentica usuário via Supabase"""
        try:
            # Busca usuário com empresa
            result = self.client.table('users').select(
                'id, company_id, username, password_hash, full_name, team, role, is_super_admin, active, companies(name, active)'
            ).eq('username', username).execute()
            
            if not result.data:
                return None
            
            user = result.data[0]
            company = user['companies']
            
            # Verifica se usuário e empresa estão ativos
            if not user['active'] or not company['active']:
                return None
            
            # Verifica senha
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return None
            
            return {
                'id': user['id'],
                'company_id': user['company_id'],
                'company_name': company['name'],
                'username': user['username'],
                'full_name': user['full_name'],
                'team': user['team'],
                'role': user['role'],
                'is_super_admin': user.get('is_super_admin', False)
            }
        except Exception as e:
            print(f"Erro na autenticação: {e}")
            return None
    
    def hash_password(self, password: str) -> str:
        """Gera hash bcrypt da senha"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # === USUÁRIOS ===
    def create_user(self, username: str, password: str, full_name: str, team: str, company_id: int, role: str = 'user') -> tuple[bool, str]:
        """Cria novo usuário"""
        try:
            if len(password) < 6:
                return False, "A senha deve ter no mínimo 6 caracteres."
            
            # Verifica se username já existe
            existing = self.client.table('users').select('id').eq('username', username).execute()
            if existing.data:
                return False, "Nome de usuário já existe."
            
            # Cria usuário
            user_data = {
                'company_id': company_id,
                'username': username,
                'password_hash': self.hash_password(password),
                'full_name': full_name,
                'team': team,
                'role': role,
                'active': True,
                'created_at': datetime.utcnow().isoformat()
            }
            
            self.client.table('users').insert(user_data).execute()
            return True, "Usuário criado com sucesso!"
        except Exception as e:
            return False, f"Erro ao criar usuário: {str(e)}"
    
    def get_all_users(self, company_id: int) -> List[dict]:
        """Retorna usuários de uma empresa"""
        try:
            result = self.client.table('users').select('*').eq('company_id', company_id).order('full_name').execute()
            return result.data or []
        except Exception as e:
            print(f"Erro ao buscar usuários: {e}")
            return []
    
    def get_user_by_id(self, user_id: int, company_id: int = None) -> Optional[dict]:
        """Retorna usuário por ID"""
        try:
            query = self.client.table('users').select('*').eq('id', user_id)
            if company_id:
                query = query.eq('company_id', company_id)
            result = query.execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return None
    
    def update_password(self, user_id: int, new_password: str, company_id: int) -> tuple[bool, str]:
        """Atualiza senha do usuário"""
        try:
            if len(new_password) < 6:
                return False, "A senha deve ter no mínimo 6 caracteres."
            
            result = self.client.table('users').update({
                'password_hash': self.hash_password(new_password)
            }).eq('id', user_id).eq('company_id', company_id).execute()
            
            if result.data:
                return True, "Senha atualizada com sucesso!"
            return False, "Usuário não encontrado."
        except Exception as e:
            return False, f"Erro ao atualizar senha: {str(e)}"
    
    def toggle_user_status(self, user_id: int, company_id: int) -> tuple[bool, str]:
        """Ativa/desativa usuário"""
        try:
            # Busca usuário atual
            user = self.get_user_by_id(user_id, company_id)
            if not user:
                return False, "Usuário não encontrado."
            
            new_status = not user['active']
            self.client.table('users').update({
                'active': new_status
            }).eq('id', user_id).eq('company_id', company_id).execute()
            
            status = "ativado" if new_status else "desativado"
            return True, f"Usuário {status} com sucesso!"
        except Exception as e:
            return False, f"Erro ao alterar status: {str(e)}"
    
    def delete_user(self, user_id: int, company_id: int) -> tuple[bool, str]:
        """Exclui usuário"""
        try:
            # Exclui tarefas do usuário primeiro
            self.client.table('task_assignments').delete().eq('assigned_to', user_id).execute()
            
            # Exclui usuário
            result = self.client.table('users').delete().eq('id', user_id).eq('company_id', company_id).execute()
            
            if result.data:
                return True, "Usuário excluído com sucesso!"
            return False, "Usuário não encontrado."
        except Exception as e:
            return False, f"Erro ao excluir usuário: {str(e)}"
    
    # === EMPRESAS ===
    def get_all_companies(self) -> List[dict]:
        """Retorna todas as empresas"""
        try:
            result = self.client.table('companies').select('*').order('name').execute()
            return result.data or []
        except Exception as e:
            print(f"Erro ao buscar empresas: {e}")
            return []
    
    def create_company(self, name: str, slug: str) -> tuple[bool, str, int]:
        """Cria nova empresa"""
        try:
            if not name.strip() or not slug.strip():
                return False, "Nome e slug são obrigatórios.", None
            
            # Verifica se slug já existe
            existing = self.client.table('companies').select('id').eq('slug', slug).execute()
            if existing.data:
                return False, "Já existe uma empresa com este slug.", None
            
            company_data = {
                'name': name.strip(),
                'slug': slug.strip().lower(),
                'active': True,
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.client.table('companies').insert(company_data).execute()
            company_id = result.data[0]['id'] if result.data else None
            return True, "Empresa criada com sucesso!", company_id
        except Exception as e:
            return False, f"Erro ao criar empresa: {str(e)}", None
    
    def toggle_company_status(self, company_id: int) -> tuple[bool, str]:
        """Ativa/desativa empresa"""
        try:
            # Busca empresa atual
            result = self.client.table('companies').select('active').eq('id', company_id).execute()
            if not result.data:
                return False, "Empresa não encontrada."
            
            new_status = not result.data[0]['active']
            self.client.table('companies').update({
                'active': new_status
            }).eq('id', company_id).execute()
            
            status = "ativada" if new_status else "desativada"
            return True, f"Empresa {status} com sucesso!"
        except Exception as e:
            return False, f"Erro ao alterar status: {str(e)}"
    
    # === TAREFAS ATRIBUÍDAS ===
    def create_task_assignment(self, assignment_data: dict) -> tuple[bool, str, int]:
        """Cria nova tarefa atribuída"""
        try:
            data = {
                'company_id': assignment_data['company_id'],
                'assigned_by': assignment_data['assigned_by'],
                'assigned_to': assignment_data['assigned_to'],
                'title': assignment_data['title'],
                'description': assignment_data.get('description'),
                'address': assignment_data.get('address'),
                'latitude': assignment_data.get('latitude'),
                'longitude': assignment_data.get('longitude'),
                'status': assignment_data.get('status', 'pendente'),
                'priority': assignment_data.get('priority', 'media'),
                'due_date': assignment_data.get('due_date'),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.client.table('task_assignments').insert(data).execute()
            assignment_id = result.data[0]['id'] if result.data else None
            return True, "Tarefa criada com sucesso!", assignment_id
        except Exception as e:
            return False, f"Erro ao criar tarefa: {str(e)}", None
    
    def get_task_assignments(self, company_id: int, user_id: int = None, status: str = None) -> List[dict]:
        """Retorna tarefas atribuídas"""
        try:
            query = self.client.table('task_assignments').select(
                '*, assigned_to_user:users!assigned_to(full_name), assigned_by_user:users!assigned_by(full_name)'
            ).eq('company_id', company_id)
            
            if user_id:
                query = query.eq('assigned_to', user_id)
            if status:
                query = query.eq('status', status)
            
            result = query.order('created_at', desc=True).execute()
            return result.data or []
        except Exception as e:
            print(f"Erro ao buscar tarefas: {e}")
            return []
    
    def get_task_assignment_by_id(self, assignment_id: int, company_id: int = None) -> Optional[dict]:
        """Retorna tarefa por ID"""
        try:
            query = self.client.table('task_assignments').select(
                '*, assigned_to_user:users!assigned_to(full_name), assigned_by_user:users!assigned_by(full_name)'
            ).eq('id', assignment_id)
            
            if company_id:
                query = query.eq('company_id', company_id)
            
            result = query.execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erro ao buscar tarefa: {e}")
            return None
    
    def update_task_status(self, assignment_id: int, status: str, observations: str = None) -> tuple[bool, str]:
        """Atualiza status da tarefa"""
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow().isoformat()
            }
            if observations:
                update_data['observations'] = observations
            
            result = self.client.table('task_assignments').update(update_data).eq('id', assignment_id).execute()
            
            if result.data:
                return True, "Status atualizado com sucesso!"
            return False, "Tarefa não encontrada."
        except Exception as e:
            return False, f"Erro ao atualizar status: {str(e)}"
    
    # === NOTIFICAÇÕES ===
    def create_notification(self, user_id: int, company_id: int, type: str, title: str, message: str = None, reference_id: int = None) -> bool:
        """Cria notificação"""
        try:
            data = {
                'user_id': user_id,
                'company_id': company_id,
                'type': type,
                'title': title,
                'message': message,
                'reference_id': reference_id,
                'read': False,
                'created_at': datetime.utcnow().isoformat()
            }
            
            self.client.table('notifications').insert(data).execute()
            return True
        except Exception as e:
            print(f"Erro ao criar notificação: {e}")
            return False
    
    def get_notifications(self, user_id: int, unread_only: bool = False) -> List[dict]:
        """Retorna notificações do usuário"""
        try:
            query = self.client.table('notifications').select('*').eq('user_id', user_id)
            if unread_only:
                query = query.eq('read', False)
            
            result = query.order('created_at', desc=True).execute()
            return result.data or []
        except Exception as e:
            print(f"Erro ao buscar notificações: {e}")
            return []
    
    def mark_notification_as_read(self, notification_id: int, user_id: int) -> bool:
        """Marca notificação como lida"""
        try:
            self.client.table('notifications').update({
                'read': True
            }).eq('id', notification_id).eq('user_id', user_id).execute()
            return True
        except Exception as e:
            print(f"Erro ao marcar notificação: {e}")
            return False
    
    def get_unread_count(self, user_id: int) -> int:
        """Retorna quantidade de notificações não lidas"""
        try:
            result = self.client.table('notifications').select('id', count='exact').eq('user_id', user_id).eq('read', False).execute()
            return result.count or 0
        except Exception as e:
            print(f"Erro ao contar notificações: {e}")
            return 0

# Instância global
db = SupabaseDatabase()

# Funções de compatibilidade para manter a API existente
def get_session():
    """Context manager compatível - retorna a instância do Supabase"""
    class MockSession:
        def __enter__(self):
            return db
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def commit(self):
            pass
        def rollback(self):
            pass
        def close(self):
            pass
    
    return MockSession()

def get_db():
    """Generator compatível - retorna a instância do Supabase"""
    yield db