// Configuração da API - ajuste a URL conforme necessário
const API_BASE_URL = 'http://localhost:8501'; // URL do Streamlit

export const authService = {
  // Login real conectando ao banco PostgreSQL
  async login(username, password) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          password: password
        })
      });

      if (!response.ok) {
        return { success: false, error: 'Erro de conexão com servidor' };
      }

      const data = await response.json();
      
      if (data.success) {
        return {
          success: true,
          user: {
            id: data.user.id,
            username: data.user.username,
            fullName: data.user.full_name,
            team: data.user.team,
            role: data.user.role
          }
        };
      }

      return { success: false, error: data.error || 'Credenciais inválidas' };
    } catch (error) {
      console.error('Erro na autenticação:', error);
      return { success: false, error: 'Erro de conexão' };
    }
  },

  // Buscar tarefas do usuário
  async getUserTasks(userId) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks/${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        return { success: false, error: 'Erro ao carregar tarefas' };
      }

      const data = await response.json();
      return { success: true, tasks: data.tasks || [] };
    } catch (error) {
      console.error('Erro ao buscar tarefas:', error);
      return { success: false, error: 'Erro de conexão' };
    }
  }
};