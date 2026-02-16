class User {
  final int id;
  final int companyId;
  final String username;
  final String fullName;
  final String team;
  final String role;
  final bool active;
  final String? companyName;
  final String? pushToken;
  final DateTime? createdAt;

  User({
    required this.id,
    required this.companyId,
    required this.username,
    required this.fullName,
    required this.team,
    required this.role,
    required this.active,
    this.companyName,
    this.pushToken,
    this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int,
      companyId: json['company_id'] as int,
      username: json['username'] as String,
      fullName: json['full_name'] as String,
      team: json['team'] as String,
      role: json['role'] as String,
      active: json['active'] as bool? ?? true,
      companyName: json['company_name'] as String?,
      pushToken: json['push_token'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'company_id': companyId,
      'username': username,
      'full_name': fullName,
      'team': team,
      'role': role,
      'active': active,
      'company_name': companyName,
      'push_token': pushToken,
      'created_at': createdAt?.toIso8601String(),
    };
  }

  bool get isAdmin => role == 'admin';
  bool get isSuperAdmin => role == 'super_admin';
}
