-- Migração: Permitir assigned_to NULL na tabela task_assignments
-- Execute este SQL no Supabase SQL Editor

-- Permite que assigned_to seja NULL (para tarefas na caixa da empresa)
ALTER TABLE task_assignments 
ALTER COLUMN assigned_to DROP NOT NULL;

-- Verifica a alteração
SELECT column_name, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'task_assignments' 
AND column_name = 'assigned_to';
