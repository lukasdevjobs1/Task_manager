"""
Página de detalhes da tarefa com visualização de fotos e opções de edição/exclusão.
"""

import streamlit as st
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentication import require_login, get_current_user, is_admin
from database.connection import SessionLocal
from database.models import Task, User
from utils.file_handler import (
    get_task_photos,
    delete_task_photos,
    delete_single_photo,
    save_uploaded_files,
    format_file_size,
)
from config import TIPOS_FIBRA, MAX_FILES_PER_TASK


def get_task_by_id(task_id: int, company_id: int) -> dict:
    """Retorna uma tarefa pelo ID."""
    session = SessionLocal()
    try:
        task = session.query(Task, User.full_name).join(User).filter(
            Task.id == task_id,
            Task.company_id == company_id
        ).first()

        if not task:
            return None

        t, user_name = task
        return {
            "id": t.id,
            "user_id": t.user_id,
            "user_name": user_name,
            "empresa": t.empresa,
            "bairro": t.bairro,
            "abertura_caixa_emenda": t.abertura_caixa_emenda,
            "fechamento_caixa_emenda": t.fechamento_caixa_emenda,
            "abertura_cto": t.abertura_cto,
            "fechamento_cto": t.fechamento_cto,
            "abertura_rozeta": t.abertura_rozeta,
            "fechamento_rozeta": t.fechamento_rozeta,
            "qtd_cto": t.qtd_cto,
            "qtd_caixa_emenda": t.qtd_caixa_emenda,
            "tipo_fibra": t.tipo_fibra,
            "fibra_lancada": float(t.fibra_lancada) if t.fibra_lancada else 0,
            "observacoes": t.observacoes,
            "created_at": t.created_at,
        }
    finally:
        session.close()


def update_task(task_id: int, company_id: int, data: dict) -> tuple[bool, str]:
    """Atualiza os dados de uma tarefa."""
    session = SessionLocal()
    try:
        task = session.query(Task).filter(
            Task.id == task_id,
            Task.company_id == company_id
        ).first()

        if not task:
            return False, "Tarefa não encontrada."

        # Atualiza campos
        task.empresa = data.get("empresa", task.empresa)
        task.bairro = data.get("bairro", task.bairro)
        task.abertura_caixa_emenda = data.get("abertura_caixa_emenda", task.abertura_caixa_emenda)
        task.fechamento_caixa_emenda = data.get("fechamento_caixa_emenda", task.fechamento_caixa_emenda)
        task.abertura_cto = data.get("abertura_cto", task.abertura_cto)
        task.fechamento_cto = data.get("fechamento_cto", task.fechamento_cto)
        task.abertura_rozeta = data.get("abertura_rozeta", task.abertura_rozeta)
        task.fechamento_rozeta = data.get("fechamento_rozeta", task.fechamento_rozeta)
        task.qtd_cto = data.get("qtd_cto", task.qtd_cto)
        task.qtd_caixa_emenda = data.get("qtd_caixa_emenda", task.qtd_caixa_emenda)
        task.tipo_fibra = data.get("tipo_fibra", task.tipo_fibra)
        task.fibra_lancada = data.get("fibra_lancada", task.fibra_lancada)
        task.observacoes = data.get("observacoes", task.observacoes)

        session.commit()
        return True, "Tarefa atualizada com sucesso!"
    except Exception as e:
        session.rollback()
        return False, f"Erro ao atualizar tarefa: {str(e)}"
    finally:
        session.close()


def delete_task(task_id: int, company_id: int) -> tuple[bool, str]:
    """Exclui uma tarefa e suas fotos."""
    session = SessionLocal()
    try:
        task = session.query(Task).filter(
            Task.id == task_id,
            Task.company_id == company_id
        ).first()

        if not task:
            return False, "Tarefa não encontrada."

        # Primeiro exclui as fotos do Supabase
        delete_task_photos(task_id)

        # Depois exclui a tarefa
        session.delete(task)
        session.commit()
        return True, "Tarefa excluída com sucesso!"
    except Exception as e:
        session.rollback()
        return False, f"Erro ao excluir tarefa: {str(e)}"
    finally:
        session.close()


def render_task_details_page():
    """Renderiza a página de detalhes da tarefa."""
    require_login()
    user = get_current_user()

    # Verifica se há uma tarefa selecionada
    task_id = st.session_state.get("selected_task_id")

    if not task_id:
        st.warning("Nenhuma tarefa selecionada.")
        if st.button("Voltar ao Dashboard"):
            st.session_state["current_page"] = "dashboard"
            st.rerun()
        return

    # Busca dados da tarefa
    task = get_task_by_id(task_id, user["company_id"])

    if not task:
        st.error("Tarefa não encontrada.")
        if st.button("Voltar ao Dashboard"):
            st.session_state["current_page"] = "dashboard"
            st.rerun()
        return

    # Verifica permissão (próprio usuário ou admin)
    can_edit = task["user_id"] == user["id"] or is_admin()

    # Header
    st.title("Detalhes da Tarefa")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Criada por:** {task['user_name']}")
        st.markdown(f"**Data:** {task['created_at'].strftime('%d/%m/%Y %H:%M')}")
    with col2:
        if st.button("← Voltar", use_container_width=True):
            st.session_state["current_page"] = "dashboard"
            if "selected_task_id" in st.session_state:
                del st.session_state["selected_task_id"]
            st.rerun()

    st.markdown("---")

    # Tabs para organizar conteúdo
    tab1, tab2, tab3 = st.tabs(["📋 Dados", "📷 Fotos", "⚙️ Ações"])

    # Tab 1: Dados da Tarefa
    with tab1:
        if can_edit:
            st.subheader("Editar Dados da Tarefa")

            with st.form("edit_task_form"):
                col1, col2 = st.columns(2)
                with col1:
                    empresa = st.text_input("Empresa *", value=task["empresa"])
                with col2:
                    bairro = st.text_input("Bairro *", value=task["bairro"])

                st.markdown("**Atividades Realizadas**")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown("*Caixa de Emenda*")
                    abertura_caixa_emenda = st.checkbox(
                        "Abertura", value=task["abertura_caixa_emenda"], key="edit_abertura_ce"
                    )
                    fechamento_caixa_emenda = st.checkbox(
                        "Fechamento", value=task["fechamento_caixa_emenda"], key="edit_fechamento_ce"
                    )
                    qtd_caixa_emenda = st.number_input(
                        "Quantidade", value=task["qtd_caixa_emenda"], min_value=0, key="edit_qtd_ce"
                    )

                with col2:
                    st.markdown("*CTO*")
                    abertura_cto = st.checkbox(
                        "Abertura", value=task["abertura_cto"], key="edit_abertura_cto"
                    )
                    fechamento_cto = st.checkbox(
                        "Fechamento", value=task["fechamento_cto"], key="edit_fechamento_cto"
                    )
                    qtd_cto = st.number_input(
                        "Quantidade", value=task["qtd_cto"], min_value=0, key="edit_qtd_cto"
                    )

                with col3:
                    st.markdown("*Rozeta*")
                    abertura_rozeta = st.checkbox(
                        "Abertura", value=task["abertura_rozeta"], key="edit_abertura_roz"
                    )
                    fechamento_rozeta = st.checkbox(
                        "Fechamento", value=task["fechamento_rozeta"], key="edit_fechamento_roz"
                    )

                st.markdown("**Informações de Fibra**")
                col1, col2 = st.columns(2)
                with col1:
                    tipo_fibra_options = [""] + TIPOS_FIBRA
                    tipo_fibra_index = 0
                    if task["tipo_fibra"] in tipo_fibra_options:
                        tipo_fibra_index = tipo_fibra_options.index(task["tipo_fibra"])
                    tipo_fibra = st.selectbox(
                        "Tipo de Fibra", options=tipo_fibra_options, index=tipo_fibra_index
                    )
                with col2:
                    fibra_lancada = st.number_input(
                        "Fibra Lançada (m)", value=task["fibra_lancada"], min_value=0.0, step=0.5
                    )

                observacoes = st.text_area("Observações", value=task["observacoes"] or "")

                submitted = st.form_submit_button("Salvar Alterações", type="primary", use_container_width=True)

                if submitted:
                    if not empresa.strip() or not bairro.strip():
                        st.error("Empresa e Bairro são obrigatórios.")
                    else:
                        data = {
                            "empresa": empresa.strip(),
                            "bairro": bairro.strip(),
                            "abertura_caixa_emenda": abertura_caixa_emenda,
                            "fechamento_caixa_emenda": fechamento_caixa_emenda,
                            "abertura_cto": abertura_cto,
                            "fechamento_cto": fechamento_cto,
                            "abertura_rozeta": abertura_rozeta,
                            "fechamento_rozeta": fechamento_rozeta,
                            "qtd_cto": qtd_cto,
                            "qtd_caixa_emenda": qtd_caixa_emenda,
                            "tipo_fibra": tipo_fibra if tipo_fibra else None,
                            "fibra_lancada": fibra_lancada,
                            "observacoes": observacoes.strip() if observacoes else None,
                        }
                        success, msg = update_task(task_id, user["company_id"], data)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
        else:
            # Visualização apenas (sem permissão de edição)
            st.subheader("Dados da Tarefa")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Empresa:** {task['empresa']}")
                st.markdown(f"**Bairro:** {task['bairro']}")
            with col2:
                st.markdown(f"**Tipo de Fibra:** {task['tipo_fibra'] or 'N/A'}")
                st.markdown(f"**Fibra Lançada:** {task['fibra_lancada']} m")

            st.markdown("**Atividades:**")
            activities = []
            if task["abertura_caixa_emenda"]:
                activities.append("Abertura Caixa Emenda")
            if task["fechamento_caixa_emenda"]:
                activities.append("Fechamento Caixa Emenda")
            if task["abertura_cto"]:
                activities.append("Abertura CTO")
            if task["fechamento_cto"]:
                activities.append("Fechamento CTO")
            if task["abertura_rozeta"]:
                activities.append("Abertura Rozeta")
            if task["fechamento_rozeta"]:
                activities.append("Fechamento Rozeta")

            if activities:
                st.write(", ".join(activities))
            else:
                st.write("Nenhuma atividade marcada")

            st.markdown(f"**Qtd CTOs:** {task['qtd_cto']} | **Qtd Caixas Emenda:** {task['qtd_caixa_emenda']}")

            if task["observacoes"]:
                st.markdown(f"**Observações:** {task['observacoes']}")

    # Tab 2: Fotos
    with tab2:
        st.subheader("Fotos da Tarefa")

        photos = get_task_photos(task_id)

        if photos:
            st.write(f"**{len(photos)} foto(s)**")

            # Grid de fotos
            cols = st.columns(min(len(photos), 3))
            for idx, photo in enumerate(photos):
                with cols[idx % 3]:
                    if photo.get("public_url"):
                        st.image(
                            photo["public_url"],
                            caption=photo["original_name"],
                            use_container_width=True
                        )
                        st.caption(f"Tamanho: {format_file_size(photo['file_size'])}")

                        # Botão de excluir foto (se tiver permissão)
                        if can_edit:
                            if st.button(f"🗑️ Excluir", key=f"delete_photo_{photo['id']}"):
                                success, msg = delete_single_photo(photo["id"])
                                if success:
                                    st.success("Foto excluída!")
                                    st.rerun()
                                else:
                                    st.error(msg)
                    else:
                        st.warning(f"Erro ao carregar: {photo['original_name']}")
        else:
            st.info("Nenhuma foto encontrada para esta tarefa.")

        # Upload de novas fotos (se tiver permissão)
        if can_edit:
            st.markdown("---")
            st.subheader("Adicionar Novas Fotos")

            current_photo_count = len(photos) if photos else 0
            remaining_slots = MAX_FILES_PER_TASK - current_photo_count

            if remaining_slots > 0:
                st.caption(f"Você pode adicionar mais {remaining_slots} foto(s)")

                uploaded_files = st.file_uploader(
                    "Selecione as fotos",
                    type=["jpg", "jpeg", "png"],
                    accept_multiple_files=True,
                    key="new_photos_upload"
                )

                if uploaded_files:
                    if len(uploaded_files) > remaining_slots:
                        st.warning(f"Máximo de {remaining_slots} foto(s) permitidas.")
                    else:
                        if st.button("Enviar Fotos", type="primary"):
                            success, msg, _ = save_uploaded_files(
                                uploaded_files, task_id, user["company_id"]
                            )
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
            else:
                st.warning(f"Limite de {MAX_FILES_PER_TASK} fotos atingido.")

    # Tab 3: Ações
    with tab3:
        if can_edit:
            st.subheader("Ações da Tarefa")

            st.markdown("---")

            # Excluir tarefa
            st.markdown("### Excluir Tarefa")
            st.warning("Esta ação é irreversível. Todos os dados e fotos serão excluídos permanentemente.")

            confirm_delete = st.checkbox("Confirmo que desejo excluir esta tarefa", key="confirm_delete_task")

            if st.button("🗑️ Excluir Tarefa", type="secondary", disabled=not confirm_delete):
                success, msg = delete_task(task_id, user["company_id"])
                if success:
                    st.success(msg)
                    st.session_state["current_page"] = "dashboard"
                    if "selected_task_id" in st.session_state:
                        del st.session_state["selected_task_id"]
                    st.rerun()
                else:
                    st.error(msg)
        else:
            st.info("Você não tem permissão para realizar ações nesta tarefa.")


if __name__ == "__main__":
    render_task_details_page()
