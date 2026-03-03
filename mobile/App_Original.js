import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Image,
  FlatList,
  ActivityIndicator,
} from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { registerRootComponent } from 'expo';
import * as ImagePicker from 'expo-image-picker';
import * as Notifications from 'expo-notifications';

// Importar serviços
import { authenticateUser, saveUserToStorage, loadUserFromStorage, clearUserFromStorage } from './src/services/auth';
import { getMyTasks, updateTaskStatus, uploadTaskPhoto } from './src/services/tasks';

// Configuração de notificações
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

// Paleta de cores dinâmica
const colors = {
  primary: '#6366f1',
  primaryDark: '#4f46e5',
  secondary: '#06b6d4',
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  background: '#f8fafc',
  surface: '#ffffff',
  text: '#1e293b',
  textSecondary: '#64748b',
  border: '#e2e8f0',
  gradient: ['#6366f1', '#8b5cf6'],
};

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Tela de Login com autenticação real
function LoginScreen({ navigation }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Verificar se já existe usuário logado
    checkExistingUser();
  }, []);

  const checkExistingUser = async () => {
    try {
      const savedUser = await loadUserFromStorage();
      if (savedUser) {
        setUser(savedUser);
        navigation.navigate('MainTabs');
      }
    } catch (error) {
      console.error('Erro ao verificar usuário:', error);
    }
  };

  const handleLogin = async () => {
    if (!username.trim()) {
      Alert.alert('Erro', 'Informe o nome de usuário.');
      return;
    }
    if (!password.trim()) {
      Alert.alert('Erro', 'Informe a senha.');
      return;
    }

    setLoading(true);
    try {
      const userData = await authenticateUser(username.trim(), password);
      await saveUserToStorage(userData);
      setUser(userData);
      
      Alert.alert(
        'Login realizado!',
        `Bem-vindo, ${userData.full_name}!`,
        [{ text: 'OK', onPress: () => navigation.navigate('MainTabs') }]
      );
    } catch (error) {
      Alert.alert('Erro', error.message || 'Falha na autenticação');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <View style={styles.logoContainer}>
        <View style={styles.iconCircle}>
          <Ionicons name="construct" size={48} color="#ffffff" />
        </View>
        <Text style={styles.title}>Task Manager</Text>
        <Text style={styles.subtitle}>Acesse sua conta para continuar</Text>
      </View>

      <View style={styles.formContainer}>
        <View style={styles.inputContainer}>
          <Ionicons name="person-outline" size={20} color="#8e8e93" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="Nome de usuário"
            placeholderTextColor="#8e8e93"
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
            autoCorrect={false}
          />
        </View>

        <View style={styles.inputContainer}>
          <Ionicons name="lock-closed-outline" size={20} color="#8e8e93" style={styles.inputIcon} />
          <TextInput
            style={styles.input}
            placeholder="Senha"
            placeholderTextColor="#8e8e93"
            value={password}
            onChangeText={setPassword}
            secureTextEntry={!showPassword}
            autoCapitalize="none"
            autoCorrect={false}
          />
          <TouchableOpacity
            style={styles.eyeButton}
            onPress={() => setShowPassword(!showPassword)}
          >
            <Ionicons
              name={showPassword ? 'eye-off-outline' : 'eye-outline'}
              size={20}
              color="#8e8e93"
            />
          </TouchableOpacity>
        </View>

        <TouchableOpacity 
          style={[styles.loginButton, loading && styles.loginButtonDisabled]} 
          onPress={handleLogin}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator size="small" color="#ffffff" />
          ) : (
            <Text style={styles.loginButtonText}>Entrar</Text>
          )}
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

// Dados simulados do sistema hierárquico
const systemData = {
  // Empresas cadastradas pelo Admin Geral
  empresas: [
    {
      id: 1,
      nome: 'TechNet Soluções',
      gerente: 'Carlos Silva',
      email: 'carlos@technet.com',
      telefone: '(11) 99999-1234',
      ativa: true
    },
    {
      id: 2,
      nome: 'FibraMax Telecom',
      gerente: 'Ana Santos',
      email: 'ana@fibramax.com',
      telefone: '(11) 99999-5678',
      ativa: true
    },
    {
      id: 3,
      nome: 'ConectaBrasil ISP',
      gerente: 'Roberto Lima',
      email: 'roberto@conectabrasil.com',
      telefone: '(11) 99999-9012',
      ativa: true
    }
  ],
  // Colaboradores por empresa
  colaboradores: {
    1: ['João Técnico', 'Maria Instaladora', 'Pedro Manutenção'],
    2: ['Lucas Campo', 'Carla Fibra', 'Diego Reparo'],
    3: ['Felipe Rede', 'Juliana Cabo', 'Marcos Instalação']
  }
};

// Tela Home com dados reais
function HomeScreen({ navigation }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);

  useEffect(() => {
    loadUserAndTasks();
  }, []);

  const loadUserAndTasks = async () => {
    try {
      const userData = await loadUserFromStorage();
      if (userData) {
        setUser(userData);
        const userTasks = await getMyTasks(userData.id);
        setTasks(userTasks);
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      Alert.alert('Erro', 'Falha ao carregar tarefas');
    } finally {
      setLoading(false);
    }
  };

  const showNewTaskNotification = async () => {
    const newTask = {
      empresaNome: 'TechNet Soluções',
      gerente: 'Carlos Silva',
      colaborador: user?.full_name || 'Colaborador',
      cliente: 'Edifício Copacabana',
      bairro: 'Itaim Bibi',
      endereco: 'Rua Pedroso Alvarenga, 1245 - Cobertura',
      tipo: 'Instalação Urgente',
      prioridade: 'alta',
      prazo: 'Hoje até 19:00'
    };

    await Notifications.scheduleNotificationAsync({
      content: {
        title: '🚨 Nova Tarefa Atribuída!',
        body: `${newTask.empresaNome}\n📍 ${newTask.bairro} - ${newTask.cliente}\n⚡ ${newTask.tipo}\n👥 Atribuído por: ${newTask.gerente}`,
        data: newTask,
        sound: true,
      },
      trigger: null,
    });

    Alert.alert(
      '🚨 Nova Tarefa Atribuída',
      `EMPRESA: ${newTask.empresaNome}\n\nGERENTE RESPONSÁVEL:\n${newTask.gerente}\n\nCOLABORADOR DESIGNADO:\n${newTask.colaborador}\n\nCLIENTE:\n${newTask.cliente}\n\nLOCALIZAÇÃO:\n${newTask.bairro}\n${newTask.endereco}\n\nTIPO DE SERVIÇO:\n${newTask.tipo}\n\nPRIORIDADE: ${newTask.prioridade.toUpperCase()}\n\n⏰ PRAZO: ${newTask.prazo}`,
      [
        { text: 'Ver Depois', style: 'cancel' },
        { text: 'Aceitar Tarefa', onPress: () => navigation.navigate('TaskList') },
      ]
    );
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

  const getPriorityIcon = (prioridade) => {
    switch (prioridade) {
      case 'alta': return 'arrow-up-circle';
      case 'media': return 'remove-circle';
      case 'baixa': return 'arrow-down-circle';
      default: return 'help-circle';
    }
  };

  const getPriorityColor = (prioridade) => {
    switch (prioridade) {
      case 'alta': return colors.error;
      case 'media': return colors.warning;
      case 'baixa': return colors.success;
      default: return colors.textSecondary;
    }
  };

  const pendentes = tasks.filter(t => t.status === 'pendente').length;
  const emAndamento = tasks.filter(t => t.status === 'em_andamento').length;
  const concluidas = tasks.filter(t => t.status === 'concluida').length;

  return (
    <ScrollView style={[styles.homeContainer, { backgroundColor: colors.background }]}>
      <View style={[styles.header, { backgroundColor: colors.surface }]}>
        <Text style={[styles.welcomeTitle, { color: colors.primary }]}>Minhas Tarefas</Text>
        <Text style={[styles.welcomeSubtitle, { color: colors.textSecondary }]}>Gerencie suas atividades de campo</Text>
      </View>
      
      <View style={styles.statsContainer}>
        <View style={[styles.statCard, { borderLeftColor: colors.warning, borderLeftWidth: 4 }]}>
          <Ionicons name="time" size={28} color={colors.warning} />
          <Text style={[styles.statNumber, { color: colors.text }]}>{pendentes}</Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>Pendentes</Text>
        </View>
        <View style={[styles.statCard, { borderLeftColor: colors.secondary, borderLeftWidth: 4 }]}>
          <Ionicons name="play-circle" size={28} color={colors.secondary} />
          <Text style={[styles.statNumber, { color: colors.text }]}>{emAndamento}</Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>Em Andamento</Text>
        </View>
        <View style={[styles.statCard, { borderLeftColor: colors.success, borderLeftWidth: 4 }]}>
          <Ionicons name="checkmark-circle" size={28} color={colors.success} />
          <Text style={[styles.statNumber, { color: colors.text }]}>{concluidas}</Text>
          <Text style={[styles.statLabel, { color: colors.textSecondary }]}>Concluídas</Text>
        </View>
      </View>

      <View style={styles.sectionHeader}>
        <Text style={[styles.sectionTitle, { color: colors.text }]}>Tarefas Recentes</Text>
        <TouchableOpacity onPress={() => navigation.navigate('TaskList')}>
          <Text style={[styles.seeAllText, { color: colors.primary }]}>Ver todas</Text>
        </TouchableOpacity>
      </View>

      {tasks.slice(0, 3).map((task) => (
        <TouchableOpacity key={task.id} style={[styles.taskCard, { backgroundColor: colors.surface }]}>
          <View style={styles.taskHeader}>
            <View style={styles.taskInfo}>
              <Text style={[styles.taskEmpresa, { color: colors.text }]}>{task.empresaNome}</Text>
              <Text style={[styles.taskGerente, { color: colors.primary }]}>Gerente: {task.gerente}</Text>
              <Text style={[styles.taskTipo, { color: colors.secondary }]}>{task.tipo}</Text>
              <Text style={[styles.taskCliente, { color: colors.textSecondary }]}>{task.cliente} - {task.bairro}</Text>
            </View>
            <View style={styles.taskMeta}>
              <Ionicons 
                name={getPriorityIcon(task.prioridade)} 
                size={24} 
                color={getPriorityColor(task.prioridade)} 
              />
            </View>
          </View>
          <View style={styles.taskDetails}>
            <Text style={[styles.taskColaborador, { color: colors.text }]}>👤 {task.colaboradorAtribuido}</Text>
            <Text style={[styles.taskPrazo, { color: colors.warning }]}>⏰ {task.prazo}</Text>
          </View>
          <View style={styles.taskFooter}>
            <View style={[styles.statusBadge, { backgroundColor: getStatusColor(task.status) }]}>
              <Text style={styles.statusText}>{getStatusText(task.status)}</Text>
            </View>
            <Text style={[styles.taskDate, { color: colors.textSecondary }]}>{task.dataAtribuicao}</Text>
          </View>
        </TouchableOpacity>
      ))}}

      <TouchableOpacity 
        style={[styles.testNotificationButton, { backgroundColor: colors.primary }]}
        onPress={showNewTaskNotification}
      >
        <Ionicons name="notifications" size={20} color="white" />
        <Text style={styles.testNotificationText}>Simular Nova Tarefa</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

// Tela de Lista de Tarefas
function TaskListScreen({ navigation }) {
  const [tasks] = useState([
    {
      id: 1,
      empresa: 'NET Fibra',
      bairro: 'Centro',
      endereco: 'Rua das Flores, 123',
      status: 'pendente',
      prioridade: 'alta',
      dataAtribuicao: '2024-01-15',
      tipo: 'Instalação',
      descricao: 'Instalação de fibra ótica residencial'
    },
    {
      id: 2,
      empresa: 'Vivo Telecom',
      bairro: 'Jardim América',
      endereco: 'Av. Principal, 456',
      status: 'em_andamento',
      prioridade: 'media',
      dataAtribuicao: '2024-01-14',
      tipo: 'Manutenção',
      descricao: 'Reparo em caixa de emenda'
    },
    {
      id: 3,
      empresa: 'Claro Internet',
      bairro: 'Vila Nova',
      endereco: 'Rua dos Pinheiros, 789',
      status: 'concluida',
      prioridade: 'baixa',
      dataAtribuicao: '2024-01-13',
      tipo: 'Reparo',
      descricao: 'Substituição de cabo danificado'
    }
  ]);

  const [filter, setFilter] = useState('todas');

  const filteredTasks = tasks.filter(task => {
    if (filter === 'todas') return true;
    return task.status === filter;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'pendente': return '#ff9800';
      case 'em_andamento': return '#2196f3';
      case 'concluida': return '#4caf50';
      default: return '#666';
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

  const getPriorityIcon = (prioridade) => {
    switch (prioridade) {
      case 'alta': return 'arrow-up-circle';
      case 'media': return 'remove-circle';
      case 'baixa': return 'arrow-down-circle';
      default: return 'help-circle';
    }
  };

  const getPriorityColor = (prioridade) => {
    switch (prioridade) {
      case 'alta': return '#f44336';
      case 'media': return '#ff9800';
      case 'baixa': return '#4caf50';
      default: return '#666';
    }
  };

  return (
    <View style={styles.taskListContainer}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterContainer}>
        {['todas', 'pendente', 'em_andamento', 'concluida'].map((status) => (
          <TouchableOpacity
            key={status}
            style={[
              styles.filterButton,
              filter === status && styles.filterButtonActive
            ]}
            onPress={() => setFilter(status)}
          >
            <Text style={[
              styles.filterButtonText,
              filter === status && styles.filterButtonTextActive
            ]}>
              {status === 'todas' ? 'Todas' : getStatusText(status)}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <ScrollView style={styles.taskList}>
        {filteredTasks.map((task) => (
          <TouchableOpacity 
            key={task.id} 
            style={styles.taskCardDetailed}
            onPress={() => navigation.navigate('TaskDetail', { task })}
          >
            <View style={styles.taskHeader}>
              <View style={styles.taskInfo}>
                <Text style={styles.taskEmpresa}>{task.empresa}</Text>
                <Text style={styles.taskTipo}>{task.tipo}</Text>
                <Text style={styles.taskBairro}>{task.bairro}</Text>
              </View>
              <View style={styles.taskMeta}>
                <Ionicons 
                  name={getPriorityIcon(task.prioridade)} 
                  size={24} 
                  color={getPriorityColor(task.prioridade)} 
                />
              </View>
            </View>
            <Text style={styles.taskDescricao}>{task.descricao}</Text>
            <View style={styles.taskFooter}>
              <View style={[styles.statusBadge, { backgroundColor: getStatusColor(task.status) }]}>
                <Text style={styles.statusText}>{getStatusText(task.status)}</Text>
              </View>
              <Text style={styles.taskDate}>{task.dataAtribuicao}</Text>
            </View>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
}
// Tela de Registro de Tarefas melhorada com fotos
function RegisterTaskScreen() {
  const [empresa, setEmpresa] = useState('');
  const [bairro, setBairro] = useState('');
  const [endereco, setEndereco] = useState('');
  const [tipoFibra, setTipoFibra] = useState('F.06');
  const [fibraLancada, setFibraLancada] = useState('');
  const [caixaEmenda, setCaixaEmenda] = useState({ abertura: false, fechamento: false, qtd: '' });
  const [cto, setCto] = useState({ abertura: false, fechamento: false, qtd: '' });
  const [rozeta, setRozeta] = useState({ abertura: false, fechamento: false });
  const [observacoes, setObservacoes] = useState('');
  const [fotos, setFotos] = useState([]);

  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Erro', 'Permissão para acessar a galeria é necessária!');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
    });

    if (!result.canceled) {
      setFotos([...fotos, result.assets[0]]);
    }
  };

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Erro', 'Permissão para usar a câmera é necessária!');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
    });

    if (!result.canceled) {
      setFotos([...fotos, result.assets[0]]);
    }
  };

  const removePhoto = (index) => {
    const newFotos = fotos.filter((_, i) => i !== index);
    setFotos(newFotos);
  };

  const showPhotoOptions = () => {
    Alert.alert(
      'Adicionar Foto',
      'Escolha uma opção:',
      [
        { text: 'Câmera', onPress: takePhoto },
        { text: 'Galeria', onPress: pickImage },
        { text: 'Cancelar', style: 'cancel' },
      ]
    );
  };

  const handleSubmit = async () => {
    if (!empresa.trim() || !bairro.trim() || !endereco.trim()) {
      Alert.alert('Erro', 'Preencha todos os campos obrigatórios.');
      return;
    }
    
    if (fotos.length === 0) {
      Alert.alert('Erro', 'Adicione pelo menos uma foto da tarefa.');
      return;
    }

    // Simular envio de notificação
    await Notifications.scheduleNotificationAsync({
      content: {
        title: '✅ Nova Tarefa Atribuída!',
        body: `${empresa} - ${bairro}\n${endereco}\nTipo: Instalação de Fibra`,
        data: {
          empresa,
          bairro,
          endereco,
          tipo: 'Instalação',
          prioridade: 'alta'
        },
      },
      trigger: { seconds: 2 },
    });

    Alert.alert('Sucesso', 'Tarefa registrada com sucesso!\nNotificação enviada ao técnico.');
    
    // Reset form
    setEmpresa('');
    setBairro('');
    setEndereco('');
    setFibraLancada('');
    setCaixaEmenda({ abertura: false, fechamento: false, qtd: '' });
    setCto({ abertura: false, fechamento: false, qtd: '' });
    setRozeta({ abertura: false, fechamento: false });
    setObservacoes('');
    setFotos([]);
  };

  return (
    <ScrollView style={[styles.formScreen, { backgroundColor: colors.background }]}>
      <View style={styles.formHeader}>
        <Text style={[styles.formTitle, { color: colors.primary }]}>Nova Tarefa de Campo</Text>
        <Text style={[styles.formSubtitle, { color: colors.textSecondary }]}>Preencha os dados da tarefa</Text>
      </View>
      
      <View style={[styles.section, styles.card]}>
        <Text style={[styles.sectionTitle, { color: colors.text }]}>Informações Básicas</Text>
        
        <View style={styles.inputGroup}>
          <Text style={[styles.label, { color: colors.text }]}>Empresa *</Text>
          <TextInput
            style={[styles.formInput, { borderColor: colors.border, backgroundColor: colors.surface }]}
            placeholder="Nome da empresa cliente"
            placeholderTextColor={colors.textSecondary}
            value={empresa}
            onChangeText={setEmpresa}
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={[styles.label, { color: colors.text }]}>Bairro *</Text>
          <TextInput
            style={[styles.formInput, { borderColor: colors.border, backgroundColor: colors.surface }]}
            placeholder="Localização do serviço"
            placeholderTextColor={colors.textSecondary}
            value={bairro}
            onChangeText={setBairro}
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={[styles.label, { color: colors.text }]}>Endereço Completo *</Text>
          <TextInput
            style={[styles.formInput, { borderColor: colors.border, backgroundColor: colors.surface }]}
            placeholder="Rua, número, complemento"
            placeholderTextColor={colors.textSecondary}
            value={endereco}
            onChangeText={setEndereco}
          />
        </View>
      </View>

      <View style={[styles.section, styles.card]}>
        <Text style={[styles.sectionTitle, { color: colors.text }]}>Fotos da Tarefa *</Text>
        
        <TouchableOpacity style={[styles.photoButton, { borderColor: colors.primary }]} onPress={showPhotoOptions}>
          <Ionicons name="camera" size={24} color={colors.primary} />
          <Text style={[styles.photoButtonText, { color: colors.primary }]}>Adicionar Foto</Text>
        </TouchableOpacity>

        {fotos.length > 0 && (
          <View style={styles.photosContainer}>
            <FlatList
              data={fotos}
              horizontal
              showsHorizontalScrollIndicator={false}
              keyExtractor={(item, index) => index.toString()}
              renderItem={({ item, index }) => (
                <View style={styles.photoItem}>
                  <Image source={{ uri: item.uri }} style={styles.photoPreview} />
                  <TouchableOpacity 
                    style={[styles.removePhotoButton, { backgroundColor: colors.error }]}
                    onPress={() => removePhoto(index)}
                  >
                    <Ionicons name="close" size={16} color="white" />
                  </TouchableOpacity>
                </View>
              )}
            />
          </View>
        )}
      </View>

      <View style={styles.inputGroup}>
        <Text style={[styles.label, { color: colors.text }]}>Observações</Text>
        <TextInput
          style={[styles.formInput, styles.textArea, { borderColor: colors.border, backgroundColor: colors.surface }]}
          placeholder="Detalhes adicionais sobre a tarefa"
          placeholderTextColor={colors.textSecondary}
          value={observacoes}
          onChangeText={setObservacoes}
          multiline
          numberOfLines={4}
        />
      </View>

      <TouchableOpacity style={[styles.submitButton, { backgroundColor: colors.primary }]} onPress={handleSubmit}>
        <Ionicons name="checkmark-circle" size={20} color="#ffffff" />
        <Text style={styles.submitButtonText}>Registrar Tarefa</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

// Tela de Detalhes da Tarefa
function TaskDetailScreen({ route, navigation }) {
  const { task } = route.params;
  const [status, setStatus] = useState(task.status);

  const updateStatus = (newStatus) => {
    setStatus(newStatus);
    Alert.alert('Sucesso', `Status atualizado para: ${getStatusText(newStatus)}`);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pendente': return '#ff9800';
      case 'em_andamento': return '#2196f3';
      case 'concluida': return '#4caf50';
      default: return '#666';
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

  const getPriorityColor = (prioridade) => {
    switch (prioridade) {
      case 'alta': return '#f44336';
      case 'media': return '#ff9800';
      case 'baixa': return '#4caf50';
      default: return '#666';
    }
  };

  return (
    <ScrollView style={styles.taskDetailContainer}>
      <View style={styles.taskDetailHeader}>
        <Text style={styles.taskDetailTitle}>{task.empresa}</Text>
        <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(task.prioridade) }]}>
          <Text style={styles.priorityText}>{task.prioridade.toUpperCase()}</Text>
        </View>
      </View>

      <View style={styles.detailCard}>
        <View style={styles.detailRow}>
          <Ionicons name="business" size={20} color="#666" />
          <View style={styles.detailContent}>
            <Text style={styles.detailLabel}>Tipo de Serviço</Text>
            <Text style={styles.detailValue}>{task.tipo}</Text>
          </View>
        </View>

        <View style={styles.detailRow}>
          <Ionicons name="location" size={20} color="#666" />
          <View style={styles.detailContent}>
            <Text style={styles.detailLabel}>Localização</Text>
            <Text style={styles.detailValue}>{task.bairro}</Text>
            <Text style={styles.detailSubValue}>{task.endereco}</Text>
          </View>
        </View>

        <View style={styles.detailRow}>
          <Ionicons name="calendar" size={20} color="#666" />
          <View style={styles.detailContent}>
            <Text style={styles.detailLabel}>Data de Atribuição</Text>
            <Text style={styles.detailValue}>{task.dataAtribuicao}</Text>
          </View>
        </View>

        <View style={styles.detailRow}>
          <Ionicons name="document-text" size={20} color="#666" />
          <View style={styles.detailContent}>
            <Text style={styles.detailLabel}>Descrição</Text>
            <Text style={styles.detailValue}>{task.descricao}</Text>
          </View>
        </View>
      </View>

      <View style={styles.statusSection}>
        <Text style={styles.sectionTitle}>Status da Tarefa</Text>
        <View style={[styles.currentStatusBadge, { backgroundColor: getStatusColor(status) }]}>
          <Text style={styles.currentStatusText}>{getStatusText(status)}</Text>
        </View>
      </View>

      <View style={styles.actionButtons}>
        {status === 'pendente' && (
          <TouchableOpacity 
            style={[styles.actionButton, { backgroundColor: '#2196f3' }]}
            onPress={() => updateStatus('em_andamento')}
          >
            <Ionicons name="play" size={20} color="#ffffff" />
            <Text style={styles.actionButtonText}>Iniciar Tarefa</Text>
          </TouchableOpacity>
        )}
        
        {status === 'em_andamento' && (
          <TouchableOpacity 
            style={[styles.actionButton, { backgroundColor: '#4caf50' }]}
            onPress={() => updateStatus('concluida')}
          >
            <Ionicons name="checkmark" size={20} color="#ffffff" />
            <Text style={styles.actionButtonText}>Concluir Tarefa</Text>
          </TouchableOpacity>
        )}

        <TouchableOpacity 
          style={[styles.actionButton, styles.secondaryButton]}
          onPress={() => navigation.navigate('RegisterTask')}
        >
          <Ionicons name="camera" size={20} color="#1a73e8" />
          <Text style={[styles.actionButtonText, { color: '#1a73e8' }]}>Adicionar Fotos</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}
function ProfileScreen({ navigation }) {
  const handleLogout = () => {
    Alert.alert(
      'Sair',
      'Deseja realmente sair da aplicação?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'Sair', onPress: () => navigation.navigate('Login') },
      ]
    );
  };

  return (
    <View style={styles.profileContainer}>
      <View style={styles.profileHeader}>
        <View style={styles.avatarContainer}>
          <Ionicons name="person" size={48} color="#ffffff" />
        </View>
        <Text style={styles.profileName}>Admin</Text>
        <Text style={styles.profileRole}>Administrador</Text>
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Ionicons name="log-out-outline" size={20} color="#d32f2f" />
        <Text style={styles.logoutButtonText}>Sair</Text>
      </TouchableOpacity>
    </View>
  );
}

// Navegação por Abas atualizada
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;
          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'TaskList') {
            iconName = focused ? 'list' : 'list-outline';
          } else if (route.name === 'RegisterTask') {
            iconName = focused ? 'add-circle' : 'add-circle-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          }
          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#1a73e8',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen} 
        options={{ title: 'Início' }}
      />
      <Tab.Screen 
        name="TaskList" 
        component={TaskListScreen} 
        options={{ title: 'Tarefas' }}
      />
      <Tab.Screen 
        name="RegisterTask" 
        component={RegisterTaskScreen} 
        options={{ title: 'Nova Tarefa' }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen} 
        options={{ title: 'Perfil' }}
      />
    </Tab.Navigator>
  );
}

function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Login">
        <Stack.Screen 
          name="Login" 
          component={LoginScreen}
          options={{ headerShown: false }}
        />
        <Stack.Screen 
          name="MainTabs" 
          component={MainTabs}
          options={{ headerShown: false }}
        />
        <Stack.Screen 
          name="TaskDetail" 
          component={TaskDetailScreen}
          options={{ 
            title: 'Detalhes da Tarefa',
            headerStyle: { backgroundColor: '#1a73e8' },
            headerTintColor: '#ffffff'
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    justifyContent: 'center',
    paddingHorizontal: 24,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  iconCircle: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  title: {
    fontSize: 32,
    fontWeight: '800',
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
    borderRadius: 16,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: colors.border,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  inputIcon: {
    marginLeft: 16,
  },
  input: {
    flex: 1,
    paddingVertical: 16,
    paddingHorizontal: 12,
    fontSize: 16,
    color: colors.text,
  },
  eyeButton: {
    padding: 16,
  },
  loginButton: {
    backgroundColor: colors.primary,
    borderRadius: 16,
    paddingVertical: 18,
    alignItems: 'center',
    marginTop: 8,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  loginButtonDisabled: {
    opacity: 0.6,
  },
  loginButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '700',
  },
  homeContainer: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    padding: 24,
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24,
    marginBottom: 20,
  },
  welcomeTitle: {
    fontSize: 28,
    fontWeight: '800',
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
    padding: 20,
    borderRadius: 20,
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 6,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: '800',
    color: colors.text,
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4,
    textAlign: 'center',
    fontWeight: '600',
  },
  formScreen: {
    flex: 1,
    backgroundColor: colors.background,
    padding: 20,
  },
  formHeader: {
    alignItems: 'center',
    marginBottom: 24,
  },
  formTitle: {
    fontSize: 28,
    fontWeight: '800',
    color: colors.primary,
    marginBottom: 8,
  },
  formSubtitle: {
    fontSize: 16,
    color: colors.textSecondary,
  },
  section: {
    marginBottom: 20,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 20,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 6,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.text,
    marginBottom: 16,
  },
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 8,
  },
  formInput: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    borderWidth: 2,
    borderColor: colors.border,
    color: colors.text,
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  photoButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: colors.primary,
    borderStyle: 'dashed',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
  },
  photoButtonText: {
    marginLeft: 8,
    fontSize: 16,
    fontWeight: '600',
  },
  photosContainer: {
    marginTop: 12,
  },
  photoItem: {
    position: 'relative',
    marginRight: 12,
  },
  photoPreview: {
    width: 80,
    height: 80,
    borderRadius: 12,
  },
  removePhotoButton: {
    position: 'absolute',
    top: -8,
    right: -8,
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  submitButton: {
    backgroundColor: colors.primary,
    borderRadius: 16,
    paddingVertical: 18,
    alignItems: 'center',
    marginTop: 20,
    flexDirection: 'row',
    justifyContent: 'center',
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginBottom: 16,
  },
  seeAllText: {
    fontSize: 14,
    color: colors.primary,
    fontWeight: '600',
  },
  taskCard: {
    backgroundColor: colors.surface,
    marginHorizontal: 20,
    marginBottom: 12,
    borderRadius: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 6,
  },
  taskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  taskInfo: {
    flex: 1,
  },
  taskEmpresa: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.text,
    marginBottom: 2,
  },
  taskGerente: {
    fontSize: 12,
    color: colors.primary,
    fontWeight: '600',
    marginBottom: 4,
  },
  taskTipo: {
    fontSize: 14,
    color: colors.secondary,
    fontWeight: '600',
    marginBottom: 2,
  },
  taskCliente: {
    fontSize: 13,
    color: colors.textSecondary,
    marginBottom: 2,
  },
  taskBairro: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  taskDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  taskColaborador: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.text,
  },
  taskPrazo: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.warning,
  },
  taskMeta: {
    alignItems: 'flex-end',
  },
  taskFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  statusText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '700',
  },
  taskDate: {
    fontSize: 12,
    color: colors.textSecondary,
    fontWeight: '500',
  },
  testNotificationButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    marginHorizontal: 20,
    marginTop: 20,
    marginBottom: 30,
    paddingVertical: 16,
    borderRadius: 16,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  testNotificationText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
    marginLeft: 8,
  },
  profileContainer: {
    flex: 1,
    backgroundColor: colors.background,
    padding: 20,
  },
  profileHeader: {
    alignItems: 'center',
    marginBottom: 40,
    backgroundColor: colors.surface,
    padding: 30,
    borderRadius: 20,
  },
  avatarContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  profileName: {
    fontSize: 24,
    fontWeight: '800',
    color: colors.text,
    marginBottom: 4,
  },
  profileRole: {
    fontSize: 16,
    color: colors.textSecondary,
    fontWeight: '600',
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surface,
    borderRadius: 16,
    paddingVertical: 16,
    borderWidth: 2,
    borderColor: colors.error,
  },
  logoutButtonText: {
    color: colors.error,
    fontSize: 16,
    fontWeight: '700',
    marginLeft: 8,
  },
});
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  statCard: {
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
    textAlign: 'center',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a',
  },
  seeAllText: {
    fontSize: 14,
    color: '#1a73e8',
    fontWeight: '500',
  },
  taskCard: {
    backgroundColor: '#ffffff',
    marginHorizontal: 20,
    marginBottom: 12,
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  taskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  taskInfo: {
    flex: 1,
  },
  taskEmpresa: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  taskTipo: {
    fontSize: 14,
    color: '#1a73e8',
    fontWeight: '500',
    marginBottom: 2,
  },
  taskBairro: {
    fontSize: 14,
    color: '#666',
  },
  taskMeta: {
    alignItems: 'flex-end',
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
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
  },
  taskDate: {
    fontSize: 12,
    color: '#666',
  },
  taskListContainer: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  filterContainer: {
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#ffffff',
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  filterButtonActive: {
    backgroundColor: '#1a73e8',
    borderColor: '#1a73e8',
  },
  filterButtonText: {
    fontSize: 14,
    color: '#666',
  },
  filterButtonTextActive: {
    color: '#ffffff',
    fontWeight: '600',
  },
  taskList: {
    flex: 1,
  },
  taskCardDetailed: {
    backgroundColor: '#ffffff',
    marginHorizontal: 20,
    marginBottom: 12,
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  taskDescricao: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
    lineHeight: 20,
  },
  formScreen: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  formTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1a73e8',
    marginBottom: 24,
    textAlign: 'center',
  },
  section: {
    marginBottom: 24,
  },
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 8,
  },
  formInput: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  radioGroup: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  radioOption: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 20,
    marginBottom: 8,
  },
  radioText: {
    marginLeft: 8,
    fontSize: 16,
    color: '#1a1a1a',
  },
  checkboxGroup: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  checkboxOption: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 20,
  },
  checkboxText: {
    marginLeft: 8,
    fontSize: 16,
    color: '#1a1a1a',
  },
  submitButton: {
    backgroundColor: '#1a73e8',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 20,
    flexDirection: 'row',
    justifyContent: 'center',
  },
  submitButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
    marginLeft: 8,
  },
  taskDetailContainer: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  taskDetailHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  taskDetailTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1a1a1a',
    flex: 1,
  },
  priorityBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  priorityText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
  },
  detailCard: {
    backgroundColor: '#ffffff',
    margin: 20,
    borderRadius: 12,
    padding: 16,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  detailContent: {
    marginLeft: 12,
    flex: 1,
  },
  detailLabel: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  detailValue: {
    fontSize: 16,
    color: '#1a1a1a',
    fontWeight: '500',
  },
  detailSubValue: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  statusSection: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  currentStatusBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 16,
    marginTop: 8,
  },
  currentStatusText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  actionButtons: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  secondaryButton: {
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#1a73e8',
  },
  actionButtonText: {
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
    color: '#ffffff',
  },
  profileContainer: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  profileHeader: {
    alignItems: 'center',
    marginBottom: 40,
  },
  avatarContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#1a73e8',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  profileName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  profileRole: {
    fontSize: 16,
    color: '#666',
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 12,
    paddingVertical: 16,
    borderWidth: 1,
    borderColor: '#d32f2f',
  },
  logoutButtonText: {
    color: '#d32f2f',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
});

export default registerRootComponent(App);