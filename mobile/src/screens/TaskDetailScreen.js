import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, Alert, Image, ActivityIndicator, Linking } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { supabase } from '../config/supabase';
import { useAuth } from '../contexts/AuthContext';
import { getAssignmentDetail } from '../services/tasks';

const colors = {
  primary: "#6366f1",
  secondary: "#06b6d4",
  success: "#10b981",
  warning: "#f59e0b",
  error: "#ef4444",
  background: "#f8fafc",
  surface: "#ffffff",
  text: "#1e293b",
  textSecondary: "#64748b",
  border: "#e2e8f0",
};

export default function TaskDetailScreen({ route, navigation }) {
  const { assignmentId } = route.params;
  const { user } = useAuth();
  const [task, setTask] = useState(null);
  const [serviceNotes, setServiceNotes] = useState('');
  const [materials, setMaterials] = useState('');
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState('pending');

  useEffect(() => {
    loadTask();
  }, []);

  const loadTask = async () => {
    try {
      const data = await getAssignmentDetail(assignmentId);
      setTask(data);
      setServiceNotes(data.service_notes || '');
      setMaterials(data.materials || '');
      setStatus(data.status || 'pending');
      
      // Carregar fotos após ter o task
      if (data?.id) {
        const { data: photosData, error } = await supabase
          .from('assignment_photos')
          .select('*')
          .eq('assignment_id', data.id)
          .order('uploaded_at', { ascending: false });
        
        if (!error && photosData) {
          setPhotos(photosData);
        }
      }
    } catch (error) {
      console.error('Erro ao carregar tarefa:', error);
      Alert.alert('Erro', 'Não foi possível carregar a tarefa');
    } finally {
      setLoading(false);
    }
  };

  const loadPhotos = async () => {
    if (!task?.id) return;
    try {
      const { data, error } = await supabase
        .from('assignment_photos')
        .select('*')
        .eq('assignment_id', task.id)
        .order('uploaded_at', { ascending: false });

      if (!error && data) {
        setPhotos(data);
      }
    } catch (error) {
      console.error('Erro ao carregar fotos:', error);
    }
  };

  const pickImage = async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permissão necessária', 'Precisamos de permissão para acessar suas fotos');
        return;
      }

      const result = await ImagePicker.launchImagePickerAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets[0]) {
        await uploadPhoto(result.assets[0].uri);
      }
    } catch (error) {
      Alert.alert('Erro', 'Erro ao selecionar foto: ' + error.message);
      console.error('Erro pickImage:', error);
    }
  };

  const takePhoto = async () => {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permissão necessária', 'Precisamos de permissão para usar a câmera');
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets[0]) {
        await uploadPhoto(result.assets[0].uri);
      }
    } catch (error) {
      Alert.alert('Erro', 'Erro ao tirar foto: ' + error.message);
      console.error('Erro takePhoto:', error);
    }
  };

  const uploadPhoto = async (uri) => {
    if (!task?.id) return;
    try {
      const fileName = `task_${task.id}_${Date.now()}.jpg`;
      
      const { data, error } = await supabase
        .from('assignment_photos')
        .insert({
          assignment_id: task.id,
          photo_url: uri,
          photo_path: fileName,
          uploaded_at: new Date().toISOString(),
        })
        .select()
        .single();

      if (error) throw error;

      Alert.alert('Sucesso', 'Foto adicionada!');
      
      // Adicionar foto ao estado local imediatamente
      setPhotos(prev => [data, ...prev]);
    } catch (error) {
      Alert.alert('Erro', 'Erro ao adicionar foto: ' + error.message);
      console.error('Erro upload:', error);
    }
  };

  const openMaps = () => {
    if (task?.latitude && task?.longitude) {
      const url = `https://www.google.com/maps/dir/?api=1&destination=${task.latitude},${task.longitude}`;
      Linking.openURL(url);
    } else {
      Alert.alert('Erro', 'Coordenadas não disponíveis');
    }
  };

  const saveTask = async () => {
    if (!task) return;
    setLoading(true);
    try {
      const { error } = await supabase
        .from('task_assignments')
        .update({
          status: status,
          service_notes: serviceNotes,
          materials: materials,
          updated_at: new Date().toISOString(),
        })
        .eq('id', task.id);

      if (error) throw error;

      Alert.alert('Sucesso', 'Informações salvas!');
      navigation.goBack();
    } catch (error) {
      Alert.alert('Erro', 'Erro ao salvar');
      console.error('Erro ao salvar:', error);
    } finally {
      setLoading(false);
    }
  };

  const completeTask = async () => {
    if (!task) return;
    if (!serviceNotes.trim()) {
      Alert.alert('Atenção', 'Descreva o serviço realizado antes de concluir');
      return;
    }

    Alert.alert(
      'Concluir Tarefa',
      'Tem certeza que deseja concluir esta tarefa?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Concluir',
          onPress: async () => {
            setLoading(true);
            try {
              const { error } = await supabase
                .from('task_assignments')
                .update({
                  status: 'concluida',
                  service_notes: serviceNotes,
                  materials: materials,
                  completed_at: new Date().toISOString(),
                  updated_at: new Date().toISOString(),
                })
                .eq('id', task.id);

              if (error) throw error;

              await supabase.from('notifications').insert({
                user_id: task.assigned_by,
                company_id: user.company_id || 1,
                type: 'task_completed',
                title: 'Tarefa Concluída',
                message: `${user.full_name} concluiu a tarefa "${task.title}"`,
                reference_id: task.id,
                read: false,
                created_at: new Date().toISOString(),
              });

              Alert.alert('Sucesso', 'Tarefa concluída!');
              navigation.goBack();
            } catch (error) {
              Alert.alert('Erro', 'Erro ao concluir tarefa');
              console.error('Erro:', error);
            } finally {
              setLoading(false);
            }
          },
        },
      ]
    );
  };

  if (loading || !task) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Carregando...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Detalhes da Tarefa</Text>
        <View style={{ width: 24 }} />
      </View>

      <View style={styles.card}>
        <Text style={styles.title}>{task.title}</Text>
        <Text style={styles.description}>{task.description}</Text>
        <TouchableOpacity style={styles.locationButton} onPress={openMaps}>
          <Ionicons name="location" size={16} color={colors.primary} />
          <Text style={styles.locationText}>{task.address}</Text>
          <Ionicons name="chevron-forward" size={16} color={colors.primary} />
        </TouchableOpacity>
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Status da Tarefa</Text>
        <View style={styles.statusContainer}>
          <TouchableOpacity 
            style={[styles.statusButton, status === 'pending' && styles.statusActive]}
            onPress={() => setStatus('pending')}
          >
            <Text style={[styles.statusText, status === 'pending' && styles.statusTextActive]}>Pendente</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.statusButton, status === 'in_progress' && styles.statusActive]}
            onPress={() => setStatus('in_progress')}
          >
            <Text style={[styles.statusText, status === 'in_progress' && styles.statusTextActive]}>Em Andamento</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Serviço Realizado</Text>
        <TextInput
          style={styles.textArea}
          placeholder="Descreva o serviço realizado..."
          value={serviceNotes}
          onChangeText={setServiceNotes}
          multiline
          numberOfLines={4}
        />
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Materiais Utilizados</Text>
        <TextInput
          style={styles.textArea}
          placeholder="Ex: 2 CTOs, 1 CEO, 50m de cabo..."
          value={materials}
          onChangeText={setMaterials}
          multiline
          numberOfLines={4}
        />
      </View>

      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Fotos ({photos.length})</Text>
        
        <View style={styles.photoButtons}>
          <TouchableOpacity style={styles.photoButton} onPress={takePhoto}>
            <Ionicons name="camera" size={24} color="white" />
            <Text style={styles.photoButtonText}>Câmera</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.photoButton} onPress={pickImage}>
            <Ionicons name="images" size={24} color="white" />
            <Text style={styles.photoButtonText}>Galeria</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.photoGrid}>
          {photos.map((photo) => (
            <View key={photo.id} style={styles.photoItem}>
              <Image source={{ uri: photo.photo_url }} style={styles.photo} />
            </View>
          ))}
        </View>
      </View>

      <View style={styles.actions}>
        <TouchableOpacity
          style={[styles.button, styles.saveButton]}
          onPress={saveTask}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <>
              <Ionicons name="save" size={20} color="white" />
              <Text style={styles.buttonText}>Salvar</Text>
            </>
          )}
        </TouchableOpacity>

        {task.status !== 'concluida' && (
          <TouchableOpacity
            style={[styles.button, styles.completeButton]}
            onPress={completeTask}
            disabled={loading}
          >
            <Ionicons name="checkmark-circle" size={20} color="white" />
            <Text style={styles.buttonText}>Concluir</Text>
          </TouchableOpacity>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.background },
  loadingText: { marginTop: 12, fontSize: 16, color: colors.textSecondary },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 16, backgroundColor: colors.surface },
  headerTitle: { fontSize: 18, fontWeight: '700', color: colors.text },
  card: { backgroundColor: colors.surface, margin: 16, padding: 16, borderRadius: 12 },
  title: { fontSize: 20, fontWeight: '700', color: colors.text, marginBottom: 8 },
  description: { fontSize: 14, color: colors.textSecondary, marginBottom: 8 },
  address: { fontSize: 14, color: colors.textSecondary },
  sectionTitle: { fontSize: 16, fontWeight: '600', color: colors.text, marginBottom: 12 },
  textArea: { borderWidth: 1, borderColor: colors.border, borderRadius: 8, padding: 12, fontSize: 14, minHeight: 100, textAlignVertical: 'top' },
  photoButtons: { flexDirection: 'row', gap: 12, marginBottom: 16 },
  photoButton: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: colors.primary, padding: 12, borderRadius: 8, gap: 8 },
  photoButtonText: { color: 'white', fontWeight: '600' },
  photoGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  photoItem: { width: '48%', aspectRatio: 1, borderRadius: 8, overflow: 'hidden' },
  photo: { width: '100%', height: '100%' },
  locationButton: { flexDirection: 'row', alignItems: 'center', padding: 8, backgroundColor: colors.background, borderRadius: 8, marginTop: 8 },
  locationText: { flex: 1, marginLeft: 8, fontSize: 14, color: colors.primary, fontWeight: '500' },
  statusContainer: { flexDirection: 'row', gap: 12 },
  statusButton: { flex: 1, padding: 12, borderRadius: 8, borderWidth: 1, borderColor: colors.border, alignItems: 'center' },
  statusActive: { backgroundColor: colors.primary, borderColor: colors.primary },
  statusText: { fontSize: 14, color: colors.text },
  statusTextActive: { color: 'white', fontWeight: '600' },
  actions: { padding: 16, gap: 12 },
  button: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', padding: 16, borderRadius: 8, gap: 8 },
  saveButton: { backgroundColor: colors.primary },
  completeButton: { backgroundColor: colors.success },
  buttonText: { color: 'white', fontSize: 16, fontWeight: '600' },
});
