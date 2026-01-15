"""
Sistema de Gerenciamento de Tarefas - Provedor de Internet
Aplicação principal Streamlit com navegação entre páginas.
"""

import streamlit as st
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.authentication import is_logged_in, is_admin, logout_user, get_current_user
from pages.login import render_login_page
from pages.register_task import render_register_task_page
from pages.dashboard import render_dashboard_page
from pages.admin import render_admin_page


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
        .sidebar .sidebar-content {
            background-color: #f5f5f5;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    """Renderiza a barra lateral com navegação."""
    user = get_current_user()

    with st.sidebar:
        st.title("📋 Sistema de Tarefas")
        st.markdown("---")

        # Informações do usuário e empresa
        st.markdown(f"**Empresa:** {user['company_name']}")
        st.markdown(f"**Usuário:** {user['full_name']}")
        st.markdown(f"**Equipe:** {user['team'].capitalize()}")
        if is_admin():
            st.markdown("**Perfil:** Administrador")
        st.markdown("---")

        # Menu de navegação
        st.subheader("Menu")

        # Opções de navegação
        pages = {
            "📝 Registrar Tarefa": "register",
            "📊 Dashboard": "dashboard",
        }

        if is_admin():
            pages["⚙️ Administração"] = "admin"

        # Botões de navegação
        for label, page_key in pages.items():
            if st.button(label, use_container_width=True, key=f"nav_{page_key}"):
                st.session_state["current_page"] = page_key
                st.rerun()

        st.markdown("---")

        # Botão de logout
        if st.button("🚪 Sair", use_container_width=True, type="secondary"):
            logout_user()
            st.rerun()

        st.markdown("---")
        st.caption("Sistema de Gerenciamento de Tarefas")
        st.caption("Provedor de Internet v1.0")


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
