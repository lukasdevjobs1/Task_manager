import React, { useEffect, useRef } from 'react';
import { StatusBar } from 'expo-status-bar';
import { NavigationContainer } from '@react-navigation/native';
import { AuthProvider } from './src/contexts/AuthContext';
import AppNavigator from './src/navigation/AppNavigator';
import {
  registerForPushNotificationsAsync,
  setupNotificationListeners,
} from './src/services/pushNotifications';

export default function App() {
  const navigationRef = useRef(null);

  useEffect(() => {
    // Set up push notification listeners
    const cleanup = setupNotificationListeners(
      // Called when a notification is received while app is in foreground
      (notification) => {
        console.log('Notification received in foreground:', notification.request.content);
      },
      // Called when the user taps a notification
      (response) => {
        const data = response.notification.request.content.data;
        console.log('Notification tapped:', data);

        // Navigate to the relevant screen based on notification data
        if (data?.type === 'task_assigned' || data?.type === 'task_updated') {
          if (data?.reference_id && navigationRef.current) {
            navigationRef.current.navigate('Home', {
              screen: 'TaskDetail',
              params: { assignmentId: data.reference_id },
            });
          }
        }
      }
    );

    return cleanup;
  }, []);

  return (
    <AuthProvider>
      <NavigationContainer ref={navigationRef}>
        <StatusBar style="light" />
        <AppNavigator />
      </NavigationContainer>
    </AuthProvider>
  );
}
