"""
Página de login do sistema.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentication import authenticate_user, login_user, is_logged_in


def render_login_page():
    """Renderiza a página de login."""

    # Se já está logado, não mostra o login
    if is_logged_in():
        return True

    st.markdown(
        """
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Centraliza o formulário
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.title("Sistema de Tarefas ISP")
        st.subheader("Login")

        with st.form("login_form"):
            username = st.text_input("Usuário", placeholder="Digite seu usuário")
            password = st.text_input(
                "Senha", type="password", placeholder="Digite sua senha"
            )
            submit = st.form_submit_button("Entrar", use_container_width=True)

            if submit:
                if not username or not password:
                    st.error("Por favor, preencha todos os campos.")
                else:
                    user = authenticate_user(username, password)
                    if user:
                        login_user(user)
                        st.success(f"Bem-vindo, {user.full_name}!")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")

        st.markdown("---")
        st.caption("Sistema de Gerenciamento de Tarefas - Provedor de Internet")

    return False


if __name__ == "__main__":
    render_login_page()
