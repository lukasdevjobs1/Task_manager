import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://ntatkxgsykdnsfrqxwnz.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YXRreGdzeWtkbnNmcnF4d256Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjIwNzEsImV4cCI6MjA4NDAzODA3MX0.wmv7xL8z-1D5OYmOzDr-RUzFAgFBbWxMrJk7TMSFv4M';

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