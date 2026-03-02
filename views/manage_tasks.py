"""
Gerenciamento completo de tarefas - Gerentes podem atribuir, reatribuir e deixar na caixa da empresa
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentication import require_admin, get_current_user
from database.supabase_only_connection import db


def render_manage_tasks_page():
    """Renderiza página de gerenciamento de tarefas"""
    require_admin()
    user = get_current_user()

    st.title("📋 Gerenciar Tarefas")
    st.markdown("Atribua, reatribua ou deixe tarefas na caixa da empresa para distribuição posterior.")
    st.markdown("---")

    # Tabs para organização
    tab1, tab2 = st.tabs(["🗂️ Caixa da Empresa", "👥 Tarefas Atribuídas"])

    # === TAB 1: CAIXA DA EMPRESA ===
    with tab1:
        st.subheader("Tarefas Não Atribuídas")
        st.caption("Tarefas aguardando atribuição a um colaborador específico")
        
        # Buscar tarefas sem atribuição (assigned_to = NULL)
        unassigned = db.client.table('task_assignments').select(
            '*, assigned_by_user:users!assigned_by(full_name)'
        ).eq('company_id', user['company_id']).is_('assigned_to', 'null').order('created_at', desc=True).execute()
        
        if unassigned.data:
            for task in unassigned.data:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        priority_icon = {"baixa": "🟢", "media": "🟡", "alta": "🔴"}.get(task['priority'], "⚪")
                        st.markdown(f"**{priority_icon} {task['title']}**")
                        st.caption(f"Criada por: {task['assigned_by_user']['full_name']}")
                        if task.get('address'):
                            st.caption(f"📍 {task['address']}")
                    
                    with col2:
                        st.caption(f"Status: {task['status']}")
                        if task.get('due_date'):
                            st.caption(f"Prazo: {task['due_date'][:10]}")
                    
                    with col3:
                        # Botão para atribuir
                        if st.button("Atribuir", key=f"assign_{task['id']}"):
                            st.session_state[f'assigning_{task["id"]}'] = True
                            st.rerun()
                    
                    # Modal de atribuição
                    if st.session_state.get(f'assigning_{task["id"]}'):
                        with st.form(key=f"form_assign_{task['id']}"):
                            st.markdown(f"**Atribuir: {task['title']}**")
                            
                            # Buscar usuários disponíveis
                            users = db.get_all_users(user['company_id'])
                            available = [u for u in users if u['active'] and u['role'] != 'admin']
                            
                            if available:
                                user_options = {f"{u['full_name']} ({u['team'].capitalize()})": u['id'] for u in available}
                                selected = st.selectbox("Atribuir para:", list(user_options.keys()))
                                
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if st.form_submit_button("✅ Confirmar", use_container_width=True):
                                        # Atualizar tarefa
                                        db.client.table('task_assignments').update({
                                            'assigned_to': user_options[selected]
                                        }).eq('id', task['id']).execute()
                                        
                                        # Criar notificação
                                        db.create_notification(
                                            user_id=user_options[selected],
                                            company_id=user['company_id'],
                                            type='task_assigned',
                                            title='Nova Tarefa Atribuída',
                                            message=f'{user["full_name"]} atribuiu: {task["title"]}',
                                            reference_id=task['id']
                                        )
                                        
                                        st.session_state.pop(f'assigning_{task["id"]}')
                                        st.success("Tarefa atribuída!")
                                        st.rerun()
                                
                                with col_b:
                                    if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                        st.session_state.pop(f'assigning_{task["id"]}')
                                        st.rerun()
                            else:
                                st.warning("Nenhum colaborador disponível")
                                if st.form_submit_button("Fechar"):
                                    st.session_state.pop(f'assigning_{task["id"]}')
                                    st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("✅ Nenhuma tarefa na caixa da empresa")

    # === TAB 2: TAREFAS ATRIBUÍDAS ===
    with tab2:
        st.subheader("Tarefas Atribuídas a Colaboradores")
        
        # Filtros
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_user = st.selectbox(
                "Filtrar por colaborador:",
                ["Todos"] + [u['full_name'] for u in db.get_all_users(user['company_id']) if u['role'] != 'admin']
            )
        with col_f2:
            filter_status = st.selectbox(
                "Filtrar por status:",
                ["Todos", "pendente", "em_andamento", "concluida"]
            )
        
        # Buscar tarefas atribuídas
        query = db.client.table('task_assignments').select(
            '*, assigned_to_user:users!assigned_to(id, full_name, team), assigned_by_user:users!assigned_by(full_name)'
        ).eq('company_id', user['company_id']).not_.is_('assigned_to', 'null')
        
        if filter_status != "Todos":
            query = query.eq('status', filter_status)
        
        assigned = query.order('created_at', desc=True).execute()
        
        # Filtrar por usuário se necessário
        tasks_to_show = assigned.data or []
        if filter_user != "Todos":
            tasks_to_show = [t for t in tasks_to_show if t.get('assigned_to_user', {}).get('full_name') == filter_user]
        
        if tasks_to_show:
            st.caption(f"Total: {len(tasks_to_show)} tarefa(s)")
            
            for task in tasks_to_show:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 2])
                    
                    with col1:
                        priority_icon = {"baixa": "🟢", "media": "🟡", "alta": "🔴"}.get(task['priority'], "⚪")
                        status_icon = {"pendente": "🟡", "em_andamento": "🔵", "concluida": "🟢"}.get(task['status'], "⚪")
                        st.markdown(f"**{priority_icon} {task['title']}** {status_icon}")
                        
                        assignee = task.get('assigned_to_user', {})
                        st.caption(f"👤 {assignee.get('full_name', 'N/A')} ({assignee.get('team', 'N/A').capitalize()})")
                        
                        if task.get('address'):
                            st.caption(f"📍 {task['address']}")
                    
                    with col2:
                        st.caption(f"Status: {task['status']}")
                        if task.get('due_date'):
                            st.caption(f"Prazo: {task['due_date'][:10]}")
                    
                    with col3:
                        # Botões de ação
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("🔄", key=f"reassign_{task['id']}", help="Reatribuir"):
                                st.session_state[f'reassigning_{task["id"]}'] = True
                                st.rerun()
                        with col_b:
                            if st.button("📤", key=f"unassign_{task['id']}", help="Devolver à caixa"):
                                st.session_state[f'unassigning_{task["id"]}'] = True
                                st.rerun()
                    
                    # Modal de reatribuição
                    if st.session_state.get(f'reassigning_{task["id"]}'):
                        with st.form(key=f"form_reassign_{task['id']}"):
                            st.markdown(f"**Reatribuir: {task['title']}**")
                            
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
                                        
                                        st.session_state.pop(f'reassigning_{task["id"]}')
                                        st.success("Tarefa reatribuída!")
                                        st.rerun()
                                
                                with col_b:
                                    if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                        st.session_state.pop(f'reassigning_{task["id"]}')
                                        st.rerun()
                            else:
                                st.warning("Nenhum outro colaborador disponível")
                                if st.form_submit_button("Fechar"):
                                    st.session_state.pop(f'reassigning_{task["id"]}')
                                    st.rerun()
                    
                    # Modal de devolução à caixa
                    if st.session_state.get(f'unassigning_{task["id"]}'):
                        with st.form(key=f"form_unassign_{task['id']}"):
                            st.warning(f"**Devolver '{task['title']}' à caixa da empresa?**")
                            st.caption("A tarefa ficará disponível para atribuição posterior.")
                            
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
                    
                    st.markdown("---")
        else:
            st.info("Nenhuma tarefa atribuída encontrada")
