#!/usr/bin/env python3
"""
Migração para adicionar campo profile_photo na tabela users
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# Adicionar o diretório raiz ao path para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_connection

def add_profile_photo_column():
    """Adiciona coluna profile_photo na tabela users"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("Adicionando coluna profile_photo na tabela users...")
        
        # Verificar se a coluna já existe
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'profile_photo'
        """)
        
        if cursor.fetchone():
            print("Coluna profile_photo ja existe na tabela users")
            return
        
        # Adicionar coluna profile_photo
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN profile_photo TEXT
        """)
        
        conn.commit()
        print("Coluna profile_photo adicionada com sucesso!")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Erro ao adicionar coluna profile_photo: {e}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Iniciando migracao para adicionar profile_photo...")
    add_profile_photo_column()
    print("Migracao concluida!")