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

import re

from auth.authentication import require_login, get_current_user, is_admin
from database.supabase_only_connection import db


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
    
    return {'ctos': ctos, 'ceos': ceos, 'cabo_metros': cabo_metros}



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


def render_assignment_card(assignment: dict, show_assignee: bool = False, card_index: int = 0, is_manager: bool = False):
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

    # Calcular todas as métricas ISP dos campos estruturados E do campo materials (texto)
    total_ctos = 0
    total_cx_emenda = 0
    total_fibra = 0
    total_abert_cx_emenda = 0
    total_abert_cto = 0
    total_abert_rozeta = 0

    for a in all_assignments:
        total_ctos += a.get('quantidade_cto') or 0
        total_cx_emenda += a.get('quantidade_cx_emenda') or 0
        total_fibra += float(a.get('fibra_lancada') or 0)
        total_abert_cx_emenda += a.get('abertura_fechamento_cx_emenda') or 0
        total_abert_cto += a.get('abertura_fechamento_cto') or 0
        total_abert_rozeta += a.get('abertura_fechamento_rozeta') or 0

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
        st.metric("Qtd CTOs", int(total_ctos))
    with kpi_isp2:
        st.metric("Qtd Cx Emenda", int(total_cx_emenda))
    with kpi_isp3:
        st.metric("Fibra Lançada (m)", f"{total_fibra:.0f}")

    kpi_isp4, kpi_isp5, kpi_isp6 = st.columns(3)
    with kpi_isp4:
        st.metric("Abert./Fech. Cx Emenda", int(total_abert_cx_emenda))
    with kpi_isp5:
        st.metric("Abert./Fech. CTO", int(total_abert_cto))
    with kpi_isp6:
        st.metric("Abert./Fech. Rozeta", int(total_abert_rozeta))

    # ── Tabs ───────────────────────────────────────────────────────────────
    tab_geral, tab_empresa, tab_desempenho, tab_materiais = st.tabs(
        ["📊 Geral", "🏢 Por Empresa", "👥 Desempenho", "🔧 Materiais"]
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
                    emp_metrics[emp] = {
                        'Tarefas': 0,
                        'Qtd CTO': 0, 'Qtd Cx Emenda': 0, 'Fibra (m)': 0.0,
                        'Abert. Cx Emenda': 0, 'Abert. CTO': 0, 'Abert. Rozeta': 0,
                    }

                emp_metrics[emp]['Qtd CTO'] += a.get('quantidade_cto') or 0
                emp_metrics[emp]['Qtd Cx Emenda'] += a.get('quantidade_cx_emenda') or 0
                emp_metrics[emp]['Fibra (m)'] += float(a.get('fibra_lancada') or 0)
                emp_metrics[emp]['Abert. Cx Emenda'] += a.get('abertura_fechamento_cx_emenda') or 0
                emp_metrics[emp]['Abert. CTO'] += a.get('abertura_fechamento_cto') or 0
                emp_metrics[emp]['Abert. Rozeta'] += a.get('abertura_fechamento_rozeta') or 0

                if a.get('materials'):
                    materials_data = extract_materials_from_text(a['materials'])
                    emp_metrics[emp]['Qtd CTO'] += materials_data['ctos']
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

            # Calcular todas as métricas ISP por usuário
            user_ctos = 0
            user_cx_emenda = 0
            user_fibra = 0
            user_abert_cx_emenda = 0
            user_abert_cto = 0
            user_abert_rozeta = 0

            for a in u_tasks:
                user_ctos += a.get('quantidade_cto') or 0
                user_cx_emenda += a.get('quantidade_cx_emenda') or 0
                user_fibra += float(a.get('fibra_lancada') or 0)
                user_abert_cx_emenda += a.get('abertura_fechamento_cx_emenda') or 0
                user_abert_cto += a.get('abertura_fechamento_cto') or 0
                user_abert_rozeta += a.get('abertura_fechamento_rozeta') or 0

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
                'Qtd Cx Emenda': int(user_cx_emenda),
                'Fibra (m)': round(user_fibra, 2),
                'Abert. Cx Emenda': int(user_abert_cx_emenda),
                'Abert. CTO': int(user_abert_cto),
                'Abert. Rozeta': int(user_abert_rozeta),
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
    
    # ── TAB MATERIAIS ──────────────────────────────────────────────────────
    with tab_materiais:
        st.subheader("🔧 Detalhamento de Materiais por Tarefa")
        
        # Filtros específicos da tab materiais
        col_m1, col_m2, col_m3 = st.columns(3)
        
        with col_m1:
            tipo_filtro = st.selectbox(
                "Tipo de Filtro",
                ["Período Rápido", "Data Específica", "Intervalo de Datas"],
                key="mat_tipo_filtro"
            )
        
        # Filtrar tarefas por data
        tarefas_filtradas = list(all_assignments_raw)
        
        if tipo_filtro == "Período Rápido":
            with col_m2:
                periodo_mat = st.selectbox(
                    "Período",
                    ["Hoje", "Ontem", "Esta Semana", "Semana Passada", "Este Mês", "Mês Passado", "Todos"],
                    key="mat_periodo"
                )
            
            hoje = datetime.now().date()
            if periodo_mat == "Hoje":
                tarefas_filtradas = [a for a in tarefas_filtradas if parse_date(a.get('created_at')).date() == hoje]
            elif periodo_mat == "Ontem":
                ontem = hoje - timedelta(days=1)
                tarefas_filtradas = [a for a in tarefas_filtradas if parse_date(a.get('created_at')).date() == ontem]
            elif periodo_mat == "Esta Semana":
                inicio_semana = hoje - timedelta(days=hoje.weekday())
                tarefas_filtradas = [a for a in tarefas_filtradas if parse_date(a.get('created_at')).date() >= inicio_semana]
            elif periodo_mat == "Semana Passada":
                inicio_semana_passada = hoje - timedelta(days=hoje.weekday() + 7)
                fim_semana_passada = inicio_semana_passada + timedelta(days=6)
                tarefas_filtradas = [a for a in tarefas_filtradas if inicio_semana_passada <= parse_date(a.get('created_at')).date() <= fim_semana_passada]
            elif periodo_mat == "Este Mês":
                tarefas_filtradas = [a for a in tarefas_filtradas if parse_date(a.get('created_at')).month == hoje.month and parse_date(a.get('created_at')).year == hoje.year]
            elif periodo_mat == "Mês Passado":
                mes_passado = (hoje.replace(day=1) - timedelta(days=1))
                tarefas_filtradas = [a for a in tarefas_filtradas if parse_date(a.get('created_at')).month == mes_passado.month and parse_date(a.get('created_at')).year == mes_passado.year]
        
        elif tipo_filtro == "Data Específica":
            with col_m2:
                data_especifica = st.date_input(
                    "Selecione a Data",
                    value=datetime.now().date(),
                    key="mat_data_especifica"
                )
            tarefas_filtradas = [a for a in tarefas_filtradas if parse_date(a.get('created_at')).date() == data_especifica]
        
        elif tipo_filtro == "Intervalo de Datas":
            with col_m2:
                data_inicio = st.date_input(
                    "Data Início",
                    value=datetime.now().date() - timedelta(days=30),
                    key="mat_data_inicio"
                )
            with col_m3:
                data_fim = st.date_input(
                    "Data Fim",
                    value=datetime.now().date(),
                    key="mat_data_fim"
                )
            tarefas_filtradas = [a for a in tarefas_filtradas if data_inicio <= parse_date(a.get('created_at')).date() <= data_fim]
        
        # Preparar dados de materiais por tarefa (usando tarefas_filtradas)
        materiais_tarefas = []
        for a in tarefas_filtradas:
            task_ctos = a.get('quantidade_cto') or 0
            task_cx_emenda = a.get('quantidade_cx_emenda') or 0
            task_fibra = float(a.get('fibra_lancada') or 0)
            task_abert_cx_emenda = a.get('abertura_fechamento_cx_emenda') or 0
            task_abert_cto = a.get('abertura_fechamento_cto') or 0
            task_abert_rozeta = a.get('abertura_fechamento_rozeta') or 0

            if a.get('materials'):
                mat_data = extract_materials_from_text(a['materials'])
                task_ctos += mat_data['ctos']
                task_fibra += mat_data['cabo_metros']

            # Só adiciona se tiver alguma métrica preenchida
            has_data = any([task_ctos, task_cx_emenda, task_fibra,
                            task_abert_cx_emenda, task_abert_cto, task_abert_rozeta])
            if has_data:
                assignee = a.get('assigned_to_user', {})
                materiais_tarefas.append({
                    'ID': a['id'],
                    'Data': parse_date(a.get('created_at')).strftime('%d/%m/%Y'),
                    'Tarefa': a['title'],
                    'Empresa': a.get('empresa_nome', 'N/A'),
                    'Técnico': assignee.get('full_name', 'N/A') if isinstance(assignee, dict) else 'N/A',
                    'Status': a['status'],
                    'Qtd CTO': int(task_ctos),
                    'Qtd Cx Emenda': int(task_cx_emenda),
                    'Fibra (m)': round(task_fibra, 2),
                    'Abert. Cx Emenda': int(task_abert_cx_emenda),
                    'Abert. CTO': int(task_abert_cto),
                    'Abert. Rozeta': int(task_abert_rozeta),
                })
        
        if materiais_tarefas:
            df_materiais = pd.DataFrame(materiais_tarefas)
            
            # Filtros adicionais
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                status_mat_filter = st.selectbox(
                    "Filtrar por Status",
                    ["Todos", "concluida", "em_andamento", "pendente"],
                    key="mat_status_filter"
                )
            with col_f2:
                empresa_mat_filter = st.selectbox(
                    "Filtrar por Empresa",
                    ["Todas"] + sorted(df_materiais['Empresa'].unique().tolist()),
                    key="mat_empresa_filter"
                )
            
            # Aplicar filtros
            if status_mat_filter != "Todos":
                df_materiais = df_materiais[df_materiais['Status'] == status_mat_filter]
            if empresa_mat_filter != "Todas":
                df_materiais = df_materiais[df_materiais['Empresa'] == empresa_mat_filter]
            
            # Exibir tabela
            st.markdown(f"**{len(df_materiais)} tarefa(s) encontrada(s)**")
            st.dataframe(df_materiais, use_container_width=True, hide_index=True)
            
            # Botão para exportar
            csv = df_materiais.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📊 Exportar para CSV",
                data=csv,
                file_name=f"materiais_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_materiais"
            )
            
            # Totais
            st.markdown("---")
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                st.metric("Total de Tarefas", len(df_materiais))
            with col_t2:
                st.metric("Qtd CTO Total", int(df_materiais['Qtd CTO'].sum()))
            with col_t3:
                st.metric("Qtd Cx Emenda Total", int(df_materiais['Qtd Cx Emenda'].sum()))

            col_t4, col_t5, col_t6, col_t7 = st.columns(4)
            with col_t4:
                st.metric("Fibra Lançada (m)", f"{df_materiais['Fibra (m)'].sum():.0f}")
            with col_t5:
                st.metric("Abert. Cx Emenda", int(df_materiais['Abert. Cx Emenda'].sum()))
            with col_t6:
                st.metric("Abert. CTO", int(df_materiais['Abert. CTO'].sum()))
            with col_t7:
                st.metric("Abert. Rozeta", int(df_materiais['Abert. Rozeta'].sum()))
            
            # Gráfico de materiais por empresa
            if empresa_mat_filter == "Todas" and len(df_materiais) > 0:
                st.subheader("📊 Materiais por Empresa")
                mat_por_emp = df_materiais.groupby('Empresa').agg({
                    'Qtd CTO': 'sum',
                    'Qtd Cx Emenda': 'sum',
                    'Fibra (m)': 'sum',
                    'Abert. CTO': 'sum',
                    'Abert. Cx Emenda': 'sum',
                    'Abert. Rozeta': 'sum',
                }).reset_index()
                
                fig_mat = go.Figure(data=[
                    go.Bar(name='Qtd CTO', x=mat_por_emp['Empresa'], y=mat_por_emp['Qtd CTO'], marker_color='#2196F3'),
                    go.Bar(name='Qtd Cx Emenda', x=mat_por_emp['Empresa'], y=mat_por_emp['Qtd Cx Emenda'], marker_color='#4CAF50'),
                    go.Bar(name='Abert. CTO', x=mat_por_emp['Empresa'], y=mat_por_emp['Abert. CTO'], marker_color='#FF9800'),
                    go.Bar(name='Abert. Cx Emenda', x=mat_por_emp['Empresa'], y=mat_por_emp['Abert. Cx Emenda'], marker_color='#9C27B0'),
                ])
                fig_mat.update_layout(title='Materiais Utilizados por Empresa', barmode='group', height=400)
                st.plotly_chart(fig_mat, use_container_width=True, key="chart_mat_empresa")
                
                # Gráfico de evolução diária (se intervalo > 1 dia)
                if tipo_filtro == "Intervalo de Datas" and (data_fim - data_inicio).days > 1:
                    st.subheader("📈 Evolução Diária de Materiais")
                    df_materiais['Data_dt'] = pd.to_datetime(df_materiais['Data'], format='%d/%m/%Y')
                    evolucao = df_materiais.groupby('Data_dt').agg({
                        'Qtd CTO': 'sum',
                        'Fibra (m)': 'sum',
                        'Abert. CTO': 'sum',
                    }).reset_index()
                    evolucao = evolucao.sort_values('Data_dt')

                    fig_evolucao = go.Figure()
                    fig_evolucao.add_trace(go.Scatter(
                        x=evolucao['Data_dt'],
                        y=evolucao['Qtd CTO'],
                        mode='lines+markers',
                        name='Qtd CTO',
                        line=dict(color='#2196F3', width=3)
                    ))
                    fig_evolucao.add_trace(go.Scatter(
                        x=evolucao['Data_dt'],
                        y=evolucao['Abert. CTO'],
                        mode='lines+markers',
                        name='Abert. CTO',
                        line=dict(color='#FF9800', width=3)
                    ))
                    fig_evolucao.add_trace(go.Scatter(
                        x=evolucao['Data_dt'],
                        y=evolucao['Fibra (m)'],
                        mode='lines+markers',
                        name='Fibra (m)',
                        line=dict(color='#4CAF50', width=3),
                        yaxis='y2'
                    ))
                    fig_evolucao.update_layout(
                        title='Evolução de Materiais no Período',
                        xaxis_title='Data',
                        yaxis_title='CTOs',
                        yaxis2=dict(title='Fibra (m)', overlaying='y', side='right'),
                        height=400
                    )
                    st.plotly_chart(fig_evolucao, use_container_width=True, key="chart_evolucao")
        else:
            st.info("ℹ️ Nenhuma tarefa com materiais registrados no período selecionado.")



if __name__ == "__main__":
    render_dashboard_page()
