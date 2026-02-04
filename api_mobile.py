from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from datetime import datetime
import os
from config import SUPABASE_URL, SUPABASE_KEY
from database.supabase_connection import supabase_manager
import bcrypt

app = Flask(__name__)
CORS(app)

# Configuração Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({'success': True, 'message': 'API funcionando!'})

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        response = supabase.table('users').select('username, full_name, role').eq('active', True).order('username').execute()
        return jsonify({'success': True, 'users': response.data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        print(f"Tentativa de login: {username}")
        
        # Buscar usuário no Supabase
        response = supabase.table('users').select('*').eq('username', username).eq('active', True).execute()
        
        if response.data:
            user = response.data[0]
            print(f"Usuário encontrado: {user['username']}")
            
            # Para teste, aceita senha '123456' para todos os usuários
            # Em produção, implementar verificação de hash bcrypt
            if password == '123456':
                result = {
                    'success': True,
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'full_name': user['full_name'],
                        'team': user['team'],
                        'role': user['role'],
                        'company_id': user['company_id']
                    }
                }
                print(f"Login bem-sucedido: {result}")
                return jsonify(result)
            else:
                print("Senha incorreta")
                return jsonify({'success': False, 'message': 'Senha incorreta'})
        else:
            print("Usuário não encontrado")
            return jsonify({'success': False, 'message': 'Usuário não encontrado'})
            
    except Exception as e:
        print(f"Erro no login: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/users/<int:user_id>/push-token', methods=['PUT'])
def update_push_token(user_id):
    try:
        data = request.json
        push_token = data.get('push_token')
        
        # Atualizar no Supabase
        response = supabase.table('users').update({
            'push_token': push_token
        }).eq('id', user_id).execute()
        
        # Usar o manager para sincronização
        supabase_manager.update_push_token(user_id, push_token)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/tasks/<int:user_id>', methods=['GET'])
def get_user_tasks(user_id):
    try:
        response = supabase.table('task_assignments').select(
            '*, assigned_by_user:users!task_assignments_assigned_by_fkey(full_name)'
        ).eq('assigned_to', user_id).order('created_at', desc=True).execute()
        
        return jsonify({'success': True, 'tasks': response.data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/tasks/<int:task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    try:
        data = request.json
        new_status = data.get('status')
        observations = data.get('observations', '')
        
        update_data = {
            'status': new_status,
            'observations': observations,
            'updated_at': datetime.now().isoformat()
        }
        
        # Atualizar timestamps baseado no status
        if new_status in ['in_progress', 'em_andamento']:
            update_data['started_at'] = datetime.now().isoformat()
        elif new_status in ['completed', 'concluida']:
            update_data['completed_at'] = datetime.now().isoformat()
        
        # Atualizar no Supabase
        response = supabase.table('task_assignments').update(update_data).eq('id', task_id).execute()
        
        # Usar manager para sincronização
        supabase_manager.update_task_status(task_id, new_status, observations)
        
        # Criar notificação para o gerente
        if response.data:
            task = response.data[0]
            status_messages = {
                'in_progress': 'iniciou',
                'em_andamento': 'iniciou', 
                'completed': 'concluiu',
                'concluida': 'concluiu',
                'pending': 'atualizou',
                'pendente': 'atualizou'
            }
            
            notification_data = {
                'user_id': task['assigned_by'],
                'company_id': task['company_id'],
                'type': 'task_updated',
                'title': 'Tarefa Atualizada',
                'message': f"A tarefa '{task['title']}' foi {status_messages.get(new_status, 'atualizada')}",
                'reference_id': task_id
            }
            supabase_manager.create_notification(notification_data)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"API rodando na porta: {port}")
    print("Endpoints disponíveis:")
    print("- POST /api/login")
    print("- PUT /api/users/<user_id>/push-token")
    print("- GET /api/tasks/<user_id>")
    print("- PUT /api/tasks/<task_id>/status")
    print("- POST /api/tasks/<task_id>/photos")
    print("- GET /api/tasks/<task_id>/photos")
    print("- GET /api/notifications/<user_id>")
    print("- PUT /api/notifications/<notification_id>/read")
    app.run(debug=False, host='0.0.0.0', port=port)

@app.route('/api/tasks/<int:task_id>/photos', methods=['POST'])
def upload_task_photo(task_id):
    try:
        if 'photo' not in request.files:
            return jsonify({'success': False, 'message': 'Nenhuma foto enviada'})
        
        file = request.files['photo']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Arquivo vazio'})
        
        # Gerar nome único para o arquivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        file_name = f"{timestamp}_{task_id}.{file_extension}"
        
        # Upload para Supabase Storage
        file_data = file.read()
        file_path = supabase_manager.upload_photo(file_data, file_name, task_id)
        
        if file_path:
            # Obter URL pública
            photo_url = supabase_manager.get_photo_url(file_path)
            
            return jsonify({
                'success': True, 
                'photo_url': photo_url,
                'file_path': file_path
            })
        else:
            return jsonify({'success': False, 'message': 'Erro no upload da foto'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/tasks/<int:task_id>/photos', methods=['GET'])
def get_task_photos(task_id):
    try:
        response = supabase.table('assignment_photos').select('*').eq('assignment_id', task_id).order('uploaded_at', desc=True).execute()
        
        photos = []
        for photo in response.data:
            photo_url = supabase_manager.get_photo_url(photo['file_path'])
            photos.append({
                'id': photo['id'],
                'url': photo_url,
                'original_name': photo['original_name'],
                'uploaded_at': photo['uploaded_at']
            })
        
        return jsonify({'success': True, 'photos': photos})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/notifications/<int:user_id>', methods=['GET'])
def get_user_notifications(user_id):
    try:
        response = supabase.table('notifications').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(50).execute()
        
        return jsonify({'success': True, 'notifications': response.data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    try:
        response = supabase.table('notifications').update({
            'read': True
        }).eq('id', notification_id).execute()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})