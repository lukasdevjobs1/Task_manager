"""
Migração para adicionar coluna is_super_admin na tabela users.
Define o primeiro admin como super_admin.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database.connection import engine


def run_migration():
    """Executa a migração para adicionar is_super_admin."""
    with engine.connect() as conn:
        # Verificar se a coluna já existe
        check_query = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
            AND column_name = 'is_super_admin'
            AND table_schema = 'public'
        """)
        result = conn.execute(check_query).fetchone()

        if result:
            print("Coluna is_super_admin já existe.")
        else:
            # Adicionar coluna is_super_admin
            print("Adicionando coluna is_super_admin...")
            try:
                conn.execute(text("""
                    ALTER TABLE users
                    ADD COLUMN is_super_admin BOOLEAN DEFAULT FALSE
                """))
                conn.commit()
                print("Coluna is_super_admin adicionada com sucesso!")
            except Exception as e:
                print(f"Erro ao adicionar coluna: {e}")
                conn.rollback()
                return

        # Definir o primeiro admin (id=1) como super_admin
        print("Definindo admin principal como super_admin...")
        conn.execute(text("""
            UPDATE users
            SET is_super_admin = TRUE
            WHERE id = 1
        """))
        conn.commit()
        print("Admin principal definido como super_admin!")

        # Mostrar status
        result = conn.execute(text("""
            SELECT id, username, full_name, is_super_admin
            FROM users
            WHERE role = 'admin'
        """))
        print("\nAdmins no sistema:")
        for row in result:
            super_status = "SUPER ADMIN" if row[3] else "Admin de empresa"
            print(f"  - ID {row[0]}: {row[2]} (@{row[1]}) - {super_status}")


if __name__ == "__main__":
    run_migration()
