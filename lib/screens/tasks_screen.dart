import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';
import '../providers/task_provider.dart';
import '../providers/offline_provider.dart';
import '../config/theme.dart';
import '../widgets/task_card.dart';

class TasksScreen extends StatefulWidget {
  const TasksScreen({super.key});

  @override
  State<TasksScreen> createState() => _TasksScreenState();
}

class _TasksScreenState extends State<TasksScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadData();
  }

  Future<void> _loadData() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final taskProvider = Provider.of<TaskProvider>(context, listen: false);
    final offlineProvider = Provider.of<OfflineProvider>(context, listen: false);

    if (authProvider.user != null) {
      await offlineProvider.checkConnectivity();
      await taskProvider.loadTasks(authProvider.user!.id);
      if (offlineProvider.isOnline && offlineProvider.hasPendingUpdates) {
        await taskProvider.syncPendingUpdates(authProvider.user!.id);
      }
    }
  }

  Future<void> _refreshData() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final taskProvider = Provider.of<TaskProvider>(context, listen: false);
    if (authProvider.user != null) {
      await taskProvider.loadTasks(authProvider.user!.id, forceRefresh: true);
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final taskProvider = Provider.of<TaskProvider>(context);
    final offlineProvider = Provider.of<OfflineProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Minhas Tarefas'),
            if (!offlineProvider.isOnline)
              Text(
                'Modo Offline',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppTheme.warningColor,
                    ),
              ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Atualizar',
            onPressed: _refreshData,
          ),
        ],
        bottom: PreferredSize(
          preferredSize:
              Size.fromHeight(offlineProvider.hasPendingUpdates ? 96 : 48),
          child: Column(
            children: [
              if (offlineProvider.hasPendingUpdates)
                Container(
                  width: double.infinity,
                  padding:
                      const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  color: AppTheme.warningColor.withValues(alpha: 0.2),
                  child: Row(
                    children: [
                      const Icon(Icons.sync_problem,
                          size: 16, color: AppTheme.warningColor),
                      const SizedBox(width: 8),
                      Text(
                        '${offlineProvider.pendingUpdates} atualização(ões) pendente(s)',
                        style: const TextStyle(
                            fontSize: 12, color: AppTheme.warningColor),
                      ),
                    ],
                  ),
                ),
              TabBar(
                controller: _tabController,
                labelColor: AppTheme.primaryColor,
                unselectedLabelColor: AppTheme.textSecondary,
                indicatorColor: AppTheme.primaryColor,
                tabs: const [
                  Tab(text: 'Todas'),
                  Tab(text: 'Pendentes'),
                  Tab(text: 'Em Andamento'),
                  Tab(text: 'Concluídas'),
                ],
              ),
            ],
          ),
        ),
      ),
      body: taskProvider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _refreshData,
              child: TabBarView(
                controller: _tabController,
                children: [
                  _buildTaskList(taskProvider.tasks),
                  _buildTaskList(taskProvider.getTasksByStatus('pending')),
                  _buildTaskList(
                      taskProvider.getTasksByStatus('em_andamento')),
                  _buildTaskList(taskProvider.completedTasksList),
                ],
              ),
            ),
    );
  }

  Widget _buildTaskList(List tasks) {
    if (tasks.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.assignment_outlined,
                size: 64, color: AppTheme.textDisabled),
            const SizedBox(height: 16),
            Text(
              'Nenhuma tarefa encontrada',
              style: TextStyle(fontSize: 16, color: AppTheme.textSecondary),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: tasks.length,
      itemBuilder: (context, index) {
        return TaskCard(
          task: tasks[index],
          onTap: () => context.push('/task/${tasks[index].id}'),
        );
      },
    );
  }
}
