const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://ntatkxgsykdnsfrqxwnz.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YXRreGdzeWtkbnNmcnF4d256Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjIwNzEsImV4cCI6MjA4NDAzODA3MX0.wmv7xL8z-1D5OYmOzDr-RUzFAgFBbWxMrJk7TMSFv4M';

const supabase = createClient(supabaseUrl, supabaseKey);

async function createVerifyFunction() {
  try {
    console.log('Criando função verify_password...');
    
    // Executar SQL para criar a função
    const { data, error } = await supabase.rpc('sql', {
      query: `
        CREATE EXTENSION IF NOT EXISTS pgcrypto;
        
        CREATE OR REPLACE FUNCTION verify_password(password_input TEXT, hash_input TEXT)
        RETURNS BOOLEAN
        LANGUAGE plpgsql
        SECURITY DEFINER
        AS $$
        BEGIN
          RETURN crypt(password_input, hash_input) = hash_input;
        EXCEPTION
          WHEN OTHERS THEN
            RETURN FALSE;
        END;
        $$;
        
        GRANT EXECUTE ON FUNCTION verify_password(TEXT, TEXT) TO anon;
        GRANT EXECUTE ON FUNCTION verify_password(TEXT, TEXT) TO authenticated;
      `
    });
    
    if (error) {
      console.error('Erro ao criar função:', error);
    } else {
      console.log('Função criada com sucesso!');
    }
    
    // Testar a função
    console.log('Testando função...');
    const testResult = await supabase.rpc('verify_password', {
      password_input: '123456',
      hash_input: '$2b$12$test'
    });
    
    console.log('Resultado do teste:', testResult);
    
  } catch (error) {
    console.error('Erro:', error);
  }
}

createVerifyFunction();