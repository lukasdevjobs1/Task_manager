"""
ISP Manager — Sistema de Gerenciamento de Tarefas para Provedores de Internet
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.authentication import (
    is_logged_in,
    is_admin,
    is_super_admin,
    logout_user,
    get_current_user,
)
from views.login import render_login_page
from views.dashboard_supabase import render_dashboard_page
from views.admin import render_admin_page
from views.task_details import render_task_details_page
from views.task_management import render_task_management_page
from views.notifications import render_notifications_page, get_unread_count
from views.assignment_details import render_assignment_details_page
from views.completed_tasks_manager import show_completed_tasks_manager


# ── Páginas que não têm item próprio na nav (acessadas via link) ───────────
SPECIAL_PAGES = {"task_details", "assignment_details", "manager_dashboard"}

# Mapa: nome interno → label + ícone na nav
NAV_ITEMS_USER = [
    ("dashboard",       "Dashboard",         "📊"),
    ("notifications",   "Notificações",      "🔔"),
]
NAV_ITEMS_ADMIN = [
    ("task_management", "Gerenciar Tarefas", "📋"),
    ("completed_tasks", "Concluídas",        "✅"),
    ("admin",           "Administração",     "⚙️"),
]


def configure_page():
    st.set_page_config(
        page_title="ISP Manager",
        page_icon="📡",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(
        """
        <style>
        /* ── Fontes ────────────────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"], .stMarkdown, .stText, p, span, label {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        }

        /* ── Ocultar sidebar e controles padrão ────────────────────────── */
        section[data-testid="stSidebar"]  { display: none !important; }
        [data-testid="collapsedControl"]  { display: none !important; }
        #MainMenu                         { visibility: hidden; }
        footer                            { visibility: hidden; }
        header[data-testid="stHeader"]    { display: none !important; }

        /* ── Layout geral ──────────────────────────────────────────────── */
        .stApp {
            background: #f1f5f9;
        }
        .main .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }

        /* ── Header principal ──────────────────────────────────────────── */
        .isp-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
            padding: 0 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 60px;
            position: sticky;
            top: 0;
            z-index: 999;
            box-shadow: 0 2px 12px rgba(0,0,0,0.3);
        }
        .isp-brand {
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
        }
        .isp-brand-icon {
            font-size: 22px;
        }
        .isp-brand-name {
            font-size: 17px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.3px;
        }
        .isp-brand-sub {
            font-size: 11px;
            color: #94a3b8;
            margin-left: 4px;
        }
        .isp-user-area {
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .isp-company-badge {
            background: rgba(59,130,246,0.2);
            border: 1px solid rgba(59,130,246,0.4);
            color: #93c5fd;
            font-size: 12px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 20px;
            letter-spacing: 0.3px;
        }
        .isp-user-name {
            font-size: 13px;
            font-weight: 500;
            color: #cbd5e1;
        }
        .isp-user-role {
            font-size: 11px;
            color: #64748b;
        }

        /* ── Barra de navegação ────────────────────────────────────────── */

        /* Container branco da navbar */
        div[data-testid="stHorizontalBlock"].isp-nav-row > div {
            padding: 0 !important;
        }

        /* Radio horizontal como nav pills */
        [data-testid="stRadio"] > div[role="radiogroup"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 2px !important;
            align-items: center;
        }

        /* Cada opção do radio */
        [data-testid="stRadio"] label {
            padding: 7px 15px !important;
            border-radius: 8px !important;
            transition: background 0.15s, color 0.15s !important;
            cursor: pointer !important;
            margin: 0 !important;
        }

        /* Texto de cada opção */
        [data-testid="stRadio"] label p {
            font-size: 13.5px !important;
            font-weight: 500 !important;
            color: #475569 !important;
            margin: 0 !important;
            white-space: nowrap;
        }

        /* Esconde o círculo do radio */
        [data-testid="stRadio"] label > div:first-of-type {
            display: none !important;
        }

        /* Hover */
        [data-testid="stRadio"] label:hover {
            background: #f1f5f9 !important;
        }
        [data-testid="stRadio"] label:hover p {
            color: #1e293b !important;
        }

        /* Estado ativo (selecionado) */
        [data-testid="stRadio"] label:has(input:checked) {
            background: #eff6ff !important;
        }
        [data-testid="stRadio"] label:has(input:checked) p {
            color: #2563eb !important;
            font-weight: 600 !important;
        }

        /* Label do widget radio (ocultar) */
        [data-testid="stRadio"] > [data-testid="stWidgetLabel"] {
            display: none !important;
        }

        /* Botão logout estilizado como nav */
        div.nav-logout .stButton > button {
            background: transparent !important;
            border: 1px solid #e2e8f0 !important;
            color: #64748b !important;
            border-radius: 8px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            padding: 6px 14px !important;
            height: auto !important;
        }
        div.nav-logout .stButton > button:hover {
            background: #fef2f2 !important;
            color: #dc2626 !important;
            border-color: #fca5a5 !important;
        }

        /* ── Conteúdo ──────────────────────────────────────────────────── */
        .isp-content {
            padding: 1.5rem 2rem;
        }

        /* ── Cards / KPIs ──────────────────────────────────────────────── */
        div[data-testid="metric-container"] {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1rem 1.25rem !important;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.7rem !important;
            font-weight: 700;
            color: #0f172a;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.78rem !important;
            font-weight: 500;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* ── Títulos ────────────────────────────────────────────────────── */
        h1 { font-size: 1.5rem !important; font-weight: 700; color: #0f172a; }
        h2 { font-size: 1.2rem !important; font-weight: 600; color: #1e293b; }
        h3 { font-size: 1rem  !important; font-weight: 600; color: #334155; }

        /* ── Tabs do Streamlit ──────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            background: transparent;
            border-bottom: 2px solid #e2e8f0;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 8px 18px;
            font-size: 13.5px;
            font-weight: 500;
            color: #64748b;
            background: transparent;
        }
        .stTabs [aria-selected="true"] {
            background: #eff6ff !important;
            color: #2563eb !important;
            font-weight: 600;
        }

        /* ── Dataframes ────────────────────────────────────────────────── */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #e2e8f0;
        }

        /* ── Botões ─────────────────────────────────────────────────────── */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
            font-size: 13.5px;
            transition: all 0.15s;
        }
        .stButton > button[kind="primary"] {
            background: #2563eb;
            border-color: #2563eb;
        }
        .stButton > button[kind="primary"]:hover {
            background: #1d4ed8;
            border-color: #1d4ed8;
        }

        /* ── Inputs ────────────────────────────────────────────────────── */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stTextArea > div > div > textarea {
            border-radius: 8px;
            border-color: #e2e8f0;
            font-size: 14px;
        }

        /* ── Divider ────────────────────────────────────────────────────── */
        hr {
            border-color: #e2e8f0;
            margin: 1rem 0;
        }

        /* ── Expanders ──────────────────────────────────────────────────── */
        .streamlit-expanderHeader {
            background: #f8fafc;
            border-radius: 8px;
            font-weight: 500;
            color: #334155;
        }

        /* ── Alertas / Info boxes ───────────────────────────────────────── */
        .stAlert {
            border-radius: 10px;
        }

        /* ── Separador de página ────────────────────────────────────────── */
        .isp-page-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.25rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #e2e8f0;
        }
        .isp-page-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: #0f172a;
        }

        /* ── Responsivo ─────────────────────────────────────────────────── */
        @media (max-width: 768px) {
            .isp-header        { padding: 0 1rem; }
            .isp-navbar        { padding: 0 0.5rem; gap: 2px; overflow-x: auto; }
            .isp-nav-item      { padding: 6px 10px; font-size: 12px; }
            .isp-content       { padding: 1rem; }
            .isp-brand-sub     { display: none; }
            .isp-company-badge { display: none; }
            div[data-testid="stMetricValue"] { font-size: 1.3rem !important; }
        }
        @media (max-width: 480px) {
            .isp-nav-item span.nav-label { display: none; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_topbar(user: dict, unread: int):
    """Header visual (HTML — apenas estético)."""
    role_badge = ""
    if is_super_admin():
        role_badge = '<span class="isp-company-badge">Super Admin</span>'
    elif is_admin():
        role_badge = f'<span class="isp-company-badge">{user["company_name"]}</span>'
    else:
        role_badge = f'<span class="isp-company-badge">{user["company_name"]}</span>'

    st.markdown(
        f"""
        <div class="isp-header">
            <div class="isp-brand">
                <span class="isp-brand-icon">📡</span>
                <span class="isp-brand-name">ISP Manager</span>
                <span class="isp-brand-sub">Sistema de Tarefas</span>
            </div>
            <div class="isp-user-area">
                {role_badge}
                <div>
                    <div class="isp-user-name">{user['full_name']}</div>
                    <div class="isp-user-role">Equipe {user['team'].capitalize()}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_navbar(user: dict, unread: int):
    """Barra de navegação horizontal com radio pills + botão logout."""
    current_page = st.session_state.get("current_page", "dashboard")
    if current_page in SPECIAL_PAGES:
        current_page = "dashboard"

    nav_items = list(NAV_ITEMS_USER)
    if is_admin():
        nav_items += NAV_ITEMS_ADMIN

    # Monta labels e mapa label→page
    labels = []
    page_map = {}
    current_index = 0
    for i, (page, label, icon) in enumerate(nav_items):
        suffix = f" ({unread})" if page == "notifications" and unread > 0 else ""
        full_label = f"{icon} {label}{suffix}"
        labels.append(full_label)
        page_map[full_label] = page
        if page == current_page:
            current_index = i

    # Navbar: fundo branco, borda inferior
    st.markdown(
        "<div style='background:#fff;border-bottom:1px solid #e2e8f0;"
        "padding:8px 24px;display:flex;align-items:center;gap:8px;"
        "box-shadow:0 1px 3px rgba(0,0,0,0.05);'>",
        unsafe_allow_html=True,
    )

    col_radio, col_logout = st.columns([10, 1])

    with col_radio:
        selected = st.radio(
            "nav",
            labels,
            index=current_index,
            horizontal=True,
            label_visibility="collapsed",
            key="main_nav_radio",
        )

    with col_logout:
        st.markdown('<div class="nav-logout">', unsafe_allow_html=True)
        if st.button("🚪 Sair", key="nav_logout", use_container_width=True):
            logout_user()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Navega se mudou — compara contra a página "efetiva" (special pages → dashboard)
    new_page = page_map.get(selected, "dashboard")
    effective = st.session_state.get("current_page", "dashboard")
    if effective in SPECIAL_PAGES:
        effective = "dashboard"
    if new_page != effective:
        st.session_state["current_page"] = new_page
        st.rerun()


def main():
    configure_page()

    if not is_logged_in():
        render_login_page()
        return

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "dashboard"

    user = get_current_user()
    unread = get_unread_count(user["id"])

    # ── Header + Navbar ────────────────────────────────────────────────────
    render_topbar(user, unread)
    render_navbar(user, unread)

    # ── Conteúdo com padding ───────────────────────────────────────────────
    st.markdown('<div class="isp-content">', unsafe_allow_html=True)

    current_page = st.session_state.get("current_page", "dashboard")

    if current_page == "dashboard":
        render_dashboard_page()
    elif current_page == "notifications":
        render_notifications_page()
    elif current_page == "task_management" and is_admin():
        render_task_management_page()
    elif current_page == "completed_tasks" and is_admin():
        show_completed_tasks_manager()
    elif current_page == "admin" and is_admin():
        render_admin_page()
    elif current_page == "task_details":
        render_task_details_page()
    elif current_page == "assignment_details":
        render_assignment_details_page()
    elif current_page == "manager_dashboard" and is_admin():
        from views.manager_dashboard import render_manager_dashboard
        render_manager_dashboard()
    else:
        render_dashboard_page()

    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
