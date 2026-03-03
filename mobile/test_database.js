const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://ntatkxgsykdnsfrqxwnz.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YXRreGdzeWtkbnNmcnF4d256Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjIwNzEsImV4cCI6MjA4NDAzODA3MX0.wmv7xL8z-1D5OYmOzDr-RUzFAgFBbWxMrJk7TMSFv4M';

const supabase = createClient(supabaseUrl, supabaseKey);

async function testDatabase() {
  try {
    console.log('=== TESTE DE CONECTIVIDADE ===');
    
    // 1. Testar conexão básica
    const { data: users, error: usersError } = await supabase
      .from('users')
      .select('id, username, full_name')
      .limit(5);
    
    if (usersError) {
      console.error('Erro ao buscar usuários:', usersError);
      return;
    }
    
    console.log('✅ Conexão OK!');
    console.log('Usuários encontrados:', users.length);
    users.forEach(user => {
      console.log(`- ${user.username} (${user.full_name})`);
    });
    
    // 2. Testar tabela task_assignments
    const { data: tasks, error: tasksError } = await supabase
      .from('task_assignments')
      .select('id, title, status')
      .limit(5);
    
    if (tasksError) {
      console.error('Erro ao buscar tarefas:', tasksError);
    } else {
      console.log('Tarefas encontradas:', tasks.length);
      tasks.forEach(task => {
        console.log(`- ${task.title} (${task.status})`);
      });
    }
    
    // 3. Testar inserção de teste
    console.log('\n=== TESTE DE INSERÇÃO ===');
    const testData = {
      test_field: `teste_${Date.now()}`,
      created_at: new Date().toISOString()
    };
    
    // Criar tabela de teste se não existir
    const { error: createError } = await supabase.rpc('create_test_table');
    
    console.log('Teste concluído!');
    
  } catch (error) {
    console.error('Erro geral:', error);
  }
}

testDatabase();