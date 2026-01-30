import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';
import { getMyAssignments } from '../services/tasks';

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

function formatDate(dateString) {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

function isOverdue(dueDateString) {
  if (!dueDateString) return false;
  const dueDate = new Date(dueDateString);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return dueDate < today;
}

export default function HomeScreen({ navigation }) {
  const { user } = useAuth();
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState('all');

  const fetchAssignments = useCallback(async () => {
    if (!user?.id) return;
    try {
      const data = await getMyAssignments(user.id);
      setAssignments(data);
    } catch (error) {
      console.error('Error fetching assignments:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [user?.id]);

  useFocusEffect(
    useCallback(() => {
      setLoading(true);
      fetchAssignments();
    }, [fetchAssignments])
  );

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchAssignments();
  }, [fetchAssignments]);

  const filteredAssignments = assignments.filter((item) => {
    if (filter === 'all') return true;
    return item.status === filter;
  });

  const renderFilterButton = (filterKey, label) => (
    <TouchableOpacity
      style={[styles.filterButton, filter === filterKey && styles.filterButtonActive]}
      onPress={() => setFilter(filterKey)}
    >
      <Text style={[styles.filterButtonText, filter === filterKey && styles.filterButtonTextActive]}>
        {label}
      </Text>
    </TouchableOpacity>
  );

  const renderAssignmentItem = ({ item }) => {
    const statusConfig = STATUS_CONFIG[item.status] || STATUS_CONFIG.pending;
    const priorityConfig = PRIORITY_CONFIG[item.priority] || PRIORITY_CONFIG.medium;
    const overdue = isOverdue(item.due_date) && item.status !== 'completed';

    return (
      <TouchableOpacity
        style={styles.card}
        onPress={() => navigation.navigate('TaskDetail', { assignmentId: item.id })}
        activeOpacity={0.7}
      >
        <View style={styles.cardHeader}>
          <View style={styles.cardTitleRow}>
            <Text style={styles.cardTitle} numberOfLines={2}>
              {item.title}
            </Text>
            <View style={[styles.priorityBadge, { backgroundColor: priorityConfig.color + '20' }]}>
              <Text style={[styles.priorityText, { color: priorityConfig.color }]}>
                {priorityConfig.label}
              </Text>
            </View>
          </View>
        </View>

        {item.description ? (
          <Text style={styles.cardDescription} numberOfLines={2}>
            {item.description}
          </Text>
        ) : null}

        {item.address ? (
          <View style={styles.cardInfoRow}>
            <Ionicons name="location-outline" size={14} color="#666" />
            <Text style={styles.cardInfoText} numberOfLines={1}>
              {item.address}
            </Text>
          </View>
        ) : null}

        <View style={styles.cardFooter}>
          <View style={[styles.statusBadge, { backgroundColor: statusConfig.color + '20' }]}>
            <Ionicons name={statusConfig.icon} size={14} color={statusConfig.color} />
            <Text style={[styles.statusText, { color: statusConfig.color }]}>
              {statusConfig.label}
            </Text>
          </View>

          <View style={styles.dateContainer}>
            <Ionicons
              name="calendar-outline"
              size={14}
              color={overdue ? '#f44336' : '#666'}
            />
            <Text style={[styles.dateText, overdue && styles.overdueText]}>
              {formatDate(item.due_date)}
            </Text>
            {overdue && (
              <Text style={styles.overdueLabel}>Atrasada</Text>
            )}
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#1a73e8" />
        <Text style={styles.loadingText}>Carregando tarefas...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.filterContainer}>
        <FlatList
          horizontal
          showsHorizontalScrollIndicator={false}
          data={[
            { key: 'all', label: 'Todas' },
            { key: 'pending', label: 'Pendentes' },
            { key: 'in_progress', label: 'Em Andamento' },
            { key: 'completed', label: 'Concluidas' },
          ]}
          renderItem={({ item }) => renderFilterButton(item.key, item.label)}
          keyExtractor={(item) => item.key}
          contentContainerStyle={styles.filterList}
        />
      </View>

      <FlatList
        data={filteredAssignments}
        renderItem={renderAssignmentItem}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={['#1a73e8']}
            tintColor="#1a73e8"
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="document-text-outline" size={64} color="#ccc" />
            <Text style={styles.emptyTitle}>Nenhuma tarefa encontrada</Text>
            <Text style={styles.emptySubtitle}>
              {filter === 'all'
                ? 'Voce nao possui tarefas atribuidas.'
                : 'Nenhuma tarefa com este filtro.'}
            </Text>
          </View>
        }
      />
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
  filterContainer: {
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  filterList: {
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f0f0f0',
    marginHorizontal: 4,
  },
  filterButtonActive: {
    backgroundColor: '#1a73e8',
  },
  filterButtonText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  filterButtonTextActive: {
    color: '#ffffff',
  },
  listContent: {
    padding: 12,
    paddingBottom: 24,
  },
  card: {
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
  cardHeader: {
    marginBottom: 8,
  },
  cardTitleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1a1a1a',
    flex: 1,
    marginRight: 8,
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  priorityText: {
    fontSize: 12,
    fontWeight: '600',
  },
  cardDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
    lineHeight: 20,
  },
  cardInfoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  cardInfoText: {
    fontSize: 13,
    color: '#666',
    marginLeft: 4,
    flex: 1,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 4,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4,
  },
  dateContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dateText: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  overdueText: {
    color: '#f44336',
    fontWeight: '600',
  },
  overdueLabel: {
    fontSize: 11,
    color: '#f44336',
    fontWeight: '700',
    marginLeft: 4,
    textTransform: 'uppercase',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 80,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#999',
    marginTop: 16,
  },
  emptySubtitle: {
    fontSize: 14,
    color: '#bbb',
    marginTop: 8,
    textAlign: 'center',
  },
});
