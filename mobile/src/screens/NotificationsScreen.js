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
import {
  getNotifications,
  markAsRead,
  markAllAsRead,
} from '../services/notifications';

const NOTIFICATION_ICONS = {
  task_assigned: { name: 'document-text', color: '#1a73e8' },
  task_updated: { name: 'refresh-circle', color: '#ff9800' },
  task_completed: { name: 'checkmark-circle', color: '#4caf50' },
  task_cancelled: { name: 'close-circle', color: '#f44336' },
  general: { name: 'notifications', color: '#666' },
};

function formatTimeAgo(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Agora';
  if (diffMins < 60) return `${diffMins} min atras`;
  if (diffHours < 24) return `${diffHours}h atras`;
  if (diffDays < 7) return `${diffDays}d atras`;

  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

export default function NotificationsScreen() {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchNotifications = useCallback(async () => {
    if (!user?.id) return;
    try {
      const data = await getNotifications(user.id);
      setNotifications(data);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [user?.id]);

  useFocusEffect(
    useCallback(() => {
      setLoading(true);
      fetchNotifications();
    }, [fetchNotifications])
  );

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchNotifications();
  }, [fetchNotifications]);

  const handleMarkAsRead = async (notificationId) => {
    try {
      await markAsRead(notificationId);
      setNotifications((prev) =>
        prev.map((n) => (n.id === notificationId ? { ...n, read: true } : n))
      );
    } catch (error) {
      console.error('Error marking as read:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    if (!user?.id) return;
    try {
      await markAllAsRead(user.id);
      setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  const renderNotificationItem = ({ item }) => {
    const iconConfig = NOTIFICATION_ICONS[item.type] || NOTIFICATION_ICONS.general;

    return (
      <TouchableOpacity
        style={[styles.notificationCard, !item.read && styles.unreadCard]}
        onPress={() => handleMarkAsRead(item.id)}
        activeOpacity={0.7}
      >
        <View style={[styles.iconContainer, { backgroundColor: iconConfig.color + '15' }]}>
          <Ionicons name={iconConfig.name} size={24} color={iconConfig.color} />
        </View>
        <View style={styles.contentContainer}>
          <View style={styles.notificationHeader}>
            <Text style={[styles.notificationTitle, !item.read && styles.unreadTitle]}>
              {item.title}
            </Text>
            {!item.read && <View style={styles.unreadDot} />}
          </View>
          <Text style={styles.notificationMessage} numberOfLines={2}>
            {item.message}
          </Text>
          <Text style={styles.notificationTime}>{formatTimeAgo(item.created_at)}</Text>
        </View>
      </TouchableOpacity>
    );
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#1a73e8" />
        <Text style={styles.loadingText}>Carregando notificacoes...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header Actions */}
      {unreadCount > 0 && (
        <View style={styles.headerActions}>
          <Text style={styles.unreadLabel}>
            {unreadCount} {unreadCount === 1 ? 'nao lida' : 'nao lidas'}
          </Text>
          <TouchableOpacity onPress={handleMarkAllAsRead}>
            <Text style={styles.markAllText}>Marcar todas como lidas</Text>
          </TouchableOpacity>
        </View>
      )}

      <FlatList
        data={notifications}
        renderItem={renderNotificationItem}
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
            <Ionicons name="notifications-off-outline" size={64} color="#ccc" />
            <Text style={styles.emptyTitle}>Nenhuma notificacao</Text>
            <Text style={styles.emptySubtitle}>
              Voce sera notificado quando houver novas tarefas ou atualizacoes.
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
  headerActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  unreadLabel: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  markAllText: {
    fontSize: 14,
    color: '#1a73e8',
    fontWeight: '600',
  },
  listContent: {
    padding: 12,
    paddingBottom: 24,
  },
  notificationCard: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 3,
    elevation: 1,
  },
  unreadCard: {
    backgroundColor: '#f0f7ff',
    borderLeftWidth: 3,
    borderLeftColor: '#1a73e8',
  },
  iconContainer: {
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  contentContainer: {
    flex: 1,
  },
  notificationHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  notificationTitle: {
    fontSize: 15,
    fontWeight: '500',
    color: '#333',
    flex: 1,
  },
  unreadTitle: {
    fontWeight: '700',
    color: '#1a1a1a',
  },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#1a73e8',
    marginLeft: 8,
  },
  notificationMessage: {
    fontSize: 13,
    color: '#666',
    lineHeight: 18,
    marginBottom: 4,
  },
  notificationTime: {
    fontSize: 12,
    color: '#999',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 80,
    paddingHorizontal: 32,
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
    lineHeight: 20,
  },
});
