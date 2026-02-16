class ChatMessage {
  final int id;
  final int taskAssignmentId;
  final int senderId;
  final String senderName;
  final String message;
  final DateTime createdAt;
  final bool isRead;

  ChatMessage({
    required this.id,
    required this.taskAssignmentId,
    required this.senderId,
    required this.senderName,
    required this.message,
    required this.createdAt,
    required this.isRead,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] as int,
      taskAssignmentId: json['task_assignment_id'] as int,
      senderId: json['sender_id'] as int,
      senderName: json['sender_name'] as String,
      message: json['message'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      isRead: json['is_read'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'task_assignment_id': taskAssignmentId,
      'sender_id': senderId,
      'sender_name': senderName,
      'message': message,
      'created_at': createdAt.toIso8601String(),
      'is_read': isRead,
    };
  }
}
