import 'dart:typed_data';

import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/user.dart' as app_user;
import '../models/task_assignment.dart';
import '../models/task_material.dart';
import '../models/notification.dart';
import '../models/chat_message.dart';

class SupabaseService {
  static final SupabaseClient _client = Supabase.instance.client;
  
  // Autenticação
  static Future<app_user.User?> authenticateUser(String username, String password) async {
    try {
      print('SupabaseService: Buscando usuário $username');
      
      // Busca usuário ativo com empresa ativa
      final response = await _client
          .from('users')
          .select('''
            *,
            companies!inner(
              id,
              name,
              active
            )
          ''')
          .eq('username', username)
          .eq('active', true)
          .eq('companies.active', true)
          .maybeSingle();

      print('SupabaseService: Resposta recebida: ${response != null}');
      
      if (response == null) {
        print('SupabaseService: Usuário não encontrado');
        return null;
      }

      // TODO: Validar senha (bcrypt)
      // Por enquanto, senha simplificada para teste
      print('SupabaseService: Usuário encontrado, criando objeto User');
      
      final userData = Map<String, dynamic>.from(response);
      userData['company_name'] = userData['companies']['name'];
      userData['company_id'] = userData['companies']['id'];
      
      final user = app_user.User.fromJson(userData);
      print('SupabaseService: Login bem-sucedido para ${user.username}');
      
      return user;
    } catch (e) {
      print('Erro na autenticação: $e');
      return null;
    }
  }
  
  // Atualizar push token
  static Future<bool> updatePushToken(int userId, String token) async {
    try {
      await _client
          .from('users')
          .update({'push_token': token})
          .eq('id', userId);
      return true;
    } catch (e) {
      print('Erro ao atualizar push token: $e');
      return false;
    }
  }
  
  // Buscar tarefas do usuário
  static Future<List<TaskAssignment>> getUserTasks(int userId, {String? status}) async {
    try {
      var query = _client
          .from('task_assignments')
          .select('''
            *,
            assigned_by_user:users!assigned_by(
              full_name
            )
          ''')
          .eq('assigned_to', userId);
      
      if (status != null) {
        query = query.eq('status', status);
      }
      
      final response = await query.order('created_at', ascending: false);
      
      return (response as List).map((task) {
        final taskData = Map<String, dynamic>.from(task);
        if (taskData['assigned_by_user'] != null) {
          taskData['assigned_by_name'] = taskData['assigned_by_user']['full_name'];
        }
        return TaskAssignment.fromJson(taskData);
      }).toList();
    } catch (e) {
      print('Erro ao buscar tarefas: $e');
      return [];
    }
  }
  
  // Buscar detalhes de uma tarefa
  static Future<TaskAssignment?> getTaskById(int taskId) async {
    try {
      final response = await _client
          .from('task_assignments')
          .select('''
            *,
            assigned_by_user:users!assigned_by(
              full_name
            ),
            photos:assignment_photos(*),
            materials:task_materials(*)
          ''')
          .eq('id', taskId)
          .maybeSingle();
      
      if (response == null) return null;
      
      final taskData = Map<String, dynamic>.from(response);
      if (taskData['assigned_by_user'] != null) {
        taskData['assigned_by_name'] = taskData['assigned_by_user']['full_name'];
      }
      
      return TaskAssignment.fromJson(taskData);
    } catch (e) {
      print('Erro ao buscar tarefa: $e');
      return null;
    }
  }
  
  // Atualizar status da tarefa
  static Future<bool> updateTaskStatus(
    int taskId,
    String newStatus, {
    String? observations,
  }) async {
    try {
      final Map<String, dynamic> updateData = {
        'status': newStatus,
        'updated_at': DateTime.now().toIso8601String(),
      };
      
      if (newStatus == 'em_andamento' || newStatus == 'in_progress') {
        updateData['started_at'] = DateTime.now().toIso8601String();
      } else if (newStatus == 'concluida' || newStatus == 'completed') {
        updateData['completed_at'] = DateTime.now().toIso8601String();
      }
      
      if (observations != null) {
        updateData['observations'] = observations;
      }
      
      await _client
          .from('task_assignments')
          .update(updateData)
          .eq('id', taskId);
      
      return true;
    } catch (e) {
      print('Erro ao atualizar status: $e');
      return false;
    }
  }
  
  // Criar notificação
  static Future<bool> createNotification({
    required int userId,
    required int companyId,
    required String type,
    required String title,
    required String message,
    int? referenceId,
  }) async {
    try {
      await _client.from('notifications').insert({
        'user_id': userId,
        'company_id': companyId,
        'type': type,
        'title': title,
        'message': message,
        'reference_id': referenceId,
        'read': false,
        'created_at': DateTime.now().toIso8601String(),
      });
      return true;
    } catch (e) {
      print('Erro ao criar notificação: $e');
      return false;
    }
  }
  
  // Buscar notificações do usuário
  static Future<List<AppNotification>> getUserNotifications(int userId) async {
    try {
      final response = await _client
          .from('notifications')
          .select('*')
          .eq('user_id', userId)
          .order('created_at', ascending: false)
          .limit(50);
      
      return (response as List)
          .map((n) => AppNotification.fromJson(n))
          .toList();
    } catch (e) {
      print('Erro ao buscar notificações: $e');
      return [];
    }
  }
  
  // Marcar notificação como lida
  static Future<bool> markNotificationAsRead(int notificationId) async {
    try {
      await _client
          .from('notifications')
          .update({'read': true})
          .eq('id', notificationId);
      return true;
    } catch (e) {
      print('Erro ao marcar notificação como lida: $e');
      return false;
    }
  }
  
  // Upload de foto
  static Future<String?> uploadTaskPhoto(
    int taskId,
    String filePath,
    List<int> fileBytes,
  ) async {
    try {
      final fileName = 'task_${taskId}_${DateTime.now().millisecondsSinceEpoch}.jpg';
      final originalName = filePath.split('/').last;
      final fileSize = fileBytes.length;

      print('Upload: iniciando para task $taskId, arquivo $fileName, ${fileSize} bytes');

      await _client.storage
          .from('task-photos')
          .uploadBinary(
            fileName,
            Uint8List.fromList(fileBytes),
            fileOptions: const FileOptions(contentType: 'image/jpeg'),
          );

      print('Upload: storage OK');

      final photoUrl = _client.storage
          .from('task-photos')
          .getPublicUrl(fileName);

      print('Upload: URL gerada $photoUrl');

      await _client.from('assignment_photos').insert({
        'assignment_id': taskId,
        'file_path': fileName,
        'photo_url': photoUrl,
        'photo_path': fileName,
        'original_name': originalName,
        'file_size': fileSize,
        'uploaded_at': DateTime.now().toIso8601String(),
      });

      print('Upload: registro no banco OK');

      return photoUrl;
    } catch (e) {
      print('ERRO upload foto: $e');
      return null;
    }
  }
  
  // Chat - Enviar mensagem
  static Future<bool> sendChatMessage(
    int taskAssignmentId,
    int senderId,
    String senderName,
    String message,
  ) async {
    try {
      await _client.from('chat_messages').insert({
        'task_assignment_id': taskAssignmentId,
        'sender_id': senderId,
        'sender_name': senderName,
        'message': message,
        'is_read': false,
        'created_at': DateTime.now().toIso8601String(),
      });
      return true;
    } catch (e) {
      print('Erro ao enviar mensagem: $e');
      return false;
    }
  }
  
  // Chat - Buscar mensagens
  static Future<List<ChatMessage>> getChatMessages(int taskAssignmentId) async {
    try {
      final response = await _client
          .from('chat_messages')
          .select('*')
          .eq('task_assignment_id', taskAssignmentId)
          .order('created_at', ascending: true);
      
      return (response as List)
          .map((m) => ChatMessage.fromJson(m))
          .toList();
    } catch (e) {
      print('Erro ao buscar mensagens: $e');
      return [];
    }
  }
  
  // ─── Materiais ────────────────────────────────────────────────────────────

  /// Salva lista de materiais de uma tarefa (deleta os antigos e insere novos)
  static Future<bool> saveTaskMaterials(
    int assignmentId,
    int userId,
    List<TaskMaterial> materials,
  ) async {
    try {
      // Remove materiais anteriores desta execução
      await _client
          .from('task_materials')
          .delete()
          .eq('assignment_id', assignmentId)
          .eq('user_id', userId);

      if (materials.isEmpty) return true;

      final rows = materials
          .map((m) => {
                'assignment_id': assignmentId,
                'user_id': userId,
                'material_name': m.materialName,
                'quantity': m.quantity,
                'unit': m.unit,
                'created_at': DateTime.now().toIso8601String(),
              })
          .toList();

      await _client.from('task_materials').insert(rows);
      return true;
    } catch (e) {
      print('Erro ao salvar materiais: $e');
      return false;
    }
  }

  /// Busca materiais de uma tarefa específica
  static Future<List<TaskMaterial>> getTaskMaterials(int assignmentId) async {
    try {
      final response = await _client
          .from('task_materials')
          .select('*')
          .eq('assignment_id', assignmentId)
          .order('created_at', ascending: true);

      return (response as List)
          .map((m) => TaskMaterial.fromJson(m))
          .toList();
    } catch (e) {
      print('Erro ao buscar materiais: $e');
      return [];
    }
  }

  /// Retorna resumo de materiais do usuário no período (em dias)
  static Future<List<MaterialSummary>> getUserMaterialsSummary(
    int userId, {
    int periodDays = 30,
  }) async {
    try {
      final since = DateTime.now()
          .subtract(Duration(days: periodDays))
          .toIso8601String();

      final response = await _client
          .from('task_materials')
          .select('material_name, unit, quantity')
          .eq('user_id', userId)
          .gte('created_at', since);

      // Agrupa client-side
      final Map<String, Map<String, dynamic>> grouped = {};
      for (final row in response as List) {
        final name = row['material_name'] as String;
        final qty = (row['quantity'] as num).toDouble();
        final unit = row['unit'] as String? ?? 'un';
        if (grouped.containsKey(name)) {
          grouped[name]!['quantity'] =
              (grouped[name]!['quantity'] as double) + qty;
          grouped[name]!['count'] =
              (grouped[name]!['count'] as int) + 1;
        } else {
          grouped[name] = {
            'quantity': qty,
            'unit': unit,
            'count': 1,
          };
        }
      }

      return grouped.entries
          .map((e) => MaterialSummary(
                materialName: e.key,
                unit: e.value['unit'] as String,
                totalQuantity: e.value['quantity'] as double,
                timesUsed: e.value['count'] as int,
              ))
          .toList()
        ..sort((a, b) => b.totalQuantity.compareTo(a.totalQuantity));
    } catch (e) {
      print('Erro ao buscar resumo de materiais: $e');
      return [];
    }
  }

  // Subscription para real-time
  static RealtimeChannel subscribeToTaskUpdates(
    int userId,
    void Function(TaskAssignment) onUpdate,
  ) {
    return _client
        .channel('task_updates_$userId')
        .onPostgresChanges(
          event: PostgresChangeEvent.all,
          schema: 'public',
          table: 'task_assignments',
          filter: PostgresChangeFilter(
            type: PostgresChangeFilterType.eq,
            column: 'assigned_to',
            value: userId,
          ),
          callback: (payload) {
            final newRecord = payload.newRecord;
            if (newRecord != null) {
              onUpdate(TaskAssignment.fromJson(newRecord));
            }
          },
        )
        .subscribe();
  }
}
