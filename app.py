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
from views.task_details import render_task_details_page


def configure_page():
    """Configurações da página Streamlit."""
    st.set_page_config(
        page_title="Sistema de Tarefas ISP",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="auto",  # Colapsa automaticamente em mobile
    )

    # CSS customizado com otimizações para mobile
    st.markdown(
        """
        <style>
        /* Estilos gerais */
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

        /* Otimizações para Mobile */
        @media (max-width: 768px) {
            /* Reduz padding geral */
            .main {
                padding: 0.5rem;
            }

            /* Ajusta métricas para caber em tela menor */
            div[data-testid="stMetricValue"] {
                font-size: 1.2rem;
            }
            div[data-testid="stMetricLabel"] {
                font-size: 0.8rem;
            }

            /* Melhora visualização de tabelas */
            .stDataFrame {
                font-size: 0.75rem;
            }

            /* Ajusta títulos */
            h1 {
                font-size: 1.5rem !important;
            }
            h2 {
                font-size: 1.25rem !important;
            }
            h3 {
                font-size: 1.1rem !important;
            }

            /* Botões mais acessíveis em touch */
            .stButton > button {
                min-height: 48px;
                font-size: 1rem;
            }

            /* Inputs mais acessíveis */
            .stTextInput > div > div > input,
            .stSelectbox > div > div > div,
            .stNumberInput > div > div > input {
                min-height: 44px;
                font-size: 16px !important; /* Previne zoom no iOS */
            }

            /* Checkboxes maiores */
            .stCheckbox {
                padding: 8px 0;
            }

            /* Sidebar mais compacta */
            section[data-testid="stSidebar"] > div {
                padding: 1rem 0.5rem;
            }

            /* Imagens responsivas */
            .stImage {
                max-width: 100%;
            }

            /* Cards de métricas empilhados */
            div[data-testid="column"] {
                min-width: 45% !important;
            }

            /* Expanders mais acessíveis */
            .streamlit-expanderHeader {
                font-size: 1rem;
                padding: 0.75rem;
            }

            /* File uploader otimizado */
            .stFileUploader > div {
                padding: 1rem;
            }
        }

        /* Telas muito pequenas (smartphones) */
        @media (max-width: 480px) {
            .main {
                padding: 0.25rem;
            }

            h1 {
                font-size: 1.3rem !important;
            }

            /* Métricas em coluna única */
            div[data-testid="column"] {
                min-width: 100% !important;
            }

            /* Tabelas com scroll horizontal */
            .stDataFrame > div {
                overflow-x: auto;
            }
        }

        /* Melhoria de touch targets */
        @media (hover: none) and (pointer: coarse) {
            .stButton > button,
            .stDownloadButton > button {
                min-height: 48px;
                padding: 12px 24px;
            }

            .stRadio > div > label {
                padding: 12px 8px;
                min-height: 44px;
            }
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

        # Páginas especiais que não estão no menu (como task_details)
        special_pages = ["task_details"]
        is_special_page = current_page in special_pages

        # Encontra índice da página atual (ou usa dashboard se for página especial)
        current_index = 0
        display_page = "dashboard" if is_special_page else current_page
        for i, option in enumerate(menu_options):
            if page_map.get(option) == display_page:
                current_index = i
                break

        # Radio menu
        selected = st.radio(
            "Navegação",
            menu_options,
            index=current_index,
            label_visibility="collapsed",
        )

        # Atualiza página se mudou (mas só se o usuário realmente clicou em uma opção diferente)
        new_page = page_map.get(selected, "dashboard")
        # Se está em página especial, só muda se o usuário escolheu algo diferente do dashboard
        if is_special_page:
            if new_page != "dashboard":
                st.session_state["current_page"] = new_page
                st.rerun()
        elif new_page != current_page:
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

    # Debug: mostra página atual (remover depois)
    st.sidebar.caption(f"Página: {current_page}")

    if current_page == "register":
        render_register_task_page()
    elif current_page == "dashboard":
        render_dashboard_page()
    elif current_page == "task_details":
        render_task_details_page()
    elif current_page == "admin" and is_admin():
        render_admin_page()
    else:
        render_dashboard_page()


if __name__ == "__main__":
    main()
