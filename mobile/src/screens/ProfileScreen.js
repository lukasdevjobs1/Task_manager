import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, Alert, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
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

export default function ProfileScreen({ navigation }) {
  const { user, updateUser, logout } = useAuth();
  const [profilePhoto, setProfilePhoto] = useState(user?.profile_photo);
  const [loading, setLoading] = useState(false);

  const handleLogout = () => {
    Alert.alert(
      'Sair',
      'Tem certeza que deseja sair da sua conta?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'Sair', style: 'destructive', onPress: logout },
      ]
    );
  };

  const pickImage = async () => {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permissão necessária', 'Precisamos de permissão para acessar suas fotos');
      return;
    }

    const result = await ImagePicker.launchImagePickerAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled) {
      uploadProfilePhoto(result.assets[0].uri);
    }
  };

  const takePhoto = async () => {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permissão necessária', 'Precisamos de permissão para usar a câmera');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled) {
      uploadProfilePhoto(result.assets[0].uri);
    }
  };

  const uploadProfilePhoto = async (uri) => {
    setLoading(true);
    try {
      const { error } = await supabase
        .from('users')
        .update({ profile_photo: uri })
        .eq('id', user.id);

      if (error) throw error;

      setProfilePhoto(uri);
      updateUser({ ...user, profile_photo: uri });
      Alert.alert('Sucesso', 'Foto de perfil atualizada!');
    } catch (error) {
      Alert.alert('Erro', 'Erro ao atualizar foto de perfil');
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  };

  const showPhotoOptions = () => {
    Alert.alert(
      'Foto de Perfil',
      'Escolha uma opção',
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'Câmera', onPress: takePhoto },
        { text: 'Galeria', onPress: pickImage },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Meu Perfil</Text>
        <View style={{ width: 24 }} />
      </View>

      <View style={styles.content}>
        <TouchableOpacity style={styles.photoContainer} onPress={showPhotoOptions}>
          {profilePhoto ? (
            <Image source={{ uri: profilePhoto }} style={styles.profilePhoto} />
          ) : (
            <View style={styles.photoPlaceholder}>
              <Ionicons name="person" size={64} color={colors.textSecondary} />
            </View>
          )}
          <View style={styles.photoButton}>
            <Ionicons name="camera" size={20} color="white" />
          </View>
          {loading && (
            <View style={styles.loadingOverlay}>
              <ActivityIndicator color={colors.primary} />
            </View>
          )}
        </TouchableOpacity>

        <View style={styles.infoCard}>
          <Text style={styles.userName}>{user?.full_name}</Text>
          <Text style={styles.userRole}>{user?.role}</Text>
          <Text style={styles.userTeam}>{user?.team}</Text>
        </View>

        <View style={styles.menuItems}>
          <TouchableOpacity 
            style={styles.menuItem}
            onPress={() => navigation.navigate('Metrics')}
          >
            <Ionicons name="stats-chart" size={24} color={colors.primary} />
            <Text style={styles.menuText}>Minhas Métricas</Text>
            <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.menuItem}
            onPress={() => navigation.navigate('CompletedTasks')}
          >
            <Ionicons name="checkmark-circle" size={24} color={colors.success} />
            <Text style={styles.menuText}>Tarefas Concluídas</Text>
            <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.menuItem, styles.logoutButton]}
            onPress={handleLogout}
          >
            <Ionicons name="log-out" size={24} color={colors.error} />
            <Text style={[styles.menuText, styles.logoutText]}>Sair da Conta</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 16, backgroundColor: colors.surface },
  headerTitle: { fontSize: 18, fontWeight: '700', color: colors.text },
  content: { flex: 1, padding: 16 },
  photoContainer: { alignSelf: 'center', marginBottom: 24, position: 'relative' },
  profilePhoto: { width: 120, height: 120, borderRadius: 60 },
  photoPlaceholder: { width: 120, height: 120, borderRadius: 60, backgroundColor: colors.border, justifyContent: 'center', alignItems: 'center' },
  photoButton: { position: 'absolute', bottom: 0, right: 0, backgroundColor: colors.primary, width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center' },
  loadingOverlay: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(255,255,255,0.8)', borderRadius: 60, justifyContent: 'center', alignItems: 'center' },
  infoCard: { backgroundColor: colors.surface, padding: 20, borderRadius: 12, alignItems: 'center', marginBottom: 24 },
  userName: { fontSize: 20, fontWeight: '700', color: colors.text, marginBottom: 4 },
  userRole: { fontSize: 16, color: colors.primary, marginBottom: 2 },
  userTeam: { fontSize: 14, color: colors.textSecondary },
  menuItems: { gap: 12 },
  menuItem: { flexDirection: 'row', alignItems: 'center', backgroundColor: colors.surface, padding: 16, borderRadius: 12 },
  menuText: { flex: 1, marginLeft: 12, fontSize: 16, color: colors.text },
  logoutButton: { borderWidth: 1, borderColor: colors.error },
  logoutText: { color: colors.error, fontWeight: '600' },
});