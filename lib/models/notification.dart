class AppNotification {
  final int id;
  final int userId;
  final int companyId;
  final String type;
  final String title;
  final String? message;
  final int? referenceId;
  final bool read;
  final DateTime createdAt;

  AppNotification({
    required this.id,
    required this.userId,
    required this.companyId,
    required this.type,
    required this.title,
    this.message,
    this.referenceId,
    required this.read,
    required this.createdAt,
  });

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      companyId: json['company_id'] as int,
      type: json['type'] as String,
      title: json['title'] as String,
      message: json['message'] as String?,
      referenceId: json['reference_id'] as int?,
      read: json['read'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'company_id': companyId,
      'type': type,
      'title': title,
      'message': message,
      'reference_id': referenceId,
      'read': read,
      'created_at': createdAt.toIso8601String(),
    };
  }
  
  String get typeDisplay {
    switch (type) {
      case 'task_assigned':
        return 'Nova Tarefa';
      case 'task_updated':
        return 'Atualização';
      case 'task_completed':
        return 'Concluída';
      case 'chat_message':
        return 'Mensagem';
      default:
        return 'Notificação';
    }
  }
}
