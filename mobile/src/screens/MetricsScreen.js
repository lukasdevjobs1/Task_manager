import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, ActivityIndicator } from 'react-native';
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

export default function MetricsScreen({ navigation }) {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState({
    currentMonth: { ctos: 0, ceos: 0, tasks: 0 },
    allTime: { ctos: 0, ceos: 0, tasks: 0 }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      const currentDate = new Date();
      const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
      
      // Métricas do mês atual
      const { data: currentTasks } = await supabase
        .from('task_assignments')
        .select('materials')
        .eq('assigned_to', user.id)
        .eq('status', 'concluida')
        .gte('completed_at', firstDayOfMonth.toISOString());

      // Métricas de todos os tempos
      const { data: allTasks } = await supabase
        .from('task_assignments')
        .select('materials')
        .eq('assigned_to', user.id)
        .eq('status', 'concluida');

      const calculateMaterials = (tasks) => {
        let ctos = 0, ceos = 0;
        tasks?.forEach(task => {
          if (task.materials) {
            const ctoMatch = task.materials.match(/(\d+)\s*cto/gi);
            const ceoMatch = task.materials.match(/(\d+)\s*ceo/gi);
            if (ctoMatch) ctos += parseInt(ctoMatch[0].match(/\d+/)[0]);
            if (ceoMatch) ceos += parseInt(ceoMatch[0].match(/\d+/)[0]);
          }
        });
        return { ctos, ceos, tasks: tasks?.length || 0 };
      };

      setMetrics({
        currentMonth: calculateMaterials(currentTasks),
        allTime: calculateMaterials(allTasks)
      });
    } catch (error) {
      console.error('Erro ao carregar métricas:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Carregando métricas...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Minhas Métricas</Text>
        <View style={{ width: 24 }} />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 Mês Atual</Text>
        <View style={styles.metricsGrid}>
          <View style={styles.metricCard}>
            <Ionicons name="hardware-chip" size={32} color={colors.primary} />
            <Text style={styles.metricValue}>{metrics.currentMonth.ctos}</Text>
            <Text style={styles.metricLabel}>CTOs</Text>
          </View>
          <View style={styles.metricCard}>
            <Ionicons name="business" size={32} color={colors.secondary} />
            <Text style={styles.metricValue}>{metrics.currentMonth.ceos}</Text>
            <Text style={styles.metricLabel}>CEOs</Text>
          </View>
          <View style={styles.metricCard}>
            <Ionicons name="checkmark-circle" size={32} color={colors.success} />
            <Text style={styles.metricValue}>{metrics.currentMonth.tasks}</Text>
            <Text style={styles.metricLabel}>Tarefas</Text>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🏆 Total Geral</Text>
        <View style={styles.metricsGrid}>
          <View style={styles.metricCard}>
            <Ionicons name="hardware-chip" size={32} color={colors.primary} />
            <Text style={styles.metricValue}>{metrics.allTime.ctos}</Text>
            <Text style={styles.metricLabel}>CTOs</Text>
          </View>
          <View style={styles.metricCard}>
            <Ionicons name="business" size={32} color={colors.secondary} />
            <Text style={styles.metricValue}>{metrics.allTime.ceos}</Text>
            <Text style={styles.metricLabel}>CEOs</Text>
          </View>
          <View style={styles.metricCard}>
            <Ionicons name="checkmark-circle" size={32} color={colors.success} />
            <Text style={styles.metricValue}>{metrics.allTime.tasks}</Text>
            <Text style={styles.metricLabel}>Tarefas</Text>
          </View>
        </View>
      </View>

      <TouchableOpacity 
        style={styles.historyButton}
        onPress={() => navigation.navigate('CompletedTasks')}
      >
        <Ionicons name="time" size={20} color="white" />
        <Text style={styles.historyButtonText}>Ver Histórico Completo</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.background },
  loadingText: { marginTop: 12, fontSize: 16, color: colors.textSecondary },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 16, backgroundColor: colors.surface },
  headerTitle: { fontSize: 18, fontWeight: '700', color: colors.text },
  section: { margin: 16 },
  sectionTitle: { fontSize: 18, fontWeight: '700', color: colors.text, marginBottom: 16 },
  metricsGrid: { flexDirection: 'row', gap: 12 },
  metricCard: { flex: 1, backgroundColor: colors.surface, padding: 16, borderRadius: 12, alignItems: 'center' },
  metricValue: { fontSize: 24, fontWeight: '700', color: colors.text, marginTop: 8 },
  metricLabel: { fontSize: 12, color: colors.textSecondary, marginTop: 4 },
  historyButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: colors.primary, margin: 16, padding: 16, borderRadius: 12, gap: 8 },
  historyButtonText: { color: 'white', fontSize: 16, fontWeight: '600' },
});