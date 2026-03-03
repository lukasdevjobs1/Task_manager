-- Migration 003: Tabela de materiais utilizados nas tarefas
-- Aplicar no Supabase SQL Editor

CREATE TABLE IF NOT EXISTS task_materials (
    id          SERIAL PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES task_assignments(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    material_name TEXT NOT NULL,
    quantity    NUMERIC(10, 2) NOT NULL DEFAULT 1,
    unit        TEXT NOT NULL DEFAULT 'un',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_task_materials_assignment ON task_materials(assignment_id);
CREATE INDEX IF NOT EXISTS idx_task_materials_user      ON task_materials(user_id);
CREATE INDEX IF NOT EXISTS idx_task_materials_created   ON task_materials(created_at);

-- RLS: técnico vê/insere apenas seus próprios materiais
ALTER TABLE task_materials ENABLE ROW LEVEL SECURITY;

-- Política: leitura — técnico vê os seus; gestor (admin/super_admin) vê todos da empresa
CREATE POLICY "materials_select" ON task_materials
    FOR SELECT USING (
        user_id = (SELECT id FROM users WHERE username = current_user)
        OR
        EXISTS (
            SELECT 1 FROM users u
            WHERE u.username = current_user
              AND u.role IN ('admin', 'super_admin')
        )
    );

-- Política: inserção — apenas o próprio técnico
CREATE POLICY "materials_insert" ON task_materials
    FOR INSERT WITH CHECK (
        user_id = (SELECT id FROM users WHERE username = current_user)
    );

-- Política: deleção — apenas o próprio técnico (para re-salvar ao re-executar)
CREATE POLICY "materials_delete" ON task_materials
    FOR DELETE USING (
        user_id = (SELECT id FROM users WHERE username = current_user)
    );

-- View de resumo para o painel do gestor (bonificações)
CREATE OR REPLACE VIEW vw_technician_materials_summary AS
SELECT
    u.id             AS user_id,
    u.full_name      AS technician_name,
    u.team,
    tm.material_name,
    tm.unit,
    SUM(tm.quantity) AS total_quantity,
    COUNT(*)         AS times_used,
    DATE_TRUNC('month', tm.created_at) AS reference_month
FROM task_materials tm
JOIN users u ON u.id = tm.user_id
JOIN task_assignments ta ON ta.id = tm.assignment_id
WHERE ta.status IN ('concluida', 'completed')
GROUP BY u.id, u.full_name, u.team, tm.material_name, tm.unit,
         DATE_TRUNC('month', tm.created_at)
ORDER BY reference_month DESC, total_quantity DESC;

-- View de desempenho completo do técnico (tarefas + materiais) para cálculo de bonificação
CREATE OR REPLACE VIEW vw_technician_performance AS
SELECT
    u.id             AS user_id,
    u.full_name      AS technician_name,
    u.team,
    DATE_TRUNC('month', ta.completed_at) AS reference_month,
    COUNT(DISTINCT ta.id)                AS tasks_completed,
    COUNT(DISTINCT tm.id)                AS materials_entries,
    SUM(tm.quantity)                     AS total_materials_qty
FROM users u
LEFT JOIN task_assignments ta
    ON ta.assigned_to = u.id
   AND ta.status IN ('concluida', 'completed')
LEFT JOIN task_materials tm
    ON tm.assignment_id = ta.id
   AND tm.user_id = u.id
WHERE u.role = 'technician'
  AND ta.completed_at IS NOT NULL
GROUP BY u.id, u.full_name, u.team,
         DATE_TRUNC('month', ta.completed_at)
ORDER BY reference_month DESC, tasks_completed DESC;
