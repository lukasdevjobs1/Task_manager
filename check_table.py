from database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

# Verificar se a tabela notifications existe
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_name = 'notifications';")
table_exists = cursor.fetchone()
print(f"Tabela notifications existe: {bool(table_exists)}")

if table_exists:
    # Verificar colunas da tabela notifications
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'notifications';")
    columns = [row[0] for row in cursor.fetchall()]
    print(f"Colunas: {columns}")

conn.close()