import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';

export default function ProfileScreen() {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    Alert.alert(
      'Sair',
      'Deseja realmente sair da sua conta?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Sair',
          style: 'destructive',
          onPress: logout,
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
      {/* User Avatar & Name */}
      <View style={styles.profileHeader}>
        <View style={styles.avatarContainer}>
          <Ionicons name="person" size={48} color="#ffffff" />
        </View>
        <Text style={styles.fullName}>{user?.full_name || 'Usuario'}</Text>
        <Text style={styles.username}>@{user?.username || '-'}</Text>
      </View>

      {/* User Info */}
      <View style={styles.infoSection}>
        <Text style={styles.sectionTitle}>Informacoes</Text>

        <View style={styles.infoRow}>
          <View style={styles.infoIconContainer}>
            <Ionicons name="person-outline" size={20} color="#1a73e8" />
          </View>
          <View style={styles.infoContent}>
            <Text style={styles.infoLabel}>Nome Completo</Text>
            <Text style={styles.infoValue}>{user?.full_name || '-'}</Text>
          </View>
        </View>

        <View style={styles.infoRow}>
          <View style={styles.infoIconContainer}>
            <Ionicons name="at-outline" size={20} color="#1a73e8" />
          </View>
          <View style={styles.infoContent}>
            <Text style={styles.infoLabel}>Usuario</Text>
            <Text style={styles.infoValue}>{user?.username || '-'}</Text>
          </View>
        </View>

        <View style={styles.infoRow}>
          <View style={styles.infoIconContainer}>
            <Ionicons name="people-outline" size={20} color="#1a73e8" />
          </View>
          <View style={styles.infoContent}>
            <Text style={styles.infoLabel}>Equipe</Text>
            <Text style={styles.infoValue}>{user?.team || '-'}</Text>
          </View>
        </View>

        <View style={styles.infoRow}>
          <View style={styles.infoIconContainer}>
            <Ionicons name="shield-checkmark-outline" size={20} color="#1a73e8" />
          </View>
          <View style={styles.infoContent}>
            <Text style={styles.infoLabel}>Funcao</Text>
            <Text style={styles.infoValue}>{user?.role || '-'}</Text>
          </View>
        </View>
      </View>

      {/* Actions */}
      <View style={styles.actionsSection}>
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Ionicons name="log-out-outline" size={22} color="#f44336" />
          <Text style={styles.logoutButtonText}>Sair da Conta</Text>
        </TouchableOpacity>
      </View>

      {/* App Version */}
      <Text style={styles.versionText}>Task Manager v1.0.0</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContent: {
    paddingBottom: 32,
  },
  profileHeader: {
    alignItems: 'center',
    paddingVertical: 32,
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  avatarContainer: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: '#1a73e8',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#1a73e8',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  fullName: {
    fontSize: 22,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  username: {
    fontSize: 16,
    color: '#666',
  },
  infoSection: {
    backgroundColor: '#ffffff',
    marginTop: 16,
    marginHorizontal: 16,
    borderRadius: 12,
    padding: 16,
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
    marginBottom: 16,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  infoIconContainer: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#e8f0fe',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  infoContent: {
    flex: 1,
  },
  infoLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 2,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  infoValue: {
    fontSize: 15,
    color: '#333',
    fontWeight: '500',
  },
  actionsSection: {
    marginTop: 16,
    marginHorizontal: 16,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 12,
    paddingVertical: 16,
    borderWidth: 1,
    borderColor: '#f44336',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
    elevation: 2,
  },
  logoutButtonText: {
    color: '#f44336',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  versionText: {
    textAlign: 'center',
    fontSize: 13,
    color: '#bbb',
    marginTop: 24,
  },
});
