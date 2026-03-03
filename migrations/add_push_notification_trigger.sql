-- Migration: Adicionar trigger para enviar notificações push quando tarefa é criada
-- Execute este script no SQL Editor do Supabase

-- 1. Habilitar extensão pg_net para fazer HTTP requests (se ainda não estiver habilitada)
-- CREATE EXTENSION IF NOT EXISTS pg_net;

-- 2. Adicionar colunas adicionais na tabela task_assignments se necessário
ALTER TABLE task_assignments
ADD COLUMN IF NOT EXISTS started_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP WITH TIME ZONE;

-- 3. Atualizar tabela assignment_photos para compatibilidade com o app
ALTER TABLE assignment_photos
ADD COLUMN IF NOT EXISTS photo_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS photo_path VARCHAR(500),
ADD COLUMN IF NOT EXISTS description TEXT;

-- Migrar dados antigos se existirem
UPDATE assignment_photos
SET photo_path = file_path,
    photo_url = file_path
WHERE photo_path IS NULL AND file_path IS NOT NULL;

-- 4. Criar função para inserir notificação no banco quando tarefa é criada
CREATE OR REPLACE FUNCTION notify_task_assigned()
RETURNS TRIGGER AS $$
DECLARE
    assigner_name VARCHAR(100);
BEGIN
    -- Só cria notificação se a tarefa foi atribuída a alguém
    IF NEW.assigned_to IS NULL THEN
        RETURN NEW;
    END IF;

    -- Buscar nome do usuário que atribuiu
    SELECT full_name INTO assigner_name
    FROM users
    WHERE id = NEW.assigned_by;

    -- Inserir notificação no banco
    INSERT INTO notifications (
        user_id,
        company_id,
        type,
        title,
        message,
        reference_id,
        read,
        created_at
    ) VALUES (
        NEW.assigned_to,
        NEW.company_id,
        'task_assigned',
        'Nova Tarefa Atribuída',
        'Você recebeu uma nova tarefa: ' || NEW.title || ' - Atribuída por ' || COALESCE(assigner_name, 'Sistema'),
        NEW.id,
        false,
        NOW()
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5. Criar trigger que dispara quando tarefa é inserida
DROP TRIGGER IF EXISTS trigger_notify_task_assigned ON task_assignments;
CREATE TRIGGER trigger_notify_task_assigned
    AFTER INSERT ON task_assignments
    FOR EACH ROW
    EXECUTE FUNCTION notify_task_assigned();

-- 6. Criar função para notificar mudança de status
CREATE OR REPLACE FUNCTION notify_task_status_changed()
RETURNS TRIGGER AS $$
BEGIN
    -- Só notifica se o status realmente mudou
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO notifications (
            user_id,
            company_id,
            type,
            title,
            message,
            reference_id,
            read,
            created_at
        ) VALUES (
            NEW.assigned_by, -- Notifica quem criou a tarefa
            NEW.company_id,
            'task_status_changed',
            'Status da Tarefa Atualizado',
            'A tarefa "' || NEW.title || '" foi atualizada para: ' ||
            CASE NEW.status
                WHEN 'em_andamento' THEN 'Em Andamento'
                WHEN 'in_progress' THEN 'Em Andamento'
                WHEN 'concluida' THEN 'Concluída'
                WHEN 'completed' THEN 'Concluída'
                ELSE NEW.status
            END,
            NEW.id,
            false,
            NOW()
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 7. Criar trigger para mudança de status
DROP TRIGGER IF EXISTS trigger_notify_task_status_changed ON task_assignments;
CREATE TRIGGER trigger_notify_task_status_changed
    AFTER UPDATE ON task_assignments
    FOR EACH ROW
    EXECUTE FUNCTION notify_task_status_changed();

-- 8. Criar tabela para armazenar configurações de push (FCM Server Key, etc.)
CREATE TABLE IF NOT EXISTS app_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inserir configuração placeholder para FCM Server Key
-- IMPORTANTE: Substitua pelo seu Server Key real do Firebase Console
INSERT INTO app_settings (key, value)
VALUES ('fcm_server_key', 'YOUR_FCM_SERVER_KEY_HERE')
ON CONFLICT (key) DO NOTHING;

-- 9. Índice para buscar configurações rapidamente
CREATE INDEX IF NOT EXISTS idx_app_settings_key ON app_settings(key);

-- 10. Comentários
COMMENT ON FUNCTION notify_task_assigned() IS 'Cria notificação no banco quando tarefa é atribuída';
COMMENT ON FUNCTION notify_task_status_changed() IS 'Cria notificação quando status da tarefa muda';
