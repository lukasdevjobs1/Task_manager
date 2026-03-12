import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../providers/notification_provider.dart';
import '../services/supabase_service.dart';
import '../config/theme.dart';
import 'package:intl/intl.dart';

class NotificationsScreen extends StatelessWidget {
  const NotificationsScreen({super.key});

  Future<void> _onVerTarefa(BuildContext context, int taskId) async {
    final task = await SupabaseService.getTaskById(taskId);
    if (!context.mounted) return;

    if (task != null && task.isCompleted) {
      context.push('/task/$taskId');
    } else {
      context.go('/tasks');
    }
  }

  @override
  Widget build(BuildContext context) {
    final notificationProvider = Provider.of<NotificationProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Notificações'),
        actions: [
          if (notificationProvider.unreadCount > 0)
            TextButton(
              onPressed: () => notificationProvider.markAllAsRead(),
              child: const Text('Marcar todas como lidas'),
            ),
        ],
      ),
      body: notificationProvider.notifications.isEmpty
          ? const Center(child: Text('Nenhuma notificação'))
          : ListView.builder(
              itemCount: notificationProvider.notifications.length,
              itemBuilder: (context, index) {
                final notification = notificationProvider.notifications[index];
                return ListTile(
                  leading: Icon(
                    notification.read ? Icons.notifications_outlined : Icons.notifications_active,
                    color: notification.read ? AppTheme.textSecondary : AppTheme.primaryColor,
                  ),
                  title: Text(
                    notification.title,
                    style: TextStyle(
                      fontWeight: notification.read ? FontWeight.normal : FontWeight.bold,
                    ),
                  ),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (notification.message != null) Text(notification.message!),
                      const SizedBox(height: 4),
                      Text(
                        DateFormat('dd/MM/yyyy HH:mm').format(notification.createdAt),
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      if (notification.referenceId != null) ...[
                        const SizedBox(height: 6),
                        TextButton.icon(
                          onPressed: () {
                            if (!notification.read) {
                              notificationProvider.markAsRead(notification.id);
                            }
                            _onVerTarefa(context, notification.referenceId!);
                          },
                          icon: const Icon(Icons.open_in_new, size: 16),
                          label: const Text('Ver tarefa'),
                          style: TextButton.styleFrom(
                            padding: EdgeInsets.zero,
                            minimumSize: const Size(0, 0),
                            tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                            foregroundColor: AppTheme.primaryColor,
                          ),
                        ),
                      ],
                    ],
                  ),
                  onTap: () {
                    if (!notification.read) {
                      notificationProvider.markAsRead(notification.id);
                    }
                  },
                );
              },
            ),
    );
  }
}
