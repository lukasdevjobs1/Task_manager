import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'supabase_service.dart';

class NotificationService {
  static final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  static final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();
  
  static Future<void> initialize() async {
    // Solicitar permissão
    NotificationSettings settings = await _firebaseMessaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
    );
    
    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      print('Permissão de notificação concedida');
    }
    
    // Configurar notificações locais
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );
    
    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );
    
    await _localNotifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );
    
    // Configurar handlers
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);
    FirebaseMessaging.onMessageOpenedApp.listen(_handleBackgroundMessage);
    FirebaseMessaging.onBackgroundMessage(_firebaseBackgroundHandler);
  }
  
  // Obter token do dispositivo
  static Future<String?> getDeviceToken() async {
    try {
      return await _firebaseMessaging.getToken();
    } catch (e) {
      print('Erro ao obter token: $e');
      return null;
    }
  }
  
  // Atualizar token no servidor
  static Future<void> updateTokenOnServer(int userId) async {
    final token = await getDeviceToken();
    if (token != null) {
      await SupabaseService.updatePushToken(userId, token);
    }
  }
  
  // Handler para mensagens em foreground
  static void _handleForegroundMessage(RemoteMessage message) {
    print('Mensagem recebida em foreground: ${message.notification?.title}');
    
    // Mostrar notificação local
    _showLocalNotification(
      title: message.notification?.title ?? 'Nova Notificação',
      body: message.notification?.body ?? '',
      payload: message.data.toString(),
    );
  }
  
  // Handler para mensagens em background
  static void _handleBackgroundMessage(RemoteMessage message) {
    print('Mensagem aberta do background: ${message.notification?.title}');
    // Navegar para tela apropriada
  }
  
  // Mostrar notificação local
  static Future<void> _showLocalNotification({
    required String title,
    required String body,
    String? payload,
  }) async {
    const androidDetails = AndroidNotificationDetails(
      'task_channel',
      'Tarefas',
      channelDescription: 'Notificações de tarefas',
      importance: Importance.high,
      priority: Priority.high,
      showWhen: true,
    );
    
    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );
    
    const notificationDetails = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );
    
    await _localNotifications.show(
      DateTime.now().millisecond,
      title,
      body,
      notificationDetails,
      payload: payload,
    );
  }
  
  // Callback quando notificação é tocada
  static void _onNotificationTapped(NotificationResponse response) {
    print('Notificação tocada: ${response.payload}');
    // Navegar para tela apropriada
  }
}

// Handler para mensagens em background (deve ser top-level)
@pragma('vm:entry-point')
Future<void> _firebaseBackgroundHandler(RemoteMessage message) async {
  print('Mensagem em background: ${message.notification?.title}');
}
