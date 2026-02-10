// Configurações do App Mobile - Task Manager ISP v2.0

export const CONFIG = {
  // URLs da API
  API_BASE_URL: __DEV__ 
    ? 'http://localhost:5000/api'  // Desenvolvimento local
    : 'https://sua-api-producao.com/api',  // Produção
  
  // Configurações Supabase (mesmas do sistema web)
  SUPABASE: {
    URL: 'https://ntatkxgsykdnsfrqxwnz.supabase.co',
    ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YXRreGdzeWtkbnNmcnF4d256Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjIwNzEsImV4cCI6MjA4NDAzODA3MX0.wmv7xL8z-1D5OYmOzDr-RUzFAgFBbWxMrJk7TMSFv4M',
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