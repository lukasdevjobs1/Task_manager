from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Configuração Supabase
SUPABASE_URL = "https://ntatxgsykdnsfqxwnz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YXRreGdzeWtkbnNmcnF4d256Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjIwNzEsImV4cCI6MjA4NDAzODA3MX0.wmv7xL8z-1D5OYmOzDr-RUzFAgFBbWxMrJk7TMSFv4M"
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
        
        response = supabase.table('users').select('*').ilike('username', username).eq('active', True).execute()
        
        if response.data:
            user = response.data[0]
            print(f"Usuário encontrado: {user['username']}")
            
            # Verificação simples de senha para teste
            if password == '123456':
                result = {
                    'success': True,
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'full_name': user['full_name'],
                        'team': user['team'],
                        'role': user['role']
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
        
        response = supabase.table('users').update({
            'push_token': push_token
        }).eq('id', user_id).execute()
        
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
        notes = data.get('notes', '')
        
        update_data = {
            'status': new_status,
            'notes': notes,
            'updated_at': datetime.now().isoformat()
        }
        
        if new_status == 'em_andamento':
            update_data['started_at'] = datetime.now().isoformat()
        elif new_status == 'concluida':
            update_data['completed_at'] = datetime.now().isoformat()
        
        response = supabase.table('task_assignments').update(update_data).eq('id', task_id).execute()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    print("API rodando em: http://192.168.1.4:5000")
    print("Endpoints disponíveis:")
    print("- POST /api/login")
    print("- PUT /api/users/<user_id>/push-token")
    print("- GET /api/tasks/<user_id>")
    print("- PUT /api/tasks/<task_id>/status")
    app.run(debug=True, host='0.0.0.0', port=5000)