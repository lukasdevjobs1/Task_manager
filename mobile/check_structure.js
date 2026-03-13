import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://ntatkxgsykdnsfrqxwnz.supabase.co';
const supabaseKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY;

const supabase = createClient(supabaseUrl, supabaseKey);

async function checkTableStructure() {
  console.log('🔍 Verificando estrutura das tabelas...');
  
  try {
    // Verificar estrutura da tabela task_assignments
    const { data, error } = await supabase
      .from('task_assignments')
      .select('*')
      .limit(1);

    if (data && data.length > 0) {
      console.log('📋 Colunas da tabela task_assignments:');
      console.log(Object.keys(data[0]));
    } else {
      console.log('❌ Erro ou tabela vazia:', error?.message);
    }

  } catch (error) {
    console.log('❌ Erro:', error.message);
  }
}

checkTableStructure();