"""
Gerenciamento Completo de Tarefas - Criar, Atribuir, Visualizar e Gerenciar em uma única página
"""

import streamlit as st
import sys
import os
from datetime import datetime, date
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentication import require_admin, get_current_user
from database.supabase_only_connection import db
from utils.push_notification import notify_task_assigned


PAGE_SIZE_MGMT = 15


def _pagination_controls(page_key: str, total: int, filter_sig: str = "") -> int:
    """Controles de paginação para task_management. Retorna página atual (0-indexed)."""
    if st.session_state.get(f"{page_key}_sig") != filter_sig:
        st.session_state[f"{page_key}_sig"] = filter_sig
        st.session_state[page_key] = 0

    total_pages = max(1, -(-total // PAGE_SIZE_MGMT))
    page = st.session_state.get(page_key, 0)
    page = min(page, total_pages - 1)

    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        if st.button("← Anterior", key=f"{page_key}_prev", disabled=page == 0, use_container_width=True):
            st.session_state[page_key] = page - 1
            st.rerun()
    with c2:
        s = page * PAGE_SIZE_MGMT + 1
        e = min((page + 1) * PAGE_SIZE_MGMT, total)
        st.caption(f"Mostrando {s}–{e} de {total}  |  Página {page + 1}/{total_pages}")
    with c3:
        if st.button("Próximo →", key=f"{page_key}_next", disabled=page >= total_pages - 1, use_container_width=True):
            st.session_state[page_key] = page + 1
            st.rerun()
    return page


def _is_overdue(task: dict) -> bool:
    """Retorna True se a tarefa tem prazo vencido e ainda não foi concluída."""
    if task.get("status") == "concluida":
        return False
    due = task.get("due_date")
    if not due:
        return False
    try:
        due_dt = datetime.fromisoformat(str(due).replace("Z", "+00:00")).replace(tzinfo=None)
        return due_dt < datetime.now()
    except Exception:
        return False


def send_push_for_task(user_id: int, task_id: int, task_title: str, assigned_by_name: str):
    """Envia push notification para o usuário."""
    try:
        assigned_user = db.get_user_by_id(user_id)
        if assigned_user and assigned_user.get('push_token'):
            notify_task_assigned(
                user_push_token=assigned_user['push_token'],
                task_id=task_id,
                task_title=task_title,
                assigned_by_name=assigned_by_name,
                server_key=os.environ.get('FCM_SERVER_KEY')
            )
    except Exception as e:
        print(f"Erro ao enviar push: {e}")


def parse_google_maps_link(link: str) -> tuple:
    """Extrai latitude e longitude de um link do Google Maps."""
    if not link:
        return None, None
    match = re.search(r'@(-?\d+\.?\d*),(-?\d+\.?\d*)', link)
    if match:
        return float(match.group(1)), float(match.group(2))
    match = re.search(r'q=(-?\d+\.?\d*),(-?\d+\.?\d*)', link)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None


def render_task_management_page():
    """Renderiza página unificada de gerenciamento de tarefas"""
    require_admin()
    user = get_current_user()

    st.title("📋 Gerenciamento de Tarefas")
    st.markdown("Crie, atribua e gerencie todas as tarefas da empresa em um só lugar")
    st.markdown("---")

    # Tabs principais
    tab1, tab2, tab3 = st.tabs(["➕ Criar Tarefa", "🗂️ Caixa da Empresa", "👥 Tarefas Atribuídas"])

    # === TAB 1: CRIAR TAREFA ===
    with tab1:
        st.subheader("Nova Tarefa")
        
        # Busca empresas ativas (fora do form para evitar chamadas desnecessárias)
        empresas_result = db.client.table('companies').select('name').eq('active', True).order('name').execute()
        empresa_options = [e['name'] for e in empresas_result.data] if empresas_result.data else []

        with st.form("create_task_form", clear_on_submit=True):
            # Empresa
            empresa_nome = st.selectbox("Empresa *", empresa_options) if empresa_options else st.text_input("Empresa *", placeholder="Nome da empresa")

            # Atribuição
            assign_now = st.checkbox("Atribuir a um colaborador agora", value=False)
            
            selected_user_id = None
            if assign_now:
                users = db.get_all_users(user['company_id'])
                available = [u for u in users if u['active'] and u['role'] != 'admin']
                
                if available:
                    user_options = {f"{u['full_name']} ({u['team'].capitalize()})": u['id'] for u in available}
                    selected_label = st.selectbox("Atribuir para:", list(user_options.keys()))
                    selected_user_id = user_options[selected_label]
                else:
                    st.warning("Nenhum colaborador disponível")
            else:
                st.info("📦 Tarefa será criada na caixa da empresa")
            
            # Dados da tarefa
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Título *", max_chars=200)
            with col2:
                priority = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"], index=1)
            
            description = st.text_area("Descrição", max_chars=2000, height=100)
            
            # Localização
            st.markdown("**Localização**")
            col1, col2 = st.columns(2)
            with col1:
                address = st.text_input("Endereço", max_chars=300)
            with col2:
                maps_link = st.text_input("Link Google Maps", placeholder="https://maps.google.com/...")
            
            col1, col2 = st.columns(2)
            with col1:
                lat_input = st.text_input("Latitude", placeholder="-23.550520")
            with col2:
                lng_input = st.text_input("Longitude", placeholder="-46.633309")
            
            # Prazo
            has_due = st.checkbox("Definir prazo")
            due_date = None
            if has_due:
                due_date_val = st.date_input("Data do prazo", min_value=date.today())
                due_date = datetime.combine(due_date_val, datetime.max.time())
            
            submitted = st.form_submit_button("✅ Criar Tarefa", use_container_width=True, type="primary")
        
        if submitted:
            if not title.strip():
                st.error("Título é obrigatório")
            else:
                # Resolver coordenadas
                latitude, longitude = None, None
                if maps_link:
                    latitude, longitude = parse_google_maps_link(maps_link)
                if latitude is None and lat_input:
                    try:
                        latitude = float(lat_input)
                    except:
                        pass
                if longitude is None and lng_input:
                    try:
                        longitude = float(lng_input)
                    except:
                        pass
                
                # Criar tarefa
                priority_map = {"Baixa": "baixa", "Média": "media", "Alta": "alta"}
                assignment_data = {
                    'company_id': user['company_id'],
                    'assigned_by': user['id'],
                    'assigned_to': selected_user_id,
                    'title': title.strip(),
                    'description': description.strip() if description else None,
                    'address': address.strip() if address else None,
                    'latitude': latitude,
                    'longitude': longitude,
                    'priority': priority_map[priority],
                    'due_date': due_date.isoformat() if due_date else None,
                    'empresa_nome': empresa_nome if empresa_nome else None,
                }
                
                success, message, task_id = db.create_task_assignment(assignment_data)
                
                if success:
                    if selected_user_id:
                        db.create_notification(
                            user_id=selected_user_id,
                            company_id=user['company_id'],
                            type='task_assigned',
                            title='Nova Tarefa Atribuída',
                            message=f'{user["full_name"]} atribuiu: {title.strip()}',
                            reference_id=task_id
                        )
                        # Enviar push notification
                        send_push_for_task(selected_user_id, task_id, title.strip(), user["full_name"])
                        st.success(f"✅ Tarefa criada e atribuída! (ID: {task_id})")
                    else:
                        st.success(f"📦 Tarefa criada na caixa da empresa! (ID: {task_id})")
                    st.balloons()
                    
                    # Mostrar detalhes da tarefa criada
                    st.markdown("---")
                    st.markdown("**📄 Tarefa Criada:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Título:** {title.strip()}")
                        st.write(f"**Prioridade:** {priority}")
                        if selected_user_id:
                            assignee = db.get_user_by_id(selected_user_id, user['company_id'])
                            st.write(f"**Atribuída a:** {assignee['full_name']}")
                        else:
                            st.write(f"**Status:** Na caixa da empresa")
                    with col2:
                        if address:
                            st.write(f"**Endereço:** {address.strip()}")
                        if latitude and longitude:
                            st.write(f"**Coordenadas:** {latitude}, {longitude}")
                        if due_date:
                            st.write(f"**Prazo:** {due_date_val}")
                else:
                    st.error(message)

    # === TAB 2: CAIXA DA EMPRESA ===
    with tab2:
        st.subheader("Tarefas Aguardando Atribuição")
        
        _pagination_controls("tab2_page", 0, "")  # pre-render para não mudar layout
        unassigned_data, unassigned_total = db.get_task_assignments_paginated(
            company_id=user['company_id'],
            page=st.session_state.get("tab2_page", 0),
            page_size=PAGE_SIZE_MGMT,
            unassigned_only=True,
        )
        _pagination_controls("tab2_page", unassigned_total, "unassigned")

        if unassigned_data:
            st.caption(f"Total: {unassigned_total} tarefa(s)")

            overdue_count = sum(1 for t in unassigned_data if _is_overdue(t))
            if overdue_count:
                st.warning(f"⚠️ {overdue_count} tarefa(s) com prazo vencido nesta página.")

            for task in unassigned_data:
                overdue = _is_overdue(task)
                p_icon = "🔴" if task["priority"] == "alta" else "🟡" if task["priority"] == "media" else "🟢"
                overdue_badge = " ⚠️ VENCIDA" if overdue else ""
                with st.expander(f"{p_icon} {task['title']}{overdue_badge}", expanded=False):
                    if overdue:
                        st.error(f"⚠️ Prazo vencido em {task['due_date'][:10]}")
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.write(f"**Descrição:** {task.get('description', 'N/A')}")
                        st.write(f"**Criada por:** {task['assigned_by_user']['full_name']}")
                        if task.get('address'):
                            st.write(f"**📍 Endereço:** {task['address']}")
                        if task.get('latitude') and task.get('longitude'):
                            st.write(f"**Coordenadas:** {task['latitude']}, {task['longitude']}")
                        if task.get('due_date'):
                            st.write(f"**⏰ Prazo:** {task['due_date'][:10]}")
                        st.caption(f"Criada em: {task['created_at'][:16]}")
                    
                    with col2:
                        st.write(f"**ID:** {task['id']}")
                        st.write(f"**Prioridade:** {task['priority'].capitalize()}")
                        st.write(f"**Status:** {task['status']}")
                        
                        # Atribuir
                        if st.button("👤 Atribuir", key=f"assign_{task['id']}", use_container_width=True):
                            st.session_state[f'assigning_{task["id"]}'] = True
                            st.rerun()
                        
                        # Excluir
                        if st.button("🗑️ Excluir", key=f"del_{task['id']}", use_container_width=True, type="secondary"):
                            st.session_state[f'deleting_{task["id"]}'] = True
                            st.rerun()
                    
                    # Modal atribuir
                    if st.session_state.get(f'assigning_{task["id"]}'):
                        st.markdown("---")
                        with st.form(key=f"form_assign_{task['id']}"):
                            users = db.get_all_users(user['company_id'])
                            available = [u for u in users if u['active'] and u['role'] != 'admin']
                            
                            if available:
                                user_options = {f"{u['full_name']} ({u['team'].capitalize()})": u['id'] for u in available}
                                selected = st.selectbox("Atribuir para:", list(user_options.keys()))
                                
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if st.form_submit_button("✅ Confirmar", use_container_width=True):
                                        db.client.table('task_assignments').update({
                                            'assigned_to': user_options[selected]
                                        }).eq('id', task['id']).execute()

                                        db.create_notification(
                                            user_id=user_options[selected],
                                            company_id=user['company_id'],
                                            type='task_assigned',
                                            title='Nova Tarefa Atribuída',
                                            message=f'{user["full_name"]} atribuiu: {task["title"]}',
                                            reference_id=task['id']
                                        )
                                        # Enviar push notification
                                        send_push_for_task(user_options[selected], task['id'], task["title"], user["full_name"])

                                        st.session_state.pop(f'assigning_{task["id"]}')
                                        st.success("Tarefa atribuída!")
                                        st.rerun()
                                
                                with col_b:
                                    if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                        st.session_state.pop(f'assigning_{task["id"]}')
                                        st.rerun()
                    
                    # Modal excluir
                    if st.session_state.get(f'deleting_{task["id"]}'):
                        st.markdown("---")
                        with st.form(key=f"form_del_{task['id']}"):
                            st.warning(f"**Confirma exclusão de '{task['title']}'?**")
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.form_submit_button("✅ Sim, excluir", use_container_width=True):
                                    try:
                                        photos_to_del = db.get_assignment_photos(task["id"])
                                        for p in photos_to_del:
                                            db.client.table("assignment_photos").delete().eq("id", p["id"]).execute()

                                        db.client.table("task_assignments").delete()\
                                            .eq("id", task["id"])\
                                            .eq("company_id", user["company_id"])\
                                            .execute()

                                        st.session_state.pop(f'deleting_{task["id"]}')
                                        st.success("Tarefa excluída!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao excluir tarefa: {e}")
                            
                            with col_b:
                                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                    st.session_state.pop(f'deleting_{task["id"]}')
                                    st.rerun()
        else:
            st.info("✅ Nenhuma tarefa na caixa da empresa")

    # === TAB 3: TAREFAS ATRIBUÍDAS ===
    with tab3:
        st.subheader("Tarefas Atribuídas a Colaboradores")
        
        # Filtros
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            all_users = db.get_all_users(user['company_id'])
            filter_user = st.selectbox(
                "Filtrar por colaborador:",
                ["Todos"] + [u['full_name'] for u in all_users if u['role'] != 'admin']
            )
        with col_f2:
            filter_status = st.selectbox(
                "Filtrar por status:",
                ["Todos", "pendente", "em_andamento", "concluida"]
            )
        
        # Buscar tarefas com paginação
        status_param = filter_status if filter_status != "Todos" else None
        name_param = filter_user if filter_user != "Todos" else None
        filter_sig_tab3 = f"{filter_user}|{filter_status}"

        tab3_page = st.session_state.get("tab3_page", 0)
        tasks_to_show, total_tab3 = db.get_task_assignments_paginated(
            company_id=user['company_id'],
            page=tab3_page,
            page_size=PAGE_SIZE_MGMT,
            assigned_only=True,
            status=status_param,
            assigned_to_name=name_param,
        )
        _pagination_controls("tab3_page", total_tab3, filter_sig_tab3)

        if tasks_to_show:
            overdue_count = sum(1 for t in tasks_to_show if _is_overdue(t))
            col_cap, col_warn = st.columns([1, 2])
            col_cap.caption(f"Total: {total_tab3} tarefa(s)")
            if overdue_count:
                col_warn.warning(f"⚠️ {overdue_count} tarefa(s) com prazo vencido nesta página")

            for task in tasks_to_show:
                overdue = _is_overdue(task)
                status_icon   = {"pendente": "🟡", "em_andamento": "🔵", "concluida": "🟢"}.get(task["status"], "⚪")
                priority_icon = {"baixa": "🟢", "media": "🟡", "alta": "🔴"}.get(task["priority"], "⚪")
                overdue_badge = " ⚠️ VENCIDA" if overdue else ""

                with st.expander(f"{priority_icon} {task['title']} {status_icon}{overdue_badge}", expanded=False):
                    if overdue:
                        st.error(f"⚠️ Prazo vencido em {task['due_date'][:10]}")
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        assignee = task.get("assigned_to_user", {})
                        st.write(f"**👤 Atribuída a:** {assignee.get('full_name', 'N/A')} ({assignee.get('team', 'N/A').capitalize()})")
                        st.write(f"**Descrição:** {task.get('description', 'N/A')}")
                        if task.get("address"):
                            st.write(f"**📍 Endereço:** {task['address']}")
                        if task.get("due_date"):
                            prazo_label = f"**⚠️ Prazo (VENCIDO):** {task['due_date'][:10]}" if overdue else f"**⏰ Prazo:** {task['due_date'][:10]}"
                            st.write(prazo_label)
                        st.caption(f"Criada em: {task['created_at'][:16]}")
                    
                    with col2:
                        st.write(f"**ID:** {task['id']}")
                        st.write(f"**Status:** {task['status']}")
                        st.write(f"**Prioridade:** {task['priority'].capitalize()}")
                        
                        # Ver detalhes
                        if st.button("👁️ Ver Detalhes", key=f"view_details_{task['id']}_{hash(str(task))}", use_container_width=True, type="primary"):
                            st.session_state["selected_assignment_id"] = task["id"]
                            st.session_state["current_page"] = "assignment_details"
                            st.rerun()
                        
                        # Reatribuir
                        if st.button("🔄 Reatribuir", key=f"reassign_{task['id']}", use_container_width=True):
                            st.session_state[f'reassigning_{task["id"]}'] = True
                            st.rerun()
                        
                        # Devolver
                        if st.button("📤 Devolver", key=f"unassign_{task['id']}", use_container_width=True):
                            st.session_state[f'unassigning_{task["id"]}'] = True
                            st.rerun()
                    
                    # Modal reatribuir
                    if st.session_state.get(f'reassigning_{task["id"]}'):
                        st.markdown("---")
                        with st.form(key=f"form_reassign_{task['id']}"):
                            users = db.get_all_users(user['company_id'])
                            available = [u for u in users if u['active'] and u['role'] != 'admin' and u['id'] != task['assigned_to']]
                            
                            if available:
                                user_options = {f"{u['full_name']} ({u['team'].capitalize()})": u['id'] for u in available}
                                selected = st.selectbox("Reatribuir para:", list(user_options.keys()))
                                
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if st.form_submit_button("✅ Confirmar", use_container_width=True):
                                        db.client.table('task_assignments').update({
                                            'assigned_to': user_options[selected]
                                        }).eq('id', task['id']).execute()

                                        db.create_notification(
                                            user_id=user_options[selected],
                                            company_id=user['company_id'],
                                            type='task_assigned',
                                            title='Tarefa Reatribuída',
                                            message=f'{user["full_name"]} reatribuiu: {task["title"]}',
                                            reference_id=task['id']
                                        )
                                        # Enviar push notification
                                        send_push_for_task(user_options[selected], task['id'], task["title"], user["full_name"])

                                        st.session_state.pop(f'reassigning_{task["id"]}')
                                        st.success("Tarefa reatribuída!")
                                        st.rerun()
                                
                                with col_b:
                                    if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                        st.session_state.pop(f'reassigning_{task["id"]}')
                                        st.rerun()
                    
                    # Modal devolver
                    if st.session_state.get(f'unassigning_{task["id"]}'):
                        st.markdown("---")
                        with st.form(key=f"form_unassign_{task['id']}"):
                            st.warning(f"**Devolver '{task['title']}' à caixa da empresa?**")
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.form_submit_button("✅ Confirmar", use_container_width=True):
                                    db.client.table('task_assignments').update({
                                        'assigned_to': None
                                    }).eq('id', task['id']).execute()
                                    
                                    st.session_state.pop(f'unassigning_{task["id"]}')
                                    st.success("Tarefa devolvida à caixa!")
                                    st.rerun()
                            
                            with col_b:
                                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                    st.session_state.pop(f'unassigning_{task["id"]}')
                                    st.rerun()
        else:
            st.info("Nenhuma tarefa atribuída encontrada")
