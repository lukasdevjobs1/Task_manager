import { supabase } from '../config/supabase';
import * as SecureStore from 'expo-secure-store';

const USER_KEY = 'task_manager_user';

export const authenticateUser = async (username, password) => {
  try {
    console.log('Tentando autenticar:', username);
    
    // Buscar usuário com empresa
    const { data, error } = await supabase
      .from('users')
      .select(`
        id, company_id, username, password_hash, full_name, team, role, active,
        companies(name, active)
      `)
      .eq('username', username)
      .single();

    if (error || !data) {
      console.log('Usuário não encontrado:', error);
      throw new Error('Usuário não encontrado');
    }

    const user = data;
    const company = user.companies;

    console.log('Usuário encontrado:', user.username);
    console.log('Empresa ativa:', company?.active);
    console.log('Usuário ativo:', user.active);

    // Verificar se usuário e empresa estão ativos
    if (!user.active || !company?.active) {
      throw new Error('Usuário ou empresa inativo');
    }

    // TEMPORÁRIO: Aceitar qualquer senha para debug
    // TODO: Implementar verificação bcrypt correta
    console.log('Autenticação bem-sucedida para:', user.username);

    return {
      id: user.id,
      company_id: user.company_id,
      company_name: company.name,
      username: user.username,
      full_name: user.full_name,
      team: user.team,
      role: user.role
    };
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