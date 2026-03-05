import streamlit as st
from database.supabase_only_connection import db
from auth.authentication import require_login, get_current_user
from datetime import datetime


def show_completed_tasks_manager():
    require_login()
    user = get_current_user()

    if not user:
        st.error("Usuário não encontrado")
        return

    st.title("Tarefas Concluídas")

    # ── Filtros ────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        date_filter = st.date_input("Filtrar por data", value=None)
    with col2:
        collaborators = _get_collaborators(user)
        collaborator_filter = st.selectbox(
            "Filtrar por colaborador", ["Todos"] + collaborators
        )

    # ── Busca ──────────────────────────────────────────────────────────────
    tasks = db.get_task_assignments(user["company_id"], status="concluida")

    if date_filter:
        tasks = [
            t for t in tasks
            if t.get("completed_at")
            and _parse_dt(t["completed_at"]).date() == date_filter
        ]

    if collaborator_filter != "Todos":
        tasks = [
            t for t in tasks
            if (t.get("assigned_to_user") or {}).get("full_name") == collaborator_filter
        ]

    # ── KPIs usando colunas estruturadas ──────────────────────────────────
    total_ctos           = sum(t.get("quantidade_cto") or 0 for t in tasks)
    total_cx_emenda      = sum(t.get("quantidade_cx_emenda") or 0 for t in tasks)
    total_fibra          = sum(float(t.get("fibra_lancada") or 0) for t in tasks)
    total_abert_cx       = sum(t.get("abertura_fechamento_cx_emenda") or 0 for t in tasks)
    total_abert_cto      = sum(t.get("abertura_fechamento_cto") or 0 for t in tasks)
    total_abert_rozeta   = sum(t.get("abertura_fechamento_rozeta") or 0 for t in tasks)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Tarefas", len(tasks))
    col2.metric("Fibra Lançada (m)", f"{total_fibra:.0f}")
    col3.metric("Qtd CTOs", int(total_ctos))
    col4.metric("Qtd Cx Emenda", int(total_cx_emenda))

    col5, col6, col7 = st.columns(3)
    col5.metric("Abert./Fech. Cx Emenda", int(total_abert_cx))
    col6.metric("Abert./Fech. CTO", int(total_abert_cto))
    col7.metric("Abert./Fech. Rozeta", int(total_abert_rozeta))

    st.divider()

    # ── Lista de tarefas ───────────────────────────────────────────────────
    if not tasks:
        st.info("Nenhuma tarefa concluída encontrada.")
        return

    for task in tasks:
        assignee = (task.get("assigned_to_user") or {}).get("full_name", "N/A")
        with st.expander(f"{task['title']} — {assignee}"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Empresa:** {task.get('empresa_nome') or '—'}")
                st.write(f"**Descrição:** {task.get('description') or '—'}")
                st.write(f"**Endereço:** {task.get('address') or '—'}")
                st.write(f"**Concluída em:** {_fmt_dt(task.get('completed_at'))}")

                if task.get("observations"):
                    st.write("**Observações:**")
                    st.text_area(
                        "",
                        task["observations"],
                        height=80,
                        disabled=True,
                        key=f"obs_{task['id']}",
                    )

                # Dados técnicos ISP
                cto          = task.get("quantidade_cto") or 0
                cx           = task.get("quantidade_cx_emenda") or 0
                fibra        = float(task.get("fibra_lancada") or 0)
                abert_cx     = task.get("abertura_fechamento_cx_emenda") or 0
                abert_cto    = task.get("abertura_fechamento_cto") or 0
                abert_rozeta = task.get("abertura_fechamento_rozeta") or 0
                if cto or cx or fibra or abert_cx or abert_cto or abert_rozeta:
                    st.write("**Dados Técnicos:**")
                    tc1, tc2, tc3 = st.columns(3)
                    tc1.metric("Qtd CTOs", cto)
                    tc2.metric("Qtd Cx Emenda", cx)
                    tc3.metric("Fibra (m)", f"{fibra:.0f}")
                    tc4, tc5, tc6 = st.columns(3)
                    tc4.metric("Abert./Fech. Cx Emenda", abert_cx)
                    tc5.metric("Abert./Fech. CTO", abert_cto)
                    tc6.metric("Abert./Fech. Rozeta", abert_rozeta)

            with col2:
                photos = db.get_assignment_photos(task["id"])
                if photos:
                    st.write(f"**Fotos ({len(photos)}):**")
                    for idx, photo in enumerate(photos):
                        url = photo.get("photo_url", "")
                        if url and not url.startswith("data:"):
                            st.image(url, caption=f"Foto {idx+1}", use_container_width=True)
                else:
                    st.caption("Sem fotos")


def _get_collaborators(user: dict) -> list:
    users = db.get_all_users(user["company_id"])
    return [u["full_name"] for u in users if u.get("role") == "user"]


def _parse_dt(dt_str: str) -> datetime:
    try:
        return datetime.fromisoformat(str(dt_str).replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return datetime.min


def _fmt_dt(dt_str) -> str:
    if not dt_str:
        return "N/A"
    try:
        return _parse_dt(dt_str).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(dt_str)
