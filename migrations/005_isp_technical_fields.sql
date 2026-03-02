-- Migration 005: Campos técnicos ISP em task_assignments
-- Aplicar no Supabase SQL Editor antes de testar o app

ALTER TABLE task_assignments
  ADD COLUMN IF NOT EXISTS abertura_fechamento_cx_emenda INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS abertura_fechamento_cto       INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS abertura_fechamento_rozeta    INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS quantidade_cto                INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS quantidade_cx_emenda          INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS fibra_lancada                 NUMERIC(10,2) DEFAULT 0;
