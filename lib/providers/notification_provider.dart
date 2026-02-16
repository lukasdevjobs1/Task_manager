import 'package:flutter/material.dart';
import '../models/notification.dart';
import '../services/supabase_service.dart';

class NotificationProvider with ChangeNotifier {
  List<AppNotification> _notifications = [];
  bool _isLoading = false;
  
  List<AppNotification> get notifications => _notifications;
  bool get isLoading => _isLoading;
  int get unreadCount => _notifications.where((n) => !n.read).length;
  
  List<AppNotification> get unreadNotifications {
    return _notifications.where((n) => !n.read).toList();
  }
  
  // Carregar notificações
  Future<void> loadNotifications(int userId) async {
    _isLoading = true;
    notifyListeners();
    
    try {
      _notifications = await SupabaseService.getUserNotifications(userId);
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      print('Erro ao carregar notificações: $e');
      _isLoading = false;
      notifyListeners();
    }
  }
  
  // Marcar como lida
  Future<void> markAsRead(int notificationId) async {
    try {
      final success = await SupabaseService.markNotificationAsRead(notificationId);
      
      if (success) {
        final index = _notifications.indexWhere((n) => n.id == notificationId);
        if (index != -1) {
          _notifications[index] = AppNotification(
            id: _notifications[index].id,
            userId: _notifications[index].userId,
            companyId: _notifications[index].companyId,
            type: _notifications[index].type,
            title: _notifications[index].title,
            message: _notifications[index].message,
            referenceId: _notifications[index].referenceId,
            read: true,
            createdAt: _notifications[index].createdAt,
          );
          notifyListeners();
        }
      }
    } catch (e) {
      print('Erro ao marcar como lida: $e');
    }
  }
  
  // Marcar todas como lidas
  Future<void> markAllAsRead() async {
    for (var notification in unreadNotifications) {
      await markAsRead(notification.id);
    }
  }
}
