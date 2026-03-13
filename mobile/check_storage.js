// Script para verificar e criar bucket no Supabase Storage
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://ntatxgsykdnsfqxwnz.supabase.co';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY; // Service role key

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function checkAndCreateBucket() {
  try {
    console.log('Verificando buckets existentes...');
    
    // Lista buckets existentes
    const { data: buckets, error: listError } = await supabase.storage.listBuckets();
    
    if (listError) {
      console.error('Erro ao listar buckets:', listError);
      return;
    }
    
    console.log('Buckets existentes:', buckets.map(b => b.name));
    
    // Verifica se o bucket task-photos existe
    const taskPhotosBucket = buckets.find(bucket => bucket.name === 'task-photos');
    
    if (!taskPhotosBucket) {
      console.log('Criando bucket task-photos...');
      
      const { data, error } = await supabase.storage.createBucket('task-photos', {
        public: true,
        allowedMimeTypes: ['image/jpeg', 'image/png', 'image/jpg'],
        fileSizeLimit: 5242880 // 5MB
      });
      
      if (error) {
        console.error('Erro ao criar bucket:', error);
      } else {
        console.log('Bucket task-photos criado com sucesso!');
      }
    } else {
      console.log('Bucket task-photos já existe!');
    }
    
    // Testa upload de uma imagem pequena
    console.log('Testando upload...');
    const testData = new Blob(['test'], { type: 'text/plain' });
    
    const { data: uploadData, error: uploadError } = await supabase.storage
      .from('task-photos')
      .upload('test.txt', testData);
    
    if (uploadError) {
      console.error('Erro no teste de upload:', uploadError);
    } else {
      console.log('Teste de upload bem-sucedido!');
      
      // Remove arquivo de teste
      await supabase.storage.from('task-photos').remove(['test.txt']);
    }
    
  } catch (error) {
    console.error('Erro geral:', error);
  }
}

checkAndCreateBucket();