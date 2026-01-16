"""
Página de registro de tarefas diárias.
"""

import streamlit as st
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentication import require_login, get_current_user
from database.connection import SessionLocal
from database.models import Task
from utils.file_handler import save_uploaded_files, format_file_size
from config import TIPOS_FIBRA, MAX_FILES_PER_TASK, MAX_FILE_SIZE_BYTES


def render_register_task_page():
    """Renderiza a página de registro de tarefas."""
    require_login()
    user = get_current_user()

    st.title("Registrar Nova Tarefa")
    st.markdown(f"**Usuário:** {user['full_name']} | **Equipe:** {user['team'].capitalize()}")
    st.markdown("---")

    with st.form("task_form", clear_on_submit=True):
        # Informações Gerais
        st.subheader("Informações Gerais")
        col1, col2 = st.columns(2)
        with col1:
            empresa = st.text_input("Empresa *", placeholder="Nome da empresa")
        with col2:
            bairro = st.text_input("Bairro *", placeholder="Nome do bairro")

        st.markdown("---")

        # Atividades
        st.subheader("Atividades Realizadas")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Caixa de Emenda**")
            abertura_caixa_emenda = st.checkbox("Abertura em Caixa de Emenda")
            fechamento_caixa_emenda = st.checkbox("Fechamento em Caixa de Emenda")
            qtd_caixa_emenda = st.number_input(
                "Quantidade de Caixa de Emenda", min_value=0, value=0, step=1
            )

        with col2:
            st.markdown("**CTO**")
            abertura_cto = st.checkbox("Abertura em CTO")
            fechamento_cto = st.checkbox("Fechamento em CTO")
            qtd_cto = st.number_input("Quantidade de CTO", min_value=0, value=0, step=1)

        with col3:
            st.markdown("**Rozeta**")
            abertura_rozeta = st.checkbox("Abertura em Rozeta")
            fechamento_rozeta = st.checkbox("Fechamento em Rozeta")

        st.markdown("---")

        # Fibra
        st.subheader("Informações de Fibra")
        col1, col2 = st.columns(2)
        with col1:
            tipo_fibra = st.selectbox("Tipo de Fibra", options=[""] + TIPOS_FIBRA)
        with col2:
            fibra_lancada = st.number_input(
                "Fibra Lançada (metros)", min_value=0.0, value=0.0, step=0.5, format="%.2f"
            )

        st.markdown("---")

        # Observações
        st.subheader("Observações")
        observacoes = st.text_area(
            "Observações adicionais",
            placeholder="Descreva detalhes adicionais sobre a tarefa...",
            height=100,
        )

        st.markdown("---")

        # Upload de Fotos
        st.subheader("Fotos")
        st.caption(
            f"Upload de até {MAX_FILES_PER_TASK} fotos (máx. {format_file_size(MAX_FILE_SIZE_BYTES)} cada). "
            "Formatos aceitos: JPG, JPEG, PNG"
        )

        uploaded_files = st.file_uploader(
            "Selecione as fotos *",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            help=f"Máximo de {MAX_FILES_PER_TASK} arquivos",
        )

        if uploaded_files:
            st.info(f"{len(uploaded_files)} arquivo(s) selecionado(s)")
            if len(uploaded_files) > MAX_FILES_PER_TASK:
                st.warning(f"Atenção: Máximo de {MAX_FILES_PER_TASK} fotos permitidas.")

        st.markdown("---")

        # Botão de envio
        submitted = st.form_submit_button(
            "Registrar Tarefa", use_container_width=True, type="primary"
        )

        if submitted:
            # Validações
            errors = []

            if not empresa.strip():
                errors.append("O campo Empresa é obrigatório.")
            if not bairro.strip():
                errors.append("O campo Bairro é obrigatório.")

            # Verificar se pelo menos uma atividade foi marcada
            has_activity = any([
                abertura_caixa_emenda,
                fechamento_caixa_emenda,
                abertura_cto,
                fechamento_cto,
                abertura_rozeta,
                fechamento_rozeta,
                qtd_cto > 0,
                qtd_caixa_emenda > 0,
                fibra_lancada > 0,
            ])

            if not has_activity:
                errors.append("Selecione pelo menos uma atividade ou quantidade.")

            if not uploaded_files:
                errors.append("É obrigatório enviar pelo menos uma foto.")
            elif len(uploaded_files) > MAX_FILES_PER_TASK:
                errors.append(f"Máximo de {MAX_FILES_PER_TASK} fotos permitidas.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Salvar tarefa
                session = SessionLocal()
                try:
                    task = Task(
                        company_id=user["company_id"],
                        user_id=user["id"],
                        empresa=empresa.strip(),
                        bairro=bairro.strip(),
                        abertura_caixa_emenda=abertura_caixa_emenda,
                        fechamento_caixa_emenda=fechamento_caixa_emenda,
                        abertura_cto=abertura_cto,
                        fechamento_cto=fechamento_cto,
                        abertura_rozeta=abertura_rozeta,
                        fechamento_rozeta=fechamento_rozeta,
                        qtd_cto=qtd_cto,
                        qtd_caixa_emenda=qtd_caixa_emenda,
                        tipo_fibra=tipo_fibra if tipo_fibra else None,
                        fibra_lancada=fibra_lancada,
                        observacoes=observacoes.strip() if observacoes else None,
                    )
                    session.add(task)
                    session.commit()

                    # Salvar fotos no Supabase Storage
                    success, msg, _ = save_uploaded_files(
                        uploaded_files, task.id, user["company_id"]
                    )

                    if success:
                        st.success("Tarefa registrada com sucesso!")
                        st.balloons()
                    else:
                        st.warning(f"Tarefa salva, mas houve erro nas fotos: {msg}")

                except Exception as e:
                    session.rollback()
                    st.error(f"Erro ao registrar tarefa: {str(e)}")
                finally:
                    session.close()


if __name__ == "__main__":
    render_register_task_page()
