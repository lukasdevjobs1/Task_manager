"""
Detalhes completos de uma tarefa — informações, dados técnicos ISP,
fotos da execução e ações de gerenciamento (admin).
"""

import streamlit as st
from datetime import datetime

from auth.authentication import require_login, get_current_user, is_admin
from database.supabase_only_connection import db
from utils.push_notification import notify_task_assigned
import os


# ── Helpers ────────────────────────────────────────────────────────────────

STATUS_LABEL = {
    "pendente":    ("Pendente",    "#f59e0b", "#fffbeb"),
    "em_andamento":("Em Andamento","#3b82f6", "#eff6ff"),
    "concluida":   ("Concluída",   "#22c55e", "#f0fdf4"),
}
PRIORITY_LABEL = {
    "baixa": ("Baixa", "#22c55e"),
    "media": ("Média", "#f59e0b"),
    "alta":  ("Alta",  "#ef4444"),
}


def _fmt_dt(dt_str) -> str:
    if not dt_str:
        return "—"
    try:
        dt = datetime.fromisoformat(str(dt_str).replace("Z", "+00:00")).replace(tzinfo=None)
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(dt_str)[:16]


def _badge(text: str, color: str, bg: str) -> str:
    return (
        f'<span style="background:{bg};color:{color};border:1px solid {color}33;'
        f'padding:3px 12px;border-radius:20px;font-size:12px;font-weight:600;">'
        f'{text}</span>'
    )


def _info_row(label: str, value: str):
    st.markdown(
        f'<div style="display:flex;gap:8px;padding:6px 0;border-bottom:1px solid #f1f5f9;">'
        f'<span style="min-width:160px;font-size:13px;color:#64748b;font-weight:500;">{label}</span>'
        f'<span style="font-size:13px;color:#0f172a;">{value}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _section(title: str):
    st.markdown(
        f'<p style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;'
        f'letter-spacing:1px;margin:16px 0 8px;">{title}</p>',
        unsafe_allow_html=True,
    )


def _card_open(padding="20px"):
    st.markdown(
        f'<div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;'
        f'padding:{padding};margin-bottom:16px;box-shadow:0 1px 4px rgba(0,0,0,0.04);">',
        unsafe_allow_html=True,
    )


def _card_close():
    st.markdown("</div>", unsafe_allow_html=True)


# ── Página principal ────────────────────────────────────────────────────────

def render_assignment_details_page():
    require_login()
    user = get_current_user()

    assignment_id = st.session_state.get("selected_assignment_id")
    if not assignment_id:
        st.warning("Nenhuma tarefa selecionada.")
        if st.button("← Voltar ao Dashboard"):
            st.session_state["current_page"] = "dashboard"
            st.rerun()
        return

    task = db.get_task_assignment_by_id(assignment_id, user["company_id"])
    if not task:
        st.error("Tarefa não encontrada.")
        if st.button("← Voltar"):
            st.session_state["current_page"] = "dashboard"
            st.rerun()
        return

    # Permissão
    can_view = (
        task.get("assigned_to") == user["id"]
        or task.get("assigned_by") == user["id"]
        or is_admin()
    )
    if not can_view:
        st.error("Sem permissão para ver esta tarefa.")
        return

    # ── Header da página ────────────────────────────────────────────────────
    col_back, col_title = st.columns([1, 10])
    with col_back:
        back_page = st.session_state.pop("assignment_details_back", "dashboard")
        if st.button("← Voltar", key="btn_back"):
            st.session_state["current_page"] = back_page
            st.rerun()

    status_info   = STATUS_LABEL.get(task.get("status", ""), ("—", "#64748b", "#f8fafc"))
    priority_info = PRIORITY_LABEL.get(task.get("priority", ""), ("—", "#64748b"))

    st.markdown(
        f'<div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;'
        f'padding:20px 24px;margin-bottom:20px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">'
        f'<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;">'
        f'<div>'
        f'<h2 style="margin:0 0 8px;font-size:1.25rem;color:#0f172a;">{task["title"]}</h2>'
        f'<div style="display:flex;gap:8px;flex-wrap:wrap;">'
        f'{_badge(status_info[0], status_info[1], status_info[2])}'
        f'{_badge("Prioridade " + priority_info[0], priority_info[1], priority_info[1] + "15")}'
        + (f'{_badge(task["empresa_nome"], "#6366f1", "#eef2ff")}' if task.get("empresa_nome") else "")
        + f'</div></div>'
        f'<div style="text-align:right;font-size:12px;color:#94a3b8;">ID #{task["id"]}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── Tabs ────────────────────────────────────────────────────────────────
    tabs = ["Informações", "Dados Técnicos", "Fotos"]
    if is_admin() or task.get("assigned_by") == user["id"]:
        tabs.append("Gerenciamento")

    tab_list = st.tabs(tabs)

    # ── TAB 1: Informações ───────────────────────────────────────────────────
    with tab_list[0]:
        col1, col2 = st.columns(2)

        with col1:
            _section("Atribuição")
            _card_open()
            assigner = (task.get("assigned_by_user") or {}).get("full_name", "—")
            assignee = (task.get("assigned_to_user") or {}).get("full_name", "Caixa da Empresa")
            _info_row("Criada por", assigner)
            _info_row("Atribuída a", assignee)
            _info_row("Criada em", _fmt_dt(task.get("created_at")))
            _info_row("Atualizada em", _fmt_dt(task.get("updated_at")))
            if task.get("started_at"):
                _info_row("Iniciada em", _fmt_dt(task["started_at"]))
            if task.get("completed_at"):
                _info_row("Concluída em", _fmt_dt(task["completed_at"]))
            if task.get("due_date"):
                _info_row("Prazo", _fmt_dt(task["due_date"]))
            _card_close()

        with col2:
            _section("Localização")
            _card_open()
            _info_row("Endereço", task.get("address") or "—")
            if task.get("latitude") and task.get("longitude"):
                _info_row("Coordenadas", f'{task["latitude"]}, {task["longitude"]}')
                maps_url = f'https://www.google.com/maps?q={task["latitude"]},{task["longitude"]}'
                st.markdown(
                    f'<a href="{maps_url}" target="_blank" style="display:inline-flex;'
                    f'align-items:center;gap:6px;margin-top:8px;padding:7px 16px;'
                    f'background:#eff6ff;color:#2563eb;border:1px solid #bfdbfe;'
                    f'border-radius:8px;font-size:13px;font-weight:500;text-decoration:none;">'
                    f'🗺️ Abrir no Google Maps</a>',
                    unsafe_allow_html=True,
                )
            _card_close()

        if task.get("description"):
            _section("Descrição")
            _card_open("16px 20px")
            st.markdown(
                f'<p style="font-size:14px;color:#334155;line-height:1.6;margin:0;">'
                f'{task["description"]}</p>',
                unsafe_allow_html=True,
            )
            _card_close()

        if task.get("observations"):
            _section("Observações do técnico")
            _card_open("16px 20px")
            st.markdown(
                f'<p style="font-size:14px;color:#334155;line-height:1.6;margin:0;">'
                f'{task["observations"]}</p>',
                unsafe_allow_html=True,
            )
            _card_close()

    # ── TAB 2: Dados Técnicos ISP ─────────────────────────────────────────────
    with tab_list[1]:
        isp_fields = [
            ("Abert./Fech. Cx Emenda", task.get("abertura_fechamento_cx_emenda") or 0, ""),
            ("Abert./Fech. CTO",        task.get("abertura_fechamento_cto") or 0,       ""),
            ("Abert./Fech. Rozeta",     task.get("abertura_fechamento_rozeta") or 0,    ""),
            ("Qtd CTO",                 task.get("quantidade_cto") or 0,               ""),
            ("Qtd Cx de Emenda",        task.get("quantidade_cx_emenda") or 0,         ""),
            ("Fibra Lançada",           task.get("fibra_lancada") or 0,                "m"),
        ]

        has_data = any(v[1] > 0 for v in isp_fields)

        if has_data:
            _section("Métricas de Campo")
            cols = st.columns(3)
            for i, (label, value, unit) in enumerate(isp_fields):
                with cols[i % 3]:
                    display = f"{float(value):.0f} {unit}".strip() if unit else str(int(value))
                    st.markdown(
                        f'<div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;'
                        f'padding:16px 20px;text-align:center;margin-bottom:12px;">'
                        f'<div style="font-size:1.5rem;font-weight:700;color:#0f172a;">{display}</div>'
                        f'<div style="font-size:11px;font-weight:600;color:#64748b;'
                        f'text-transform:uppercase;letter-spacing:0.5px;margin-top:4px;">{label}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.markdown(
                '<div style="background:#f8fafc;border:1px dashed #e2e8f0;border-radius:12px;'
                'padding:40px;text-align:center;">'
                '<p style="color:#94a3b8;font-size:14px;margin:0;">Nenhum dado técnico preenchido ainda.</p>'
                '<p style="color:#cbd5e1;font-size:12px;margin:6px 0 0;">O técnico preenche estes campos ao executar a tarefa no app.</p>'
                '</div>',
                unsafe_allow_html=True,
            )

    # ── TAB 3: Fotos ──────────────────────────────────────────────────────────
    with tab_list[2]:
        photos = db.get_assignment_photos(assignment_id)

        if photos:
            _section(f"{len(photos)} foto(s) anexada(s)")
            cols = st.columns(3)
            for i, photo in enumerate(photos):
                url = photo.get("photo_url", "")
                if url and not url.startswith("data:"):
                    with cols[i % 3]:
                        st.image(
                            url,
                            caption=photo.get("original_name") or f"Foto {i+1}",
                            use_container_width=True,
                        )
        else:
            st.markdown(
                '<div style="background:#f8fafc;border:1px dashed #e2e8f0;border-radius:12px;'
                'padding:40px;text-align:center;">'
                '<p style="color:#94a3b8;font-size:14px;margin:0;">Nenhuma foto anexada ainda.</p>'
                '</div>',
                unsafe_allow_html=True,
            )

    # ── TAB 4: Gerenciamento (admin/gerente) ────────────────────────────────
    if len(tab_list) == 4:
        with tab_list[3]:
            _section("Alterar Status")
            _card_open()
            status_map = {
                "pendente":     "Pendente",
                "em_andamento": "Em Andamento",
                "concluida":    "Concluída",
            }
            current_status = task.get("status", "pendente")
            keys = list(status_map.keys())
            new_status = st.selectbox(
                "Status atual",
                options=keys,
                format_func=lambda x: status_map[x],
                index=keys.index(current_status) if current_status in keys else 0,
                key="mgmt_status",
            )
            if st.button("Salvar Status", type="primary", key="btn_save_status"):
                if new_status != current_status:
                    ok, msg = db.update_task_status(assignment_id, new_status)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.info("Status não alterado.")
            _card_close()

            _section("Reatribuir Tarefa")
            _card_open()
            all_users = db.get_all_users(user["company_id"])
            available = [u for u in all_users if u.get("active") and u.get("role") != "admin"]
            if available:
                user_opts = {f"{u['full_name']} ({u['team'].capitalize()})": u["id"] for u in available}
                selected_label = st.selectbox("Atribuir para:", list(user_opts.keys()), key="mgmt_reassign")
                if st.button("Confirmar Reatribuição", key="btn_reassign"):
                    new_uid = user_opts[selected_label]
                    db.client.table("task_assignments").update(
                        {"assigned_to": new_uid}
                    ).eq("id", assignment_id).execute()
                    db.create_notification(
                        user_id=new_uid,
                        company_id=user["company_id"],
                        type="task_assigned",
                        title="Tarefa Reatribuída",
                        message=f'{user["full_name"]} reatribuiu: {task["title"]}',
                        reference_id=assignment_id,
                    )
                    try:
                        assigned_user = db.get_user_by_id(new_uid)
                        if assigned_user and assigned_user.get("push_token"):
                            notify_task_assigned(
                                user_push_token=assigned_user["push_token"],
                                task_id=assignment_id,
                                task_title=task["title"],
                                assigned_by_name=user["full_name"],
                                server_key=os.environ.get("FCM_SERVER_KEY"),
                            )
                    except Exception:
                        pass
                    st.success("Tarefa reatribuída!")
                    st.rerun()
            _card_close()

            _section("Devolver à Caixa da Empresa")
            _card_open()
            st.markdown(
                '<p style="font-size:13px;color:#64748b;">A tarefa volta a ficar disponível para ser atribuída.</p>',
                unsafe_allow_html=True,
            )
            if st.button("Devolver à caixa", key="btn_unassign"):
                db.client.table("task_assignments").update(
                    {"assigned_to": None}
                ).eq("id", assignment_id).execute()
                st.success("Tarefa devolvida à caixa da empresa!")
                st.session_state["current_page"] = "task_management"
                st.rerun()
            _card_close()

            _section("Zona de Perigo")
            _card_open()
            st.markdown(
                '<p style="font-size:13px;color:#ef4444;">Esta ação é irreversível. Todas as fotos e dados serão removidos.</p>',
                unsafe_allow_html=True,
            )
            confirm = st.checkbox("Confirmo que desejo excluir permanentemente esta tarefa", key="chk_delete")
            if confirm:
                if st.button("Excluir Tarefa", type="secondary", key="btn_delete"):
                    try:
                        photos_to_del = db.get_assignment_photos(assignment_id)
                        for p in photos_to_del:
                            db.client.table("assignment_photos").delete().eq("id", p["id"]).execute()
                        db.client.table("task_assignments").delete().eq(
                            "id", assignment_id
                        ).eq("company_id", user["company_id"]).execute()
                        st.success("Tarefa excluída.")
                        st.session_state["current_page"] = "dashboard"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir: {e}")
            _card_close()
