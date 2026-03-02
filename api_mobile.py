from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from datetime import datetime
import os
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY
from database.supabase_only_connection import db
import bcrypt

app = Flask(__name__)
CORS(app)

# Configuração Supabase - usar service key se disponível
supabase_key = SUPABASE_SERVICE_KEY if SUPABASE_SERVICE_KEY else SUPABASE_KEY
supabase: Client = create_client(SUPABASE_URL, supabase_key)

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
        
        # Usar a função de autenticação do banco
        user = db.authenticate_user(username, password)
        
        if user:
            result = {
                'success': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'team': user['team'],
                    'role': user['role'],
                    'company_id': user['company_id'],
                    'company_name': user['company_name']
                }
            }
            print(f"Login bem-sucedido: {result}")
            return jsonify(result)
        else:
            print("Credenciais inválidas")
            return jsonify({'success': False, 'message': 'Credenciais inválidas'})
            
    except Exception as e:
        print(f"Erro no login: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/users/<int:user_id>/push-token', methods=['PUT'])
def update_push_token(user_id):
    try:
        data = request.json
        push_token = data.get('push_token')
        
        # Atualizar no Supabase via db
        response = supabase.table('users').update({
            'push_token': push_token
        }).eq('id', user_id).execute()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/tasks/<int:user_id>', methods=['GET'])
def get_user_tasks(user_id):
    try:
        # Buscar usuário para obter company_id
        user = db.get_user_by_id(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'})
        
        # Buscar tarefas do usuário
        tasks = db.get_task_assignments(user['company_id'], user_id)
        
        return jsonify({'success': True, 'tasks': tasks})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/tasks/<int:task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    try:
        data = request.json
        new_status = data.get('status')
        notes = data.get('notes', '')
        
        # Atualizar status usando db
        success, message = db.update_task_status(task_id, new_status, notes)
        
        if success:
            # Buscar tarefa para criar notificação
            task = db.get_task_assignment_by_id(task_id)
            if task:
                status_messages = {
                    'em_andamento': 'iniciou',
                    'concluida': 'concluiu',
                    'pendente': 'atualizou'
                }
                
                # Criar notificação para o gerente
                db.create_notification(
                    user_id=task['assigned_by'],
                    company_id=task['company_id'],
                    type='task_updated',
                    title='Tarefa Atualizada',
                    message=f"A tarefa '{task['title']}' foi {status_messages.get(new_status, 'atualizada')}",
                    reference_id=task_id
                )
        
        return jsonify({'success': success, 'message': message})
        
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
        
        # Upload para Supabase Storage (implementar se necessário)
        # Por enquanto, salvar localmente
        upload_folder = 'uploads'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        file_path = os.path.join(upload_folder, file_name)
        file.save(file_path)
        
        # Registrar no banco
        photo_url = f"/uploads/{file_name}"
        success, message = db.create_assignment_photo(task_id, photo_url, file_path, file.filename)
        
        if success:
            return jsonify({
                'success': True, 
                'photo_url': photo_url,
                'file_path': file_path
            })
        else:
            return jsonify({'success': False, 'message': message})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/tasks/<int:task_id>/photos', methods=['GET'])
def get_task_photos(task_id):
    try:
        photos = db.get_assignment_photos(task_id)
        
        return jsonify({'success': True, 'photos': photos})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/notifications/<int:user_id>', methods=['GET'])
def get_user_notifications(user_id):
    try:
        notifications = db.get_notifications(user_id)
        
        return jsonify({'success': True, 'notifications': notifications})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    try:
        # Buscar notificação para obter user_id
        notification = supabase.table('notifications').select('user_id').eq('id', notification_id).execute()
        if not notification.data:
            return jsonify({'success': False, 'message': 'Notificação não encontrada'})
        
        user_id = notification.data[0]['user_id']
        success = db.mark_notification_as_read(notification_id, user_id)
        
        return jsonify({'success': success})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})