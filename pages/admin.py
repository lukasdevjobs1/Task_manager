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
    tab1, tab2, tab3 = st.tabs(["Usuários", "Novo Usuário", "Alterar Senha"])

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


if __name__ == "__main__":
    render_admin_page()
