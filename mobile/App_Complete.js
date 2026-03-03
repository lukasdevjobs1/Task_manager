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

function App() {
  const [currentScreen, setCurrentScreen] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = () => {
    if (!username.trim() || !password.trim()) {
      Alert.alert('Erro', 'Preencha todos os campos');
      return;
    }

    setLoading(true);
    setTimeout(() => {
      // Contas GCNet
      const gcnetUsers = {
        'joao.tecnico': { password: '123456', name: 'João Técnico', team: 'Infraestrutura' },
        'maria.instaladora': { password: '123456', name: 'Maria Instaladora', team: 'Instalação' },
        'lucas.campo': { password: '123456', name: 'Lucas Campo', team: 'Campo' },
        'felipe.rede': { password: '123456', name: 'Felipe Rede', team: 'Rede' },
        'admin.gcnet': { password: 'gcnet2024', name: 'Admin GCNet', team: 'Administração' },
        'supervisor.gcnet': { password: 'super123', name: 'Supervisor GCNet', team: 'Supervisão' }
      };

      const user = gcnetUsers[username.toLowerCase()];
      if (user && user.password === password) {
        setCurrentScreen('home');
        Alert.alert('Sucesso!', `Bem-vindo, ${user.name}!`);
      } else {
        Alert.alert('Erro', 'Usuário ou senha inválidos\n\nContas GCNet disponíveis:\n• joao.tecnico / 123456\n• maria.instaladora / 123456\n• lucas.campo / 123456\n• felipe.rede / 123456\n• admin.gcnet / gcnet2024\n• supervisor.gcnet / super123');
      }
      setLoading(false);
    }, 1000);
  };

  const handleLogout = () => {
    Alert.alert('Sair', 'Deseja sair do app?', [
      { text: 'Cancelar', style: 'cancel' },
      { text: 'Sair', onPress: () => {
        setCurrentScreen('login');
        setUsername('');
        setPassword('');
      }}
    ]);
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
            Contas GCNet:
            {"\n"}• joao.tecnico / 123456
            {"\n"}• maria.instaladora / 123456
            {"\n"}• lucas.campo / 123456
            {"\n"}• felipe.rede / 123456
            {"\n"}• admin.gcnet / gcnet2024
            {"\n"}• supervisor.gcnet / super123
          </Text>
        </View>
      </View>
    );
  }

  return (
    <ScrollView style={styles.homeContainer}>
      <View style={styles.header}>
        <Text style={styles.welcomeTitle}>GCNet - Minhas Tarefas</Text>
        <Text style={styles.welcomeSubtitle}>Sistema Integrado de Gerenciamento</Text>
      </View>
      
      <View style={styles.statsContainer}>
        <View style={[styles.statCard, styles.pendingCard]}>
          <Text style={styles.statIcon}>⏰</Text>
          <Text style={styles.statNumber}>2</Text>
          <Text style={styles.statLabel}>Pendentes</Text>
        </View>
        <View style={[styles.statCard, styles.progressCard]}>
          <Text style={styles.statIcon}>🔄</Text>
          <Text style={styles.statNumber}>1</Text>
          <Text style={styles.statLabel}>Em Andamento</Text>
        </View>
        <View style={[styles.statCard, styles.completedCard]}>
          <Text style={styles.statIcon}>✅</Text>
          <Text style={styles.statNumber}>5</Text>
          <Text style={styles.statLabel}>Concluídas</Text>
        </View>
      </View>

      <Text style={styles.sectionTitle}>Tarefas Recentes</Text>

      <View style={styles.taskCard}>
        <View style={styles.taskHeader}>
          <Text style={styles.taskCompany}>GCNet Telecomunicações</Text>
          <View style={styles.priorityHigh} />
        </View>
        <Text style={styles.taskType}>Instalação Fibra Óptica</Text>
        <Text style={styles.taskClient}>Residencial Premium - Jardins</Text>
        <View style={styles.taskFooter}>
          <View style={styles.statusPending}>
            <Text style={styles.statusText}>Pendente</Text>
          </View>
          <Text style={styles.taskTime}>⏰ 16/01 18:00</Text>
        </View>
      </View>

      <View style={styles.taskCard}>
        <View style={styles.taskHeader}>
          <Text style={styles.taskCompany}>FibraMax Telecom</Text>
          <View style={styles.priorityMedium} />
        </View>
        <Text style={styles.taskType}>Manutenção Empresarial</Text>
        <Text style={styles.taskClient}>Comercial Center - Pinheiros</Text>
        <View style={styles.taskFooter}>
          <View style={styles.statusProgress}>
            <Text style={styles.statusText}>Em Andamento</Text>
          </View>
          <Text style={styles.taskTime}>⏰ 15/01 17:00</Text>
        </View>
      </View>

      <TouchableOpacity style={styles.notificationButton} onPress={() => 
        Alert.alert('🚨 Nova Tarefa', 'TechNet Soluções\n📍 Itaim Bibi\n⚡ Instalação Urgente')
      }>
        <Text style={styles.notificationText}>🔔 Simular Nova Tarefa</Text>
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
  taskCompany: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.text,
  },
  priorityHigh: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: colors.error,
  },
  priorityMedium: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: colors.warning,
  },
  taskType: {
    fontSize: 14,
    color: colors.primary,
    fontWeight: '600',
    marginBottom: 4,
  },
  taskClient: {
    fontSize: 13,
    color: colors.textSecondary,
    marginBottom: 12,
  },
  taskFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusPending: {
    backgroundColor: colors.warning,
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusProgress: {
    backgroundColor: colors.secondary,
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
  notificationButton: {
    backgroundColor: colors.primary,
    marginHorizontal: 20,
    marginTop: 20,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  notificationText: {
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