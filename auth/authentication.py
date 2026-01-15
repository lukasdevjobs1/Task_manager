"""
Sistema de autenticação com bcrypt e gerenciamento de sessão Streamlit.
"""

import bcrypt
import streamlit as st
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import SessionLocal
from database.models import User, Company


def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Autentica um usuário pelo username e senha.
    Retorna dict com dados do usuário se válido, None caso contrário.
    """
    session = SessionLocal()
    try:
        user = session.query(User).join(Company).filter(User.username == username).first()
        if user and user.active and user.company.active and verify_password(password, user.password_hash):
            # Retorna um dicionário com todos os dados necessários
            return {
                "id": user.id,
                "company_id": user.company_id,
                "company_name": user.company.name,
                "username": user.username,
                "full_name": user.full_name,
                "team": user.team,
                "role": user.role,
                "is_super_admin": getattr(user, 'is_super_admin', False) or False,
            }
        return None
    finally:
        session.close()


def create_user(
    username: str,
    password: str,
    full_name: str,
    team: str,
    company_id: int,
    role: str = "user",
) -> tuple[bool, str]:
    """
    Cria um novo usuário no sistema.
    Retorna (sucesso, mensagem).
    """
    if len(password) < 6:
        return False, "A senha deve ter no mínimo 6 caracteres."

    session = SessionLocal()
    try:
        # Verifica se username já existe
        existing = session.query(User).filter(User.username == username).first()
        if existing:
            return False, "Nome de usuário já existe."

        # Cria novo usuário
        new_user = User(
            company_id=company_id,
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            team=team,
            role=role,
            active=True,
        )
        session.add(new_user)
        session.commit()
        return True, "Usuário criado com sucesso!"
    except Exception as e:
        session.rollback()
        return False, f"Erro ao criar usuário: {str(e)}"
    finally:
        session.close()


def update_password(user_id: int, new_password: str, company_id: int) -> tuple[bool, str]:
    """Atualiza a senha de um usuário (validando company_id)."""
    if len(new_password) < 6:
        return False, "A senha deve ter no mínimo 6 caracteres."

    session = SessionLocal()
    try:
        user = session.query(User).filter(
            User.id == user_id,
            User.company_id == company_id
        ).first()
        if not user:
            return False, "Usuário não encontrado."

        user.password_hash = hash_password(new_password)
        session.commit()
        return True, "Senha atualizada com sucesso!"
    except Exception as e:
        session.rollback()
        return False, f"Erro ao atualizar senha: {str(e)}"
    finally:
        session.close()


def toggle_user_status(user_id: int, company_id: int) -> tuple[bool, str]:
    """Ativa/desativa um usuário (validando company_id)."""
    session = SessionLocal()
    try:
        user = session.query(User).filter(
            User.id == user_id,
            User.company_id == company_id
        ).first()
        if not user:
            return False, "Usuário não encontrado."

        user.active = not user.active
        status = "ativado" if user.active else "desativado"
        session.commit()
        return True, f"Usuário {status} com sucesso!"
    except Exception as e:
        session.rollback()
        return False, f"Erro ao alterar status: {str(e)}"
    finally:
        session.close()


def get_all_users(company_id: int) -> list:
    """Retorna lista de usuários de uma empresa."""
    session = SessionLocal()
    try:
        users = session.query(User).filter(
            User.company_id == company_id
        ).order_by(User.full_name).all()
        # Converte para dicionários para evitar problemas de sessão
        return [
            {
                "id": u.id,
                "username": u.username,
                "full_name": u.full_name,
                "team": u.team,
                "role": u.role,
                "active": u.active,
                "created_at": u.created_at,
            }
            for u in users
        ]
    finally:
        session.close()


def get_user_by_id(user_id: int, company_id: int = None) -> Optional[dict]:
    """Retorna um usuário pelo ID (opcionalmente validando company_id)."""
    session = SessionLocal()
    try:
        query = session.query(User).filter(User.id == user_id)
        if company_id:
            query = query.filter(User.company_id == company_id)
        user = query.first()
        if user:
            return {
                "id": user.id,
                "company_id": user.company_id,
                "username": user.username,
                "full_name": user.full_name,
                "team": user.team,
                "role": user.role,
                "active": user.active,
                "created_at": user.created_at,
            }
        return None
    finally:
        session.close()


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
    """Retorna lista de todas as empresas."""
    session = SessionLocal()
    try:
        companies = session.query(Company).order_by(Company.name).all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "active": c.active,
                "created_at": c.created_at,
            }
            for c in companies
        ]
    finally:
        session.close()


def create_company(name: str, slug: str) -> tuple[bool, str, int]:
    """
    Cria uma nova empresa.
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

    session = SessionLocal()
    try:
        # Verifica se slug já existe
        existing = session.query(Company).filter(Company.slug == slug).first()
        if existing:
            return False, "Já existe uma empresa com este slug.", None

        new_company = Company(
            name=name.strip(),
            slug=slug.strip().lower(),
            active=True,
        )
        session.add(new_company)
        session.commit()
        return True, "Empresa criada com sucesso!", new_company.id
    except Exception as e:
        session.rollback()
        return False, f"Erro ao criar empresa: {str(e)}", None
    finally:
        session.close()


def toggle_company_status(company_id: int) -> tuple[bool, str]:
    """Ativa/desativa uma empresa."""
    session = SessionLocal()
    try:
        company = session.query(Company).filter(Company.id == company_id).first()
        if not company:
            return False, "Empresa não encontrada."

        company.active = not company.active
        status = "ativada" if company.active else "desativada"
        session.commit()
        return True, f"Empresa {status} com sucesso!"
    except Exception as e:
        session.rollback()
        return False, f"Erro ao alterar status: {str(e)}"
    finally:
        session.close()


def get_company_stats(company_id: int) -> dict:
    """Retorna estatísticas de uma empresa."""
    session = SessionLocal()
    try:
        from database.models import Task
        user_count = session.query(User).filter(User.company_id == company_id).count()
        task_count = session.query(Task).filter(Task.company_id == company_id).count()
        return {
            "users": user_count,
            "tasks": task_count,
        }
    finally:
        session.close()


def update_company(company_id: int, name: str = None, active: bool = None) -> tuple[bool, str]:
    """Atualiza dados de uma empresa."""
    session = SessionLocal()
    try:
        company = session.query(Company).filter(Company.id == company_id).first()
        if not company:
            return False, "Empresa não encontrada."

        if name is not None:
            company.name = name
        if active is not None:
            company.active = active

        session.commit()
        return True, "Empresa atualizada com sucesso!"
    except Exception as e:
        session.rollback()
        return False, f"Erro ao atualizar empresa: {str(e)}"
    finally:
        session.close()


def delete_company(company_id: int) -> tuple[bool, str]:
    """Exclui uma empresa e todos os seus dados."""
    session = SessionLocal()
    try:
        from database.models import Task, TaskPhoto

        company = session.query(Company).filter(Company.id == company_id).first()
        if not company:
            return False, "Empresa não encontrada."

        # Excluir fotos das tarefas
        task_ids = [t.id for t in session.query(Task).filter(Task.company_id == company_id).all()]
        if task_ids:
            session.query(TaskPhoto).filter(TaskPhoto.task_id.in_(task_ids)).delete(synchronize_session=False)

        # Excluir tarefas
        session.query(Task).filter(Task.company_id == company_id).delete(synchronize_session=False)

        # Excluir usuários
        session.query(User).filter(User.company_id == company_id).delete(synchronize_session=False)

        # Excluir empresa
        session.delete(company)
        session.commit()

        return True, "Empresa excluída com sucesso!"
    except Exception as e:
        session.rollback()
        return False, f"Erro ao excluir empresa: {str(e)}"
    finally:
        session.close()


def delete_user(user_id: int, company_id: int) -> tuple[bool, str]:
    """Exclui um usuário (validando company_id)."""
    session = SessionLocal()
    try:
        from database.models import Task, TaskPhoto

        user = session.query(User).filter(
            User.id == user_id,
            User.company_id == company_id
        ).first()

        if not user:
            return False, "Usuário não encontrado."

        # Excluir fotos das tarefas do usuário
        task_ids = [t.id for t in session.query(Task).filter(Task.user_id == user_id).all()]
        if task_ids:
            session.query(TaskPhoto).filter(TaskPhoto.task_id.in_(task_ids)).delete(synchronize_session=False)

        # Excluir tarefas do usuário
        session.query(Task).filter(Task.user_id == user_id).delete(synchronize_session=False)

        # Excluir usuário
        session.delete(user)
        session.commit()

        return True, "Usuário excluído com sucesso!"
    except Exception as e:
        session.rollback()
        return False, f"Erro ao excluir usuário: {str(e)}"
    finally:
        session.close()


def get_users_by_company(company_id: int) -> list:
    """Retorna lista de usuários de uma empresa específica."""
    session = SessionLocal()
    try:
        users = session.query(User).filter(
            User.company_id == company_id
        ).order_by(User.full_name).all()

        return [
            {
                "id": u.id,
                "username": u.username,
                "full_name": u.full_name,
                "team": u.team,
                "role": u.role,
                "active": u.active,
                "created_at": u.created_at,
            }
            for u in users
        ]
    finally:
        session.close()
