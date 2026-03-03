import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
  ActivityIndicator,
  AppRegistry,
} from 'react-native';

const colors = {
  primary: '#6366f1',
  secondary: '#06b6d4',
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  background: '#f8fafc',
  surface: '#ffffff',
  text: '#1e293b',
  textSecondary: '#64748b',
  border: '#e2e8f0',
};

// Simulação da conexão com banco PostgreSQL
const authenticateUser = async (username, password) => {
  // Aqui seria a conexão real com o banco PostgreSQL
  // Por enquanto, vamos simular com os dados que existem no banco
  
  // Simulando delay de rede
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Dados simulados baseados no banco real
  const users = {
    'joao.tecnico': { 
      id: 1, 
      password: '123456', 
      full_name: 'João Técnico', 
      team: 'Infraestrutura',
      role: 'colaborador'
    },
    'maria.instaladora': { 
      id: 2, 
      password: '123456', 
      full_name: 'Maria Instaladora', 
      team: 'Instalação',
      role: 'colaborador'
    },
    'lucas.campo': { 
      id: 3, 
      password: '123456', 
      full_name: 'Lucas Campo', 
      team: 'Campo',
      role: 'colaborador'
    },
    'felipe.rede': { 
      id: 4, 
      password: '123456', 
      full_name: 'Felipe Rede', 
      team: 'Rede',
      role: 'colaborador'
    }
  };

  const user = users[username.toLowerCase()];
  if (user && user.password === password) {
    return { success: true, user };
  }
  
  return { success: false, error: 'Usuário ou senha inválidos' };
};

const getUserTasks = async (userId) => {
  // Simulação de tarefas do banco
  await new Promise(resolve => setTimeout(resolve, 500));
  
  const tasks = [
    {
      id: 1,
      title: 'Instalação Fibra Óptica',
      description: 'Instalação de fibra óptica residencial',
      address: 'Rua das Flores, 123 - Jardins',
      priority: 'alta',
      status: 'pendente',
      due_date: '2024-01-16T18:00:00Z',
      assigned_by: 'Gerente Carlos'
    },
    {
      id: 2,
      title: 'Manutenção Preventiva',
      description: 'Verificação de equipamentos de rede',
      address: 'Av. Paulista, 1000 - Bela Vista',
      priority: 'media',
      status: 'em_andamento',
      due_date: '2024-01-15T17:00:00Z',
      assigned_by: 'Gerente Ana'
    }
  ];
  
  return { success: true, tasks };
};

function App() {
  const [currentScreen, setCurrentScreen] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [tasks, setTasks] = useState([]);

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      Alert.alert('Erro', 'Preencha todos os campos');
      return;
    }

    setLoading(true);
    
    try {
      const result = await authenticateUser(username, password);
      
      if (result.success) {
        setUser(result.user);
        setCurrentScreen('home');
        Alert.alert('Sucesso!', `Bem-vindo, ${result.user.full_name}!`);
        
        // Carregar tarefas do usuário
        const tasksResult = await getUserTasks(result.user.id);
        if (tasksResult.success) {
          setTasks(tasksResult.tasks);
        }
      } else {
        Alert.alert('Erro', result.error);
      }
    } catch (error) {
      Alert.alert('Erro', 'Erro de conexão com servidor');
    }
    
    setLoading(false);
  };

  const handleLogout = () => {
    Alert.alert('Sair', 'Deseja sair do app?', [
      { text: 'Cancelar', style: 'cancel' },
      { text: 'Sair', onPress: () => {
        setCurrentScreen('login');
        setUsername('');
        setPassword('');
        setUser(null);
        setTasks([]);
      }}
    ]);
  };

  const refreshTasks = async () => {
    if (user) {
      const result = await getUserTasks(user.id);
      if (result.success) {
        setTasks(result.tasks);
        Alert.alert('Sucesso', 'Tarefas atualizadas!');
      }
    }
  };

  if (currentScreen === 'login') {
    return (
      <View style={styles.container}>
        <View style={styles.logoContainer}>
          <View style={styles.iconCircle}>
            <Text style={styles.iconText}>🔧</Text>
          </View>
          <Text style={styles.title}>Task Manager ISP</Text>
          <Text style={styles.subtitle}>Sistema Integrado com PostgreSQL</Text>
        </View>

        <View style={styles.formContainer}>
          <View style={styles.inputContainer}>
            <Text style={styles.inputIcon}>👤</Text>
            <TextInput
              style={styles.input}
              placeholder="Nome de usuário"
              value={username}
              onChangeText={setUsername}
              autoCapitalize="none"
            />
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.inputIcon}>🔒</Text>
            <TextInput
              style={styles.input}
              placeholder="Senha"
              value={password}
              onChangeText={setPassword}
              secureTextEntry
            />
          </View>

          <TouchableOpacity 
            style={[styles.loginButton, loading && styles.buttonDisabled]} 
            onPress={handleLogin}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="white" />
            ) : (
              <Text style={styles.loginButtonText}>Entrar</Text>
            )}
          </TouchableOpacity>

          <Text style={styles.testInfo}>
            Usuários do banco PostgreSQL:
            {"\n"}• joao.tecnico / 123456
            {"\n"}• maria.instaladora / 123456
            {"\n"}• lucas.campo / 123456
            {"\n"}• felipe.rede / 123456
          </Text>
        </View>
      </View>
    );
  }

  const pendentes = tasks.filter(t => t.status === 'pendente').length;
  const emAndamento = tasks.filter(t => t.status === 'em_andamento').length;
  const concluidas = tasks.filter(t => t.status === 'concluida').length;

  return (
    <ScrollView style={styles.homeContainer}>
      <View style={styles.header}>
        <Text style={styles.welcomeTitle}>Sistema Task Manager</Text>
        <Text style={styles.welcomeSubtitle}>{user?.full_name} - {user?.team}</Text>
      </View>
      
      <View style={styles.statsContainer}>
        <View style={[styles.statCard, styles.pendingCard]}>
          <Text style={styles.statIcon}>⏰</Text>
          <Text style={styles.statNumber}>{pendentes}</Text>
          <Text style={styles.statLabel}>Pendentes</Text>
        </View>
        <View style={[styles.statCard, styles.progressCard]}>
          <Text style={styles.statIcon}>🔄</Text>
          <Text style={styles.statNumber}>{emAndamento}</Text>
          <Text style={styles.statLabel}>Em Andamento</Text>
        </View>
        <View style={[styles.statCard, styles.completedCard]}>
          <Text style={styles.statIcon}>✅</Text>
          <Text style={styles.statNumber}>{concluidas}</Text>
          <Text style={styles.statLabel}>Concluídas</Text>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Tarefas Atribuídas</Text>

      {tasks.length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyText}>Nenhuma tarefa atribuída</Text>
          <Text style={styles.emptySubtext}>Aguarde novas atribuições do gerente</Text>
        </View>
      ) : (
        tasks.map((task) => (
          <View key={task.id} style={styles.taskCard}>
            <View style={styles.taskHeader}>
              <Text style={styles.taskTitle}>{task.title}</Text>
              <View style={[
                styles.priorityDot,
                { backgroundColor: 
                  task.priority === 'alta' ? colors.error :
                  task.priority === 'media' ? colors.warning : colors.success
                }
              ]} />
            </View>
            <Text style={styles.taskDescription}>{task.description}</Text>
            <Text style={styles.taskAddress}>📍 {task.address}</Text>
            <Text style={styles.taskAssignedBy}>👤 Atribuído por: {task.assigned_by}</Text>
            <View style={styles.taskFooter}>
              <View style={[
                styles.statusBadge,
                { backgroundColor:
                  task.status === 'pendente' ? colors.warning :
                  task.status === 'em_andamento' ? colors.secondary : colors.success
                }
              ]}>
                <Text style={styles.statusText}>
                  {task.status === 'pendente' ? 'Pendente' :
                   task.status === 'em_andamento' ? 'Em Andamento' : 'Concluída'}
                </Text>
              </View>
              <Text style={styles.taskTime}>⏰ {new Date(task.due_date).toLocaleDateString('pt-BR')}</Text>
            </View>
          </View>
        ))
      )}

      <TouchableOpacity style={styles.refreshButton} onPress={refreshTasks}>
        <Text style={styles.refreshText}>🔄 Atualizar Tarefas</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutText}>🚪 Sair</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    justifyContent: 'center',
    padding: 24,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  iconCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  iconText: {
    fontSize: 40,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: colors.textSecondary,
  },
  formContainer: {
    width: '100%',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 12,
    marginBottom: 16,
    paddingHorizontal: 16,
    borderWidth: 1,
    borderColor: colors.border,
  },
  inputIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  input: {
    flex: 1,
    paddingVertical: 16,
    fontSize: 16,
    color: colors.text,
  },
  loginButton: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  loginButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  testInfo: {
    textAlign: 'center',
    marginTop: 16,
    fontSize: 14,
    color: colors.textSecondary,
    fontStyle: 'italic',
  },
  homeContainer: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    backgroundColor: colors.surface,
    padding: 24,
    alignItems: 'center',
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    marginBottom: 20,
  },
  welcomeTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.primary,
    marginBottom: 8,
  },
  welcomeSubtitle: {
    fontSize: 16,
    color: colors.textSecondary,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    marginBottom: 24,
  },
  statCard: {
    backgroundColor: colors.surface,
    padding: 16,
    borderRadius: 16,
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 4,
  },
  pendingCard: {
    borderLeftWidth: 4,
    borderLeftColor: colors.warning,
  },
  progressCard: {
    borderLeftWidth: 4,
    borderLeftColor: colors.secondary,
  },
  completedCard: {
    borderLeftWidth: 4,
    borderLeftColor: colors.success,
  },
  statIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.text,
  },
  statLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
    paddingHorizontal: 20,
    marginBottom: 16,
  },
  emptyState: {
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 18,
    color: colors.textSecondary,
    marginBottom: 8,
  },
  emptySubtext: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  taskCard: {
    backgroundColor: colors.surface,
    marginHorizontal: 20,
    marginBottom: 12,
    borderRadius: 12,
    padding: 16,
  },
  taskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  taskTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.text,
    flex: 1,
  },
  priorityDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  taskDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 8,
  },
  taskAddress: {
    fontSize: 13,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  taskAssignedBy: {
    fontSize: 13,
    color: colors.textSecondary,
    marginBottom: 12,
  },
  taskFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  taskTime: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  refreshButton: {
    backgroundColor: colors.secondary,
    marginHorizontal: 20,
    marginTop: 20,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  refreshText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  logoutButton: {
    backgroundColor: colors.surface,
    marginHorizontal: 20,
    marginTop: 12,
    marginBottom: 30,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: colors.error,
  },
  logoutText: {
    color: colors.error,
    fontSize: 16,
    fontWeight: 'bold',
  },
});

AppRegistry.registerComponent('main', () => App);
export default App;