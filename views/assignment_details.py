"""
Página de detalhes de uma tarefa atribuída (TaskAssignment).
Mostra informações, mapa, status e permite atualizar.
"""

import streamlit as st
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentication import require_login, get_current_user, is_admin
from database.supabase_only_connection import db


def get_assignment_detail(assignment_id: int, company_id: int) -> dict:
    """Retorna detalhes completos de uma tarefa atribuída via Supabase."""
    return db.get_task_assignment_by_id(assignment_id, company_id)


def update_assignment_status(assignment_id: int, new_status: str, company_id: int, user_id: int, observations: str = None) -> tuple:
    """Atualiza o status de uma tarefa atribuída."""
    session = SessionLocal()
    try:
        assignment = session.query(TaskAssignment).filter(
            TaskAssignment.id == assignment_id,
            TaskAssignment.company_id == company_id,
        ).first()

        if not assignment:
            return False, "Tarefa não encontrada."

        old_status = assignment.status
        assignment.status = new_status
        assignment.updated_at = datetime.utcnow()

        if observations:
            assignment.observations = observations

        # Criar notificação para o gerente quando status muda
        if new_status != old_status:
            status_labels = {
                "pending": "Pendente",
                "in_progress": "Em Andamento",
                "completed": "Concluída",
            }
            assignee = session.query(User).filter(User.id == assignment.assigned_to).first()
            assignee_name = assignee.full_name if assignee else "Usuário"

            # Notifica quem atribuiu
            notification = Notification(
                user_id=assignment.assigned_by,
                company_id=company_id,
                type="task_updated" if new_status != "completed" else "task_completed",
                title=f"Tarefa {status_labels.get(new_status, new_status)}",
                message=f"{assignee_name} atualizou '{assignment.title}' para {status_labels.get(new_status, new_status)}.",
                reference_id=assignment.id,
                read=False,
            )
            session.add(notification)

        session.commit()
        return True, "Status atualizado com sucesso!"
    except Exception as e:
        session.rollback()
        return False, f"Erro ao atualizar: {str(e)}"
    finally:
        session.close()


def delete_assignment(assignment_id: int, company_id: int) -> tuple:
    """Exclui uma tarefa atribuída."""
    session = SessionLocal()
    try:
        assignment = session.query(TaskAssignment).filter(
            TaskAssignment.id == assignment_id,
            TaskAssignment.company_id == company_id,
        ).first()

        if not assignment:
            return False, "Tarefa não encontrada."

        # Remover notificações relacionadas
        session.query(Notification).filter(
            Notification.reference_id == assignment_id,
            Notification.type.in_(["task_assigned", "task_updated", "task_completed"]),
        ).delete(synchronize_session=False)

        # Remover fotos do storage
        photos = session.query(AssignmentPhoto).filter(
            AssignmentPhoto.assignment_id == assignment_id
        ).all()
        if photos:
            try:
                from utils.file_handler import get_supabase_service_client, SUPABASE_BUCKET
                supabase = get_supabase_service_client()
                file_paths = [p.file_path for p in photos]
                supabase.storage.from_(SUPABASE_BUCKET).remove(file_paths)
            except Exception:
                pass
            for p in photos:
                session.delete(p)

        session.delete(assignment)
        session.commit()
        return True, "Tarefa excluída com sucesso!"
    except Exception as e:
        session.rollback()
        return False, f"Erro ao excluir: {str(e)}"
    finally:
        session.close()


def render_assignment_details_page():
    """Renderiza a página de detalhes da tarefa atribuída."""
    require_login()
    user = get_current_user()

    assignment_id = st.session_state.get("selected_assignment_id")
    if not assignment_id:
        st.warning("Nenhuma tarefa selecionada.")
        if st.button("Voltar ao Dashboard"):
            st.session_state["current_page"] = "dashboard"
            st.rerun()
        return

    detail = get_assignment_detail(assignment_id, user["company_id"])
    if not detail:
        st.error("Tarefa não encontrada ou sem permissão.")
        if st.button("Voltar ao Dashboard"):
            st.session_state["current_page"] = "dashboard"
            st.rerun()
        return

    # Verificar permissão (pode ver se é assigned_to, assigned_by, ou admin)
    can_view = (
        detail["assigned_to"] == user["id"]
        or detail["assigned_by"] == user["id"]
        or is_admin()
    )
    if not can_view:
        st.error("Sem permissão para ver esta tarefa.")
        return

    is_assignee = detail["assigned_to"] == user["id"]
    is_assigner = detail["assigned_by"] == user["id"]

    # Cabeçalho
    st.title(f"Tarefa: {detail['title']}")

    # Botão voltar
    if st.button("← Voltar"):
        st.session_state["current_page"] = "dashboard"
        st.rerun()

    st.markdown("---")

    # Status badges
    status_colors = {
        "pending": "🟡 Pendente",
        "in_progress": "🔵 Em Andamento",
        "completed": "🟢 Concluída",
    }
    priority_colors = {
        "low": "🟢 Baixa",
        "medium": "🟡 Média",
        "high": "🟠 Alta",
        "urgent": "🔴 Urgente",
    }

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Status:** {status_colors.get(detail['status'], detail['status'])}")
    with col2:
        st.markdown(f"**Prioridade:** {priority_colors.get(detail['priority'], detail['priority'])}")
    with col3:
        if detail["due_date"]:
            try:
                # Se for string, converter para datetime
                if isinstance(detail["due_date"], str):
                    from datetime import datetime
                    due_date = datetime.fromisoformat(detail["due_date"].replace('Z', '+00:00'))
                    st.markdown(f"**Prazo:** {due_date.strftime('%d/%m/%Y')}")
                else:
                    st.markdown(f"**Prazo:** {detail['due_date'].strftime('%d/%m/%Y')}")
            except:
                st.markdown(f"**Prazo:** {detail['due_date']}")
        else:
            st.markdown("**Prazo:** Sem prazo")

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3 = st.tabs(["Informações", "Fotos", "Ações"])

    with tab1:
        st.subheader("Detalhes")

        col1, col2 = st.columns(2)
        with col1:
            # Usar os nomes corretos retornados pelo Supabase
            assigner_name = 'N/A'
            assignee_name = 'N/A'
            
            try:
                if isinstance(detail.get('assigned_by_user'), dict):
                    assigner_name = detail['assigned_by_user'].get('full_name', 'N/A')
                if isinstance(detail.get('assigned_to_user'), dict):
                    assignee_name = detail['assigned_to_user'].get('full_name', 'N/A')
            except:
                pass
            
            st.markdown(f"**Atribuído por:** {assigner_name}")
            st.markdown(f"**Atribuído para:** {assignee_name}")
            st.markdown(f"**Criado em:** {detail.get('created_at', 'N/A')}")
            if detail.get("updated_at"):
                st.markdown(f"**Atualizado em:** {detail.get('updated_at', 'N/A')}")

        with col2:
            if detail["address"]:
                st.markdown(f"**Endereço:** {detail['address']}")
            if detail["latitude"] and detail["longitude"]:
                st.markdown(f"**Coordenadas:** {detail['latitude']}, {detail['longitude']}")
                maps_url = f"https://www.google.com/maps?q={detail['latitude']},{detail['longitude']}"
                st.markdown(f"[Abrir no Google Maps]({maps_url})")

        if detail["description"]:
            st.markdown("**Descrição:**")
            st.text_area("", value=detail["description"], disabled=True, height=100, key="desc_view")

        if detail["observations"]:
            st.markdown("**Observações do campo:**")
            st.text_area("", value=detail["observations"], disabled=True, height=100, key="obs_view")

        if detail["materials"]:
            st.markdown("**Materiais utilizados:**")
            st.text_area("", value=detail["materials"], disabled=True, height=80, key="materials_view")

        # Mapa
        if detail["latitude"] and detail["longitude"]:
            st.subheader("Localização no Mapa")
            import pandas as pd
            map_data = pd.DataFrame({
                "lat": [detail["latitude"]],
                "lon": [detail["longitude"]],
            })
            st.map(map_data, zoom=15)

    with tab2:
        st.subheader("Fotos da Execução")

        # Buscar fotos usando o db
        photos = db.get_assignment_photos(assignment_id)
        
        if photos:
            cols = st.columns(3)
            for i, photo in enumerate(photos):
                with cols[i % 3]:
                    if photo.get("photo_url"):
                        st.image(photo["photo_url"], caption=photo.get("original_name", "Foto"), use_container_width=True)
                    else:
                        st.warning(f"Foto não disponível: {photo.get('original_name', 'Sem nome')}")
        else:
            st.info("Nenhuma foto adicionada ainda.")

    with tab3:
        st.subheader("Ações")

        # Ações do assignee (usuário de campo)
        if is_assignee:
            if detail["status"] == "pendente":
                if st.button("▶ Iniciar Tarefa", use_container_width=True, type="primary"):
                    success, msg = db.update_task_status(assignment_id, "em_andamento")
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            if detail["status"] == "em_andamento":
                st.markdown("**Concluir Tarefa**")
                observations = st.text_area(
                    "Observações da execução",
                    placeholder="Descreva o que foi feito, problemas encontrados, etc.",
                    key="complete_obs",
                )
                if st.button("✅ Concluir Tarefa", use_container_width=True, type="primary"):
                    success, msg = db.update_task_status(
                        assignment_id, "concluida", observations if observations else None
                    )
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            if detail["status"] in ["pendente", "em_andamento"]:
                st.markdown("---")
                st.markdown("**Atualizar Observações**")
                new_obs = st.text_area(
                    "Observações",
                    value=detail.get("notes") or "",
                    key="update_obs",
                )
                if st.button("Salvar Observações", key="save_obs"):
                    success, msg = db.update_task_status(assignment_id, detail["status"], new_obs)
                    if success:
                        st.success("Observações salvas!")
                        st.rerun()
                    else:
                        st.error(msg)

        # Ações do admin/gerente
        if is_assigner or is_admin():
            st.markdown("---")
            st.markdown("**Ações do Gerente**")

            if detail["status"] != "concluida":
                status_map = {"pendente": "Pendente", "em_andamento": "Em Andamento", "concluida": "Concluída"}
                new_status = st.selectbox(
                    "Alterar Status",
                    options=["pendente", "em_andamento", "concluida"],
                    format_func=lambda x: status_map[x],
                    index=max(0, list(status_map.keys()).index(detail["status"]) if detail["status"] in status_map else 0),
                    key="admin_status",
                )
                if st.button("Atualizar Status", key="admin_update_status"):
                    if new_status != detail["status"]:
                        success, msg = db.update_task_status(assignment_id, new_status)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

            st.markdown("---")
            st.markdown("**Excluir Tarefa**")
            st.warning("Esta ação é irreversível!")
            confirm = st.checkbox("Confirmo que desejo excluir esta tarefa", key="confirm_delete")
            if confirm:
                if st.button("🗑 Excluir Tarefa", type="secondary", use_container_width=True):
                    st.error("Função de exclusão desabilitada. Use o sistema de administração.")
