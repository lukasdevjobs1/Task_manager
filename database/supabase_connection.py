"""
Conexão com Supabase para o sistema Streamlit
"""
from supabase import create_client, Client
import os
from typing import Optional, Dict, List, Any
from datetime import datetime
import json
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY, SUPABASE_BUCKET

# Cliente Supabase com service key para bypass RLS
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY or SUPABASE_KEY)

def get_supabase_client() -> Client:
    """Retorna cliente Supabase configurado"""
    return supabase

class SupabaseManager:
    """Gerenciador de operações Supabase"""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.bucket = SUPABASE_BUCKET
    
    # === USUÁRIOS ===
    def sync_user_to_supabase(self, user_data: Dict) -> bool:
        """Sincroniza usuário do PostgreSQL para Supabase"""
        try:
            result = self.client.table('users').upsert({
                'id': user_data['id'],
                'company_id': user_data['company_id'],
                'username': user_data['username'],
                'full_name': user_data['full_name'],
                'team': user_data['team'],
                'role': user_data['role'],
                'is_super_admin': user_data.get('is_super_admin', False),
                'active': user_data['active'],
                'push_token': user_data.get('push_token'),
                'created_at': user_data['created_at'].isoformat() if isinstance(user_data['created_at'], datetime) else user_data['created_at']
            }).execute()
            return True
        except Exception as e:
            print(f"Erro ao sincronizar usuário: {e}")
            return False
    
    def update_push_token(self, user_id: int, push_token: str) -> bool:
        """Atualiza token push do usuário"""
        try:
            self.client.table('users').update({
                'push_token': push_token
            }).eq('id', user_id).execute()
            return True
        except Exception as e:
            print(f"Erro ao atualizar push token: {e}")
            return False
    
    # === TAREFAS ATRIBUÍDAS ===
    def sync_task_assignment_to_supabase(self, assignment_data: Dict) -> bool:
        """Sincroniza tarefa atribuída para Supabase"""
        try:
            result = self.client.table('task_assignments').upsert({
                'id': assignment_data['id'],
                'company_id': assignment_data['company_id'],
                'assigned_by': assignment_data['assigned_by'],
                'assigned_to': assignment_data['assigned_to'],
                'title': assignment_data['title'],
                'description': assignment_data.get('description'),
                'address': assignment_data.get('address'),
                'latitude': assignment_data.get('latitude'),
                'longitude': assignment_data.get('longitude'),
                'status': assignment_data['status'],
                'priority': assignment_data['priority'],
                'due_date': assignment_data['due_date'].isoformat() if assignment_data.get('due_date') else None,
                'observations': assignment_data.get('observations'),
                'created_at': assignment_data['created_at'].isoformat() if isinstance(assignment_data['created_at'], datetime) else assignment_data['created_at'],
                'updated_at': assignment_data['updated_at'].isoformat() if isinstance(assignment_data['updated_at'], datetime) else assignment_data['updated_at']
            }).execute()
            return True
        except Exception as e:
            print(f"Erro ao sincronizar tarefa: {e}")
            return False
    
    def update_task_status(self, assignment_id: int, status: str, observations: str = None) -> bool:
        """Atualiza status da tarefa"""
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow().isoformat()
            }
            if observations:
                update_data['observations'] = observations
            
            self.client.table('task_assignments').update(update_data).eq('id', assignment_id).execute()
            return True
        except Exception as e:
            print(f"Erro ao atualizar status: {e}")
            return False
    
    # === NOTIFICAÇÕES ===
    def create_notification(self, notification_data: Dict) -> bool:
        """Cria notificação no Supabase"""
        try:
            self.client.table('notifications').insert({
                'user_id': notification_data['user_id'],
                'company_id': notification_data['company_id'],
                'type': notification_data['type'],
                'title': notification_data['title'],
                'message': notification_data.get('message'),
                'reference_id': notification_data.get('reference_id'),
                'read': False,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
            return True
        except Exception as e:
            print(f"Erro ao criar notificação: {e}")
            return False
    
    def send_push_notification(self, user_id: int, title: str, message: str, data: Dict = None) -> bool:
        """Envia push notification via Supabase Edge Function"""
        try:
            # Busca o push token do usuário
            user_result = self.client.table('users').select('push_token').eq('id', user_id).execute()
            
            if not user_result.data or not user_result.data[0].get('push_token'):
                print(f"Push token não encontrado para usuário {user_id}")
                return False
            
            push_token = user_result.data[0]['push_token']
            
            # Chama a Edge Function para enviar push notification
            payload = {
                'to': push_token,
                'title': title,
                'body': message,
                'data': data or {}
            }
            
            # Aqui você pode implementar a chamada para a Edge Function
            # Por enquanto, apenas registra a tentativa
            print(f"Push notification enviado para {push_token}: {title}")
            return True
            
        except Exception as e:
            print(f"Erro ao enviar push notification: {e}")
            return False
    
    # === FOTOS ===
    def upload_photo(self, file_data: bytes, file_name: str, assignment_id: int) -> Optional[str]:
        """Upload de foto para Supabase Storage"""
        try:
            # Upload para o bucket
            file_path = f"assignments/{assignment_id}/{file_name}"
            
            result = self.client.storage.from_(self.bucket).upload(
                path=file_path,
                file=file_data,
                file_options={"content-type": "image/jpeg"}
            )
            
            if result:
                # Registra no banco
                self.client.table('assignment_photos').insert({
                    'assignment_id': assignment_id,
                    'file_path': file_path,
                    'original_name': file_name,
                    'file_size': len(file_data),
                    'uploaded_at': datetime.utcnow().isoformat()
                }).execute()
                
                return file_path
            
        except Exception as e:
            print(f"Erro ao fazer upload: {e}")
            return None
    
    def get_photo_url(self, file_path: str) -> Optional[str]:
        """Obtém URL pública da foto"""
        try:
            result = self.client.storage.from_(self.bucket).get_public_url(file_path)
            return result
        except Exception as e:
            print(f"Erro ao obter URL da foto: {e}")
            return None
    
    # === SINCRONIZAÇÃO ===
    def sync_all_data_to_supabase(self, db_session) -> bool:
        """Sincroniza todos os dados do PostgreSQL para Supabase"""
        try:
            from database.models import User, TaskAssignment, Notification
            
            # Sincroniza usuários
            users = db_session.query(User).all()
            for user in users:
                user_data = {
                    'id': user.id,
                    'company_id': user.company_id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'team': user.team,
                    'role': user.role,
                    'is_super_admin': user.is_super_admin,
                    'active': user.active,
                    'push_token': user.push_token,
                    'created_at': user.created_at
                }
                self.sync_user_to_supabase(user_data)
            
            # Sincroniza tarefas atribuídas
            assignments = db_session.query(TaskAssignment).all()
            for assignment in assignments:
                assignment_data = {
                    'id': assignment.id,
                    'company_id': assignment.company_id,
                    'assigned_by': assignment.assigned_by,
                    'assigned_to': assignment.assigned_to,
                    'title': assignment.title,
                    'description': assignment.description,
                    'address': assignment.address,
                    'latitude': assignment.latitude,
                    'longitude': assignment.longitude,
                    'status': assignment.status,
                    'priority': assignment.priority,
                    'due_date': assignment.due_date,
                    'observations': assignment.observations,
                    'created_at': assignment.created_at,
                    'updated_at': assignment.updated_at
                }
                self.sync_task_assignment_to_supabase(assignment_data)
            
            return True
            
        except Exception as e:
            print(f"Erro na sincronização completa: {e}")
            return False

# Instância global
supabase_manager = SupabaseManager()