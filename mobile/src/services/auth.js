import { supabase } from '../config/supabase';
import * as SecureStore from 'expo-secure-store';

const USER_KEY = 'task_manager_user';

export const authenticateUser = async (username, password) => {
  try {
    // Usar a função RPC authenticate_user do PostgreSQL
    const { data, error } = await supabase.rpc('authenticate_user', {
      username_param: username,
      password_param: password
    });

    if (error) {
      throw new Error('Usuário ou senha inválidos');
    }

    if (!data || data.length === 0) {
      throw new Error('Usuário ou senha inválidos');
    }

    const user = data[0];
    return user;
  } catch (error) {
    console.error('Erro na autenticação:', error);
    throw error;
  }
};

export const saveUserToStorage = async (user) => {
  try {
    await SecureStore.setItemAsync(USER_KEY, JSON.stringify(user));
  } catch (error) {
    console.error('Erro ao salvar usuário:', error);
    throw error;
  }
};

export const loadUserFromStorage = async () => {
  try {
    const userString = await SecureStore.getItemAsync(USER_KEY);
    return userString ? JSON.parse(userString) : null;
  } catch (error) {
    console.error('Erro ao carregar usuário:', error);
    return null;
  }
};

export const clearUserFromStorage = async () => {
  try {
    await SecureStore.deleteItemAsync(USER_KEY);
  } catch (error) {
    console.error('Erro ao limpar usuário:', error);
  }
};

export const updatePushToken = async (userId, pushToken) => {
  try {
    const { error } = await supabase
      .from('users')
      .update({ push_token: pushToken })
      .eq('id', userId);

    if (error) {
      throw error;
    }
  } catch (error) {
    console.error('Erro ao atualizar push token:', error);
    throw error;
  }
};