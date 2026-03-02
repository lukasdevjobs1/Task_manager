class TaskMaterial {
  final int? id;
  final int assignmentId;
  final int userId;
  final String materialName;
  final double quantity;
  final String unit;
  final DateTime createdAt;

  TaskMaterial({
    this.id,
    required this.assignmentId,
    required this.userId,
    required this.materialName,
    required this.quantity,
    required this.unit,
    required this.createdAt,
  });

  factory TaskMaterial.fromJson(Map<String, dynamic> json) {
    return TaskMaterial(
      id: json['id'] as int?,
      assignmentId: json['assignment_id'] as int,
      userId: json['user_id'] as int,
      materialName: json['material_name'] as String,
      quantity: (json['quantity'] as num).toDouble(),
      unit: json['unit'] as String? ?? 'un',
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'assignment_id': assignmentId,
      'user_id': userId,
      'material_name': materialName,
      'quantity': quantity,
      'unit': unit,
      'created_at': createdAt.toIso8601String(),
    };
  }

  String get displayQuantity {
    if (quantity == quantity.truncateToDouble()) {
      return '${quantity.toInt()} $unit';
    }
    return '${quantity.toStringAsFixed(2)} $unit';
  }
}

/// Resumo de materiais agrupado por nome, para métricas
class MaterialSummary {
  final String materialName;
  final String unit;
  final double totalQuantity;
  final int timesUsed;

  const MaterialSummary({
    required this.materialName,
    required this.unit,
    required this.totalQuantity,
    required this.timesUsed,
  });
}
