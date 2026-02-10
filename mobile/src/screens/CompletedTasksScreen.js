import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { supabase } from '../config/supabase';
import { useAuth } from '../contexts/AuthContext';

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

export default function CompletedTasksScreen({ navigation }) {
  const { user } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCompletedTasks();
  }, []);

  const loadCompletedTasks = async () => {
    try {
      const { data, error } = await supabase
        .from('task_assignments')
        .select('*')
        .eq('assigned_to', user.id)
        .eq('status', 'concluida')
        .order('completed_at', { ascending: false });

      if (error) throw error;
      setTasks(data || []);
    } catch (error) {
      console.error('Erro ao carregar tarefas:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const extractMaterials = (materials) => {
    if (!materials) return { ctos: 0, ceos: 0 };
    const ctoMatch = materials.match(/(\d+)\s*cto/gi);
    const ceoMatch = materials.match(/(\d+)\s*ceo/gi);
    return {
      ctos: ctoMatch ? parseInt(ctoMatch[0].match(/\d+/)[0]) : 0,
      ceos: ceoMatch ? parseInt(ceoMatch[0].match(/\d+/)[0]) : 0
    };
  };

  const renderTask = ({ item }) => {
    const materials = extractMaterials(item.materials);
    return (
      <TouchableOpacity 
        style={styles.taskCard}
        onPress={() => navigation.navigate('TaskDetail', { assignmentId: item.id })}
      >
        <View style={styles.taskHeader}>
          <Text style={styles.taskTitle}>{item.title}</Text>
          <Text style={styles.taskDate}>{formatDate(item.completed_at)}</Text>
        </View>
        <Text style={styles.taskAddress} numberOfLines={1}>📍 {item.address}</Text>
        <View style={styles.materialsRow}>
          <View style={styles.materialItem}>
            <Ionicons name="hardware-chip" size={16} color={colors.primary} />
            <Text style={styles.materialText}>{materials.ctos} CTOs</Text>
          </View>
          <View style={styles.materialItem}>
            <Ionicons name="business" size={16} color={colors.secondary} />
            <Text style={styles.materialText}>{materials.ceos} CEOs</Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Carregando histórico...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Tarefas Concluídas</Text>
        <View style={{ width: 24 }} />
      </View>

      <FlatList
        data={tasks}
        renderItem={renderTask}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Ionicons name="checkmark-circle-outline" size={64} color={colors.textSecondary} />
            <Text style={styles.emptyText}>Nenhuma tarefa concluída ainda</Text>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.background },
  loadingText: { marginTop: 12, fontSize: 16, color: colors.textSecondary },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 16, backgroundColor: colors.surface },
  headerTitle: { fontSize: 18, fontWeight: '700', color: colors.text },
  listContainer: { padding: 16 },
  taskCard: { backgroundColor: colors.surface, padding: 16, borderRadius: 12, marginBottom: 12 },
  taskHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  taskTitle: { fontSize: 16, fontWeight: '600', color: colors.text, flex: 1 },
  taskDate: { fontSize: 12, color: colors.textSecondary },
  taskAddress: { fontSize: 14, color: colors.textSecondary, marginBottom: 12 },
  materialsRow: { flexDirection: 'row', gap: 16 },
  materialItem: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  materialText: { fontSize: 12, color: colors.textSecondary },
  emptyContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', paddingTop: 100 },
  emptyText: { fontSize: 16, color: colors.textSecondary, marginTop: 16 },
});