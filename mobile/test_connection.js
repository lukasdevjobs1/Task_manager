const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://ntatxgsykdnsfqxwnz.supabase.co';
const supabaseKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY;

const supabase = createClient(supabaseUrl, supabaseKey);

async function testConnection() {
  try {
    console.log('Testando conexão com Supabase...');
    
    // Teste simples - buscar usuários
    const { data, error } = await supabase
      .from('users')
      .select('id, username')
      .limit(1);
    
    if (error) {
      console.error('Erro na consulta:', error);
    } else {
      console.log('Conexão OK! Dados:', data);
    }
    
  } catch (error) {
    console.error('Erro de conexão:', error);
  }
}

testConnection();