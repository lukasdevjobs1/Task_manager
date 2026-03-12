import streamlit as st
import pandas as pd
from database.supabase_only_connection import db
from auth.authentication import require_login, get_current_user
from datetime import datetime
from utils.export import export_to_excel, export_to_pdf


def _fmt_fibra(metros: float) -> str:
    if metros >= 1000:
        km = metros / 1000
        return f"{km:.0f} km" if km == int(km) else f"{km:.2f} km"
    return f"{metros:.0f} m"


PAGE_SIZE = 15


def _pagination_controls(page_key: str, total: int, reset_key: str = None) -> int:
    """Controles de paginação. Retorna página atual (0-indexed)."""
    total_pages = max(1, -(-total // PAGE_SIZE))
    page = st.session_state.get(page_key, 0)
    page = min(page, total_pages - 1)

    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        if st.button("← Anterior", key=f"{page_key}_prev", disabled=page == 0, use_container_width=True):
            st.session_state[page_key] = page - 1
            st.rerun()
    with c2:
        start_n = page * PAGE_SIZE + 1
        end_n = min((page + 1) * PAGE_SIZE, total)
        st.caption(f"Mostrando {start_n}–{end_n} de {total} tarefas  |  Página {page + 1}/{total_pages}")
    with c3:
        if st.button("Próximo →", key=f"{page_key}_next", disabled=page >= total_pages - 1, use_container_width=True):
            st.session_state[page_key] = page + 1
            st.rerun()
    return page


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

    # ── KPIs ──────────────────────────────────────────────────────────────
    total_ctos           = sum(t.get("quantidade_cto") or 0 for t in tasks)
    total_cx_emenda      = sum(t.get("quantidade_cx_emenda") or 0 for t in tasks)
    total_fibra          = sum(float(t.get("fibra_lancada") or 0) for t in tasks)
    total_abert_cx       = sum(t.get("abertura_fechamento_cx_emenda") or 0 for t in tasks)
    total_abert_cto      = sum(t.get("abertura_fechamento_cto") or 0 for t in tasks)
    total_abert_rozeta   = sum(t.get("abertura_fechamento_rozeta") or 0 for t in tasks)

    if collaborator_filter != "Todos":
        st.subheader(f"Resumo — {collaborator_filter}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Tarefas", len(tasks))
    col2.metric("Fibra Lançada", _fmt_fibra(total_fibra))
    col3.metric("Qtd CTOs", int(total_ctos))
    col4.metric("Qtd Cx Emenda", int(total_cx_emenda))

    col5, col6, col7 = st.columns(3)
    col5.metric("Abert./Fech. Cx Emenda", int(total_abert_cx))
    col6.metric("Abert./Fech. CTO", int(total_abert_cto))
    col7.metric("Abert./Fech. Rozeta", int(total_abert_rozeta))

    st.divider()

    if not tasks:
        st.info("Nenhuma tarefa concluída encontrada.")
        return

    # ── Exportação ─────────────────────────────────────────────────────────
    prefix = collaborator_filter.replace(" ", "_") if collaborator_filter != "Todos" else "tarefas_concluidas"
    title  = f"Tarefas Concluídas — {collaborator_filter}" if collaborator_filter != "Todos" else "Tarefas Concluídas"
    _render_export_buttons(tasks, title, prefix)

    st.divider()

    # ── Visualização por colaborador: tabela detalhada ─────────────────────
    if collaborator_filter != "Todos":
        _show_user_table(tasks, collaborator_filter)
        return

    # ── Visualização geral: expanders ──────────────────────────────────────
    # reset de página quando filtros mudam
    filter_sig = f"{date_filter}|{collaborator_filter}"
    if st.session_state.get("_ct_filter_sig") != filter_sig:
        st.session_state["_ct_filter_sig"] = filter_sig
        st.session_state["ct_page"] = 0

    page = _pagination_controls("ct_page", len(tasks))
    page_tasks = tasks[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]

    for task in page_tasks:
        assignee = (task.get("assigned_to_user") or {}).get("full_name", "N/A")
        with st.expander(f"{task['title']} — {assignee}"):
            _render_task_expander(task)


def _build_export_df(tasks: list) -> pd.DataFrame:
    """DataFrame completo usado na exportação Excel e PDF."""
    rows = []
    for t in tasks:
        fibra = float(t.get("fibra_lancada") or 0)
        assignee = (t.get("assigned_to_user") or {}).get("full_name", "N/A")
        rows.append({
            "Colaborador":            assignee,
            "Empresa":                t.get("empresa_nome") or "—",
            "Título":                 t.get("title") or "—",
            "Endereço":               t.get("address") or "—",
            "Concluída em":           _fmt_dt(t.get("completed_at")),
            "Fibra Lançada (m)":      fibra,
            "Qtd CTOs":               int(t.get("quantidade_cto") or 0),
            "Qtd Cx Emenda":          int(t.get("quantidade_cx_emenda") or 0),
            "Abert./Fech. Cx Emenda": int(t.get("abertura_fechamento_cx_emenda") or 0),
            "Abert./Fech. CTO":       int(t.get("abertura_fechamento_cto") or 0),
            "Abert./Fech. Rozeta":    int(t.get("abertura_fechamento_rozeta") or 0),
            "Observações":            t.get("observations") or "—",
        })
    return pd.DataFrame(rows)


def _render_export_buttons(tasks: list, title: str, filename_prefix: str) -> None:
    """Renderiza botões de download Excel e PDF com todas as métricas."""
    if not tasks:
        return
    now = datetime.now()
    df = _build_export_df(tasks)
    col_excel, col_pdf, _ = st.columns([1, 1, 5])
    with col_excel:
        excel_bytes = export_to_excel(df, title)
        if excel_bytes:
            st.download_button(
                label="📥 Excel",
                data=excel_bytes,
                file_name=f"{filename_prefix}_{now.strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
    with col_pdf:
        pdf_bytes = export_to_pdf(df, title, now.year, now.month)
        if pdf_bytes:
            st.download_button(
                label="📄 PDF",
                data=pdf_bytes,
                file_name=f"{filename_prefix}_{now.strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )


def _show_user_table(tasks: list, collaborator_name: str):
    """Tabela completa com todas as tarefas de um colaborador específico."""

    # Monta DataFrame
    rows = []
    for t in tasks:
        fibra = float(t.get("fibra_lancada") or 0)
        rows.append({
            "ID": t["id"],
            "Título": t.get("title") or "—",
            "Empresa": t.get("empresa_nome") or "—",
            "Endereço": t.get("address") or "—",
            "Concluída em": _fmt_dt(t.get("completed_at")),
            "Fibra Lançada": _fmt_fibra(fibra),
            "Fibra (m)": fibra,
            "Qtd CTOs": int(t.get("quantidade_cto") or 0),
            "Qtd Cx Emenda": int(t.get("quantidade_cx_emenda") or 0),
            "Abert./Fech. Cx": int(t.get("abertura_fechamento_cx_emenda") or 0),
            "Abert./Fech. CTO": int(t.get("abertura_fechamento_cto") or 0),
            "Abert./Fech. Rozeta": int(t.get("abertura_fechamento_rozeta") or 0),
        })

    df = pd.DataFrame(rows)

    st.subheader(f"Tarefas de {collaborator_name} ({len(tasks)})")

    # Tabela interativa — oculta colunas auxiliares (ID, Fibra (m))
    display_cols = [c for c in df.columns if c not in ("ID", "Fibra (m)")]
    st.dataframe(
        df[display_cols],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # ── Detalhes da tarefa selecionada ──────────────────────────────────
    st.subheader("Detalhes da tarefa")

    task_options = {f"{r['Título']} — {r['Concluída em']}": r["ID"] for r in rows}
    selected_label = st.selectbox("Selecione uma tarefa para ver detalhes:", list(task_options.keys()))

    if selected_label:
        selected_id = task_options[selected_label]
        task = next((t for t in tasks if t["id"] == selected_id), None)
        if task:
            col1, col2 = st.columns([2, 1])
            with col1:
                _render_task_expander(task)
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


def _render_task_expander(task: dict):
    """Renderiza os dados de uma tarefa (usado nos expanders e na view de detalhe)."""
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
            tc3.metric("Fibra", _fmt_fibra(fibra))
            tc4, tc5, tc6 = st.columns(3)
            tc4.metric("Abert./Fech. Cx Emenda", abert_cx)
            tc5.metric("Abert./Fech. CTO", abert_cto)
            tc6.metric("Abert./Fech. Rozeta", abert_rozeta)

    with col2:
        materiais = db.get_task_materials(task["id"])
        if materiais:
            st.write(f"**Materiais ({len(materiais)}):**")
            for m in materiais:
                qty = m.get("quantity") or 1
                unit = m.get("unit") or "un"
                name = m.get("material_name") or "—"
                qty_fmt = int(qty) if float(qty) == int(qty) else qty
                st.write(f"• {qty_fmt} {unit} — {name}")
        elif task.get("materials"):
            st.write("**Materiais:**")
            st.text(task["materials"])

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
