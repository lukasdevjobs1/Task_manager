import streamlit as st
from database.supabase_connection import get_supabase_client
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

def show_completed_tasks_manager():
    st.title("📋 Tarefas Concluídas - Visualização Gerente")
    
    supabase = get_supabase_client()
    user = st.session_state.user
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        date_filter = st.date_input("Filtrar por data", value=None)
    with col2:
        collaborator_filter = st.selectbox("Filtrar por colaborador", ["Todos"] + get_collaborators(supabase, user))
    
    # Buscar tarefas concluídas
    query = supabase.table('task_assignments').select('*, assigned_to_user:users!assigned_to(full_name, username)')
    
    if user['role'] == 'gerente':
        query = query.eq('assigned_by', user['id'])
    
    query = query.eq('status', 'concluida').order('completed_at', desc=True)
    
    response = query.execute()
    tasks = response.data if response.data else []
    
    # Aplicar filtros
    if date_filter:
        tasks = [t for t in tasks if t.get('completed_at') and datetime.fromisoformat(t['completed_at'].replace('Z', '')).date() == date_filter]
    
    if collaborator_filter != "Todos":
        tasks = [t for t in tasks if t.get('assigned_to_user', {}).get('full_name') == collaborator_filter]
    
    # Estatísticas
    st.subheader("📊 Estatísticas")
    col1, col2, col3, col4 = st.columns(4)
    
    total_ctos = 0
    total_ceos = 0
    
    for task in tasks:
        materials = task.get('materials', '').lower()
        import re
        cto_match = re.findall(r'(\d+)\s*cto', materials)
        ceo_match = re.findall(r'(\d+)\s*ceo', materials)
        total_ctos += sum(int(x) for x in cto_match)
        total_ceos += sum(int(x) for x in ceo_match)
    
    col1.metric("Total de Tarefas", len(tasks))
    col2.metric("CTOs Instaladas", total_ctos)
    col3.metric("CEOs Instaladas", total_ceos)
    col4.metric("Colaboradores", len(set(t.get('assigned_to') for t in tasks)))
    
    st.divider()
    
    # Listar tarefas
    if not tasks:
        st.info("Nenhuma tarefa concluída encontrada.")
        return
    
    for task in tasks:
        with st.expander(f"🎯 {task['title']} - {task.get('assigned_to_user', {}).get('full_name', 'N/A')}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Descrição:** {task.get('description', 'N/A')}")
                st.write(f"**Endereço:** {task.get('address', 'N/A')}")
                st.write(f"**Concluída em:** {format_datetime(task.get('completed_at'))}")
                
                st.write("**Serviço Realizado:**")
                st.text_area("", task.get('service_notes', 'Não informado'), height=100, disabled=True, key=f"notes_{task['id']}")
                
                st.write("**Materiais Utilizados:**")
                st.text_area("", task.get('materials', 'Não informado'), height=100, disabled=True, key=f"materials_{task['id']}")
            
            with col2:
                # Buscar fotos
                photos_response = supabase.table('assignment_photos').select('*').eq('assignment_id', task['id']).execute()
                photos = photos_response.data if photos_response.data else []
                
                if photos:
                    st.write(f"**Fotos ({len(photos)}):**")
                    for idx, photo in enumerate(photos):
                        try:
                            # Decodificar base64
                            if photo['photo_url'].startswith('data:image'):
                                base64_str = photo['photo_url'].split(',')[1]
                                img_data = base64.b64decode(base64_str)
                                img = Image.open(BytesIO(img_data))
                                st.image(img, caption=f"Foto {idx+1}", use_container_width=True)
                        except Exception as e:
                            st.error(f"Erro ao carregar foto: {e}")
                else:
                    st.info("Sem fotos")

def get_collaborators(supabase, user):
    query = supabase.table('users').select('full_name').eq('role', 'colaborador')
    if user['role'] == 'gerente':
        query = query.eq('company_id', user.get('company_id', 1))
    response = query.execute()
    return [u['full_name'] for u in response.data] if response.data else []

def format_datetime(dt_str):
    if not dt_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', ''))
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return dt_str
