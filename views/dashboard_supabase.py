"""
Dashboard simplificado para Supabase - Sistema de Gerenciamento de Tarefas ISP v2.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
import re
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentication import require_login, get_current_user, is_admin
from database.supabase_only_connection import db


def extract_materials_metrics(materials_text):
    """Extrai métricas de materiais do texto."""
    if not materials_text:
        return {'ctos': 0, 'ceos': 0, 'cabo_metros': 0}
    
    text = materials_text.lower()
    cto_match = re.findall(r'(\d+)\s*cto', text)
    ctos = sum(int(x) for x in cto_match) if cto_match else 0
    ceo_match = re.findall(r'(\d+)\s*ceo', text)
    ceos = sum(int(x) for x in ceo_match) if ceo_match else 0
    cabo_match = re.findall(r'(\d+)\s*m', text)
    cabo_metros = sum(int(x) for x in cabo_match) if cabo_match else 0
    
    return {'ctos': ctos, 'ceos': ceos, 'cabo_metros': cabo_metros}


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


def render_assignment_card(assignment: dict, show_assignee: bool = False, card_index: int = 0):
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
        # Chave única usando ID da tarefa e índice do card
        unique_key = f"view_assign_{assignment['id']}_{card_index}_{show_assignee}"
        if st.button("Ver", key=unique_key):
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
            for idx, assignment in enumerate(filtered):
                render_assignment_card(assignment, show_assignee=False, card_index=idx)
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
        st.header("📊 Dashboard Interativo")
        
        # Obter todas as tarefas e usuários
        all_assignments = db.get_task_assignments(user["company_id"])
        all_users = db.get_all_users(user["company_id"])
        
        # Calcular métricas por equipe
        team_data = {}
        for user_data in all_users:
            if user_data['role'] == 'admin':
                continue
            
            team = user_data['team']
            if team not in team_data:
                team_data[team] = {'tarefas': 0, 'ctos': 0, 'ceos': 0, 'cabo': 0, 'completed': 0, 'pending': 0, 'in_progress': 0}
            
            user_assignments = [a for a in all_assignments if a.get('assigned_to') == user_data['id']]
            team_data[team]['tarefas'] += len(user_assignments)
            team_data[team]['completed'] += len([a for a in user_assignments if a.get('status') == 'concluida'])
            team_data[team]['pending'] += len([a for a in user_assignments if a.get('status') == 'pendente'])
            team_data[team]['in_progress'] += len([a for a in user_assignments if a.get('status') == 'em_andamento'])
            
            for assignment in user_assignments:
                if assignment.get('status') == 'concluida' and assignment.get('materials'):
                    metrics = extract_materials_metrics(assignment['materials'])
                    team_data[team]['ctos'] += metrics['ctos']
                    team_data[team]['ceos'] += metrics['ceos']
                    team_data[team]['cabo'] += metrics['cabo_metros']
        
        # Gráficos interativos
        col1, col2 = st.columns(2)
        
        with col1:
            fig_tasks = go.Figure(data=[
                go.Bar(name='Concluídas', x=list(team_data.keys()), y=[team_data[t]['completed'] for t in team_data], marker_color='#4CAF50'),
                go.Bar(name='Em Andamento', x=list(team_data.keys()), y=[team_data[t]['in_progress'] for t in team_data], marker_color='#2196F3'),
                go.Bar(name='Pendentes', x=list(team_data.keys()), y=[team_data[t]['pending'] for t in team_data], marker_color='#FFC107')
            ])
            fig_tasks.update_layout(title='Tarefas por Equipe', barmode='stack', height=300)
            st.plotly_chart(fig_tasks, use_container_width=True)
        
        with col2:
            fig_materials = go.Figure(data=[
                go.Bar(name='CTOs', x=list(team_data.keys()), y=[team_data[t]['ctos'] for t in team_data], marker_color='#FF5722'),
                go.Bar(name='CEOs', x=list(team_data.keys()), y=[team_data[t]['ceos'] for t in team_data], marker_color='#9C27B0')
            ])
            fig_materials.update_layout(title='CTOs e CEOs por Equipe', barmode='group', height=300)
            st.plotly_chart(fig_materials, use_container_width=True)
        
        fig_cabo = go.Figure(data=[
            go.Bar(x=list(team_data.keys()), y=[team_data[t]['cabo'] for t in team_data], marker_color='#00BCD4')
        ])
        fig_cabo.update_layout(title='Cabo Lançado por Equipe (metros)', height=300)
        st.plotly_chart(fig_cabo, use_container_width=True)
        
        st.subheader("📈 Totais Gerais")
        col1, col2, col3, col4 = st.columns(4)
        
        total_tasks = sum(t['tarefas'] for t in team_data.values())
        total_ctos = sum(t['ctos'] for t in team_data.values())
        total_ceos = sum(t['ceos'] for t in team_data.values())
        total_cabo = sum(t['cabo'] for t in team_data.values())
        
        with col1:
            st.metric("Total de Tarefas", total_tasks)
        with col2:
            st.metric("🔧 CTOs", total_ctos)
        with col3:
            st.metric("📦 CEOs", total_ceos)
        with col4:
            st.metric("📏 Cabo (m)", total_cabo)
        
        # Tabela detalhada por usuário
        st.subheader("👥 Desempenho Individual")
        
        user_details = []
        for user_data in all_users:
            if user_data['role'] == 'admin':
                continue
            
            user_assignments = [a for a in all_assignments if a.get('assigned_to') == user_data['id']]
            completed = len([a for a in user_assignments if a.get('status') == 'concluida'])
            
            user_ctos = 0
            user_ceos = 0
            user_cabo = 0
            for assignment in user_assignments:
                if assignment.get('status') == 'concluida' and assignment.get('materials'):
                    metrics = extract_materials_metrics(assignment['materials'])
                    user_ctos += metrics['ctos']
                    user_ceos += metrics['ceos']
                    user_cabo += metrics['cabo_metros']
            
            user_details.append({
                'Nome': user_data['full_name'],
                'Equipe': user_data['team'].capitalize(),
                'Tarefas': len(user_assignments),
                'Concluídas': completed,
                'CTOs': user_ctos,
                'CEOs': user_ceos,
                'Cabo (m)': user_cabo
            })
        
        if user_details:
            df_users = pd.DataFrame(user_details)
            df_users = df_users.sort_values('Concluídas', ascending=False)
            st.dataframe(df_users, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.header("⚙️ Tarefas Atribuídas")

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

            for idx, assignment in enumerate(my_created_assignments):
                render_assignment_card(assignment, show_assignee=True, card_index=idx + 1000)
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
            
            for idx, assignment in enumerate(filtered_assignments[:10]):  # Limita a 10 para performance
                render_assignment_card(assignment, show_assignee=True, card_index=idx + 2000)
                st.markdown("---")
                
            if len(filtered_assignments) > 10:
                st.info(f"Mostrando apenas as 10 primeiras tarefas. Total: {len(filtered_assignments)}")
        else:
            st.info("Nenhuma tarefa encontrada na empresa.")


if __name__ == "__main__":
    render_dashboard_page()