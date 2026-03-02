#!/usr/bin/env python3
"""
Migração: Adicionar sistema de atribuição de tarefas
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
    """Executa a migração completa"""
    conn = get_connection()
    if not conn:
        logger.error("Falha ao conectar com o banco de dados")
        return False
    
    try:
        cursor = conn.cursor()
        
        # 1. Adicionar coluna push_token na tabela users
        logger.info("Adicionando coluna push_token na tabela users...")
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS push_token TEXT;
        """)
        
        # 2. Criar tabela task_assignments
        logger.info("Criando tabela task_assignments...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_assignments (
                id SERIAL PRIMARY KEY,
                assigned_to INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                assigned_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                address TEXT NOT NULL,
                latitude DECIMAL(10, 8),
                longitude DECIMAL(11, 8),
                priority VARCHAR(20) DEFAULT 'media' CHECK (priority IN ('baixa', 'media', 'alta')),
                status VARCHAR(20) DEFAULT 'pendente' CHECK (status IN ('pendente', 'em_andamento', 'concluida', 'cancelada')),
                due_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                notes TEXT
            );
        """)
        
        # 3. Criar tabela assignment_photos
        logger.info("Criando tabela assignment_photos...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignment_photos (
                id SERIAL PRIMARY KEY,
                assignment_id INTEGER NOT NULL REFERENCES task_assignments(id) ON DELETE CASCADE,
                photo_url TEXT NOT NULL,
                photo_path TEXT,
                description TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 4. Criar índices para performance
        logger.info("Criando indices...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_assignments_assigned_to ON task_assignments(assigned_to);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_assignments_assigned_by ON task_assignments(assigned_by);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_assignments_status ON task_assignments(status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignment_photos_assignment_id ON assignment_photos(assignment_id);")
        
        # 5. Habilitar extensão pgcrypto se não existir
        logger.info("Habilitando extensao pgcrypto...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        
        # 6. Inserir dados de exemplo
        logger.info("Inserindo dados de exemplo...")
        
        # Verificar se já existem usuários
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'user';")
        result = cursor.fetchone()
        user_count = result[0] if result else 0
        
        if user_count == 0:
            # Inserir colaboradores de exemplo
            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, team, role, active) VALUES
                ('joao.tecnico', crypt('123456', gen_salt('bf')), 'João Técnico', 'infraestrutura', 'user', TRUE),
                ('maria.instaladora', crypt('123456', gen_salt('bf')), 'Maria Instaladora', 'fusao', 'user', TRUE),
                ('lucas.campo', crypt('123456', gen_salt('bf')), 'Lucas Campo', 'infraestrutura', 'user', TRUE),
                ('felipe.rede', crypt('123456', gen_salt('bf')), 'Felipe Rede', 'fusao', 'user', TRUE);
            """)
            logger.info("Usuarios de exemplo criados")
        
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
        print("PASSO 1 CONCLUIDO: Banco de Dados")
        print("\nTabelas criadas:")
        print("  - task_assignments (tarefas atribuidas)")
        print("  - assignment_photos (fotos das execucoes)")
        print("  - users.push_token (tokens push)")
        print("\nUsuarios de exemplo:")
        print("  - joao.tecnico / 123456")
        print("  - maria.instaladora / 123456")
        print("  - lucas.campo / 123456")
        print("  - felipe.rede / 123456")
    else:
        print("Falha na migracao!")
        sys.exit(1)