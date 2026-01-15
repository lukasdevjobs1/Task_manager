"""
Sistema de Gerenciamento de Tarefas - Provedor de Internet
Aplicação principal Streamlit com navegação entre páginas.
"""

import streamlit as st
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.authentication import (
    is_logged_in,
    is_admin,
    is_super_admin,
    logout_user,
    get_current_user,
)
from views.login import render_login_page
from views.register_task import render_register_task_page
from views.dashboard import render_dashboard_page
from views.admin import render_admin_page


def configure_page():
    """Configurações da página Streamlit."""
    st.set_page_config(
        page_title="Sistema de Tarefas ISP",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # CSS customizado
    st.markdown(
        """
        <style>
        .main {
            padding: 1rem;
        }
        .stButton > button {
            width: 100%;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.5rem;
        }
        section[data-testid="stSidebar"] {
            background-color: #f8f9fa;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    """Renderiza a barra lateral com navegação."""
    user = get_current_user()
    user_is_super = is_super_admin()

    with st.sidebar:
        st.title("📋 Sistema de Tarefas")
        st.markdown("---")

        # Informações do usuário
        if user_is_super:
            st.markdown("🔑 **Super Administrador**")
        else:
            st.markdown(f"🏢 **{user['company_name']}**")

        st.markdown(f"👤 {user['full_name']}")
        st.markdown(f"👥 Equipe: {user['team'].capitalize()}")

        if is_admin() and not user_is_super:
            st.markdown("⭐ Gerente")

        st.markdown("---")

        # Menu de navegação usando radio
        menu_options = ["📊 Dashboard", "📝 Nova Tarefa"]

        if is_admin():
            menu_options.append("⚙️ Administração")

        # Mapeia opções para páginas
        page_map = {
            "📊 Dashboard": "dashboard",
            "📝 Nova Tarefa": "register",
            "⚙️ Administração": "admin",
        }

        # Obtém página atual
        current_page = st.session_state.get("current_page", "dashboard")

        # Encontra índice da página atual
        current_index = 0
        for i, option in enumerate(menu_options):
            if page_map.get(option) == current_page:
                current_index = i
                break

        # Radio menu
        selected = st.radio(
            "Navegação",
            menu_options,
            index=current_index,
            label_visibility="collapsed",
        )

        # Atualiza página se mudou
        new_page = page_map.get(selected, "dashboard")
        if new_page != current_page:
            st.session_state["current_page"] = new_page
            st.rerun()

        st.markdown("---")

        # Botão de logout
        if st.button("🚪 Sair", use_container_width=True, type="secondary"):
            logout_user()
            st.rerun()

        st.markdown("---")
        st.caption("Sistema de Tarefas ISP v1.1")


def main():
    """Função principal da aplicação."""
    configure_page()

    # Verifica se está logado
    if not is_logged_in():
        render_login_page()
        return

    # Inicializa página atual se não existir
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "dashboard"

    # Renderiza sidebar
    render_sidebar()

    # Renderiza página atual
    current_page = st.session_state.get("current_page", "dashboard")

    if current_page == "register":
        render_register_task_page()
    elif current_page == "dashboard":
        render_dashboard_page()
    elif current_page == "admin" and is_admin():
        render_admin_page()
    else:
        render_dashboard_page()


if __name__ == "__main__":
    main()
