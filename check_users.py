import streamlit as st
from database import get_supabase_client

def check_users():
    supabase = get_supabase_client()
    
    try:
        response = supabase.table('users').select('*').eq('active', True).execute()
        
        st.write("### Usuários Ativos no Sistema:")
        
        if response.data:
            for user in response.data:
                st.write(f"**Username:** {user['username']}")
                st.write(f"**Nome:** {user['full_name']}")
                st.write(f"**Role:** {user['role']}")
                st.write(f"**Team:** {user['team']}")
                st.write("---")
        else:
            st.write("Nenhum usuário encontrado")
            
    except Exception as e:
        st.error(f"Erro ao buscar usuários: {e}")

if __name__ == "__main__":
    check_users()