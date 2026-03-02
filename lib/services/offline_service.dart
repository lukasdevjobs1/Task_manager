import 'package:hive/hive.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../models/task_assignment.dart';
import 'supabase_service.dart';

class OfflineService {
  static final Box _tasksBox = Hive.box('tasks_cache');
  static final Connectivity _connectivity = Connectivity();

  // Verificar conectividade
  static Future<bool> isOnline() async {
    try {
      final result = await _connectivity.checkConnectivity();
      return result != ConnectivityResult.none;
    } catch (e) {
      return false;
    }
  }

  // Cachear tarefas
  static Future<void> cacheTasks(List<TaskAssignment> tasks) async {
    try {
      final tasksJson = tasks.map((t) => t.toJson()).toList();
      await _tasksBox.put('tasks', tasksJson);
      await _tasksBox.put('last_sync', DateTime.now().toIso8601String());
    } catch (e) {
      print('Erro ao cachear tarefas: $e');
    }
  }

  // Obter tarefas do cache
  static List<TaskAssignment> getCachedTasks() {
    try {
      final tasksJson = _tasksBox.get('tasks') as List?;
      if (tasksJson == null) return [];

      final result = <TaskAssignment>[];
      for (final t in tasksJson) {
        try {
          result.add(TaskAssignment.fromJson(Map<String, dynamic>.from(t as Map)));
        } catch (e) {
          print('Cache: ignorando tarefa com formato inválido: $e');
        }
      }
      return result;
    } catch (e) {
      print('Erro ao obter tarefas do cache: $e');
      // Cache corrompido — limpa para recomeçar do zero
      _tasksBox.delete('tasks');
      return [];
    }
  }

  // Obter última sincronização
  static DateTime? getLastSync() {
    try {
      final lastSync = _tasksBox.get('last_sync') as String?;
      return lastSync != null ? DateTime.parse(lastSync) : null;
    } catch (e) {
      return null;
    }
  }

  // Cachear atualizações pendentes (para sincronizar depois)
  static Future<void> cachePendingUpdate({
    required int taskId,
    required String status,
    String? observations,
  }) async {
    try {
      final pendingUpdates =
          _tasksBox.get('pending_updates', defaultValue: []) as List;

      pendingUpdates.add({
        'task_id': taskId,
        'status': status,
        'observations': observations,
        'timestamp': DateTime.now().toIso8601String(),
      });

      await _tasksBox.put('pending_updates', pendingUpdates);
    } catch (e) {
      print('Erro ao cachear atualização: $e');
    }
  }

  // Sincronizar atualizações pendentes
  static Future<int> syncPendingUpdates() async {
    try {
      final pendingUpdates =
          _tasksBox.get('pending_updates', defaultValue: []) as List;
      int syncCount = 0;

      for (var update in List.from(pendingUpdates)) {
        final success = await SupabaseService.updateTaskStatus(
          update['task_id'] as int,
          update['status'] as String,
          observations: update['observations'] as String?,
        );

        if (success) {
          pendingUpdates.remove(update);
          syncCount++;
        }
      }

      await _tasksBox.put('pending_updates', pendingUpdates);
      return syncCount;
    } catch (e) {
      print('Erro ao sincronizar: $e');
      return 0;
    }
  }

  // Verificar se há atualizações pendentes
  static int getPendingUpdatesCount() {
    try {
      final pendingUpdates =
          _tasksBox.get('pending_updates', defaultValue: []) as List;
      return pendingUpdates.length;
    } catch (e) {
      return 0;
    }
  }

  // Limpar cache
  static Future<void> clearCache() async {
    await _tasksBox.clear();
  }
}
