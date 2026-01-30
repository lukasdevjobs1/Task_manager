import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';
import { Platform } from 'react-native';

/**
 * Configure default notification behavior.
 * Notifications will be shown even when the app is in the foreground.
 */
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

/**
 * Register for push notifications and return the Expo push token.
 * This handles permission requests and Android notification channel setup.
 *
 * @returns {string|null} The Expo push token, or null if registration fails.
 */
export async function registerForPushNotificationsAsync() {
  let token = null;

  if (!Device.isDevice) {
    console.warn('Push notifications require a physical device.');
    return null;
  }

  // Check existing permissions
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  // Request permissions if not already granted
  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    console.warn('Push notification permission not granted.');
    return null;
  }

  // Set up Android notification channel
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'Padrao',
      description: 'Notificacoes gerais do Task Manager',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#1a73e8',
      sound: 'default',
    });

    await Notifications.setNotificationChannelAsync('tasks', {
      name: 'Tarefas',
      description: 'Notificacoes sobre tarefas atribuidas',
      importance: Notifications.AndroidImportance.HIGH,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#1a73e8',
      sound: 'default',
    });
  }

  // Get the Expo push token
  try {
    const projectId = Constants.expoConfig?.extra?.eas?.projectId;
    const tokenResponse = await Notifications.getExpoPushTokenAsync({
      projectId,
    });
    token = tokenResponse.data;
  } catch (error) {
    console.error('Error getting push token:', error);
    return null;
  }

  return token;
}

/**
 * Set up listeners for incoming notifications.
 *
 * @param {Function} onNotificationReceived - Called when a notification is received while app is foregrounded.
 * @param {Function} onNotificationResponse - Called when the user taps on a notification.
 * @returns {Function} Cleanup function to remove the listeners.
 */
export function setupNotificationListeners(onNotificationReceived, onNotificationResponse) {
  // Listener for notifications received while app is in foreground
  const receivedSubscription = Notifications.addNotificationReceivedListener(
    (notification) => {
      if (onNotificationReceived) {
        onNotificationReceived(notification);
      }
    }
  );

  // Listener for when user interacts with a notification (taps on it)
  const responseSubscription = Notifications.addNotificationResponseReceivedListener(
    (response) => {
      if (onNotificationResponse) {
        onNotificationResponse(response);
      }
    }
  );

  // Return cleanup function
  return () => {
    receivedSubscription.remove();
    responseSubscription.remove();
  };
}

/**
 * Get the last notification response (e.g., if app was opened from a notification).
 */
export async function getLastNotificationResponse() {
  return await Notifications.getLastNotificationResponseAsync();
}

/**
 * Get the current badge count on the app icon.
 */
export async function getBadgeCount() {
  return await Notifications.getBadgeCountAsync();
}

/**
 * Set the badge count on the app icon.
 */
export async function setBadgeCount(count) {
  await Notifications.setBadgeCountAsync(count);
}
