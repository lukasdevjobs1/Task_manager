import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  Dimensions,
  Image,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import MapView, { Marker } from 'react-native-maps';
import { getAssignmentDetail, getPhotoPublicUrl } from '../services/tasks';

const { width: SCREEN_WIDTH } = Dimensions.get('window');

const STATUS_CONFIG = {
  pending: { label: 'Pendente', color: '#ff9800', icon: 'time-outline' },
  in_progress: { label: 'Em Andamento', color: '#2196f3', icon: 'play-circle-outline' },
  completed: { label: 'Concluida', color: '#4caf50', icon: 'checkmark-circle-outline' },
};

const PRIORITY_CONFIG = {
  low: { label: 'Baixa', color: '#4caf50' },
  medium: { label: 'Media', color: '#ff9800' },
  high: { label: 'Alta', color: '#f44336' },
  urgent: { label: 'Urgente', color: '#9c27b0' },
};

function formatDateTime(dateString) {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatDate(dateString) {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

export default function TaskDetailScreen({ route, navigation }) {
  const { assignmentId } = route.params;
  const [assignment, setAssignment] = useState(null);
  const [loading, setLoading] = useState(true);

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
      data.observations = data.notes; // Mapear notes para observations
      setAssignment(data);
    } catch (error) {
      console.error('Error fetching assignment detail:', error);
      Alert.alert('Erro', 'Nao foi possivel carregar os detalhes da tarefa.');
    } finally {
      setLoading(false);
    }
  }, [assignmentId]);

  useFocusEffect(
    useCallback(() => {
      fetchDetail();
    }, [fetchDetail])
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#1a73e8" />
        <Text style={styles.loadingText}>Carregando detalhes...</Text>
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

  const statusConfig = STATUS_CONFIG[assignment.status] || STATUS_CONFIG.pending;
  const priorityConfig = PRIORITY_CONFIG[assignment.priority] || PRIORITY_CONFIG.medium;
  const hasCoordinates = assignment.latitude && assignment.longitude;
  const canExecute = assignment.status === 'pending' || assignment.status === 'in_progress';

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.headerCard}>
          <Text style={styles.title}>{assignment.title}</Text>
          <View style={styles.badgeRow}>
            <View style={[styles.statusBadge, { backgroundColor: statusConfig.color + '20' }]}>
              <Ionicons name={statusConfig.icon} size={16} color={statusConfig.color} />
              <Text style={[styles.badgeText, { color: statusConfig.color }]}>
                {statusConfig.label}
              </Text>
            </View>
            <View style={[styles.priorityBadge, { backgroundColor: priorityConfig.color + '20' }]}>
              <Text style={[styles.badgeText, { color: priorityConfig.color }]}>
                Prioridade: {priorityConfig.label}
              </Text>
            </View>
          </View>
        </View>

        {/* Description */}
        {assignment.description ? (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Descricao</Text>
            <Text style={styles.descriptionText}>{assignment.description}</Text>
          </View>
        ) : null}

        {/* Info */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Informacoes</Text>
          <View style={styles.infoRow}>
            <Ionicons name="calendar-outline" size={18} color="#666" />
            <Text style={styles.infoLabel}>Data Limite:</Text>
            <Text style={styles.infoValue}>{formatDate(assignment.due_date)}</Text>
          </View>
          <View style={styles.infoRow}>
            <Ionicons name="time-outline" size={18} color="#666" />
            <Text style={styles.infoLabel}>Criada em:</Text>
            <Text style={styles.infoValue}>{formatDateTime(assignment.created_at)}</Text>
          </View>
          {assignment.updated_at && (
            <View style={styles.infoRow}>
              <Ionicons name="refresh-outline" size={18} color="#666" />
              <Text style={styles.infoLabel}>Atualizada:</Text>
              <Text style={styles.infoValue}>{formatDateTime(assignment.updated_at)}</Text>
            </View>
          )}
        </View>

        {/* Address and Map */}
        {assignment.address ? (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Endereco</Text>
            <View style={styles.addressRow}>
              <Ionicons name="location-outline" size={18} color="#1a73e8" />
              <Text style={styles.addressText}>{assignment.address}</Text>
            </View>
            {hasCoordinates && (
              <View style={styles.mapContainer}>
                <MapView
                  style={styles.map}
                  initialRegion={{
                    latitude: parseFloat(assignment.latitude),
                    longitude: parseFloat(assignment.longitude),
                    latitudeDelta: 0.005,
                    longitudeDelta: 0.005,
                  }}
                  scrollEnabled={false}
                  zoomEnabled={false}
                >
                  <Marker
                    coordinate={{
                      latitude: parseFloat(assignment.latitude),
                      longitude: parseFloat(assignment.longitude),
                    }}
                    title={assignment.title}
                    description={assignment.address}
                  />
                </MapView>
              </View>
            )}
          </View>
        ) : null}

        {/* Observations */}
        {assignment.observations ? (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Observacoes</Text>
            <Text style={styles.descriptionText}>{assignment.observations}</Text>
          </View>
        ) : null}

        {/* Photos */}
        {assignment.photos && assignment.photos.length > 0 ? (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>
              Fotos ({assignment.photos.length})
            </Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {assignment.photos.map((photo) => {
                const photoUrl = getPhotoPublicUrl(photo.file_path);
                return (
                  <View key={photo.id} style={styles.photoCard}>
                    {photoUrl ? (
                      <Image
                        source={{ uri: photoUrl }}
                        style={styles.photoImage}
                        resizeMode="cover"
                      />
                    ) : (
                      <View style={styles.photoPlaceholder}>
                        <Ionicons name="image-outline" size={32} color="#ccc" />
                      </View>
                    )}
                    <Text style={styles.photoName} numberOfLines={1}>
                      {photo.original_name || 'Foto'}
                    </Text>
                  </View>
                );
              })}
            </ScrollView>
          </View>
        ) : null}

        {/* Spacer for fixed button */}
        {canExecute && <View style={{ height: 80 }} />}
      </ScrollView>

      {/* Execute Button */}
      {canExecute && (
        <View style={styles.bottomBar}>
          <TouchableOpacity
            style={styles.executeButton}
            onPress={() => navigation.navigate('TaskExecute', { assignmentId: assignment.id })}
          >
            <Ionicons name="play-circle" size={22} color="#ffffff" />
            <Text style={styles.executeButtonText}>
              {assignment.status === 'pending' ? 'Iniciar Tarefa' : 'Continuar Tarefa'}
            </Text>
          </TouchableOpacity>
        </View>
      )}
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
  headerCard: {
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
  title: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 12,
  },
  badgeRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
  },
  priorityBadge: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 8,
  },
  badgeText: {
    fontSize: 13,
    fontWeight: '600',
    marginLeft: 4,
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
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 12,
  },
  descriptionText: {
    fontSize: 14,
    color: '#444',
    lineHeight: 22,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  infoLabel: {
    fontSize: 14,
    color: '#666',
    marginLeft: 8,
    fontWeight: '500',
  },
  infoValue: {
    fontSize: 14,
    color: '#1a1a1a',
    marginLeft: 8,
  },
  addressRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  addressText: {
    fontSize: 14,
    color: '#444',
    marginLeft: 8,
    flex: 1,
    lineHeight: 20,
  },
  mapContainer: {
    borderRadius: 8,
    overflow: 'hidden',
    height: 180,
  },
  map: {
    width: '100%',
    height: '100%',
  },
  photoCard: {
    marginRight: 12,
    width: 120,
  },
  photoImage: {
    width: 120,
    height: 120,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
  },
  photoPlaceholder: {
    width: 120,
    height: 120,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  photoName: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
    textAlign: 'center',
  },
  bottomBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: '#ffffff',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 8,
  },
  executeButton: {
    backgroundColor: '#1a73e8',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 12,
    paddingVertical: 14,
    shadowColor: '#1a73e8',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  executeButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
});
