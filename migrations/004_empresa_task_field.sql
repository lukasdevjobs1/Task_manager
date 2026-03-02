-- Migration 004: Adiciona campo empresa_nome em task_assignments
-- Aplicar manualmente no Supabase SQL Editor

ALTER TABLE task_assignments
  ADD COLUMN IF NOT EXISTS empresa_nome VARCHAR(100);

COMMENT ON COLUMN task_assignments.empresa_nome IS
  'Nome da empresa do grupo a qual a tarefa pertence (ex: GCNET Provedor, Net Alfa)';
