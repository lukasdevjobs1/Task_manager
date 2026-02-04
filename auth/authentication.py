"""
Sistema de autenticação com bcrypt e gerenciamento de sessão Streamlit.
"""

import bcrypt
import streamlit as st
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.supabase_only_connection import db


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Autentica um usuário pelo username e senha via Supabase.
    Retorna dict com dados do usuário se válido, None caso contrário.
    """
    return db.authenticate_user(username, password)


def create_user(
    username: str,
    password: str,
    full_name: str,
    team: str,
    company_id: int,
    role: str = "user",
) -> tuple[bool, str]:
    """
    Cria um novo usuário no sistema via Supabase.
    Retorna (sucesso, mensagem).
    """
    return db.create_user(username, password, full_name, team, company_id, role)


def update_password(user_id: int, new_password: str, company_id: int) -> tuple[bool, str]:
    """Atualiza a senha de um usuário via Supabase."""
    return db.update_password(user_id, new_password, company_id)


def toggle_user_status(user_id: int, company_id: int) -> tuple[bool, str]:
    """Ativa/desativa um usuário via Supabase."""
    return db.toggle_user_status(user_id, company_id)


def get_all_users(company_id: int) -> list:
    """Retorna lista de usuários de uma empresa via Supabase."""
    return db.get_all_users(company_id)


def get_user_by_id(user_id: int, company_id: int = None) -> Optional[dict]:
    """Retorna um usuário pelo ID via Supabase."""
    return db.get_user_by_id(user_id, company_id)


# ============ Funções de Sessão Streamlit ============


def login_user(user_data: dict) -> None:
    """Salva dados do usuário na sessão do Streamlit."""
    st.session_state["logged_in"] = True
    st.session_state["user_id"] = user_data["id"]
    st.session_state["company_id"] = user_data["company_id"]
    st.session_state["company_name"] = user_data["company_name"]
    st.session_state["username"] = user_data["username"]
    st.session_state["full_name"] = user_data["full_name"]
    st.session_state["team"] = user_data["team"]
    st.session_state["role"] = user_data["role"]
    st.session_state["is_super_admin"] = user_data.get("is_super_admin", False)


def logout_user() -> None:
    """Remove dados do usuário da sessão do Streamlit."""
    keys_to_remove = [
        "logged_in", "user_id", "company_id", "company_name",
        "username", "full_name", "team", "role", "is_super_admin"
    ]
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]


def get_current_user() -> Optional[dict]:
    """Retorna dados do usuário logado ou None."""
    if st.session_state.get("logged_in"):
        return {
            "id": st.session_state.get("user_id"),
            "company_id": st.session_state.get("company_id"),
            "company_name": st.session_state.get("company_name"),
            "username": st.session_state.get("username"),
            "full_name": st.session_state.get("full_name"),
            "team": st.session_state.get("team"),
            "role": st.session_state.get("role"),
            "is_super_admin": st.session_state.get("is_super_admin", False),
        }
    return None


def is_logged_in() -> bool:
    """Verifica se há usuário logado."""
    return st.session_state.get("logged_in", False)


def is_admin() -> bool:
    """Verifica se o usuário logado é admin."""
    return st.session_state.get("role") == "admin"


def is_super_admin() -> bool:
    """Verifica se o usuário logado é super admin (admin geral)."""
    return st.session_state.get("is_super_admin", False)


def require_login():
    """Decorator/função para exigir login em páginas."""
    if not is_logged_in():
        st.warning("Você precisa fazer login para acessar esta página.")
        st.stop()


def require_admin():
    """Decorator/função para exigir permissão de admin."""
    require_login()
    if not is_admin():
        st.error("Acesso negado. Esta página é restrita a administradores.")
        st.stop()


# ============ Funções de Gestão de Empresas ============


def get_all_companies() -> list:
    """Retorna lista de todas as empresas via Supabase."""
    return db.get_all_companies()


def create_company(name: str, slug: str) -> tuple[bool, str, int]:
    """
    Cria uma nova empresa via Supabase.
    Retorna (sucesso, mensagem, company_id).
    """
    if not name.strip():
        return False, "Nome da empresa é obrigatório.", None
    if not slug.strip():
        return False, "Slug é obrigatório.", None

    # Validar slug (apenas letras minúsculas, números e hífens)
    import re
    if not re.match(r'^[a-z0-9-]+$', slug):
        return False, "Slug deve conter apenas letras minúsculas, números e hífens.", None

    return db.create_company(name, slug)


def toggle_company_status(company_id: int) -> tuple[bool, str]:
    """Ativa/desativa uma empresa via Supabase."""
    return db.toggle_company_status(company_id)


def get_company_stats(company_id: int) -> dict:
    """Retorna estatísticas de uma empresa via Supabase."""
    try:
        users = db.get_all_users(company_id)
        tasks = db.get_task_assignments(company_id)
        return {
            "users": len(users),
            "tasks": len(tasks),
        }
    except Exception as e:
        print(f"Erro ao obter estatísticas: {e}")
        return {"users": 0, "tasks": 0}


def update_company(company_id: int, name: str = None, active: bool = None) -> tuple[bool, str]:
    """Atualiza dados de uma empresa via Supabase."""
    try:
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if active is not None:
            update_data['active'] = active
        
        if update_data:
            db.client.table('companies').update(update_data).eq('id', company_id).execute()
        
        return True, "Empresa atualizada com sucesso!"
    except Exception as e:
        return False, f"Erro ao atualizar empresa: {str(e)}"


def delete_company(company_id: int) -> tuple[bool, str]:
    """Exclui uma empresa via Supabase."""
    try:
        # Excluir empresa
        result = db.client.table('companies').delete().eq('id', company_id).execute()
        return True, "Empresa excluída com sucesso!"
    except Exception as e:
        return False, f"Erro ao excluir empresa: {str(e)}"


def delete_user(user_id: int, company_id: int) -> tuple[bool, str]:
    """Exclui um usuário via Supabase."""
    return db.delete_user(user_id, company_id)


def get_users_by_company(company_id: int) -> list:
    """Retorna lista de usuários de uma empresa específica via Supabase."""
    return db.get_all_users(company_id)
