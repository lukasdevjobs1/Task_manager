import psycopg2
from config import DB_CONFIG

def check_users():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("SELECT username, full_name, role, team, active FROM users ORDER BY username")
        users = cur.fetchall()
        
        print("=== USUÁRIOS NO BANCO ===")
        for user in users:
            username, full_name, role, team, active = user
            status = "ATIVO" if active else "INATIVO"
            print(f"Username: {username}")
            print(f"Nome: {full_name}")
            print(f"Role: {role}")
            print(f"Team: {team}")
            print(f"Status: {status}")
            print("-" * 30)
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    check_users()