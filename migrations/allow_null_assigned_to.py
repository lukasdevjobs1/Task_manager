"""
Migração: Permitir assigned_to NULL na tabela task_assignments
Para suportar tarefas na caixa da empresa (sem atribuição)
"""

from supabase import create_client
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def run_migration():
    """Altera coluna assigned_to para permitir NULL"""
    
    sql = """
    ALTER TABLE task_assignments 
    ALTER COLUMN assigned_to DROP NOT NULL;
    """
    
    try:
        result = supabase.rpc('exec_sql', {'query': sql}).execute()
        print("✅ Migração executada com sucesso!")
        print("Coluna assigned_to agora permite NULL")
        return True
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        print("\nExecute manualmente no Supabase SQL Editor:")
        print(sql)
        return False

if __name__ == "__main__":
    print("Iniciando migração...")
    run_migration()
