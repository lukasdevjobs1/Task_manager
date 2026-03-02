"""
Utilitário para enviar Push Notifications via Firebase Cloud Messaging (FCM) API v1

Este módulo usa a API mais recente do FCM que requer autenticação OAuth2.

CONFIGURAÇÃO NECESSÁRIA:
1. No Firebase Console, vá em Configurações > Contas de serviço
2. Clique em "Gerar nova chave privada"
3. Salve o arquivo JSON baixado como 'firebase-credentials.json' na raiz do projeto
4. OU defina a variável de ambiente GOOGLE_APPLICATION_CREDENTIALS com o caminho do arquivo
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Escopo necessário para FCM
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

# Cache do token de acesso
_cached_credentials = None


def get_access_token(credentials_path: Optional[str] = None) -> Optional[str]:
    """
    Obtém um token de acesso OAuth2 para a API FCM v1.

    Args:
        credentials_path: Caminho para o arquivo de credenciais JSON

    Returns:
        Token de acesso ou None se falhar
    """
    global _cached_credentials

    # Determinar caminho das credenciais
    if not credentials_path:
        credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

    if not credentials_path:
        # Tentar caminhos padrão
        possible_paths = [
            'firebase-credentials.json',
            'firebase_credentials.json',
            'service-account.json',
            os.path.join(os.path.dirname(__file__), '..', 'firebase-credentials.json'),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                credentials_path = path
                break

    if not credentials_path or not os.path.exists(credentials_path):
        print("Erro: Arquivo de credenciais Firebase não encontrado")
        print("Baixe em: Firebase Console > Configurações > Contas de serviço > Gerar nova chave privada")
        return None

    try:
        # Usar credenciais em cache se ainda válidas
        if _cached_credentials and _cached_credentials.valid:
            return _cached_credentials.token

        # Carregar credenciais do arquivo
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=SCOPES
        )

        # Atualizar token se necessário
        if not credentials.valid:
            credentials.refresh(Request())

        _cached_credentials = credentials
        return credentials.token

    except Exception as e:
        print(f"Erro ao obter token de acesso: {e}")
        return None


def get_project_id(credentials_path: Optional[str] = None) -> Optional[str]:
    """Obtém o project_id do arquivo de credenciais."""
    if not credentials_path:
        credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

    if not credentials_path:
        possible_paths = [
            'firebase-credentials.json',
            'firebase_credentials.json',
            'service-account.json',
            os.path.join(os.path.dirname(__file__), '..', 'firebase-credentials.json'),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                credentials_path = path
                break

    if not credentials_path or not os.path.exists(credentials_path):
        return None

    try:
        with open(credentials_path, 'r') as f:
            data = json.load(f)
            return data.get('project_id')
    except Exception as e:
        print(f"Erro ao ler project_id: {e}")
        return None


def send_push_notification(
    token: str,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None,
    credentials_path: Optional[str] = None
) -> bool:
    """
    Envia uma notificação push para um dispositivo específico usando FCM v1.

    Args:
        token: Token FCM do dispositivo (push_token do usuário)
        title: Título da notificação
        body: Corpo/mensagem da notificação
        data: Dados extras para enviar com a notificação
        credentials_path: Caminho para o arquivo de credenciais JSON

    Returns:
        True se enviou com sucesso, False caso contrário
    """
    if not token:
        print("Erro: Token do dispositivo não fornecido")
        return False

    # Obter token de acesso
    access_token = get_access_token(credentials_path)
    if not access_token:
        return False

    # Obter project_id
    project_id = get_project_id(credentials_path)
    if not project_id:
        print("Erro: project_id não encontrado nas credenciais")
        return False

    # URL da API v1
    url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Payload no formato da API v1
    message = {
        "token": token,
        "notification": {
            "title": title,
            "body": body
        },
        "android": {
            "priority": "high",
            "notification": {
                "sound": "default",
                "click_action": "FLUTTER_NOTIFICATION_CLICK",
                "channel_id": "task_channel"
            }
        }
    }

    if data:
        # Converter todos os valores para string (requisito da API)
        message["data"] = {k: str(v) for k, v in data.items()}

    payload = {"message": message}

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            print(f"Notificação enviada com sucesso para {token[:20]}...")
            return True
        else:
            print(f"Erro ao enviar notificação: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Erro ao enviar notificação: {e}")
        return False


def send_push_to_multiple(
    tokens: list,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None,
    credentials_path: Optional[str] = None
) -> Dict[str, int]:
    """
    Envia notificação push para múltiplos dispositivos.

    Args:
        tokens: Lista de tokens FCM
        title: Título da notificação
        body: Corpo/mensagem da notificação
        data: Dados extras
        credentials_path: Caminho para credenciais

    Returns:
        Dict com contagem de sucessos e falhas
    """
    results = {"success": 0, "failure": 0}

    for token in tokens:
        if send_push_notification(token, title, body, data, credentials_path):
            results["success"] += 1
        else:
            results["failure"] += 1

    return results


def notify_task_assigned(
    user_push_token: str,
    task_id: int,
    task_title: str,
    assigned_by_name: str,
    server_key: Optional[str] = None  # Mantido para compatibilidade, mas ignorado
) -> bool:
    """
    Envia notificação quando uma tarefa é atribuída a um técnico.

    Args:
        user_push_token: Token FCM do técnico
        task_id: ID da tarefa
        task_title: Título da tarefa
        assigned_by_name: Nome de quem atribuiu
        server_key: Ignorado (mantido para compatibilidade)

    Returns:
        True se enviou com sucesso
    """
    title = "Nova Tarefa Atribuída"
    body = f"{assigned_by_name} atribuiu uma nova tarefa: {task_title}"

    data = {
        "type": "task_assigned",
        "task_id": str(task_id),
        "click_action": "FLUTTER_NOTIFICATION_CLICK"
    }

    return send_push_notification(
        token=user_push_token,
        title=title,
        body=body,
        data=data
    )


def notify_task_status_changed(
    user_push_token: str,
    task_id: int,
    task_title: str,
    new_status: str,
    server_key: Optional[str] = None  # Mantido para compatibilidade, mas ignorado
) -> bool:
    """
    Envia notificação quando o status de uma tarefa muda.

    Args:
        user_push_token: Token FCM do usuário
        task_id: ID da tarefa
        task_title: Título da tarefa
        new_status: Novo status da tarefa
        server_key: Ignorado (mantido para compatibilidade)

    Returns:
        True se enviou com sucesso
    """
    status_display = {
        "em_andamento": "Em Andamento",
        "in_progress": "Em Andamento",
        "concluida": "Concluída",
        "completed": "Concluída",
        "pending": "Pendente",
        "pendente": "Pendente"
    }.get(new_status, new_status)

    title = "Tarefa Atualizada"
    body = f"A tarefa '{task_title}' foi marcada como {status_display}"

    data = {
        "type": "task_status_changed",
        "task_id": str(task_id),
        "new_status": new_status,
        "click_action": "FLUTTER_NOTIFICATION_CLICK"
    }

    return send_push_notification(
        token=user_push_token,
        title=title,
        body=body,
        data=data
    )


if __name__ == "__main__":
    print("=" * 50)
    print("Push Notification Utility (FCM API v1)")
    print("=" * 50)
    print()
    print("CONFIGURAÇÃO:")
    print("1. Acesse: Firebase Console > Configurações > Contas de serviço")
    print("2. Clique em 'Gerar nova chave privada'")
    print("3. Salve como 'firebase-credentials.json' na raiz do projeto")
    print()

    # Verificar se credenciais existem
    cred_path = None
    for path in ['firebase-credentials.json', 'firebase_credentials.json', 'service-account.json']:
        if os.path.exists(path):
            cred_path = path
            break

    if cred_path:
        print(f"✅ Credenciais encontradas: {cred_path}")
        project_id = get_project_id(cred_path)
        if project_id:
            print(f"✅ Project ID: {project_id}")

        # Testar obtenção de token
        token = get_access_token(cred_path)
        if token:
            print(f"✅ Token de acesso obtido com sucesso")
        else:
            print("❌ Falha ao obter token de acesso")
    else:
        print("❌ Arquivo de credenciais não encontrado")
        print()
        print("Baixe o arquivo em:")
        print("Firebase Console > Configurações > Contas de serviço > Gerar nova chave privada")
