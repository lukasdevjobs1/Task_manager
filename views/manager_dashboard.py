"""
Dashboard Avançado para Gerentes - Métricas Completas de Desempenho
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import re
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentication import require_login, get_current_user, is_admin
from database.supabase_only_connection import db


def extract_materials_metrics(materials_text):
    """Extrai métricas de materiais do texto."""
    if not materials_text:
        return {'ctos': 0, 'ceos': 0, 'cabo_metros': 0}
    
    text = materials_text.lower()
    
    # CTOs
    cto_match = re.findall(r'(\d+)\s*cto', text)
    ctos = sum(int(x) for x in cto_match) if cto_match else 0
    
    # CEOs
    ceo_match = re.findall(r'(\d+)\s*ceo', text)
    ceos = sum(int(x) for x in ceo_match) if ceo_match else 0
    
    # Cabo em metros
    cabo_match = re.findall(r'(\d+)\s*m', text)
    cabo_metros = sum(int(x) for x in cabo_match) if cabo_match else 0
    
    return {'ctos': ctos, 'ceos': ceos, 'cabo_metros': cabo_metros}


def get_team_performance(company_id, team_filter=None):
    """Retorna métricas de desempenho por equipe."""
    users = db.get_all_users(company_id)
    assignments = db.get_task_assignments(company_id)
    
    team_stats = {}
    
    for user in users:
        if user['role'] == 'admin':
            continue
            
        team = user['team']
        if team_filter and team != team_filter:
            continue
        
        if team not in team_stats:
            team_stats[team] = {
                'members': [],
                'total_tasks': 0,
                'pending': 0,
                'in_progress': 0,
                'completed': 0,
                'ctos': 0,
                'ceos': 0,
                'cabo_metros': 0
            }
        
        user_assignments = [a for a in assignments if a.get('assigned_to') == user['id']]
        
        # Métricas do usuário
        user_metrics = {
            'name': user['full_name'],
            'id': user['id'],
            'total': len(user_assignments),
            'pending': len([a for a in user_assignments if a.get('status') == 'pendente']),
            'in_progress': len([a for a in user_assignments if a.get('status') == 'em_andamento']),
            'completed': len([a for a in user_assignments if a.get('status') == 'concluida']),
            'ctos': 0,
            'ceos': 0,
            'cabo_metros': 0
        }
        
        # Extrair materiais por usuário
        for assignment in user_assignments:
            if assignment.get('status') == 'concluida' and assignment.get('materials'):
                metrics = extract_materials_metrics(assignment['materials'])
                user_metrics['ctos'] += metrics['ctos']
                user_metrics['ceos'] += metrics['ceos']
                user_metrics['cabo_metros'] += metrics['cabo_metros']
        
        team_stats[team]['members'].append(user_metrics)
        team_stats[team]['total_tasks'] += user_metrics['total']
        team_stats[team]['pending'] += user_metrics['pending']
        team_stats[team]['in_progress'] += user_metrics['in_progress']
        team_stats[team]['completed'] += user_metrics['completed']
        team_stats[team]['ctos'] += user_metrics['ctos']
        team_stats[team]['ceos'] += user_metrics['ceos']
        team_stats[team]['cabo_metros'] += user_metrics['cabo_metros']
    
    return team_stats


def render_manager_dashboard():
    """Renderiza dashboard avançado para gerentes."""
    require_login()
    user = get_current_user()
    
    if not is_admin():
        st.error("Acesso restrito a gerentes")
        return
    
    st.title("📊 Dashboard Gerencial - Métricas de Desempenho")
    st.markdown(f"**Gerente:** {user['full_name']} | **Empresa:** {user['company_name']}")
    st.markdown("---")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        team_filter = st.selectbox("Filtrar por Equipe", ["Todas", "fusao", "infraestrutura"])
    with col2:
        period = st.selectbox("Período", ["Hoje", "Esta Semana", "Este Mês", "Todos"])
    
    team_filter = None if team_filter == "Todas" else team_filter
    
    # Obter dados
    team_stats = get_team_performance(user['company_id'], team_filter)
    all_assignments = db.get_task_assignments(user['company_id'])
    
    # === MÉTRICAS GERAIS ===
    st.header("📈 Visão Geral")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_tasks = sum(t['total_tasks'] for t in team_stats.values())
    total_completed = sum(t['completed'] for t in team_stats.values())
    total_pending = sum(t['pending'] for t in team_stats.values())
    total_in_progress = sum(t['in_progress'] for t in team_stats.values())
    
    with col1:
        st.metric("Total de Tarefas", total_tasks)
    with col2:
        st.metric("Concluídas", total_completed, delta=f"{(total_completed/total_tasks*100):.1f}%" if total_tasks > 0 else "0%")
    with col3:
        st.metric("Em Andamento", total_in_progress)
    with col4:
        st.metric("Pendentes", total_pending)
    
    st.markdown("---")
    
    # === MÉTRICAS DE MATERIAIS ===
    st.header("🔧 Materiais Utilizados")
    
    col1, col2, col3 = st.columns(3)
    
    total_ctos = sum(t['ctos'] for t in team_stats.values())
    total_ceos = sum(t['ceos'] for t in team_stats.values())
    total_cabo = sum(t['cabo_metros'] for t in team_stats.values())
    
    with col1:
        st.metric("CTOs Instaladas", total_ctos)
    with col2:
        st.metric("CEOs Instaladas", total_ceos)
    with col3:
        st.metric("Cabo Lançado (m)", total_cabo)
    
    st.markdown("---")
    
    # === DESEMPENHO POR EQUIPE ===
    st.header("👥 Desempenho por Equipe")
    
    for team_name, stats in team_stats.items():
        with st.expander(f"🔹 Equipe {team_name.capitalize()} - {len(stats['members'])} membros", expanded=True):
            
            # Métricas da equipe
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Tarefas", stats['total_tasks'])
            with col2:
                st.metric("Concluídas", stats['completed'])
            with col3:
                st.metric("CTOs", stats['ctos'])
            with col4:
                st.metric("Cabo (m)", stats['cabo_metros'])
            
            # Gráfico de status
            if stats['total_tasks'] > 0:
                fig = go.Figure(data=[go.Pie(
                    labels=['Concluídas', 'Em Andamento', 'Pendentes'],
                    values=[stats['completed'], stats['in_progress'], stats['pending']],
                    hole=.3,
                    marker_colors=['#4CAF50', '#2196F3', '#FFC107']
                )])
                fig.update_layout(height=300, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
            
            # Tabela de membros
            st.subheader("Desempenho Individual")
            
            members_df = pd.DataFrame(stats['members'])
            if not members_df.empty:
                members_df = members_df.rename(columns={
                    'name': 'Nome',
                    'total': 'Total',
                    'completed': 'Concluídas',
                    'in_progress': 'Em Andamento',
                    'pending': 'Pendentes',
                    'ctos': 'CTOs',
                    'ceos': 'CEOs',
                    'cabo_metros': 'Cabo (m)'
                })
                
                # Calcular taxa de conclusão
                members_df['Taxa %'] = (members_df['Concluídas'] / members_df['Total'] * 100).fillna(0).round(1)
                
                st.dataframe(
                    members_df[['Nome', 'Total', 'Concluídas', 'Em Andamento', 'Pendentes', 'Taxa %', 'CTOs', 'CEOs', 'Cabo (m)']],
                    use_container_width=True,
                    hide_index=True
                )
    
    st.markdown("---")
    
    # === RANKING DE PRODUTIVIDADE ===
    st.header("🏆 Ranking de Produtividade")
    
    all_members = []
    for team_stats_data in team_stats.values():
        all_members.extend(team_stats_data['members'])
    
    if all_members:
        ranking_df = pd.DataFrame(all_members)
        ranking_df = ranking_df.sort_values('completed', ascending=False).head(10)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top 10 - Tarefas Concluídas")
            for idx, row in ranking_df.iterrows():
                st.markdown(f"**{row['name']}**: {row['completed']} tarefas")
        
        with col2:
            st.subheader("Top 10 - CTOs Instaladas")
            ranking_ctos = ranking_df.sort_values('ctos', ascending=False).head(10)
            for idx, row in ranking_ctos.iterrows():
                st.markdown(f"**{row['name']}**: {row['ctos']} CTOs")
    
    st.markdown("---")
    
    # === TAREFAS RECENTES ===
    st.header("📋 Tarefas Recentes")
    
    recent_tasks = sorted(all_assignments, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
    
    for task in recent_tasks:
        status_icon = {"pendente": "🟡", "em_andamento": "🔵", "concluida": "🟢"}.get(task['status'], "⚪")
        
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"{status_icon} **{task['title']}**")
        with col2:
            assignee = task.get('assigned_to_user', {})
            if isinstance(assignee, dict):
                st.caption(f"Para: {assignee.get('full_name', 'N/A')}")
        with col3:
            if st.button("Ver", key=f"recent_{task['id']}"):
                st.session_state["selected_assignment_id"] = task["id"]
                st.session_state["current_page"] = "assignment_details"
                st.rerun()
        
        st.markdown("---")


if __name__ == "__main__":
    render_manager_dashboard()
