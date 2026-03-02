#!/usr/bin/env python3
"""
Migração: Adicionar campos service_notes e materials
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
    """Adiciona colunas service_notes e materials"""
    conn = get_connection()
    if not conn:
        logger.error("Falha ao conectar com o banco de dados")
        return False
    
    try:
        cursor = conn.cursor()
        
        logger.info("Adicionando colunas service_notes e materials...")
        cursor.execute("""
            ALTER TABLE task_assignments 
            ADD COLUMN IF NOT EXISTS service_notes TEXT,
            ADD COLUMN IF NOT EXISTS materials TEXT;
        """)
        
        conn.commit()
        logger.info("Migração executada com sucesso!")
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Erro na migração: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("✅ Colunas service_notes e materials adicionadas!")
    else:
        print("❌ Falha na migração!")
        sys.exit(1)
