class TaskAssignment {
  final int id;
  final int companyId;
  final int assignedBy;
  final int assignedTo;
  final String title;
  final String? description;
  final String? address;
  final double? latitude;
  final double? longitude;
  final String status;
  final String priority;
  final DateTime? dueDate;
  final String? observations;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final DateTime? startedAt;
  final DateTime? completedAt;
  
  // Dados adicionais do gerente que atribuiu
  final String? assignedByName;
  
  // Fotos associadas
  final List<AssignmentPhoto>? photos;

  TaskAssignment({
    required this.id,
    required this.companyId,
    required this.assignedBy,
    required this.assignedTo,
    required this.title,
    this.description,
    this.address,
    this.latitude,
    this.longitude,
    required this.status,
    required this.priority,
    this.dueDate,
    this.observations,
    required this.createdAt,
    this.updatedAt,
    this.startedAt,
    this.completedAt,
    this.assignedByName,
    this.photos,
  });

  factory TaskAssignment.fromJson(Map<String, dynamic> json) {
    return TaskAssignment(
      id: json['id'] as int,
      companyId: json['company_id'] as int,
      assignedBy: json['assigned_by'] as int,
      assignedTo: json['assigned_to'] as int,
      title: json['title'] as String,
      description: json['description'] as String?,
      address: json['address'] as String?,
      latitude: json['latitude'] != null
          ? (json['latitude'] as num).toDouble()
          : null,
      longitude: json['longitude'] != null
          ? (json['longitude'] as num).toDouble()
          : null,
      status: json['status'] as String? ?? 'pending',
      priority: json['priority'] as String? ?? 'medium',
      dueDate: json['due_date'] != null
          ? DateTime.parse(json['due_date'] as String)
          : null,
      observations: json['observations'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : null,
      startedAt: json['started_at'] != null
          ? DateTime.parse(json['started_at'] as String)
          : null,
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'] as String)
          : null,
      assignedByName: json['assigned_by_name'] as String?,
      photos: json['photos'] != null
          ? (json['photos'] as List)
              .map((p) => AssignmentPhoto.fromJson(p as Map<String, dynamic>))
              .toList()
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'company_id': companyId,
      'assigned_by': assignedBy,
      'assigned_to': assignedTo,
      'title': title,
      'description': description,
      'address': address,
      'latitude': latitude,
      'longitude': longitude,
      'status': status,
      'priority': priority,
      'due_date': dueDate?.toIso8601String(),
      'observations': observations,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt?.toIso8601String(),
      'started_at': startedAt?.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
      'assigned_by_name': assignedByName,
      'photos': photos?.map((p) => p.toJson()).toList(),
    };
  }

  bool get isPending => status == 'pending' || status == 'pendente';
  bool get isInProgress => status == 'in_progress' || status == 'em_andamento';
  bool get isCompleted => status == 'completed' || status == 'concluida';
  
  bool get isUrgent => priority == 'urgent' || priority == 'urgente';
  bool get isHighPriority => priority == 'high' || priority == 'alta';
  
  bool get isOverdue {
    if (dueDate == null || isCompleted) return false;
    return DateTime.now().isAfter(dueDate!);
  }
  
  String get statusDisplay {
    switch (status.toLowerCase()) {
      case 'pending':
      case 'pendente':
        return 'Pendente';
      case 'in_progress':
      case 'em_andamento':
        return 'Em Andamento';
      case 'completed':
      case 'concluida':
        return 'Concluída';
      default:
        return status;
    }
  }
  
  String get priorityDisplay {
    switch (priority.toLowerCase()) {
      case 'urgent':
      case 'urgente':
        return 'Urgente';
      case 'high':
      case 'alta':
        return 'Alta';
      case 'medium':
      case 'media':
        return 'Média';
      case 'low':
      case 'baixa':
        return 'Baixa';
      default:
        return priority;
    }
  }
}

class AssignmentPhoto {
  final int id;
  final int assignmentId;
  final String photoUrl;
  final String? photoPath;
  final String? description;
  final DateTime uploadedAt;

  AssignmentPhoto({
    required this.id,
    required this.assignmentId,
    required this.photoUrl,
    this.photoPath,
    this.description,
    required this.uploadedAt,
  });

  factory AssignmentPhoto.fromJson(Map<String, dynamic> json) {
    return AssignmentPhoto(
      id: json['id'] as int,
      assignmentId: json['assignment_id'] as int,
      photoUrl: json['photo_url'] as String,
      photoPath: json['photo_path'] as String?,
      description: json['description'] as String?,
      uploadedAt: DateTime.parse(json['uploaded_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'assignment_id': assignmentId,
      'photo_url': photoUrl,
      'photo_path': photoPath,
      'description': description,
      'uploaded_at': uploadedAt.toIso8601String(),
    };
  }
}
