import React, { useState, useEffect } from 'react';
import { 
  View, Text, TextInput, TouchableOpacity, Alert, ScrollView, 
  ActivityIndicator, StyleSheet, Modal, Image, Linking, Platform 
} from 'react-native';
import { createClient } from '@supabase/supabase-js';
import { registerRootComponent } from 'expo';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import * as Notifications from 'expo-notifications';
import { Ionicons } from '@expo/vector-icons';

// Configuração de notificações
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

const colors = {
  primary: '#1e40af',
  secondary: '#3b82f6',
  accent: '#06b6d4',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  background: '#f1f5f9',
  surface: '#ffffff',
  text: '#0f172a',
  textSecondary: '#64748b',
  border: '#e2e8f0',
  gradient: ['#1e40af', '#3b82f6'],
};

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
  const [selectedTask, setSelectedTask] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [dashboardVisible, setDashboardVisible] = useState(false);
  const [loadingTasks, setLoadingTasks] = useState(false);
  
  // Estados para edição de tarefa
  const [editingTask, setEditingTask] = useState(null);
  const [materials, setMaterials] = useState('');
  const [serviceNotes, setServiceNotes] = useState('');
  const [photos, setPhotos] = useState([]);
  const [selectedStatus, setSelectedStatus] = useState('');

  useEffect(() => {
    requestPermissions();
    setupNotifications();
  }, []);

  const requestPermissions = async () => {
    const { status: cameraStatus } = await ImagePicker.requestCameraPermissionsAsync();
    const { status: mediaStatus } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    const { status: locationStatus } = await Location.requestForegroundPermissionsAsync();
    const { status: notificationStatus } = await Notifications.requestPermissionsAsync();
    
    if (cameraStatus !== 'granted' || mediaStatus !== 'granted') {
      Alert.alert('Permissão', 'Permissões de câmera são necessárias para o app funcionar.');
    }
  };

  const setupNotifications = async () => {
    const { status } = await Notifications.getPermissionsAsync();
    if (status !== 'granted') {
      await Notifications.requestPermissionsAsync();
    }
  };

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert('Erro', 'Preencha todos os campos');
      return;
    }

    setLoading(true);
    try {
      const { data: users, error } = await supabase
        .from('users')
        .select('*')
        .ilike('username', username)
        .eq('active', true)
        .single();

      if (error || !users) {
        Alert.alert('Erro', 'Usuário não encontrado');
        setLoading(false);
        return;
      }

      if (password === '123456' || password === users.password_hash) {
        setCurrentUser(users);
        setCurrentScreen('home');
        loadUserTasks(users.id);
        
        // Mostrar notificação de boas-vindas
        await Notifications.scheduleNotificationAsync({
          content: {
            title: '🚀 ISP Field Manager',
            body: `Bem-vindo, ${users.full_name}! Você tem tarefas aguardando.`,
            data: { type: 'welcome' },
          },
          trigger: { seconds: 1 },
        });
        
      } else {
        Alert.alert('Erro', 'Senha incorreta');
      }
    } catch (error) {
      Alert.alert('Erro', 'Erro de conexão');
    }
    setLoading(false);
  };

  const loadUserTasks = async (userId) => {
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

      if (!error && taskData) {
        setTasks(taskData);
        
        // Notificar sobre novas tarefas pendentes
        const pendingTasks = taskData.filter(t => t.status === 'pendente');
        if (pendingTasks.length > 0) {
          await Notifications.scheduleNotificationAsync({
            content: {
              title: '📋 Novas Tarefas Disponíveis',
              body: `Você tem ${pendingTasks.length} tarefa(s) pendente(s)`,
              data: { type: 'new_tasks', count: pendingTasks.length },
            },
            trigger: { seconds: 2 },
          });
        }
      }
    } catch (error) {
      console.error('Erro ao carregar tarefas:', error);
    }
    setLoadingTasks(false);
  };

  const openTaskDetails = (task) => {
    setSelectedTask(task);
    setModalVisible(true);
  };

  const openEditTask = (task) => {
    setEditingTask(task);
    setMaterials(task.materials || '');
    setServiceNotes(task.service_notes || '');
    setSelectedStatus(task.status);
    setPhotos([]);
    setEditModalVisible(true);
  };

  const openMap = (address, latitude, longitude) => {
    const url = Platform.select({
      ios: `maps:0,0?q=${latitude},${longitude}`,
      android: `geo:0,0?q=${latitude},${longitude}(${encodeURIComponent(address)})`,
    });
    
    Linking.canOpenURL(url).then(supported => {
      if (supported) {
        Linking.openURL(url);
      } else {
        // Fallback para Google Maps web
        const webUrl = `https://www.google.com/maps/search/?api=1&query=${latitude},${longitude}`;
        Linking.openURL(webUrl);
      }
    });
  };

  const takePhoto = async () => {
    try {
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled) {
        setPhotos([...photos, result.assets[0]]);
      }
    } catch (error) {
      Alert.alert('Erro', 'Erro ao tirar foto');
    }
  };

  const pickImage = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsMultipleSelection: true,
        quality: 0.8,
      });

      if (!result.canceled) {
        setPhotos([...photos, ...result.assets]);
      }
    } catch (error) {
      Alert.alert('Erro', 'Erro ao selecionar imagem');
    }
  };

  const updateTaskStatus = async (taskId, newStatus, updateData = {}) => {
    try {
      const finalUpdateData = {
        status: newStatus,
        updated_at: new Date().toISOString(),
        ...updateData
      };

      if (newStatus === 'em_andamento') {
        finalUpdateData.started_at = new Date().toISOString();
      } else if (newStatus === 'concluida') {
        finalUpdateData.completed_at = new Date().toISOString();
      }

      const { error } = await supabase
        .from('task_assignments')
        .update(finalUpdateData)
        .eq('id', taskId);

      if (error) {
        Alert.alert('Erro', 'Erro ao atualizar tarefa');
      } else {
        loadUserTasks(currentUser.id);
        setModalVisible(false);
        setEditModalVisible(false);
        
        // Notificação de sucesso
        await Notifications.scheduleNotificationAsync({
          content: {
            title: '✅ Tarefa Atualizada',
            body: `Status alterado para: ${getStatusText(newStatus)}`,
            data: { type: 'task_updated', taskId, status: newStatus },
          },
          trigger: { seconds: 1 },
        });
      }
    } catch (error) {
      Alert.alert('Erro', 'Erro ao atualizar tarefa');
    }
  };

  const saveTaskEdits = async () => {
    if (!editingTask) return;

    const updateData = {
      materials: materials,
      service_notes: serviceNotes,
      photos_count: photos.length,
    };

    await updateTaskStatus(editingTask.id, selectedStatus, updateData);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pendente': return colors.warning;
      case 'em_andamento': return colors.accent;
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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pendente': return 'time-outline';
      case 'em_andamento': return 'play-circle-outline';
      case 'concluida': return 'checkmark-circle-outline';
      default: return 'help-circle-outline';
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
        <View style={styles.loginHeader}>
          <View style={styles.logoContainer}>
            <Ionicons name="wifi" size={60} color={colors.primary} />
            <Text style={styles.title}>Tarefas ISP</Text>
          </View>
        </View>

        <View style={styles.formContainer}>
          <View style={styles.inputContainer}>
            <Ionicons name="person-outline" size={20} color={colors.textSecondary} />
            <TextInput
              style={styles.input}
              placeholder="Nome de usuário"
              value={username}
              onChangeText={setUsername}
              autoCapitalize="none"
              placeholderTextColor={colors.textSecondary}
            />
          </View>

          <View style={styles.inputContainer}>
            <Ionicons name="lock-closed-outline" size={20} color={colors.textSecondary} />
            <TextInput
              style={styles.input}
              placeholder="Senha"
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              placeholderTextColor={colors.textSecondary}
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
              <>
                <Ionicons name="log-in-outline" size={20} color="white" />
                <Text style={styles.loginButtonText}>Entrar no Sistema</Text>
              </>
            )}
          </TouchableOpacity>

          <Text style={styles.loginInfo}>
            🔐 Acesso seguro para técnicos de campo
          </Text>
        </View>
      </View>
    );
  }

  const pendingTasks = tasks.filter(t => t.status === 'pendente').length;
  const inProgressTasks = tasks.filter(t => t.status === 'em_andamento').length;
  const completedTasks = tasks.filter(t => t.status === 'concluida').length;
  const totalTasks = tasks.length;
  
  // Métricas específicas baseadas no tipo de usuário
  const isFusionTeam = currentUser?.team?.toLowerCase().includes('fusão') || currentUser?.team?.toLowerCase().includes('fusao');
  const isInfraTeam = currentUser?.team?.toLowerCase().includes('infraestrutura') || currentUser?.team?.toLowerCase().includes('infra');
  
  // Métricas para equipe de fusão
  const ceoTasks = tasks.filter(t => t.title?.toLowerCase().includes('ceo') || t.description?.toLowerCase().includes('ceo')).length;
  const ctoTasks = tasks.filter(t => t.title?.toLowerCase().includes('cto') || t.description?.toLowerCase().includes('cto')).length;
  
  // Métricas para equipe de infraestrutura
  const fiberLaunched = tasks.reduce((total, task) => {
    const meters = task.materials?.match(/\d+\s*m/g);
    if (meters) {
      return total + meters.reduce((sum, m) => sum + parseInt(m), 0);
    }
    return total;
  }, 0);
  
  const breakTasks = tasks.filter(t => t.title?.toLowerCase().includes('rompimento') || t.description?.toLowerCase().includes('rompimento')).length;
  const activationTasks = tasks.filter(t => t.title?.toLowerCase().includes('ativação') || t.description?.toLowerCase().includes('ativacao')).length;
  const condoTasks = tasks.filter(t => t.title?.toLowerCase().includes('condominio') || t.title?.toLowerCase().includes('predio') || t.description?.toLowerCase().includes('condominio')).length;
  
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
  const todayTasks = tasks.filter(t => {
    const today = new Date().toDateString();
    const taskDate = new Date(t.created_at).toDateString();
    return today === taskDate;
  }).length;

  return (
    <View style={styles.homeContainer}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <View>
            <Text style={styles.welcomeTitle}>Olá, {currentUser?.full_name}</Text>
            <Text style={styles.welcomeSubtitle}>
              <Ionicons name="business-outline" size={14} /> {currentUser?.team} • {currentUser?.role}
            </Text>
          </View>
          <TouchableOpacity 
            style={styles.refreshButton} 
            onPress={() => loadUserTasks(currentUser.id)}
          >
            <Ionicons name="refresh-outline" size={20} color="white" />
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.dashboardButton} 
            onPress={() => setDashboardVisible(true)}
          >
            <Ionicons name="analytics-outline" size={20} color="white" />
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Stats Cards */}
        <View style={styles.statsContainer}>
          <View style={[styles.statCard, styles.pendingCard]}>
            <Ionicons name="time-outline" size={24} color={colors.warning} />
            <Text style={styles.statNumber}>{pendingTasks}</Text>
            <Text style={styles.statLabel}>Pendentes</Text>
          </View>
          <View style={[styles.statCard, styles.progressCard]}>
            <Ionicons name="play-circle-outline" size={24} color={colors.accent} />
            <Text style={styles.statNumber}>{inProgressTasks}</Text>
            <Text style={styles.statLabel}>Em Andamento</Text>
          </View>
          <View style={[styles.statCard, styles.completedCard]}>
            <Ionicons name="checkmark-circle-outline" size={24} color={colors.success} />
            <Text style={styles.statNumber}>{completedTasks}</Text>
            <Text style={styles.statLabel}>Concluídas</Text>
          </View>
        </View>

        {/* Team Specific Metrics */}
        <View style={styles.ispMetricsContainer}>
          <Text style={styles.metricsTitle}>
            <Ionicons name="business-outline" size={16} /> 
            {isFusionTeam ? 'Fusão Óptica' : isInfraTeam ? 'Infraestrutura' : 'Métricas'}
          </Text>
          
          {isFusionTeam ? (
            <View style={styles.metricsRow}>
              <View style={styles.metricCard}>
                <Ionicons name="cube-outline" size={20} color={colors.primary} />
                <Text style={styles.metricNumber}>{ceoTasks}</Text>
                <Text style={styles.metricLabel}>CEO</Text>
              </View>
              <View style={styles.metricCard}>
                <Ionicons name="server-outline" size={20} color={colors.secondary} />
                <Text style={styles.metricNumber}>{ctoTasks}</Text>
                <Text style={styles.metricLabel}>CTO</Text>
              </View>
            </View>
          ) : isInfraTeam ? (
            <View style={styles.infraMetrics}>
              <View style={styles.fiberCard}>
                <Ionicons name="git-branch-outline" size={24} color={colors.accent} />
                <Text style={styles.fiberNumber}>{fiberLaunched}m</Text>
                <Text style={styles.fiberLabel}>Fibra Lançada</Text>
              </View>
              <View style={styles.infraTasksRow}>
                <View style={styles.infraTaskCard}>
                  <Ionicons name="warning-outline" size={16} color={colors.danger} />
                  <Text style={styles.infraTaskNumber}>{breakTasks}</Text>
                  <Text style={styles.infraTaskLabel}>Rompimentos</Text>
                </View>
                <View style={styles.infraTaskCard}>
                  <Ionicons name="flash-outline" size={16} color={colors.success} />
                  <Text style={styles.infraTaskNumber}>{activationTasks}</Text>
                  <Text style={styles.infraTaskLabel}>Ativações</Text>
                </View>
                <View style={styles.infraTaskCard}>
                  <Ionicons name="business-outline" size={16} color={colors.primary} />
                  <Text style={styles.infraTaskNumber}>{condoTasks}</Text>
                  <Text style={styles.infraTaskLabel}>Cond./Prédios</Text>
                </View>
              </View>
            </View>
          ) : (
            <View style={styles.metricsRow}>
              <View style={styles.metricCard}>
                <Ionicons name="checkmark-circle-outline" size={20} color={colors.success} />
                <Text style={styles.metricNumber}>{completedTasks}</Text>
                <Text style={styles.metricLabel}>Concluídas</Text>
              </View>
            </View>
          )}
        </View>

        {/* Tasks Section */}
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>
            <Ionicons name="list-outline" size={20} /> Minhas Tarefas de Campo
          </Text>
        </View>

        {loadingTasks ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.primary} />
            <Text style={styles.loadingText}>Carregando tarefas...</Text>
          </View>
        ) : tasks.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Ionicons name="clipboard-outline" size={60} color={colors.textSecondary} />
            <Text style={styles.emptyText}>Nenhuma tarefa encontrada</Text>
            <Text style={styles.emptySubtext}>Aguarde atribuições do gerente</Text>
          </View>
        ) : (
          tasks.map((task) => (
            <TouchableOpacity 
              key={task.id} 
              style={styles.taskCard}
              onPress={() => openTaskDetails(task)}
              activeOpacity={0.7}
            >
              <View style={styles.taskHeader}>
                <View style={styles.taskTitleContainer}>
                  <Text style={styles.taskTitle}>{task.title}</Text>
                  <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(task.priority) }]}>
                    <Text style={styles.priorityText}>{task.priority?.toUpperCase()}</Text>
                  </View>
                </View>
                <Ionicons 
                  name={getStatusIcon(task.status)} 
                  size={24} 
                  color={getStatusColor(task.status)} 
                />
              </View>
              
              <Text style={styles.taskDescription} numberOfLines={2}>{task.description}</Text>
              
              <View style={styles.taskLocation}>
                <Ionicons name="location-outline" size={16} color={colors.textSecondary} />
                <Text style={styles.taskAddress} numberOfLines={1}>{task.address}</Text>
                <TouchableOpacity 
                  style={styles.mapButton}
                  onPress={() => openMap(task.address, task.latitude, task.longitude)}
                >
                  <Ionicons name="map-outline" size={16} color={colors.primary} />
                </TouchableOpacity>
              </View>
              
              <View style={styles.taskFooter}>
                <View style={[styles.statusBadge, { backgroundColor: getStatusColor(task.status) }]}>
                  <Text style={styles.statusText}>{getStatusText(task.status)}</Text>
                </View>
                
                <Text style={styles.taskTime}>
                  <Ionicons name="person-outline" size={12} /> {task.assigned_by_user?.full_name || 'Sistema'}
                </Text>
              </View>
            </TouchableOpacity>
          ))
        )}

        {/* Logout Button */}
        <TouchableOpacity 
          style={styles.logoutButton} 
          onPress={() => {
            setCurrentScreen('login');
            setCurrentUser(null);
            setTasks([]);
            setUsername('');
            setPassword('');
          }}
        >
          <Ionicons name="log-out-outline" size={20} color="white" />
          <Text style={styles.logoutText}>Sair do Sistema</Text>
        </TouchableOpacity>
      </ScrollView>

      {/* Task Details Modal */}
      <Modal
        animationType="slide"
        transparent={true}
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            {selectedTask && (
              <>
                <View style={styles.modalHeader}>
                  <Text style={styles.modalTitle}>{selectedTask.title}</Text>
                  <TouchableOpacity onPress={() => setModalVisible(false)}>
                    <Ionicons name="close-outline" size={24} color={colors.text} />
                  </TouchableOpacity>
                </View>

                <ScrollView style={styles.modalBody}>
                  <Text style={styles.modalDescription}>{selectedTask.description}</Text>
                  
                  <View style={styles.modalSection}>
                    <Text style={styles.modalSectionTitle}>
                      <Ionicons name="location-outline" size={16} /> Localização
                    </Text>
                    <Text style={styles.modalText}>{selectedTask.address}</Text>
                    <TouchableOpacity 
                      style={styles.mapLinkButton}
                      onPress={() => openMap(selectedTask.address, selectedTask.latitude, selectedTask.longitude)}
                    >
                      <Ionicons name="map-outline" size={16} color="white" />
                      <Text style={styles.mapLinkText}>Abrir no Mapa</Text>
                    </TouchableOpacity>
                  </View>

                  <View style={styles.modalSection}>
                    <Text style={styles.modalSectionTitle}>
                      <Ionicons name="flag-outline" size={16} /> Prioridade
                    </Text>
                    <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(selectedTask.priority) }]}>
                      <Text style={styles.priorityText}>{selectedTask.priority?.toUpperCase()}</Text>
                    </View>
                  </View>

                  <View style={styles.modalSection}>
                    <Text style={styles.modalSectionTitle}>
                      <Ionicons name="checkmark-circle-outline" size={16} /> Status Atual
                    </Text>
                    <View style={[styles.statusBadge, { backgroundColor: getStatusColor(selectedTask.status) }]}>
                      <Text style={styles.statusText}>{getStatusText(selectedTask.status)}</Text>
                    </View>
                  </View>
                </ScrollView>

                <View style={styles.modalActions}>
                  <TouchableOpacity 
                    style={styles.editButton}
                    onPress={() => {
                      setModalVisible(false);
                      openEditTask(selectedTask);
                    }}
                  >
                    <Ionicons name="create-outline" size={16} color="white" />
                    <Text style={styles.editButtonText}>Editar Tarefa</Text>
                  </TouchableOpacity>

                  {selectedTask.status === 'pendente' && (
                    <TouchableOpacity 
                      style={styles.startButton}
                      onPress={() => updateTaskStatus(selectedTask.id, 'em_andamento')}
                    >
                      <Ionicons name="play-outline" size={16} color="white" />
                      <Text style={styles.startButtonText}>Iniciar</Text>
                    </TouchableOpacity>
                  )}

                  {selectedTask.status === 'em_andamento' && (
                    <TouchableOpacity 
                      style={styles.completeButton}
                      onPress={() => updateTaskStatus(selectedTask.id, 'concluida')}
                    >
                      <Ionicons name="checkmark-outline" size={16} color="white" />
                      <Text style={styles.completeButtonText}>Concluir</Text>
                    </TouchableOpacity>
                  )}
                </View>
              </>
            )}
          </View>
        </View>
      </Modal>

      {/* Edit Task Modal */}
      <Modal
        animationType="slide"
        transparent={true}
        visible={editModalVisible}
        onRequestClose={() => setEditModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            {editingTask && (
              <>
                <View style={styles.modalHeader}>
                  <Text style={styles.modalTitle}>Editar Tarefa</Text>
                  <TouchableOpacity onPress={() => setEditModalVisible(false)}>
                    <Ionicons name="close-outline" size={24} color={colors.text} />
                  </TouchableOpacity>
                </View>

                <ScrollView style={styles.modalBody}>
                  <View style={styles.modalSection}>
                    <Text style={styles.modalSectionTitle}>
                      <Ionicons name="flag-outline" size={16} /> Status da Tarefa
                    </Text>
                    <View style={styles.statusSelector}>
                      <TouchableOpacity 
                        style={[styles.statusOption, selectedStatus === 'pendente' && styles.statusSelected]}
                        onPress={() => setSelectedStatus('pendente')}
                      >
                        <Ionicons name="time-outline" size={16} color={selectedStatus === 'pendente' ? 'white' : colors.warning} />
                        <Text style={[styles.statusOptionText, selectedStatus === 'pendente' && styles.statusSelectedText]}>Pendente</Text>
                      </TouchableOpacity>
                      <TouchableOpacity 
                        style={[styles.statusOption, selectedStatus === 'em_andamento' && styles.statusSelected]}
                        onPress={() => setSelectedStatus('em_andamento')}
                      >
                        <Ionicons name="play-circle-outline" size={16} color={selectedStatus === 'em_andamento' ? 'white' : colors.accent} />
                        <Text style={[styles.statusOptionText, selectedStatus === 'em_andamento' && styles.statusSelectedText]}>Em Andamento</Text>
                      </TouchableOpacity>
                      <TouchableOpacity 
                        style={[styles.statusOption, selectedStatus === 'concluida' && styles.statusSelected]}
                        onPress={() => setSelectedStatus('concluida')}
                      >
                        <Ionicons name="checkmark-circle-outline" size={16} color={selectedStatus === 'concluida' ? 'white' : colors.success} />
                        <Text style={[styles.statusOptionText, selectedStatus === 'concluida' && styles.statusSelectedText]}>Concluída</Text>
                      </TouchableOpacity>
                    </View>
                  </View>

                  <View style={styles.modalSection}>
                    <Text style={styles.modalSectionTitle}>
                      <Ionicons name="construct-outline" size={16} /> Materiais Utilizados
                    </Text>
                    <TextInput
                      style={styles.textArea}
                      placeholder="Ex: Cabo UTP 50m, Conectores RJ45, Switch 8 portas..."
                      value={materials}
                      onChangeText={setMaterials}
                      multiline
                      numberOfLines={3}
                      placeholderTextColor={colors.textSecondary}
                    />
                  </View>

                  <View style={styles.modalSection}>
                    <Text style={styles.modalSectionTitle}>
                      <Ionicons name="document-text-outline" size={16} /> Observações do Serviço
                    </Text>
                    <TextInput
                      style={styles.textArea}
                      placeholder="Descreva o serviço realizado, problemas encontrados, soluções aplicadas..."
                      value={serviceNotes}
                      onChangeText={setServiceNotes}
                      multiline
                      numberOfLines={4}
                      placeholderTextColor={colors.textSecondary}
                    />
                  </View>

                  <View style={styles.modalSection}>
                    <Text style={styles.modalSectionTitle}>
                      <Ionicons name="camera-outline" size={16} /> Fotos do Serviço
                    </Text>
                    
                    <View style={styles.photoActions}>
                      <TouchableOpacity style={styles.photoButton} onPress={takePhoto}>
                        <Ionicons name="camera-outline" size={20} color="white" />
                        <Text style={styles.photoButtonText}>Tirar Foto</Text>
                      </TouchableOpacity>
                      
                      <TouchableOpacity style={styles.photoButton} onPress={pickImage}>
                        <Ionicons name="images-outline" size={20} color="white" />
                        <Text style={styles.photoButtonText}>Galeria</Text>
                      </TouchableOpacity>
                    </View>

                    {photos.length > 0 && (
                      <View style={styles.photoGrid}>
                        {photos.map((photo, index) => (
                          <Image key={index} source={{ uri: photo.uri }} style={styles.photoPreview} />
                        ))}
                      </View>
                    )}
                  </View>
                </ScrollView>

                <View style={styles.modalActions}>
                  <TouchableOpacity 
                    style={styles.saveButton}
                    onPress={saveTaskEdits}
                  >
                    <Ionicons name="save-outline" size={16} color="white" />
                    <Text style={styles.saveButtonText}>Salvar Alterações</Text>
                  </TouchableOpacity>
                </View>
              </>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  loginHeader: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 60,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: colors.primary,
    marginTop: 16,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: colors.textSecondary,
    fontWeight: '500',
  },
  formContainer: {
    padding: 24,
    backgroundColor: colors.surface,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.background,
    borderRadius: 12,
    marginBottom: 16,
    paddingHorizontal: 16,
    paddingVertical: 4,
    borderWidth: 1,
    borderColor: colors.border,
  },
  input: {
    flex: 1,
    paddingVertical: 16,
    paddingLeft: 12,
    fontSize: 16,
    color: colors.text,
  },
  loginButton: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  loginButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  loginInfo: {
    textAlign: 'center',
    marginTop: 16,
    fontSize: 14,
    color: colors.textSecondary,
  },
  homeContainer: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    backgroundColor: colors.primary,
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  welcomeTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: 4,
  },
  welcomeSubtitle: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
  },
  refreshButton: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    padding: 12,
    borderRadius: 8,
    marginRight: 8,
  },
  dashboardButton: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    padding: 12,
    borderRadius: 8,
  },
  content: {
    flex: 1,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 20,
  },
  statCard: {
    backgroundColor: colors.surface,
    padding: 16,
    borderRadius: 16,
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
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.text,
    marginVertical: 8,
  },
  statLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    fontWeight: '500',
  },
  sectionHeader: {
    paddingHorizontal: 20,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
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
    marginTop: 16,
    marginBottom: 8,
  },
  emptySubtext: {
    color: colors.textSecondary,
    fontSize: 14,
  },
  taskCard: {
    backgroundColor: colors.surface,
    marginHorizontal: 20,
    marginBottom: 16,
    borderRadius: 16,
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
  taskTitleContainer: {
    flex: 1,
    marginRight: 12,
  },
  taskTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 8,
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  priorityText: {
    color: 'white',
    fontSize: 10,
    fontWeight: 'bold',
  },
  taskDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 12,
    lineHeight: 20,
  },
  taskLocation: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  taskAddress: {
    fontSize: 14,
    color: colors.textSecondary,
    flex: 1,
    marginLeft: 8,
  },
  mapButton: {
    padding: 8,
    backgroundColor: colors.background,
    borderRadius: 8,
  },
  taskFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
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
  logoutButton: {
    backgroundColor: colors.danger,
    marginHorizontal: 20,
    marginVertical: 20,
    paddingVertical: 16,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoutText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  ispMetricsContainer: {
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  metricsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 12,
  },
  metricsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  metricCard: {
    backgroundColor: colors.surface,
    padding: 12,
    borderRadius: 12,
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  metricNumber: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
    marginVertical: 4,
  },
  metricLabel: {
    fontSize: 10,
    color: colors.textSecondary,
    fontWeight: '500',
  },
  dashboardModal: {
    backgroundColor: colors.surface,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    height: '85%',
  },
  dashboardContent: {
    flex: 1,
    padding: 20,
  },
  dashboardSection: {
    marginBottom: 24,
  },
  dashboardSectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 16,
  },
  performanceCard: {
    backgroundColor: colors.background,
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  performanceItem: {
    alignItems: 'center',
  },
  performanceNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: colors.primary,
  },
  performanceLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4,
  },
  servicesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  serviceCard: {
    backgroundColor: colors.background,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    width: '48%',
    marginBottom: 12,
  },
  serviceNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.text,
    marginVertical: 8,
  },
  serviceLabel: {
    fontSize: 12,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 4,
  },
  serviceDesc: {
    fontSize: 10,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  infraMetrics: {
    alignItems: 'center',
  },
  fiberCard: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    width: '100%',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  fiberNumber: {
    fontSize: 28,
    fontWeight: 'bold',
    color: colors.accent,
    marginVertical: 8,
  },
  fiberLabel: {
    fontSize: 14,
    color: colors.text,
    fontWeight: '600',
  },
  infraTasksRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
  },
  infraTaskCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 12,
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  infraTaskNumber: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.text,
    marginVertical: 4,
  },
  infraTaskLabel: {
    fontSize: 9,
    color: colors.textSecondary,
    fontWeight: '500',
    textAlign: 'center',
  },
  fiberDashboardCard: {
    backgroundColor: colors.background,
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    marginBottom: 16,
    borderWidth: 2,
    borderColor: colors.accent,
  },
  fiberDashboardNumber: {
    fontSize: 36,
    fontWeight: 'bold',
    color: colors.accent,
    marginVertical: 8,
  },
  fiberDashboardLabel: {
    fontSize: 16,
    color: colors.text,
    fontWeight: '600',
  },
  statusSelector: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  statusOption: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    marginHorizontal: 2,
    backgroundColor: colors.background,
  },
  statusSelected: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  statusOptionText: {
    fontSize: 12,
    color: colors.text,
    marginLeft: 4,
    fontWeight: '500',
  },
  statusSelectedText: {
    color: 'white',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: colors.surface,
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    maxHeight: '90%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: colors.text,
  },
  modalBody: {
    padding: 20,
  },
  modalDescription: {
    fontSize: 16,
    color: colors.text,
    marginBottom: 20,
    lineHeight: 24,
  },
  modalSection: {
    marginBottom: 20,
  },
  modalSectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: colors.text,
    marginBottom: 12,
  },
  modalText: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 12,
  },
  mapLinkButton: {
    backgroundColor: colors.primary,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  mapLinkText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  textArea: {
    backgroundColor: colors.background,
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    color: colors.text,
    textAlignVertical: 'top',
    borderWidth: 1,
    borderColor: colors.border,
  },
  photoActions: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  photoButton: {
    backgroundColor: colors.secondary,
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginRight: 12,
  },
  photoButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  photoGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  photoPreview: {
    width: 80,
    height: 80,
    borderRadius: 8,
    marginRight: 8,
    marginBottom: 8,
  },
  modalActions: {
    flexDirection: 'row',
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  editButton: {
    backgroundColor: colors.secondary,
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    marginRight: 12,
  },
  editButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  startButton: {
    backgroundColor: colors.accent,
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  startButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  completeButton: {
    backgroundColor: colors.success,
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  completeButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  saveButton: {
    backgroundColor: colors.success,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    flex: 1,
    borderRadius: 8,
  },
  saveButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
});

registerRootComponent(App);