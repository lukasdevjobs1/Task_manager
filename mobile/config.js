// Configurações do App Mobile - Task Manager ISP v2.0

export const CONFIG = {
  // URLs da API
  API_BASE_URL: __DEV__ 
    ? 'http://localhost:5000/api'  // Desenvolvimento local
    : 'https://sua-api-producao.com/api',  // Produção
  
  // Configurações Supabase (mesmas do sistema web)
  SUPABASE: {
    URL: 'https://ntatkxgsykdnsfrqxwnz.supabase.co',
    ANON_KEY: process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY,
    BUCKET: 'task-photos'
  },
  
  // Configurações do App
  APP: {
    NAME: 'Task Manager ISP',
    VERSION: '2.0',
    TIMEOUT: 10000, // 10 segundos
    RETRY_ATTEMPTS: 3
  },
  
  // Usuários de teste (apenas desenvolvimento)
  TEST_USERS: __DEV__ ? [
    { username: 'joao.tecnico', password: '123456', name: 'João Técnico' },
    { username: 'maria.instaladora', password: '123456', name: 'Maria Instaladora' },
    { username: 'lucas.campo', password: '123456', name: 'Lucas Campo' },
    { username: 'felipe.rede', password: '123456', name: 'Felipe Rede' }
  ] : []
};

export default CONFIG;