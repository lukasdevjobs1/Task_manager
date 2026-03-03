"""
Dashboard simplificado para Supabase - Sistema de Gerenciamento de Tarefas ISP v2.0
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import sys
import os
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentication import re

def extract_materials_from_text(materials_text):
    """Extrai métricas de materiais do campo materials (texto livre)."""
    if not materials_text:
        return {'ctos': 0, 'ceos': 0, 'cabo_metros': 0}
    
    text = str(materials_text).lower()
    
    # CTOs
    cto_matches = re.findall(r'(\d+)\s*(?:cto|cts)', text)
    ctos = sum(int(x) for x in cto_matches) if cto_matches else 0
    
    # CEOs  
    ceo_matches = re.findall(r'(\d+)\s*(?:ceo|ces)', text)
    ceos = sum(int(x) for x in ceo_matches) if ceo_matches else 0
    
    # Cabo em metros
    cabo_matches = re.findall(r'(\d+)\s*(?:m|metro)', text)
    cabo_metros = sum(int(x) for x in cabo_matches) if cabo_matches else 0
    
    return {'ctos': ctos, 'ceos': ceos, 'cabo_metros': cabo_metros}quire_login, get_current_user, is_admin
from database.supabase_only_connection import db



def parse_date(date_str) -> datetime:
    """Converte string ISO para datetime."""
    if not date_str:
        return datetime.min
    try:
        return datetime.fromisoformat(str(date_str).replace('Z', '+00:00')).replace(tzinfo=None)
    except Exception:
        try:
            return datetime.strptime(str(date_str)[:19], '%Y-%m-%dT%H:%M:%S')
        except Exception:
            return datetime.min


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
            assignee = assignment.get('assigned_to_user')
            if assignee and isinstance(assignee, dict):
                st.caption(f"Para: {assignee.get('full_name', 'N/A')}")
            else:
                st.caption("Para: Caixa da Empresa")
        else:
            assigner = assignment.get('assigned_by_user', {})
            st.caption(f"De: {assigner.get('full_name', 'N/A') if isinstance(assigner, dict) else 'N/A'}")
    with col2:
        st.caption(f"Prioridade: {priority_text}")
        st.caption(f"Status: {status_text}")
    with col3:
        unique_key = f"view_assign_{assignment['id']}_{card_index}_{show_assignee}"
        if st.button("Ver", key=unique_key):
            st.session_state["selected_assignment_id"] = assignment["id"]
            st.session_state["current_page"] = "assignment_details"
            st.rerun()


def _build_detail_columns(tasks: list) -> list:
    """Retorna colunas para exibição de dataframe de tarefas."""
    desired = ['id', 'title', 'status', 'priority', 'empresa_nome', 'created_at']
    if not tasks:
        return desired
    return [c for c in desired if c in tasks[0]]


def render_dashboard_page():
    """Renderiza a página do dashboard simplificado para Supabase."""
    require_login()
    user = get_current_user()

    # Técnicos/colaboradores veem suas próprias tarefas atribuídas
    if not is_admin():
        st.header("📝 Tarefas Atribuídas a Mim")

        my_assignments = get_assigned_to_me(user["id"], user["company_id"])
        if my_assignments:
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

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Pendentes", len([a for a in my_assignments if a["status"] == "pendente"]))
            with col2:
                st.metric("Em Andamento", len([a for a in my_assignments if a["status"] == "em_andamento"]))
            with col3:
                st.metric("Concluídas", len([a for a in my_assignments if a["status"] == "concluida"]))
        else:
            st.info("Nenhuma tarefa atribuída a você.")
        return

    # ─── Dashboard Interativo (apenas admin/gerente) ──────────────────────────
    st.header("📊 Dashboard Interativo")

    # Carrega dados brutos
    all_assignments_raw = db.get_task_assignments(user["company_id"])
    all_users = db.get_all_users(user["company_id"])

    # ── Filtros globais ────────────────────────────────────────────────────
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        empresas_set = sorted({
            a.get('empresa_nome') for a in all_assignments_raw if a.get('empresa_nome')
        })
        empresa_filter = st.selectbox(
            "Empresa", ["Todas"] + list(empresas_set), key="dash_filter_empresa"
        )
    with col_f2:
        periodo = st.selectbox(
            "Período", ["Todos", "Hoje", "Esta Semana", "Este Mês"], key="dash_filter_periodo"
        )

    # Aplica filtros
    all_assignments = list(all_assignments_raw)
    if empresa_filter != "Todas":
        all_assignments = [a for a in all_assignments if a.get('empresa_nome') == empresa_filter]

    hoje = datetime.now().date()
    if periodo == "Hoje":
        all_assignments = [
            a for a in all_assignments
            if parse_date(a.get('created_at')).date() == hoje
        ]
    elif periodo == "Esta Semana":
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        all_assignments = [
            a for a in all_assignments
            if parse_date(a.get('created_at')).date() >= inicio_semana
        ]
    elif periodo == "Este Mês":
        all_assignments = [
            a for a in all_assignments
            if parse_date(a.get('created_at')).month == hoje.month
            and parse_date(a.get('created_at')).year == hoje.year
        ]

    # ── KPI Métricas ───────────────────────────────────────────────────────
    total = len(all_assignments)
    concluidas = len([a for a in all_assignments if a.get('status') == 'concluida'])
    em_andamento = len([a for a in all_assignments if a.get('status') == 'em_andamento'])
    pendentes = len([a for a in all_assignments if a.get('status') == 'pendente'])

    # Calcular materiais dos campos estruturados E do campo materials (texto)
    total_ctos = 0
    total_cx_emenda = 0 
    total_fibra = 0
    
    for a in all_assignments:
        # Campos estruturados
        total_ctos += a.get('quantidade_cto') or 0
        total_cx_emenda += a.get('quantidade_cx_emenda') or 0
        total_fibra += float(a.get('fibra_lancada') or 0)
        
        # Campo materials (texto livre)
        if a.get('materials'):
            materials_data = extract_materials_from_text(a['materials'])
            total_ctos += materials_data['ctos']
            total_fibra += materials_data['cabo_metros']

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total Tarefas", total)
    with kpi2:
        st.metric("Concluídas", concluidas)
    with kpi3:
        st.metric("Em Andamento", em_andamento)
    with kpi4:
        st.metric("Pendentes", pendentes)

    kpi_isp1, kpi_isp2, kpi_isp3 = st.columns(3)
    with kpi_isp1:
        st.metric("Total CTOs", int(total_ctos))
    with kpi_isp2:
        st.metric("Total Cx Emenda", int(total_cx_emenda))
    with kpi_isp3:
        st.metric("Fibra Lançada (m)", f"{total_fibra:.0f}")

    # ── Tabs ───────────────────────────────────────────────────────────────
    tab_geral, tab_empresa, tab_desempenho = st.tabs(
        ["📊 Geral", "🏢 Por Empresa", "👥 Desempenho"]
    )

    # ── TAB GERAL ──────────────────────────────────────────────────────────
    with tab_geral:
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            # Pizza de status (interativo)
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Concluída', 'Em Andamento', 'Pendente'],
                values=[concluidas, em_andamento, pendentes],
                marker=dict(colors=['#4CAF50', '#2196F3', '#FFC107']),
                textinfo='label+percent'
            )])
            fig_pie.update_layout(title='Distribuição de Status', height=350, showlegend=False)

            event_pie = st.plotly_chart(
                fig_pie, use_container_width=True,
                on_select="rerun", key="chart_status_pie"
            )

        with col_g2:
            # Barras empilhadas por equipe (interativo)
            team_data = {}
            for u in all_users:
                if u['role'] == 'admin':
                    continue
                team = u['team']
                if team not in team_data:
                    team_data[team] = {'concluida': 0, 'em_andamento': 0, 'pendente': 0}
                u_tasks = [a for a in all_assignments if a.get('assigned_to') == u['id']]
                team_data[team]['concluida'] += len([a for a in u_tasks if a.get('status') == 'concluida'])
                team_data[team]['em_andamento'] += len([a for a in u_tasks if a.get('status') == 'em_andamento'])
                team_data[team]['pendente'] += len([a for a in u_tasks if a.get('status') == 'pendente'])

            if team_data:
                teams = list(team_data.keys())
                fig_teams = go.Figure(data=[
                    go.Bar(name='Concluídas', x=teams, y=[team_data[t]['concluida'] for t in teams], marker_color='#4CAF50'),
                    go.Bar(name='Em Andamento', x=teams, y=[team_data[t]['em_andamento'] for t in teams], marker_color='#2196F3'),
                    go.Bar(name='Pendentes', x=teams, y=[team_data[t]['pendente'] for t in teams], marker_color='#FFC107'),
                ])
                fig_teams.update_layout(title='Tarefas por Equipe', barmode='stack', height=350)

                event_teams = st.plotly_chart(
                    fig_teams, use_container_width=True,
                    on_select="rerun", key="chart_teams_bar"
                )
            else:
                event_teams = None
                st.info("Sem dados de equipe.")

        # Detalhe ao clicar na pizza de status
        if event_pie and event_pie.selection and event_pie.selection.points:
            ponto = event_pie.selection.points[0]
            label_clicado = ponto.get("label")
            status_map = {
                'Concluída': 'concluida',
                'Em Andamento': 'em_andamento',
                'Pendente': 'pendente'
            }
            status_val = status_map.get(label_clicado)
            if status_val:
                tarefas_filtradas = [a for a in all_assignments if a.get('status') == status_val]
                st.subheader(f"Tarefas — {label_clicado} ({len(tarefas_filtradas)})")
                if tarefas_filtradas:
                    st.dataframe(
                        pd.DataFrame(tarefas_filtradas)[_build_detail_columns(tarefas_filtradas)],
                        use_container_width=True, hide_index=True
                    )

        # Detalhe ao clicar em barras de equipe
        if event_teams and event_teams.selection and event_teams.selection.points:
            ponto = event_teams.selection.points[0]
            equipe_clicada = ponto.get("x")
            if equipe_clicada:
                ids_equipe = {u['id'] for u in all_users if u['team'] == equipe_clicada and u['role'] != 'admin'}
                tarefas_equipe = [a for a in all_assignments if a.get('assigned_to') in ids_equipe]
                st.subheader(f"Tarefas — Equipe {str(equipe_clicada).capitalize()} ({len(tarefas_equipe)})")
                if tarefas_equipe:
                    st.dataframe(
                        pd.DataFrame(tarefas_equipe)[_build_detail_columns(tarefas_equipe)],
                        use_container_width=True, hide_index=True
                    )

    # ── TAB POR EMPRESA ────────────────────────────────────────────────────
    with tab_empresa:
        empresa_data: dict = {}
        for a in all_assignments:
            emp = a.get('empresa_nome') or 'Não definida'
            if emp not in empresa_data:
                empresa_data[emp] = {'concluida': 0, 'em_andamento': 0, 'pendente': 0}
            status_val = a.get('status', 'pendente')
            if status_val in empresa_data[emp]:
                empresa_data[emp][status_val] += 1

        if empresa_data:
            empresas = list(empresa_data.keys())

            col_e1, col_e2 = st.columns(2)

            with col_e1:
                fig_emp_bar = go.Figure(data=[
                    go.Bar(name='Concluídas', x=empresas, y=[empresa_data[e]['concluida'] for e in empresas], marker_color='#4CAF50'),
                    go.Bar(name='Em Andamento', x=empresas, y=[empresa_data[e]['em_andamento'] for e in empresas], marker_color='#2196F3'),
                    go.Bar(name='Pendentes', x=empresas, y=[empresa_data[e]['pendente'] for e in empresas], marker_color='#FFC107'),
                ])
                fig_emp_bar.update_layout(title='Tarefas por Empresa', barmode='group', height=350)

                event_emp = st.plotly_chart(
                    fig_emp_bar, use_container_width=True,
                    on_select="rerun", key="chart_empresa_bar"
                )

            with col_e2:
                totais_emp = {e: sum(empresa_data[e].values()) for e in empresas}
                fig_emp_pie = go.Figure(data=[go.Pie(
                    labels=list(totais_emp.keys()),
                    values=list(totais_emp.values()),
                    textinfo='label+percent'
                )])
                fig_emp_pie.update_layout(title='Proporção por Empresa', height=350, showlegend=False)
                st.plotly_chart(fig_emp_pie, use_container_width=True, key="chart_empresa_pie")

            # Detalhe ao clicar em barras de empresa
            if event_emp and event_emp.selection and event_emp.selection.points:
                ponto = event_emp.selection.points[0]
                empresa_clicada = ponto.get("x")
                if empresa_clicada:
                    tarefas_empresa = [
                        a for a in all_assignments
                        if (a.get('empresa_nome') or 'Não definida') == empresa_clicada
                    ]
                    with st.expander(f"Tarefas de {empresa_clicada} ({len(tarefas_empresa)})", expanded=True):
                        if tarefas_empresa:
                            cols = ['id', 'title', 'status', 'priority', 'created_at']
                            cols_exist = [c for c in cols if c in tarefas_empresa[0]]
                            st.dataframe(
                                pd.DataFrame(tarefas_empresa)[cols_exist],
                                use_container_width=True, hide_index=True
                            )
            # Métricas ISP por empresa
            emp_metrics: dict = {}
            for a in all_assignments:
                emp = a.get('empresa_nome') or 'Não definida'
                if emp not in emp_metrics:
                    emp_metrics[emp] = {'CTOs': 0, 'Cx Emenda': 0, 'Fibra (m)': 0.0, 'Tarefas': 0}
                
                # Campos estruturados
                emp_metrics[emp]['CTOs'] += a.get('quantidade_cto') or 0
                emp_metrics[emp]['Cx Emenda'] += a.get('quantidade_cx_emenda') or 0
                emp_metrics[emp]['Fibra (m)'] += float(a.get('fibra_lancada') or 0)
                
                # Campo materials (texto livre)
                if a.get('materials'):
                    materials_data = extract_materials_from_text(a['materials'])
                    emp_metrics[emp]['CTOs'] += materials_data['ctos']
                    emp_metrics[emp]['Fibra (m)'] += materials_data['cabo_metros']
                    
                emp_metrics[emp]['Tarefas'] += 1

            st.subheader("Métricas ISP por Empresa")
            df_emp = pd.DataFrame([{'Empresa': k, **v} for k, v in emp_metrics.items()])
            df_emp['Fibra (m)'] = df_emp['Fibra (m)'].round(2)
            st.dataframe(df_emp, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma tarefa encontrada para o filtro selecionado.")

    # ── TAB DESEMPENHO ─────────────────────────────────────────────────────
    with tab_desempenho:
        user_details = []
        for u in all_users:
            if u['role'] == 'admin':
                continue
            u_tasks = [a for a in all_assignments if a.get('assigned_to') == u['id']]
            completed_count = len([a for a in u_tasks if a.get('status') == 'concluida'])

            # Calcular materiais dos campos estruturados E do campo materials
            user_ctos = 0
            user_cx_emenda = 0
            user_fibra = 0
            
            for a in u_tasks:
                # Campos estruturados
                user_ctos += a.get('quantidade_cto') or 0
                user_cx_emenda += a.get('quantidade_cx_emenda') or 0
                user_fibra += float(a.get('fibra_lancada') or 0)
                
                # Campo materials (texto livre)
                if a.get('materials'):
                    materials_data = extract_materials_from_text(a['materials'])
                    user_ctos += materials_data['ctos']
                    user_fibra += materials_data['cabo_metros']

            user_details.append({
                'Nome': u['full_name'],
                'Equipe': u['team'].capitalize(),
                'Total': len(u_tasks),
                'Concluídas': completed_count,
                'Em Andamento': len([a for a in u_tasks if a.get('status') == 'em_andamento']),
                'Pendentes': len([a for a in u_tasks if a.get('status') == 'pendente']),
                'Qtd CTO': int(user_ctos),
                'Cx Emenda': int(user_cx_emenda),
                'Fibra (m)': round(user_fibra, 2),
            })

        if user_details:
            df_users = pd.DataFrame(user_details).sort_values('Concluídas', ascending=False)
            st.dataframe(df_users, use_container_width=True, hide_index=True)

            # Ranking horizontal
            df_sorted = df_users.sort_values('Concluídas')
            fig_ranking = go.Figure(data=[go.Bar(
                y=df_sorted['Nome'].tolist(),
                x=df_sorted['Concluídas'].tolist(),
                orientation='h',
                marker_color='#4CAF50'
            )])
            fig_ranking.update_layout(
                title='Ranking de Tarefas Concluídas',
                height=max(300, len(user_details) * 40),
                xaxis_title='Concluídas',
            )
            st.plotly_chart(fig_ranking, use_container_width=True, key="chart_ranking")
        else:
            st.info("Nenhum colaborador encontrado.")



if __name__ == "__main__":
    render_dashboard_page()
