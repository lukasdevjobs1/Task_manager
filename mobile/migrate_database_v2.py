#!/usr/bin/env python3
"""
Migração do banco de dados para suportar as novas funcionalidades do app mobile
Adiciona colunas para materiais, observações e fotos nas tarefas
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def get_db_connection():
    """Conecta ao banco de dados PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'task_manager'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None

def execute_migration():
    """Executa a migração do banco de dados"""
    
    migration_sql = """
    -- Adicionar colunas para materiais e observações do serviço
    ALTER TABLE task_assignments 
    ADD COLUMN IF NOT EXISTS materials TEXT,
    ADD COLUMN IF NOT EXISTS service_notes TEXT,
    ADD COLUMN IF NOT EXISTS photos_count INTEGER DEFAULT 0;

    -- Criar tabela para armazenar fotos das tarefas (se não existir)
    CREATE TABLE IF NOT EXISTS task_photos (
        id SERIAL PRIMARY KEY,
        task_assignment_id INTEGER REFERENCES task_assignments(id) ON DELETE CASCADE,
        photo_url TEXT NOT NULL,
        photo_path TEXT,
        description TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Criar índices para melhor performance
    CREATE INDEX IF NOT EXISTS idx_task_photos_assignment_id ON task_photos(task_assignment_id);
    CREATE INDEX IF NOT EXISTS idx_task_assignments_status ON task_assignments(status);
    CREATE INDEX IF NOT EXISTS idx_task_assignments_assigned_to ON task_assignments(assigned_to);

    -- Comentários para documentação
    COMMENT ON COLUMN task_assignments.materials IS 'Materiais utilizados na execução da tarefa';
    COMMENT ON COLUMN task_assignments.service_notes IS 'Observações e detalhes do serviço prestado';
    COMMENT ON COLUMN task_assignments.photos_count IS 'Número de fotos anexadas à tarefa';
    COMMENT ON TABLE task_photos IS 'Fotos anexadas às tarefas de campo';
    """
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        print("🔄 Executando migração do banco de dados...")
        
        # Executar migração
        cursor.execute(migration_sql)
        conn.commit()
        
        print("✅ Migração executada com sucesso!")
        
        # Verificar se as colunas foram criadas
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'task_assignments' 
            AND column_name IN ('materials', 'service_notes', 'photos_count')
        """)
        
        columns = cursor.fetchall()
        print(f"📋 Colunas adicionadas: {[col[0] for col in columns]}")
        
        # Verificar se a tabela de fotos foi criada
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'task_photos'
            )
        """)
        
        table_exists = cursor.fetchone()[0]
        if table_exists:
            print("📸 Tabela 'task_photos' criada com sucesso!")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False

def main():
    """Função principal"""
    print("🚀 ISP Field Manager - Migração do Banco v2.0")
    print("=" * 50)
    
    if execute_migration():
        print("\n✅ Migração concluída com sucesso!")
        print("📱 O app mobile agora suporta:")
        print("   • Registro de materiais utilizados")
        print("   • Observações detalhadas do serviço")
        print("   • Upload e armazenamento de fotos")
        print("   • Melhor performance com índices otimizados")
    else:
        print("\n❌ Falha na migração!")
        sys.exit(1)

if __name__ == "__main__":
    main()