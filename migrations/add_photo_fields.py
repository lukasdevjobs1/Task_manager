#!/usr/bin/env python3
"""
Migração: Adicionar campo original_name em assignment_photos
"""

import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from database.connection import get_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Adiciona coluna original_name"""
    conn = get_connection()
    if not conn:
        logger.error("Falha ao conectar com o banco de dados")
        return False
    
    try:
        cursor = conn.cursor()
        
        logger.info("Adicionando coluna original_name...")
        cursor.execute("""
            ALTER TABLE assignment_photos 
            ADD COLUMN IF NOT EXISTS original_name TEXT;
        """)
        
        conn.commit()
        logger.info("Migracao executada com sucesso!")
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Erro na migracao: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("Coluna original_name adicionada!")
    else:
        print("Falha na migracao!")
        sys.exit(1)
