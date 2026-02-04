"""
Dashboard simplificado para Supabase - Sistema de Gerenciamento de Tarefas ISP v2.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentication import require_login, get_current_user, is_admin
from database.supabase_only_connection import db


def get_assigned_to_me(user_id: int, company_id: int) -> list:
    """Retorna tarefas atribuídas ao usuário via Supabase."""
    return db.get_task_assignments(company_id, user_id)


def get_assigned_by_me(user_id: int, company_id: int) -> list:
    """Retorna tarefas que o admin atribuiu via Supabase."""
    try:
        assignments = db.get_task_assignments(company_id)
        return [a for a in assignments if a.get('assigned_by') == user_id]
    except Exception as e:
        print(f"Erro ao buscar tarefas atribuídas: {e}")
        return []


def get_company_users_stats(company_id: int) -> list:
    """Retorna estatísticas dos usuários da empresa."""
    try:
        users = db.get_all_users(company_id)
        assignments = db.get_task_assignments(company_id)
        
        user_stats = []
        for user in users:
            user_assignments = [a for a in assignments if a.get('assigned_to') == user['id']]
            pending = len([a for a in user_assignments if a.get('status') == 'pendente'])
            in_progress = len([a for a in user_assignments if a.get('status') == 'em_andamento'])
            completed = len([a for a in user_assignments if a.get('status') == 'concluida'])
            
            user_stats.append({
                'id': user['id'],
                'full_name': user['full_name'],
                'username': user['username'],
                'team': user['team'],
                'role': user['role'],
                'active': user['active'],
                'total_tasks': len(user_assignments),
                'pending': pending,
                'in_progress': in_progress,
                'completed': completed
            })
        
        return user_stats
    except Exception as e:
        print(f"Erro ao obter estatísticas: {e}")
        return []


def render_assignment_card(assignment: dict, show_assignee: bool = False):
    """Renderiza um card de tarefa atribuída."""
    status_labels = {
        "pendente": ("🟡", "Pendente"),
        "em_andamento": ("🔵", "Em Andamento"),
        "concluida": ("🟢", "Concluída"),
    }
    priority_labels = {
        "baixa": "Baixa",
        "media": "Média",
        "alta": "Alta",
    }

    icon, status_text = status_labels.get(assignment["status"], ("⚪", assignment["status"]))
    priority_text = priority_labels.get(assignment["priority"], assignment["priority"])

    col1, col2, col3 = st.columns([4, 2, 1])
    with col1:
        st.markdown(f"**{icon} {assignment['title']}**")
        if show_assignee:
            st.caption(f"Para: {assignment.get('assigned_to_user', {}).get('full_name', '')}")
        else:
            st.caption(f"De: {assignment.get('assigned_by_user', {}).get('full_name', '')}")
    with col2:
        st.caption(f"Prioridade: {priority_text}")
        st.caption(f"Status: {status_text}")
    with col3:
        if st.button("Ver", key=f"view_assign_{assignment['id']}"):
            st.session_state["selected_assignment_id"] = assignment["id"]
            st.session_state["current_page"] = "assignment_details"
            st.rerun()


def render_dashboard_page():
    """Renderiza a página do dashboard simplificado para Supabase."""
    require_login()
    user = get_current_user()

    st.title("Dashboard de Produtividade")

    # Informações do usuário
    st.markdown(f"**Usuário:** {user['full_name']} | **Equipe:** {user['team'].capitalize()}")
    st.markdown("---")

    # Seção: Tarefas Atribuídas a Mim
    st.header("📝 Tarefas Atribuídas a Mim")

    my_assignments = get_assigned_to_me(user["id"], user["company_id"])
    if my_assignments:
        # Filtros de status
        status_filter = st.selectbox(
            "Filtrar por status",
            ["Todos", "pendente", "em_andamento", "concluida"],
            key="filter_my_assignments",
        )
        
        filtered = my_assignments
        if status_filter != "Todos":
            filtered = [a for a in my_assignments if a["status"] == status_filter]

        if filtered:
            for assignment in filtered:
                render_assignment_card(assignment, show_assignee=False)
                st.markdown("---")
        else:
            st.info(f"Nenhuma tarefa com status '{status_filter}'.")

        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            pending = len([a for a in my_assignments if a["status"] == "pendente"])
            st.metric("Pendentes", pending)
        with col2:
            in_progress = len([a for a in my_assignments if a["status"] == "em_andamento"])
            st.metric("Em Andamento", in_progress)
        with col3:
            completed = len([a for a in my_assignments if a["status"] == "concluida"])
            st.metric("Concluídas", completed)
    else:
        st.info("Nenhuma tarefa atribuída a você.")

    # Seção Admin - Visão Geral
    if is_admin():
        st.markdown("---")
        st.header("⚙️ Visão Geral (Admin)")

        # Tarefas que eu atribuí
        st.subheader("Tarefas que Atribuí")
        my_created_assignments = get_assigned_by_me(user["id"], user["company_id"])
        if my_created_assignments:
            col1, col2, col3 = st.columns(3)
            with col1:
                a_pending = len([a for a in my_created_assignments if a["status"] == "pendente"])
                st.metric("Pendentes", a_pending)
            with col2:
                a_in_progress = len([a for a in my_created_assignments if a["status"] == "em_andamento"])
                st.metric("Em Andamento", a_in_progress)
            with col3:
                a_completed = len([a for a in my_created_assignments if a["status"] == "concluida"])
                st.metric("Concluídas", a_completed)

            for assignment in my_created_assignments:
                render_assignment_card(assignment, show_assignee=True)
                st.markdown("---")
        else:
            st.info("Você ainda não atribuiu nenhuma tarefa.")
        
        # Todas as tarefas da empresa
        st.subheader("Todas as Tarefas da Empresa")
        all_assignments = db.get_task_assignments(user["company_id"])
        
        if all_assignments:
            # Filtro por status
            status_filter = st.selectbox(
                "Filtrar por status",
                ["Todos", "pendente", "em_andamento", "concluida"],
                key="filter_all_assignments"
            )
            
            filtered_assignments = all_assignments
            if status_filter != "Todos":
                filtered_assignments = [a for a in all_assignments if a["status"] == status_filter]
            
            st.write(f"Mostrando {len(filtered_assignments)} de {len(all_assignments)} tarefas")
            
            for assignment in filtered_assignments[:10]:  # Limita a 10 para performance
                render_assignment_card(assignment, show_assignee=True)
                st.markdown("---")
                
            if len(filtered_assignments) > 10:
                st.info(f"Mostrando apenas as 10 primeiras tarefas. Total: {len(filtered_assignments)}")
        else:
            st.info("Nenhuma tarefa encontrada na empresa.")


if __name__ == "__main__":
    render_dashboard_page()