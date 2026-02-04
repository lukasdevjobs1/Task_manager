"""
Página de notificações in-app.
Lista notificações do usuário com status lida/não lida.
"""

import streamlit as st
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentication import require_login, get_current_user
from database.supabase_only_connection import db


def get_unread_count(user_id: int) -> int:
    """Retorna a contagem de notificações não lidas via Supabase."""
    return db.get_unread_count(user_id)


def get_notifications(user_id: int, limit: int = 50) -> list:
    """Retorna lista de notificações do usuário via Supabase."""
    return db.get_notifications(user_id)


def mark_as_read(notification_id: int) -> bool:
    """Marca uma notificação como lida via Supabase."""
    return db.mark_notification_as_read(notification_id, None)


def mark_all_as_read(user_id: int) -> int:
    """Marca todas as notificações do usuário como lidas via Supabase."""
    try:
        notifications = db.get_notifications(user_id, unread_only=True)
        count = 0
        for notif in notifications:
            if db.mark_notification_as_read(notif['id'], user_id):
                count += 1
        return count
    except Exception as e:
        print(f"Erro ao marcar notificações: {e}")
        return 0


def format_time_ago(dt: datetime) -> str:
    """Formata a diferença de tempo de forma legível."""
    now = datetime.utcnow()
    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return "agora mesmo"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"há {minutes} min"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"há {hours}h"
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f"há {days} dia(s)"
    else:
        return dt.strftime("%d/%m/%Y %H:%M")


def get_notification_icon(notification_type: str) -> str:
    """Retorna ícone baseado no tipo de notificação."""
    icons = {
        "task_assigned": "📋",
        "task_updated": "🔄",
        "task_completed": "✅",
    }
    return icons.get(notification_type, "🔔")


def render_notifications_page():
    """Renderiza a página de notificações."""
    require_login()
    user = get_current_user()

    st.title("Notificações")

    # Botão marcar todas como lidas
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Marcar todas como lidas", use_container_width=True):
            count = mark_all_as_read(user["id"])
            if count > 0:
                st.success(f"{count} notificação(ões) marcada(s) como lida(s).")
                st.rerun()
            else:
                st.info("Nenhuma notificação pendente.")

    st.markdown("---")

    # Listar notificações
    notifications = get_notifications(user["id"])

    if not notifications:
        st.info("Nenhuma notificação encontrada.")
        return

    for notif in notifications:
        icon = get_notification_icon(notif["type"])
        time_str = format_time_ago(notif["created_at"])
        read_style = "" if notif["read"] else "**"

        with st.container():
            col1, col2, col3 = st.columns([0.5, 5, 1.5])

            with col1:
                st.markdown(f"### {icon}")

            with col2:
                title_text = f"{read_style}{notif['title']}{read_style}"
                st.markdown(title_text)
                if notif["message"]:
                    st.caption(notif["message"])
                st.caption(f"🕐 {time_str}")

            with col3:
                if not notif["read"]:
                    if st.button("Marcar lida", key=f"read_{notif['id']}"):
                        mark_as_read(notif["id"])
                        st.rerun()

                if notif["reference_id"]:
                    if st.button("Ver tarefa", key=f"view_{notif['id']}"):
                        # Marca como lida ao visualizar
                        if not notif["read"]:
                            mark_as_read(notif["id"])
                        st.session_state["selected_assignment_id"] = notif["reference_id"]
                        st.session_state["current_page"] = "assignment_details"
                        st.rerun()

            st.markdown("---")
