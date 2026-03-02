import streamlit as st
from database.supabase_only_connection import db
from auth.authentication import require_login, get_current_user
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

def show_completed_tasks_manager():
    require_login()
    user = get_current_user()
    
    if not user:
        st.error("Usuário não encontrado")
        return
    
    st.title("📋 Tarefas Concluídas - Visualização Gerente")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        date_filter = st.date_input("Filtrar por data", value=None)
    with col2:
        collaborator_filter = st.selectbox("Filtrar por colaborador", ["Todos"] + get_collaborators(user))
    
    # Buscar tarefas concluídas
    tasks = db.get_task_assignments(user['company_id'], status='concluida')
    
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
                photos = db.get_assignment_photos(task['id'])
                
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

def get_collaborators(user):
    users = db.get_all_users(user['company_id'])
    return [u['full_name'] for u in users if u['role'] == 'user']

def format_datetime(dt_str):
    if not dt_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', ''))
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return dt_str
