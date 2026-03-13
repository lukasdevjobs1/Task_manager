import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://ntatkxgsykdnsfrqxwnz.supabase.co';
const supabaseKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY;

const supabase = createClient(supabaseUrl, supabaseKey);

async function migrateDatabase() {
  console.log('🚀 ISP Field Manager - Migração Supabase v2.0');
  console.log('=' .repeat(50));

  try {
    // Verificar se as colunas já existem
    console.log('🔍 Verificando estrutura atual...');
    
    const { data: existingData, error: selectError } = await supabase
      .from('task_assignments')
      .select('materials, service_notes, photos_count')
      .limit(1);

    if (selectError && selectError.code === '42703') {
      console.log('📝 Colunas não existem, executando migração via SQL...');
      
      // Como não podemos executar ALTER TABLE via JavaScript client,
      // vamos usar uma abordagem alternativa
      console.log('⚠️  ATENÇÃO: Execute este SQL manualmente no Supabase Dashboard:');
      console.log('');
      console.log('-- SQL para executar no Supabase SQL Editor:');
      console.log('ALTER TABLE task_assignments');
      console.log('ADD COLUMN IF NOT EXISTS materials TEXT,');
      console.log('ADD COLUMN IF NOT EXISTS service_notes TEXT,');
      console.log('ADD COLUMN IF NOT EXISTS photos_count INTEGER DEFAULT 0;');
      console.log('');
      console.log('CREATE TABLE IF NOT EXISTS task_photos (');
      console.log('  id SERIAL PRIMARY KEY,');
      console.log('  task_assignment_id INTEGER REFERENCES task_assignments(id) ON DELETE CASCADE,');
      console.log('  photo_url TEXT NOT NULL,');
      console.log('  photo_path TEXT,');
      console.log('  description TEXT,');
      console.log('  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP');
      console.log(');');
      console.log('');
      console.log('📋 Acesse: https://supabase.com/dashboard/project/ntatkxgsykdnsfrqxwnz/sql');
      
    } else if (!selectError) {
      console.log('✅ Colunas já existem! Migração não necessária.');
    } else {
      console.log('❌ Erro ao verificar estrutura:', selectError.message);
    }

    // Testar inserção de dados de exemplo
    console.log('🧪 Testando funcionalidades...');
    
    const { data: testData, error: testError } = await supabase
      .from('task_assignments')
      .select('id, title, materials, service_notes, photos_count')
      .limit(1);

    if (testError) {
      console.log('❌ Erro no teste:', testError.message);
    } else {
      console.log('✅ Teste bem-sucedido!');
      if (testData && testData.length > 0) {
        console.log('📋 Exemplo de tarefa:', testData[0]);
      }
    }

  } catch (error) {
    console.log('❌ Erro durante migração:', error.message);
  }
}

// Executar migração
migrateDatabase();