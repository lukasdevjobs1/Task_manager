import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/task_assignment.dart';
import '../services/supabase_service.dart';
import '../services/offline_service.dart';

class TaskProvider with ChangeNotifier {
  List<TaskAssignment> _tasks = [];
  bool _isLoading = false;
  String? _errorMessage;
  RealtimeChannel? _subscription;
  
  List<TaskAssignment> get tasks => _tasks;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  
  // Estatísticas
  int get totalTasks => _tasks.length;
  int get pendingTasks => _tasks.where((t) => t.isPending).length;
  int get inProgressTasks => _tasks.where((t) => t.isInProgress).length;
  int get completedTasks => _tasks.where((t) => t.isCompleted).length;
  int get overdueTasks => _tasks.where((t) => t.isOverdue).length;
  
  // Filtrar tarefas
  List<TaskAssignment> getTasksByStatus(String status) {
    return _tasks.where((t) => t.status == status).toList();
  }
  
  List<TaskAssignment> get activeTasks {
    return _tasks.where((t) => !t.isCompleted).toList();
  }
  
  List<TaskAssignment> get completedTasksList {
    return _tasks.where((t) => t.isCompleted).toList();
  }
  
  // Carregar tarefas
  Future<void> loadTasks(int userId, {bool forceRefresh = false}) async {
    // Se já tem tarefas e não é forçado, não recarregar
    if (_tasks.isNotEmpty && !forceRefresh) return;
    
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    
    try {
      // Verificar se está online
      final isOnline = await OfflineService.isOnline();
      
      if (isOnline) {
        // Buscar do servidor
        _tasks = await SupabaseService.getUserTasks(userId);
        
        // Cachear para uso offline
        await OfflineService.cacheTasks(_tasks);
      } else {
        // Usar cache offline
        _tasks = OfflineService.getCachedTasks();
      }
      
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _errorMessage = 'Erro ao carregar tarefas: $e';
      _isLoading = false;
      
      // Tentar usar cache em caso de erro
      _tasks = OfflineService.getCachedTasks();
      notifyListeners();
    }
  }
  
  // Atualizar status da tarefa
  Future<bool> updateTaskStatus(
    int taskId,
    String newStatus, {
    String? observations,
  }) async {
    try {
      final isOnline = await OfflineService.isOnline();
      
      if (isOnline) {
        // Atualizar no servidor
        final success = await SupabaseService.updateTaskStatus(
          taskId,
          newStatus,
          observations: observations,
        );
        
        if (success) {
          // Atualizar localmente
          final taskIndex = _tasks.indexWhere((t) => t.id == taskId);
          if (taskIndex != -1) {
            final task = await SupabaseService.getTaskById(taskId);
            if (task != null) {
              _tasks[taskIndex] = task;
              notifyListeners();
            }
          }
        }
        
        return success;
      } else {
        // Modo offline - cachear atualização
        await OfflineService.cachePendingUpdate(
          taskId: taskId,
          status: newStatus,
          observations: observations,
        );
        
        // Atualizar localmente
        final taskIndex = _tasks.indexWhere((t) => t.id == taskId);
        if (taskIndex != -1) {
          // Criar cópia atualizada (simplificado)
          _tasks[taskIndex] = TaskAssignment(
            id: _tasks[taskIndex].id,
            companyId: _tasks[taskIndex].companyId,
            assignedBy: _tasks[taskIndex].assignedBy,
            assignedTo: _tasks[taskIndex].assignedTo,
            title: _tasks[taskIndex].title,
            description: _tasks[taskIndex].description,
            address: _tasks[taskIndex].address,
            latitude: _tasks[taskIndex].latitude,
            longitude: _tasks[taskIndex].longitude,
            status: newStatus,
            priority: _tasks[taskIndex].priority,
            dueDate: _tasks[taskIndex].dueDate,
            observations: observations ?? _tasks[taskIndex].observations,
            createdAt: _tasks[taskIndex].createdAt,
            updatedAt: DateTime.now(),
          );
          notifyListeners();
        }
        
        return true;
      }
    } catch (e) {
      print('Erro ao atualizar status: $e');
      return false;
    }
  }
  
  // Sincronizar atualizações pendentes
  Future<int> syncPendingUpdates(int userId) async {
    final syncCount = await OfflineService.syncPendingUpdates();
    if (syncCount > 0) {
      // Recarregar tarefas após sincronização
      await loadTasks(userId, forceRefresh: true);
    }
    return syncCount;
  }
  
  // Obter tarefa por ID
  TaskAssignment? getTaskById(int taskId) {
    try {
      return _tasks.firstWhere((t) => t.id == taskId);
    } catch (e) {
      return null;
    }
  }
  
  // Subscribe para atualizações em tempo real
  void subscribeToUpdates(int userId) {
    _subscription = SupabaseService.subscribeToTaskUpdates(
      userId,
      (updatedTask) {
        final taskIndex = _tasks.indexWhere((t) => t.id == updatedTask.id);
        if (taskIndex != -1) {
          _tasks[taskIndex] = updatedTask;
        } else {
          _tasks.insert(0, updatedTask);
        }
        notifyListeners();
      },
    );
  }
  
  // Unsubscribe
  void unsubscribeFromUpdates() {
    _subscription?.unsubscribe();
    _subscription = null;
  }
  
  @override
  void dispose() {
    unsubscribeFromUpdates();
    super.dispose();
  }
}
