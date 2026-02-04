import React from 'react';
import { ActivityIndicator, View, StyleSheet } from 'react-native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';

// Screen imports
import LoginScreen from '../screens/LoginScreen';
import HomeScreen from '../screens/HomeScreen';
import CompletedTasksScreen from '../screens/CompletedTasksScreen';
import TaskDetailScreen from '../screens/TaskDetailScreen';
import TaskExecuteScreen from '../screens/TaskExecuteScreen';
import NotificationsScreen from '../screens/NotificationsScreen';
import ProfileScreen from '../screens/ProfileScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();
const HomeStack = createNativeStackNavigator();

/**
 * Stack navigator for the Home/Tasks tab.
 * Contains the task list, task detail, and task execution screens.
 */
function HomeStackNavigator() {
  return (
    <HomeStack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: '#1a73e8' },
        headerTintColor: '#ffffff',
        headerTitleStyle: { fontWeight: '600' },
      }}
    >
      <HomeStack.Screen
        name="TasksList"
        component={HomeScreen}
        options={{ title: 'Minhas Tarefas' }}
      />
      <HomeStack.Screen
        name="TaskDetail"
        component={TaskDetailScreen}
        options={{ title: 'Detalhes da Tarefa' }}
      />
      <HomeStack.Screen
        name="TaskExecute"
        component={TaskExecuteScreen}
        options={{ title: 'Executar Tarefa' }}
      />
    </HomeStack.Navigator>
  );
}

/**
 * Bottom Tab navigator for authenticated users.
 * Contains Home (tasks), Notifications, and Profile tabs.
 */
function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          switch (route.name) {
            case 'Home':
              iconName = focused ? 'list-circle' : 'list-circle-outline';
              break;
            case 'Completed':
              iconName = focused ? 'checkmark-done-circle' : 'checkmark-done-circle-outline';
              break;
            case 'Notifications':
              iconName = focused ? 'notifications' : 'notifications-outline';
              break;
            case 'Profile':
              iconName = focused ? 'person-circle' : 'person-circle-outline';
              break;
            default:
              iconName = 'ellipse-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#1a73e8',
        tabBarInactiveTintColor: '#8e8e93',
        tabBarStyle: {
          backgroundColor: '#ffffff',
          borderTopWidth: 1,
          borderTopColor: '#e0e0e0',
          paddingBottom: 4,
          paddingTop: 4,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
        headerShown: false,
      })}
    >
      <Tab.Screen
        name="Home"
        component={HomeStackNavigator}
        options={{ tabBarLabel: 'Tarefas' }}
      />
      <Tab.Screen
        name="Completed"
        component={CompletedTasksScreen}
        options={{
          tabBarLabel: 'Concluídas',
          headerShown: true,
          headerTitle: 'Tarefas Concluídas',
          headerStyle: { backgroundColor: '#1a73e8' },
          headerTintColor: '#ffffff',
          headerTitleStyle: { fontWeight: '600' },
        }}
      />
      <Tab.Screen
        name="Notifications"
        component={NotificationsScreen}
        options={{
          tabBarLabel: 'Notificacoes',
          headerShown: true,
          headerTitle: 'Notificacoes',
          headerStyle: { backgroundColor: '#1a73e8' },
          headerTintColor: '#ffffff',
          headerTitleStyle: { fontWeight: '600' },
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          tabBarLabel: 'Perfil',
          headerShown: true,
          headerTitle: 'Meu Perfil',
          headerStyle: { backgroundColor: '#1a73e8' },
          headerTintColor: '#ffffff',
          headerTitleStyle: { fontWeight: '600' },
        }}
      />
    </Tab.Navigator>
  );
}

/**
 * Root navigator that switches between auth and main app flows
 * based on authentication state.
 */
export default function AppNavigator() {
  const { isAuthenticated, loading } = useAuth();

  // Show loading spinner while checking auth state
  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#1a73e8" />
      </View>
    );
  }

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {isAuthenticated ? (
        <Stack.Screen name="Main" component={MainTabNavigator} />
      ) : (
        <Stack.Screen
          name="Login"
          component={LoginScreen}
          options={{ animationTypeForReplace: 'pop' }}
        />
      )}
    </Stack.Navigator>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
});
