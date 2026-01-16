"""
Dashboard de produtividade com métricas por usuário, mês e ano.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from sqlalchemy import func, extract
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentication import require_login, get_current_user, is_admin
from database.connection import SessionLocal
from database.models import Task, User
from utils.export import export_to_excel, export_to_pdf


def get_user_tasks(user_id: int, company_id: int, month: int = None, year: int = None) -> list:
    """Retorna tarefas de um usuário com filtros opcionais."""
    session = SessionLocal()
    try:
        query = session.query(Task).filter(
            Task.user_id == user_id,
            Task.company_id == company_id
        )

        if month and year:
            query = query.filter(
                extract("month", Task.created_at) == month,
                extract("year", Task.created_at) == year,
            )
        elif year:
            query = query.filter(extract("year", Task.created_at) == year)

        tasks = query.order_by(Task.created_at.desc()).all()
        return [
            {
                "id": t.id,
                "empresa": t.empresa,
                "bairro": t.bairro,
                "abertura_caixa_emenda": t.abertura_caixa_emenda,
                "fechamento_caixa_emenda": t.fechamento_caixa_emenda,
                "abertura_cto": t.abertura_cto,
                "fechamento_cto": t.fechamento_cto,
                "abertura_rozeta": t.abertura_rozeta,
                "fechamento_rozeta": t.fechamento_rozeta,
                "qtd_cto": t.qtd_cto,
                "qtd_caixa_emenda": t.qtd_caixa_emenda,
                "tipo_fibra": t.tipo_fibra,
                "fibra_lancada": float(t.fibra_lancada) if t.fibra_lancada else 0,
                "observacoes": t.observacoes,
                "created_at": t.created_at,
            }
            for t in tasks
        ]
    finally:
        session.close()


def get_all_tasks(company_id: int, month: int = None, year: int = None) -> list:
    """Retorna todas as tarefas de uma empresa (para admin) com filtros opcionais."""
    session = SessionLocal()
    try:
        query = session.query(Task, User.full_name, User.team).join(User).filter(
            Task.company_id == company_id
        )

        if month and year:
            query = query.filter(
                extract("month", Task.created_at) == month,
                extract("year", Task.created_at) == year,
            )
        elif year:
            query = query.filter(extract("year", Task.created_at) == year)

        results = query.order_by(Task.created_at.desc()).all()
        return [
            {
                "id": t.id,
                "usuario": name,
                "equipe": team,
                "empresa": t.empresa,
                "bairro": t.bairro,
                "abertura_caixa_emenda": t.abertura_caixa_emenda,
                "fechamento_caixa_emenda": t.fechamento_caixa_emenda,
                "abertura_cto": t.abertura_cto,
                "fechamento_cto": t.fechamento_cto,
                "abertura_rozeta": t.abertura_rozeta,
                "fechamento_rozeta": t.fechamento_rozeta,
                "qtd_cto": t.qtd_cto,
                "qtd_caixa_emenda": t.qtd_caixa_emenda,
                "tipo_fibra": t.tipo_fibra,
                "fibra_lancada": float(t.fibra_lancada) if t.fibra_lancada else 0,
                "observacoes": t.observacoes,
                "created_at": t.created_at,
            }
            for t, name, team in results
        ]
    finally:
        session.close()


def get_monthly_stats(company_id: int, user_id: int = None, year: int = None) -> pd.DataFrame:
    """Retorna estatísticas mensais para gráficos."""
    session = SessionLocal()
    try:
        query = session.query(
            extract("month", Task.created_at).label("mes"),
            func.count(Task.id).label("total_tarefas"),
            func.sum(Task.qtd_cto).label("total_cto"),
            func.sum(Task.qtd_caixa_emenda).label("total_caixa_emenda"),
            func.sum(Task.fibra_lancada).label("total_fibra"),
        ).filter(Task.company_id == company_id)

        if user_id:
            query = query.filter(Task.user_id == user_id)

        if year:
            query = query.filter(extract("year", Task.created_at) == year)

        query = query.group_by(extract("month", Task.created_at))
        results = query.all()

        meses = [
            "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
            "Jul", "Ago", "Set", "Out", "Nov", "Dez"
        ]

        data = {
            "Mês": meses,
            "Tarefas": [0] * 12,
            "CTOs": [0] * 12,
            "Caixas de Emenda": [0] * 12,
            "Fibra (m)": [0.0] * 12,
        }

        for row in results:
            idx = int(row.mes) - 1
            data["Tarefas"][idx] = row.total_tarefas or 0
            data["CTOs"][idx] = row.total_cto or 0
            data["Caixas de Emenda"][idx] = row.total_caixa_emenda or 0
            data["Fibra (m)"][idx] = float(row.total_fibra or 0)

        return pd.DataFrame(data)
    finally:
        session.close()


def get_team_stats(company_id: int, month: int = None, year: int = None) -> pd.DataFrame:
    """Retorna estatísticas por equipe de uma empresa."""
    session = SessionLocal()
    try:
        query = session.query(
            User.team,
            func.count(Task.id).label("total_tarefas"),
            func.sum(Task.qtd_cto).label("total_cto"),
            func.sum(Task.qtd_caixa_emenda).label("total_caixa_emenda"),
            func.sum(Task.fibra_lancada).label("total_fibra"),
        ).join(Task).filter(Task.company_id == company_id)

        if month and year:
            query = query.filter(
                extract("month", Task.created_at) == month,
                extract("year", Task.created_at) == year,
            )
        elif year:
            query = query.filter(extract("year", Task.created_at) == year)

        results = query.group_by(User.team).all()

        return pd.DataFrame([
            {
                "Equipe": r.team.capitalize(),
                "Tarefas": r.total_tarefas or 0,
                "CTOs": r.total_cto or 0,
                "Caixas de Emenda": r.total_caixa_emenda or 0,
                "Fibra (m)": float(r.total_fibra or 0),
            }
            for r in results
        ])
    finally:
        session.close()


def get_user_ranking(company_id: int, month: int = None, year: int = None) -> pd.DataFrame:
    """Retorna ranking de usuários por produtividade de uma empresa."""
    session = SessionLocal()
    try:
        query = session.query(
            User.full_name,
            User.team,
            func.count(Task.id).label("total_tarefas"),
            func.sum(Task.qtd_cto).label("total_cto"),
            func.sum(Task.qtd_caixa_emenda).label("total_caixa_emenda"),
            func.sum(Task.fibra_lancada).label("total_fibra"),
        ).join(Task).filter(Task.company_id == company_id)

        if month and year:
            query = query.filter(
                extract("month", Task.created_at) == month,
                extract("year", Task.created_at) == year,
            )
        elif year:
            query = query.filter(extract("year", Task.created_at) == year)

        results = query.group_by(User.id, User.full_name, User.team).order_by(
            func.count(Task.id).desc()
        ).all()

        return pd.DataFrame([
            {
                "Usuário": r.full_name,
                "Equipe": r.team.capitalize(),
                "Tarefas": r.total_tarefas or 0,
                "CTOs": r.total_cto or 0,
                "Caixas de Emenda": r.total_caixa_emenda or 0,
                "Fibra (m)": float(r.total_fibra or 0),
            }
            for r in results
        ])
    finally:
        session.close()


def render_dashboard_page():
    """Renderiza a página do dashboard."""
    require_login()
    user = get_current_user()

    st.title("Dashboard de Produtividade")

    # Filtros
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**Usuário:** {user['full_name']} | **Equipe:** {user['team'].capitalize()}")
    with col2:
        current_year = datetime.now().year
        years = list(range(current_year, current_year - 5, -1))
        selected_year = st.selectbox("Ano", years)
    with col3:
        months = ["Todos", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                  "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        selected_month_name = st.selectbox("Mês", months)
        selected_month = months.index(selected_month_name) if selected_month_name != "Todos" else None

    st.markdown("---")

    # Métricas do usuário
    st.subheader("Minhas Métricas")

    my_tasks = get_user_tasks(user["id"], user["company_id"], selected_month, selected_year)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Tarefas", len(my_tasks))
    with col2:
        total_cto = sum(t["qtd_cto"] for t in my_tasks)
        st.metric("Total CTOs", total_cto)
    with col3:
        total_ce = sum(t["qtd_caixa_emenda"] for t in my_tasks)
        st.metric("Total Caixas de Emenda", total_ce)
    with col4:
        total_fibra = sum(t["fibra_lancada"] for t in my_tasks)
        st.metric("Fibra Lançada (m)", f"{total_fibra:.2f}")

    # Gráfico mensal do usuário
    st.subheader("Evolução Mensal")
    monthly_data = get_monthly_stats(user["company_id"], user["id"], selected_year)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Tarefas", x=monthly_data["Mês"], y=monthly_data["Tarefas"]))
    fig.update_layout(
        title=f"Tarefas Realizadas por Mês - {selected_year}",
        xaxis_title="Mês",
        yaxis_title="Quantidade",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabela de tarefas
    st.subheader("Minhas Tarefas")
    if my_tasks:
        df_tasks = pd.DataFrame(my_tasks)
        df_tasks["created_at"] = pd.to_datetime(df_tasks["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
        df_display = df_tasks[["created_at", "empresa", "bairro", "qtd_cto", "qtd_caixa_emenda", "fibra_lancada"]]
        df_display.columns = ["Data/Hora", "Empresa", "Bairro", "CTOs", "Caixas Emenda", "Fibra (m)"]
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Ver Detalhes da Tarefa
        st.subheader("Ver Detalhes")
        task_list = [(t["id"], f"{t['created_at'].strftime('%d/%m/%Y %H:%M')} - {t['empresa']} ({t['bairro']})") for t in my_tasks]
        task_ids = [t[0] for t in task_list]
        task_labels = [t[1] for t in task_list]

        selected_index = st.selectbox(
            "Selecione uma tarefa para ver detalhes",
            options=range(len(task_labels)),
            format_func=lambda i: task_labels[i],
            key="select_task_details"
        )

        if st.button("📋 Ver Detalhes / Editar / Excluir", key="btn_view_details", use_container_width=True, type="primary"):
            st.session_state["selected_task_id"] = task_ids[selected_index]
            st.session_state["current_page"] = "task_details"
            st.rerun()

        # Exportação
        st.subheader("Exportar Relatório")
        col1, col2 = st.columns(2)
        with col1:
            excel_data = export_to_excel(df_tasks, f"Tarefas_{user['username']}_{selected_year}")
            if excel_data:
                st.download_button(
                    label="Baixar Excel",
                    data=excel_data,
                    file_name=f"tarefas_{user['username']}_{selected_year}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
        with col2:
            pdf_data = export_to_pdf(
                df_tasks,
                f"Relatório de Tarefas - {user['full_name']}",
                selected_year,
                selected_month,
            )
            if pdf_data:
                st.download_button(
                    label="Baixar PDF",
                    data=pdf_data,
                    file_name=f"tarefas_{user['username']}_{selected_year}.pdf",
                    mime="application/pdf",
                )
    else:
        st.info("Nenhuma tarefa encontrada no período selecionado.")

    # Seção Admin - Visão Geral
    if is_admin():
        st.markdown("---")
        st.header("Visão Geral (Admin)")

        # Estatísticas por equipe
        st.subheader("Estatísticas por Equipe")
        team_stats = get_team_stats(user["company_id"], selected_month, selected_year)
        if not team_stats.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig_team = px.pie(
                    team_stats,
                    values="Tarefas",
                    names="Equipe",
                    title="Distribuição de Tarefas por Equipe",
                )
                st.plotly_chart(fig_team, use_container_width=True)
            with col2:
                st.dataframe(team_stats, use_container_width=True, hide_index=True)

        # Ranking de usuários
        st.subheader("Ranking de Produtividade")
        ranking = get_user_ranking(user["company_id"], selected_month, selected_year)
        if not ranking.empty:
            fig_ranking = px.bar(
                ranking,
                x="Usuário",
                y="Tarefas",
                color="Equipe",
                title="Tarefas por Usuário",
            )
            st.plotly_chart(fig_ranking, use_container_width=True)
            st.dataframe(ranking, use_container_width=True, hide_index=True)

        # Todas as tarefas
        st.subheader("Todas as Tarefas")
        all_tasks = get_all_tasks(user["company_id"], selected_month, selected_year)
        if all_tasks:
            df_all = pd.DataFrame(all_tasks)
            df_all["created_at"] = pd.to_datetime(df_all["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
            df_display = df_all[[
                "created_at", "usuario", "equipe", "empresa", "bairro",
                "qtd_cto", "qtd_caixa_emenda", "fibra_lancada"
            ]]
            df_display.columns = [
                "Data/Hora", "Usuário", "Equipe", "Empresa", "Bairro",
                "CTOs", "Caixas Emenda", "Fibra (m)"
            ]
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # Ver Detalhes das Tarefas (Admin)
            st.subheader("Ver Detalhes (Admin)")
            admin_task_list = [(t["id"], f"{t['created_at'].strftime('%d/%m/%Y %H:%M')} - {t['usuario']} - {t['empresa']} ({t['bairro']})") for t in all_tasks]
            admin_task_ids = [t[0] for t in admin_task_list]
            admin_task_labels = [t[1] for t in admin_task_list]

            selected_admin_index = st.selectbox(
                "Selecione uma tarefa para ver detalhes",
                options=range(len(admin_task_labels)),
                format_func=lambda i: admin_task_labels[i],
                key="select_admin_task_details"
            )

            if st.button("📋 Ver Detalhes / Editar / Excluir", key="btn_admin_view_details", use_container_width=True, type="primary"):
                st.session_state["selected_task_id"] = admin_task_ids[selected_admin_index]
                st.session_state["current_page"] = "task_details"
                st.rerun()

            # Exportação admin
            st.subheader("Exportar Relatório Geral")
            col1, col2 = st.columns(2)
            with col1:
                excel_data = export_to_excel(df_all, f"Todas_Tarefas_{selected_year}")
                if excel_data:
                    st.download_button(
                        label="Baixar Excel (Todas)",
                        data=excel_data,
                        file_name=f"todas_tarefas_{selected_year}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="excel_all",
                    )
            with col2:
                pdf_data = export_to_pdf(
                    df_all,
                    "Relatório Geral de Tarefas",
                    selected_year,
                    selected_month,
                )
                if pdf_data:
                    st.download_button(
                        label="Baixar PDF (Todas)",
                        data=pdf_data,
                        file_name=f"todas_tarefas_{selected_year}.pdf",
                        mime="application/pdf",
                        key="pdf_all",
                    )
        else:
            st.info("Nenhuma tarefa encontrada no período selecionado.")


if __name__ == "__main__":
    render_dashboard_page()
