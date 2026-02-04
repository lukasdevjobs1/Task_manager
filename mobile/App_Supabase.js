import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, ScrollView, ActivityIndicator, StyleSheet } from 'react-native';
import { createClient } from '@supabase/supabase-js';
import { registerRootComponent } from 'expo';

const colors = {
  primary: '#2563eb',
  secondary: '#3b82f6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  background: '#f8fafc',
  surface: '#ffffff',
  text: '#1e293b',
  textSecondary: '#64748b',
  border: '#e2e8f0',
};

// Configuração Supabase (mesmo do Streamlit)
const supabaseUrl = 'https://ntatkxgsykdnsfrqxwnz.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50YXRreGdzeWtkbnNmcnF4d256Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg0NjIwNzEsImV4cCI6MjA4NDAzODA3MX0.wmv7xL8z-1D5OYmOzDr-RUzFAgFBbWxMrJk7TMSFv4M';
const supabase = createClient(supabaseUrl, supabaseKey);

export default function App() {
  const [currentScreen, setCurrentScreen] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [availableUsers, setAvailableUsers] = useState([]);
  const [loadingTasks, setLoadingTasks] = useState(false);

  useEffect(() => {
    // Removido carregamento de usuários para melhor segurança
  }, []);

  const loadAvailableUsers = async () => {
    console.log('=== CARREGANDO USUÁRIOS DISPONÍVEIS ==>');
    try {
      const { data: users, error } = await supabase
        .from('users')
        .select('username, full_name, role')
        .eq('active', true)
        .order('username');

      console.log('Usuários disponíveis:');
      console.log('Error:', error);
      console.log('Data:', users);

      if (!error && users) {
        setAvailableUsers(users);
      }
    } catch (error) {
      console.error('Erro ao carregar usuários:', error);
    }
  };

  const testSupabaseConnection = async () => {
    console.log('=== TESTANDO CONEXÃO SUPABASE ==>');
    try {
      const { data, error } = await supabase
        .from('users')
        .select('count')
        .limit(1);
      
      console.log('Teste de conexão:');
      console.log('Error:', error);
      console.log('Data:', data);
      
      if (error) {
        Alert.alert('Erro de Conexão', `Erro: ${error.message}`);
      } else {
        Alert.alert('Sucesso', 'Conexão com Supabase funcionando!');
      }
    } catch (error) {
      console.log('Erro de conexão:', error);
      Alert.alert('Erro', `Erro de conexão: ${error.message}`);
    }
  };

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert('Erro', 'Preencha todos os campos');
      return;
    }

    console.log('=== INICIANDO LOGIN ==>');
    console.log('Username:', username);
    console.log('Password length:', password.length);
    console.log('Supabase URL:', supabaseUrl);

    setLoading(true);
    try {
      console.log('Fazendo busca no Supabase...');
      
      // Buscar usuário no Supabase
      const { data: users, error } = await supabase
        .from('users')
        .select('*')
        .ilike('username', username)
        .eq('active', true)
        .single();

      console.log('Resposta do Supabase:');
      console.log('Error:', error);
      console.log('Data:', users);

      if (error || !users) {
        console.log('Usuário não encontrado ou erro:', error?.message);
        Alert.alert('Erro', `Usuário '${username}' não encontrado.\n\nVerifique se o usuário está cadastrado no sistema Streamlit.`);
        setLoading(false);
        return;
      }

      console.log('Usuário encontrado:', users.username);
      console.log('Verificando senha...');
      
      // Verificar senha (simulação - em produção usar bcrypt)
      if (password === '123456' || password === users.password_hash) {
        console.log('Senha correta! Fazendo login...');
        setCurrentUser(users);
        setCurrentScreen('home');
        loadUserTasks(users.id);
        Alert.alert('Sucesso!', `Bem-vindo, ${users.full_name}!`);
      } else {
        console.log('Senha incorreta');
        Alert.alert('Erro', 'Senha incorreta');
      }
    } catch (error) {
      console.log('Erro de conexão:', error);
      Alert.alert('Erro', 'Erro de conexão com o banco');
    }
    setLoading(false);
  };

  const loadUserTasks = async (userId) => {
    console.log('=== CARREGANDO TAREFAS ==>');
    console.log('User ID:', userId);
    
    setLoadingTasks(true);
    try {
      const { data: taskData, error } = await supabase
        .from('task_assignments')
        .select(`
          *,
          assigned_by_user:users!task_assignments_assigned_by_fkey(full_name)
        `)
        .eq('assigned_to', userId)
        .order('created_at', { ascending: false });

      console.log('Resposta das tarefas:');
      console.log('Error:', error);
      console.log('Data:', taskData);

      if (error) {
        console.error('Erro ao carregar tarefas:', error);
      } else {
        console.log('Tarefas carregadas:', taskData?.length || 0);
        setTasks(taskData || []);
      }
    } catch (error) {
      console.error('Erro ao carregar tarefas:', error);
    }
    setLoadingTasks(false);
  };

  const updateTaskStatus = async (taskId, newStatus, notes = '') => {
    try {
      const updateData = {
        status: newStatus,
        notes: notes,
        updated_at: new Date().toISOString()
      };

      if (newStatus === 'em_andamento') {
        updateData.started_at = new Date().toISOString();
      } else if (newStatus === 'concluida') {
        updateData.completed_at = new Date().toISOString();
      }

      const { error } = await supabase
        .from('task_assignments')
        .update(updateData)
        .eq('id', taskId);

      if (error) {
        Alert.alert('Erro', 'Erro ao atualizar tarefa');
      } else {
        loadUserTasks(currentUser.id);
        Alert.alert('Sucesso', 'Status da tarefa atualizado!');
      }
    } catch (error) {
      Alert.alert('Erro', 'Erro ao atualizar tarefa');
    }
  };

  const handleLogout = () => {
    Alert.alert('Sair', 'Deseja sair do app?', [
      { text: 'Cancelar', style: 'cancel' },
      { text: 'Sair', onPress: () => {
        setCurrentScreen('login');
        setCurrentUser(null);
        setTasks([]);
        setUsername('');
        setPassword('');
      }}
    ]);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pendente': return colors.warning;
      case 'em_andamento': return colors.secondary;
      case 'concluida': return colors.success;
      default: return colors.textSecondary;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pendente': return 'Pendente';
      case 'em_andamento': return 'Em Andamento';
      case 'concluida': return 'Concluída';
      default: return status;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'alta': return colors.danger;
      case 'media': return colors.warning;
      case 'baixa': return colors.success;
      default: return colors.textSecondary;
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
          <Text style={styles.subtitle}>Sistema de Gerenciamento v2.0</Text>
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
            Entre com suas credenciais do sistema
          </Text>

          <TouchableOpacity 
            style={[styles.testButton]} 
            onPress={testSupabaseConnection}
          >
            <Text style={styles.testButtonText}>Testar Supabase</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  const pendingTasks = tasks.filter(t => t.status === 'pendente').length;
  const inProgressTasks = tasks.filter(t => t.status === 'em_andamento').length;
  const completedTasks = tasks.filter(t => t.status === 'concluida').length;

  return (
    <ScrollView style={styles.homeContainer}>
      <View style={styles.header}>
        <Text style={styles.welcomeTitle}>Olá, {currentUser?.full_name}</Text>
        <Text style={styles.welcomeSubtitle}>{currentUser?.team} • {currentUser?.role}</Text>
        <TouchableOpacity 
          style={styles.refreshButton} 
          onPress={() => loadUserTasks(currentUser.id)}
        >
          <Text style={styles.refreshText}>🔄 Atualizar</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.statsContainer}>
        <View style={[styles.statCard, styles.pendingCard]}>
          <Text style={styles.statIcon}>⏰</Text>
          <Text style={styles.statNumber}>{pendingTasks}</Text>
          <Text style={styles.statLabel}>Pendentes</Text>
        </View>
        <View style={[styles.statCard, styles.progressCard]}>
          <Text style={styles.statIcon}>🔄</Text>
          <Text style={styles.statNumber}>{inProgressTasks}</Text>
          <Text style={styles.statLabel}>Em Andamento</Text>
        </View>
        <View style={[styles.statCard, styles.completedCard]}>
          <Text style={styles.statIcon}>✅</Text>
          <Text style={styles.statNumber}>{completedTasks}</Text>
          <Text style={styles.statLabel}>Concluídas</Text>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Minhas Tarefas</Text>

      {loadingTasks ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.loadingText}>Carregando tarefas...</Text>
        </View>
      ) : tasks.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>Nenhuma tarefa encontrada</Text>
          <Text style={styles.emptySubtext}>Aguarde atribuições do gerente</Text>
        </View>
      ) : (
        tasks.map((task) => (
          <View key={task.id} style={styles.taskCard}>
            <View style={styles.taskHeader}>
              <Text style={styles.taskTitle}>{task.title}</Text>
              <View style={[styles.priorityDot, { backgroundColor: getPriorityColor(task.priority) }]} />
            </View>
            
            <Text style={styles.taskDescription}>{task.description}</Text>
            <Text style={styles.taskAddress}>📍 {task.address}</Text>
            
            <View style={styles.taskFooter}>
              <View style={[styles.statusBadge, { backgroundColor: getStatusColor(task.status) }]}>
                <Text style={styles.statusText}>{getStatusText(task.status)}</Text>
              </View>
              
              {task.status === 'pendente' && (
                <TouchableOpacity 
                  style={styles.actionButton}
                  onPress={() => updateTaskStatus(task.id, 'em_andamento')}
                >
                  <Text style={styles.actionButtonText}>Iniciar</Text>
                </TouchableOpacity>
              )}
              
              {task.status === 'em_andamento' && (
                <TouchableOpacity 
                  style={[styles.actionButton, { backgroundColor: colors.success }]}
                  onPress={() => updateTaskStatus(task.id, 'concluida')}
                >
                  <Text style={styles.actionButtonText}>Concluir</Text>
                </TouchableOpacity>
              )}
            </View>
            
            <Text style={styles.taskTime}>
              Atribuída por: {task.assigned_by_user?.full_name || 'Sistema'}
            </Text>
          </View>
        ))
      )}

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
  testButton: {
    backgroundColor: colors.secondary,
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 12,
  },
  testButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
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
    marginBottom: 12,
  },
  refreshButton: {
    backgroundColor: colors.secondary,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  refreshText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
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
  loadingContainer: {
    alignItems: 'center',
    padding: 40,
  },
  loadingText: {
    marginTop: 12,
    color: colors.textSecondary,
  },
  emptyContainer: {
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    color: colors.textSecondary,
    fontSize: 16,
    marginBottom: 8,
  },
  emptySubtext: {
    color: colors.textSecondary,
    fontSize: 14,
    fontStyle: 'italic',
  },
  taskCard: {
    backgroundColor: colors.surface,
    marginHorizontal: 20,
    marginBottom: 16,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.border,
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
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 12,
  },
  taskFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
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
  actionButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
  },
  actionButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
  },
  taskTime: {
    fontSize: 12,
    color: colors.textSecondary,
    fontStyle: 'italic',
  },
  logoutButton: {
    backgroundColor: colors.danger,
    marginHorizontal: 20,
    marginVertical: 20,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  logoutText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

registerRootComponent(App);