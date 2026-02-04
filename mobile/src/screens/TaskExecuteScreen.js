import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  Image,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import {
  getAssignmentDetail,
  updateAssignmentStatus,
  uploadAssignmentPhotos,
} from '../services/tasks';

export default function TaskExecuteScreen({ route, navigation }) {
  const { assignmentId } = route.params;
  const [assignment, setAssignment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [observations, setObservations] = useState('');
  const [photos, setPhotos] = useState([]);
  const [uploadingPhotos, setUploadingPhotos] = useState(false);

  const fetchDetail = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getAssignmentDetail(assignmentId);
      // Mapear status da API para o app
      const statusMap = {
        'pendente': 'pending',
        'em_andamento': 'in_progress', 
        'concluida': 'completed'
      };
      data.status = statusMap[data.status] || data.status;
      setAssignment(data);
      setObservations(data.notes || ''); // Usar notes da API
    } catch (error) {
      console.error('Error fetching assignment:', error);
      Alert.alert('Erro', 'Nao foi possivel carregar a tarefa.');
    } finally {
      setLoading(false);
    }
  }, [assignmentId]);

  useFocusEffect(
    useCallback(() => {
      fetchDetail();
    }, [fetchDetail])
  );

  const pickImageFromGallery = async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permissao Necessaria', 'Permita o acesso a galeria para selecionar fotos.');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsMultipleSelection: true,
        quality: 0.8,
      });

      if (!result.canceled && result.assets) {
        const newPhotos = result.assets.map((asset) => ({
          uri: asset.uri,
          fileName: asset.fileName || `photo_${Date.now()}.jpg`,
          type: asset.mimeType || 'image/jpeg',
        }));
        setPhotos((prev) => [...prev, ...newPhotos]);
      }
    } catch (error) {
      console.error('Error picking image:', error);
      Alert.alert('Erro', 'Nao foi possivel selecionar a imagem.');
    }
  };

  const takePhoto = async () => {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permissao Necessaria', 'Permita o acesso a camera para tirar fotos.');
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const asset = result.assets[0];
        setPhotos((prev) => [
          ...prev,
          {
            uri: asset.uri,
            fileName: asset.fileName || `photo_${Date.now()}.jpg`,
            type: asset.mimeType || 'image/jpeg',
          },
        ]);
      }
    } catch (error) {
      console.error('Error taking photo:', error);
      Alert.alert('Erro', 'Nao foi possivel tirar a foto.');
    }
  };

  const removePhoto = (index) => {
    setPhotos((prev) => prev.filter((_, i) => i !== index));
  };

  const handleStartTask = async () => {
    try {
      setSaving(true);
      await updateAssignmentStatus(assignmentId, 'in_progress', observations || null);
      Alert.alert('Sucesso', 'Tarefa iniciada com sucesso!');
      fetchDetail();
    } catch (error) {
      Alert.alert('Erro', 'Nao foi possivel iniciar a tarefa.');
    } finally {
      setSaving(false);
    }
  };

  const handleCompleteTask = async () => {
    Alert.alert(
      'Concluir Tarefa',
      'Deseja marcar esta tarefa como concluida?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Concluir',
          onPress: async () => {
            try {
              setSaving(true);

              // Upload photos if any
              if (photos.length > 0) {
                setUploadingPhotos(true);
                try {
                  await uploadAssignmentPhotos(assignmentId, photos);
                } catch (uploadError) {
                  console.error('Error uploading photos:', uploadError);
                  Alert.alert('Aviso', 'Algumas fotos podem nao ter sido enviadas.');
                }
                setUploadingPhotos(false);
              }

              await updateAssignmentStatus(assignmentId, 'completed', observations || null);
              Alert.alert('Sucesso', 'Tarefa concluida com sucesso!', [
                { text: 'OK', onPress: () => navigation.goBack() },
              ]);
            } catch (error) {
              Alert.alert('Erro', 'Nao foi possivel concluir a tarefa.');
            } finally {
              setSaving(false);
            }
          },
        },
      ]
    );
  };

  const handleSaveObservations = async () => {
    try {
      setSaving(true);
      console.log('Salvando observações:', observations);
      console.log('Assignment ID:', assignmentId);
      console.log('Status atual:', assignment.status);
      
      await updateAssignmentStatus(assignmentId, assignment.status, observations);
      Alert.alert('Sucesso', 'Observacoes salvas com sucesso!');
      fetchDetail(); // Recarregar dados
    } catch (error) {
      console.error('Erro ao salvar observações:', error);
      Alert.alert('Erro', `Nao foi possivel salvar as observacoes: ${error.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#1a73e8" />
        <Text style={styles.loadingText}>Carregando tarefa...</Text>
      </View>
    );
  }

  if (!assignment) {
    return (
      <View style={styles.centerContainer}>
        <Ionicons name="alert-circle-outline" size={64} color="#ccc" />
        <Text style={styles.emptyText}>Tarefa nao encontrada.</Text>
      </View>
    );
  }

  const isStarted = assignment.status === 'in_progress';

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Task Info */}
        <View style={styles.section}>
          <Text style={styles.taskTitle}>{assignment.title}</Text>
          {assignment.address && (
            <View style={styles.addressRow}>
              <Ionicons name="location-outline" size={16} color="#1a73e8" />
              <Text style={styles.addressText}>{assignment.address}</Text>
            </View>
          )}
        </View>

        {/* Status Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Status da Tarefa</Text>
          {assignment.status === 'pending' && (
            <TouchableOpacity
              style={styles.startButton}
              onPress={handleStartTask}
              disabled={saving}
            >
              {saving ? (
                <ActivityIndicator size="small" color="#fff" />
              ) : (
                <>
                  <Ionicons name="play-circle" size={20} color="#fff" />
                  <Text style={styles.actionButtonText}>Iniciar Tarefa</Text>
                </>
              )}
            </TouchableOpacity>
          )}
          {isStarted && (
            <View style={styles.statusInfo}>
              <Ionicons name="information-circle-outline" size={18} color="#2196f3" />
              <Text style={styles.statusInfoText}>
                Tarefa em andamento. Adicione observacoes e fotos, depois conclua.
              </Text>
            </View>
          )}
        </View>

        {/* Observations */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Observacoes</Text>
          <TextInput
            style={styles.observationsInput}
            placeholder="Adicione observacoes sobre a execucao da tarefa..."
            placeholderTextColor="#999"
            value={observations}
            onChangeText={setObservations}
            multiline
            numberOfLines={5}
            textAlignVertical="top"
          />
          <TouchableOpacity
            style={styles.saveObsButton}
            onPress={handleSaveObservations}
            disabled={saving}
          >
            <Ionicons name="save-outline" size={16} color="#1a73e8" />
            <Text style={styles.saveObsButtonText}>Salvar Observacoes</Text>
          </TouchableOpacity>
        </View>

        {/* Photos */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Fotos</Text>
          <View style={styles.photoActions}>
            <TouchableOpacity style={styles.photoButton} onPress={takePhoto}>
              <Ionicons name="camera" size={24} color="#1a73e8" />
              <Text style={styles.photoButtonText}>Tirar Foto</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.photoButton} onPress={pickImageFromGallery}>
              <Ionicons name="images" size={24} color="#1a73e8" />
              <Text style={styles.photoButtonText}>Galeria</Text>
            </TouchableOpacity>
          </View>

          {photos.length > 0 && (
            <View style={styles.photoGrid}>
              {photos.map((photo, index) => (
                <View key={index} style={styles.photoItem}>
                  <Image source={{ uri: photo.uri }} style={styles.photoThumbnail} />
                  <TouchableOpacity
                    style={styles.removePhotoButton}
                    onPress={() => removePhoto(index)}
                  >
                    <Ionicons name="close-circle" size={24} color="#f44336" />
                  </TouchableOpacity>
                </View>
              ))}
            </View>
          )}

          {uploadingPhotos && (
            <View style={styles.uploadingContainer}>
              <ActivityIndicator size="small" color="#1a73e8" />
              <Text style={styles.uploadingText}>Enviando fotos...</Text>
            </View>
          )}
        </View>

        {/* Complete Button */}
        {isStarted && (
          <TouchableOpacity
            style={styles.completeButton}
            onPress={handleCompleteTask}
            disabled={saving}
          >
            {saving ? (
              <ActivityIndicator size="small" color="#fff" />
            ) : (
              <>
                <Ionicons name="checkmark-circle" size={22} color="#fff" />
                <Text style={styles.completeButtonText}>Concluir Tarefa</Text>
              </>
            )}
          </TouchableOpacity>
        )}

        <View style={{ height: 24 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#666',
  },
  emptyText: {
    marginTop: 12,
    fontSize: 16,
    color: '#999',
  },
  scrollContent: {
    padding: 16,
  },
  section: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 2,
  },
  taskTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 8,
  },
  addressRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  addressText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 6,
    flex: 1,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 12,
  },
  startButton: {
    backgroundColor: '#2196f3',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 10,
    paddingVertical: 12,
  },
  actionButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  statusInfo: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#e3f2fd',
    borderRadius: 8,
    padding: 12,
  },
  statusInfoText: {
    fontSize: 14,
    color: '#1565c0',
    marginLeft: 8,
    flex: 1,
    lineHeight: 20,
  },
  observationsInput: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 10,
    padding: 12,
    fontSize: 14,
    color: '#333',
    minHeight: 100,
    backgroundColor: '#fafafa',
  },
  saveObsButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 10,
    paddingVertical: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#1a73e8',
  },
  saveObsButtonText: {
    color: '#1a73e8',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 6,
  },
  photoActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  photoButton: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#1a73e8',
    borderStyle: 'dashed',
    flex: 1,
    marginHorizontal: 6,
  },
  photoButtonText: {
    color: '#1a73e8',
    fontSize: 14,
    fontWeight: '500',
    marginTop: 6,
  },
  photoGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  photoItem: {
    position: 'relative',
    width: 100,
    height: 100,
  },
  photoThumbnail: {
    width: 100,
    height: 100,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
  },
  removePhotoButton: {
    position: 'absolute',
    top: -8,
    right: -8,
    backgroundColor: '#ffffff',
    borderRadius: 12,
  },
  uploadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 12,
  },
  uploadingText: {
    fontSize: 14,
    color: '#1a73e8',
    marginLeft: 8,
  },
  completeButton: {
    backgroundColor: '#4caf50',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 12,
    paddingVertical: 16,
    shadowColor: '#4caf50',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  completeButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
    marginLeft: 8,
  },
});
