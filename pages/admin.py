"""
Painel administrativo para gerenciamento de usuários.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentication import (
    require_admin,
    get_current_user,
    create_user,
    update_password,
    toggle_user_status,
    get_all_users,
    get_all_companies,
    create_company,
    toggle_company_status,
    get_company_stats,
)
from config import EQUIPES, ROLES


def render_admin_page():
    """Renderiza o painel administrativo."""
    require_admin()
    user = get_current_user()

    st.title("Painel Administrativo")
    st.markdown(f"**Administrador:** {user['full_name']} | **Empresa:** {user['company_name']}")
    st.markdown("---")

    # Tabs para organizar funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["Usuários", "Novo Usuário", "Alterar Senha", "Empresas"])

    # Tab 1: Lista de Usuários
    with tab1:
        st.subheader("Usuários Cadastrados")

        users = get_all_users(user["company_id"])
        if users:
            # Criar DataFrame
            df = pd.DataFrame(users)
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y %H:%M")
            df["status"] = df["active"].apply(lambda x: "Ativo" if x else "Inativo")
            df["equipe"] = df["team"].apply(lambda x: x.capitalize())
            df["perfil"] = df["role"].apply(lambda x: "Administrador" if x == "admin" else "Usuário")

            # Tabela de visualização
            df_display = df[["full_name", "username", "equipe", "perfil", "status", "created_at"]]
            df_display.columns = ["Nome", "Usuário", "Equipe", "Perfil", "Status", "Criado em"]
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # Ativar/Desativar usuário
            st.markdown("---")
            st.subheader("Ativar/Desativar Usuário")

            col1, col2 = st.columns([3, 1])
            with col1:
                user_options = {
                    f"{u['full_name']} ({u['username']})": u["id"]
                    for u in users
                    if u["id"] != user["id"]  # Não pode desativar a si mesmo
                }
                if user_options:
                    selected_user = st.selectbox(
                        "Selecione o usuário",
                        options=list(user_options.keys()),
                        key="toggle_user",
                    )
                else:
                    st.info("Não há outros usuários para gerenciar.")
                    selected_user = None

            with col2:
                if selected_user:
                    selected_id = user_options[selected_user]
                    selected_data = next((u for u in users if u["id"] == selected_id), None)
                    action = "Desativar" if selected_data["active"] else "Ativar"

                    if st.button(action, type="primary", use_container_width=True):
                        success, msg = toggle_user_status(selected_id, user["company_id"])
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.info("Nenhum usuário cadastrado.")

    # Tab 2: Novo Usuário
    with tab2:
        st.subheader("Cadastrar Novo Usuário")

        with st.form("new_user_form"):
            col1, col2 = st.columns(2)

            with col1:
                new_full_name = st.text_input("Nome Completo *", placeholder="Nome completo")
                new_username = st.text_input("Usuário *", placeholder="Nome de usuário para login")

            with col2:
                new_team = st.selectbox("Equipe *", options=EQUIPES, format_func=str.capitalize)
                new_role = st.selectbox(
                    "Perfil *",
                    options=ROLES,
                    format_func=lambda x: "Administrador" if x == "admin" else "Usuário",
                )

            col1, col2 = st.columns(2)
            with col1:
                new_password = st.text_input("Senha *", type="password", placeholder="Mínimo 6 caracteres")
            with col2:
                confirm_password = st.text_input("Confirmar Senha *", type="password")

            submitted = st.form_submit_button("Cadastrar Usuário", use_container_width=True, type="primary")

            if submitted:
                errors = []

                if not new_full_name.strip():
                    errors.append("Nome completo é obrigatório.")
                if not new_username.strip():
                    errors.append("Usuário é obrigatório.")
                if not new_password:
                    errors.append("Senha é obrigatória.")
                elif len(new_password) < 6:
                    errors.append("Senha deve ter no mínimo 6 caracteres.")
                if new_password != confirm_password:
                    errors.append("As senhas não coincidem.")

                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    success, msg = create_user(
                        username=new_username.strip(),
                        password=new_password,
                        full_name=new_full_name.strip(),
                        team=new_team,
                        company_id=user["company_id"],
                        role=new_role,
                    )
                    if success:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)

    # Tab 3: Alterar Senha
    with tab3:
        st.subheader("Alterar Senha de Usuário")

        users = get_all_users(user["company_id"])
        user_options = {f"{u['full_name']} ({u['username']})": u["id"] for u in users}

        with st.form("change_password_form"):
            selected_user = st.selectbox(
                "Selecione o usuário",
                options=list(user_options.keys()),
            )

            col1, col2 = st.columns(2)
            with col1:
                new_pass = st.text_input("Nova Senha *", type="password", placeholder="Mínimo 6 caracteres")
            with col2:
                confirm_pass = st.text_input("Confirmar Nova Senha *", type="password")

            submitted = st.form_submit_button("Alterar Senha", use_container_width=True, type="primary")

            if submitted:
                errors = []

                if not new_pass:
                    errors.append("Nova senha é obrigatória.")
                elif len(new_pass) < 6:
                    errors.append("Senha deve ter no mínimo 6 caracteres.")
                if new_pass != confirm_pass:
                    errors.append("As senhas não coincidem.")

                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    user_id = user_options[selected_user]
                    success, msg = update_password(user_id, new_pass, user["company_id"])
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

    # Tab 4: Gestão de Empresas
    with tab4:
        st.subheader("Gestão de Empresas")

        # Lista de empresas
        companies = get_all_companies()
        if companies:
            # Criar DataFrame com estatísticas
            companies_data = []
            for c in companies:
                stats = get_company_stats(c["id"])
                companies_data.append({
                    "id": c["id"],
                    "name": c["name"],
                    "slug": c["slug"],
                    "active": c["active"],
                    "users": stats["users"],
                    "tasks": stats["tasks"],
                    "created_at": c["created_at"],
                })

            df = pd.DataFrame(companies_data)
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%d/%m/%Y")
            df["status"] = df["active"].apply(lambda x: "Ativa" if x else "Inativa")

            df_display = df[["name", "slug", "users", "tasks", "status", "created_at"]]
            df_display.columns = ["Nome", "Slug", "Usuários", "Tarefas", "Status", "Criado em"]
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # Ativar/Desativar empresa
            st.markdown("---")
            st.subheader("Ativar/Desativar Empresa")

            col1, col2 = st.columns([3, 1])
            with col1:
                company_options = {
                    f"{c['name']} ({c['slug']})": c["id"]
                    for c in companies
                    if c["id"] != user["company_id"]  # Não pode desativar própria empresa
                }
                if company_options:
                    selected_company = st.selectbox(
                        "Selecione a empresa",
                        options=list(company_options.keys()),
                        key="toggle_company",
                    )
                else:
                    st.info("Não há outras empresas para gerenciar.")
                    selected_company = None

            with col2:
                if selected_company:
                    selected_company_id = company_options[selected_company]
                    selected_company_data = next(
                        (c for c in companies if c["id"] == selected_company_id), None
                    )
                    action = "Desativar" if selected_company_data["active"] else "Ativar"

                    if st.button(action, type="primary", use_container_width=True, key="btn_toggle_company"):
                        success, msg = toggle_company_status(selected_company_id)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            st.info("Nenhuma empresa cadastrada.")

        # Criar nova empresa
        st.markdown("---")
        st.subheader("Criar Nova Empresa")

        with st.form("new_company_form"):
            col1, col2 = st.columns(2)

            with col1:
                company_name = st.text_input(
                    "Nome da Empresa *",
                    placeholder="Ex: Minha Empresa LTDA"
                )
            with col2:
                company_slug = st.text_input(
                    "Slug (identificador) *",
                    placeholder="Ex: minha-empresa",
                    help="Use apenas letras minúsculas, números e hífens"
                )

            st.markdown("---")
            st.subheader("Admin da Nova Empresa")
            st.caption("Será criado um administrador para a nova empresa")

            col1, col2 = st.columns(2)
            with col1:
                admin_name = st.text_input("Nome do Admin *", placeholder="Nome completo")
                admin_username = st.text_input("Usuário do Admin *", placeholder="Nome de usuário")
            with col2:
                admin_team = st.selectbox("Equipe *", options=EQUIPES, format_func=str.capitalize, key="company_admin_team")
                admin_password = st.text_input("Senha do Admin *", type="password", placeholder="Mínimo 6 caracteres")

            submitted = st.form_submit_button("Criar Empresa", use_container_width=True, type="primary")

            if submitted:
                errors = []

                if not company_name.strip():
                    errors.append("Nome da empresa é obrigatório.")
                if not company_slug.strip():
                    errors.append("Slug é obrigatório.")
                if not admin_name.strip():
                    errors.append("Nome do admin é obrigatório.")
                if not admin_username.strip():
                    errors.append("Usuário do admin é obrigatório.")
                if not admin_password:
                    errors.append("Senha do admin é obrigatória.")
                elif len(admin_password) < 6:
                    errors.append("Senha deve ter no mínimo 6 caracteres.")

                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Criar empresa
                    success, msg, new_company_id = create_company(
                        name=company_name.strip(),
                        slug=company_slug.strip().lower(),
                    )

                    if success and new_company_id:
                        # Criar admin da empresa
                        user_success, user_msg = create_user(
                            username=admin_username.strip(),
                            password=admin_password,
                            full_name=admin_name.strip(),
                            team=admin_team,
                            company_id=new_company_id,
                            role="admin",
                        )

                        if user_success:
                            st.success(f"Empresa '{company_name}' criada com sucesso!")
                            st.success(f"Admin '{admin_username}' criado com sucesso!")
                            st.balloons()
                        else:
                            st.warning(f"Empresa criada, mas erro ao criar admin: {user_msg}")
                    else:
                        st.error(msg)


if __name__ == "__main__":
    render_admin_page()
