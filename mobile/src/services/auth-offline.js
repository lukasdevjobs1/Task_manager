import * as SecureStore from 'expo-secure-store';

const USER_STORAGE_KEY = 'task_manager_user';

// Mock user data for testing
const MOCK_USERS = [
  {
    id: 1,
    username: 'admin',
    full_name: 'Administrador',
    team: 'infraestrutura',
    role: 'admin',
    active: true,
  },
  {
    id: 2,
    username: 'tecnico1',
    full_name: 'Técnico 1',
    team: 'fusao',
    role: 'user',
    active: true,
  },
];

/**
 * Mock authentication for testing (offline mode)
 */
export async function authenticateUser(username, password) {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  const user = MOCK_USERS.find(u => u.username === username);
  
  if (!user) {
    throw new Error('Usuário ou senha inválidos.');
  }
  
  // Simple password check for testing
  if (password !== 'admin123' && password !== 'tecnico123') {
    throw new Error('Usuário ou senha inválidos.');
  }
  
  if (!user.active) {
    throw new Error('Usuário inativo. Contate o administrador.');
  }
  
  return user;
}

/**
 * Save user data to SecureStore for session persistence.
 */
export async function saveUserToStorage(user) {
  try {
    const userData = JSON.stringify(user);
    await SecureStore.setItemAsync(USER_STORAGE_KEY, userData);
  } catch (error) {
    console.error('Error saving user to storage:', error);
    throw new Error('Erro ao salvar dados do usuário.');
  }
}

/**
 * Load user data from SecureStore.
 */
export async function loadUserFromStorage() {
  try {
    const userData = await SecureStore.getItemAsync(USER_STORAGE_KEY);
    if (userData) {
      return JSON.parse(userData);
    }
    return null;
  } catch (error) {
    console.error('Error loading user from storage:', error);
    return null;
  }
}

/**
 * Clear user data from SecureStore (logout).
 */
export async function clearUserFromStorage() {
  try {
    await SecureStore.deleteItemAsync(USER_STORAGE_KEY);
  } catch (error) {
    console.error('Error clearing user from storage:', error);
  }
}

/**
 * Mock update push token
 */
export async function updatePushToken(userId, token) {
  console.log('Mock: Updated push token for user', userId, token);
}