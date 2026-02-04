"""
Página de atribuição de tarefas - exclusiva para admins/gerentes.
Permite atribuir tarefas a usuários de campo com localização e prioridade.
"""

import streamlit as st
from datetime import datetime, date
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentication import require_admin, get_current_user
from database.supabase_only_connection import db


def get_active_users(company_id: int) -> list:
    """Retorna lista de usuários ativos da empresa via Supabase."""
    users = db.get_all_users(company_id)
    return [u for u in users if u['active']]


def parse_google_maps_link(link: str) -> tuple:
    """Extrai latitude e longitude de um link do Google Maps."""
    if not link:
        return None, None
    # Padrão: @-23.5505199,-46.6333094
    match = re.search(r'@(-?\d+\.?\d*),(-?\d+\.?\d*)', link)
    if match:
        return float(match.group(1)), float(match.group(2))
    # Padrão: q=-23.5505199,-46.6333094
    match = re.search(r'q=(-?\d+\.?\d*),(-?\d+\.?\d*)', link)
    if match:
        return float(match.group(1)), float(match.group(2))
    # Padrão: place/-23.5505199,-46.6333094
    match = re.search(r'place/(-?\d+\.?\d*),(-?\d+\.?\d*)', link)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None


def create_task_assignment(
    company_id: int,
    assigned_by: int,
    assigned_to: int,
    title: str,
    description: str,
    address: str,
    latitude: float,
    longitude: float,
    priority: str,
    due_date=None,
) -> tuple:
    """Cria uma nova atribuição de tarefa via Supabase."""
    try:
        # Criar tarefa
        assignment_data = {
            'company_id': company_id,
            'assigned_by': assigned_by,
            'assigned_to': assigned_to,
            'title': title,
            'description': description,
            'address': address,
            'latitude': latitude,
            'longitude': longitude,
            'priority': priority,
            'due_date': due_date.isoformat() if due_date else None,
        }
        
        success, message, assignment_id = db.create_task_assignment(assignment_data)
        
        if success:
            # Buscar nome do atribuidor
            assigner = db.get_user_by_id(assigned_by)
            assigner_name = assigner['full_name'] if assigner else "Gerente"
            
            # Criar notificação
            db.create_notification(
                user_id=assigned_to,
                company_id=company_id,
                type="task_assigned",
                title="Nova Tarefa Atribuída",
                message=f"{assigner_name} atribuiu a tarefa: {title}",
                reference_id=assignment_id
            )
            
            return True, "Tarefa atribuída com sucesso!", assignment_id
        else:
            return False, message, None
            
    except Exception as e:
        return False, f"Erro ao atribuir tarefa: {str(e)}", None


def render_assign_task_page():
    """Renderiza a página de atribuição de tarefas."""
    require_admin()
    user = get_current_user()

    st.title("Atribuir Tarefa")
    st.markdown("Atribua tarefas aos usuários de campo da sua equipe.")
    st.markdown("---")

    # Buscar usuários ativos
    users = get_active_users(user["company_id"])

    if not users:
        st.warning("Nenhum usuário ativo encontrado na empresa.")
        return

    # Filtrar apenas usuários que não são o próprio admin
    available_users = [u for u in users if u["id"] != user["id"]]

    if not available_users:
        st.warning("Nenhum outro usuário disponível para atribuição.")
        return

    with st.form("assign_task_form", clear_on_submit=True):
        st.subheader("Dados da Tarefa")

        # Destinatário
        user_options = {
            f"{u['full_name']} ({u['team'].capitalize()})": u["id"]
            for u in available_users
        }
        selected_user_label = st.selectbox(
            "Atribuir para *",
            options=list(user_options.keys()),
        )
        selected_user_id = user_options[selected_user_label]

        # Título
        title = st.text_input("Título da Tarefa *", max_chars=200)

        # Descrição
        description = st.text_area(
            "Descrição (o que possivelmente ocorreu / o que precisa ser feito)",
            max_chars=2000,
            height=120,
        )

        # Prioridade
        priority_map = {
            "Baixa": "baixa",
            "Média": "media",
            "Alta": "alta",
        }
        selected_priority = st.selectbox(
            "Prioridade",
            options=list(priority_map.keys()),
            index=1,  # Média como padrão
        )

        # Prazo
        st.markdown("**Prazo (opcional)**")
        has_due_date = st.checkbox("Definir prazo")
        due_date = None
        if has_due_date:
            due_date_val = st.date_input("Data do prazo", min_value=date.today())
            due_date = datetime.combine(due_date_val, datetime.max.time())

        st.markdown("---")
        st.subheader("Localização")

        # Endereço
        address = st.text_input("Endereço", max_chars=300)

        # Link do Google Maps
        maps_link = st.text_input(
            "Link do Google Maps (opcional - extrai coordenadas automaticamente)",
            placeholder="https://maps.google.com/...",
        )

        # Coordenadas manuais
        col1, col2 = st.columns(2)
        with col1:
            lat_input = st.text_input("Latitude", placeholder="-23.550520")
        with col2:
            lng_input = st.text_input("Longitude", placeholder="-46.633309")

        # Botão de envio
        st.markdown("---")
        submitted = st.form_submit_button(
            "Atribuir Tarefa",
            use_container_width=True,
            type="primary",
        )

    if submitted:
        # Validações
        if not title.strip():
            st.error("O título da tarefa é obrigatório.")
            return

        # Resolver coordenadas
        latitude = None
        longitude = None

        # Primeiro tenta do link do Google Maps
        if maps_link:
            latitude, longitude = parse_google_maps_link(maps_link)

        # Se não conseguiu do link, usa campos manuais
        if latitude is None and lat_input:
            try:
                latitude = float(lat_input)
            except ValueError:
                st.error("Latitude inválida. Use formato numérico (ex: -23.550520).")
                return

        if longitude is None and lng_input:
            try:
                longitude = float(lng_input)
            except ValueError:
                st.error("Longitude inválida. Use formato numérico (ex: -46.633309).")
                return

        # Criar tarefa
        success, message, assignment_id = create_task_assignment(
            company_id=user["company_id"],
            assigned_by=user["id"],
            assigned_to=selected_user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            address=address.strip() if address else None,
            latitude=latitude,
            longitude=longitude,
            priority=priority_map[selected_priority],
            due_date=due_date,
        )

        if success:
            st.success(f"{message} (ID: {assignment_id})")
            st.balloons()
        else:
            st.error(message)
