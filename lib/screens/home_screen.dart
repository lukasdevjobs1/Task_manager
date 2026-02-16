import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';
import '../providers/task_provider.dart';
import '../providers/notification_provider.dart';
import '../providers/offline_provider.dart';
import '../config/theme.dart';
import '../widgets/task_card.dart';
import '../widgets/stats_card.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String _selectedFilter = 'all';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadData();
  }

  Future<void> _loadData() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final taskProvider = Provider.of<TaskProvider>(context, listen: false);
    final notificationProvider = Provider.of<NotificationProvider>(context, listen: false);
    final offlineProvider = Provider.of<OfflineProvider>(context, listen: false);

    if (authProvider.user != null) {
      await offlineProvider.checkConnectivity();
      await taskProvider.loadTasks(authProvider.user!.id);
      await notificationProvider.loadNotifications(authProvider.user!.id);
      
      // Subscribe para updates em tempo real
      taskProvider.subscribeToUpdates(authProvider.user!.id);
      
      // Sincronizar pendências se online
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
    final authProvider = Provider.of<AuthProvider>(context);
    final taskProvider = Provider.of<TaskProvider>(context);
    final notificationProvider = Provider.of<NotificationProvider>(context);
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
          // Badge de notificações
          Stack(
            children: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined),
                onPressed: () => context.push('/notifications'),
              ),
              if (notificationProvider.unreadCount > 0)
                Positioned(
                  right: 8,
                  top: 8,
                  child: Container(
                    padding: const EdgeInsets.all(4),
                    decoration: const BoxDecoration(
                      color: AppTheme.errorColor,
                      shape: BoxShape.circle,
                    ),
                    constraints: const BoxConstraints(
                      minWidth: 18,
                      minHeight: 18,
                    ),
                    child: Text(
                      '${notificationProvider.unreadCount}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.person_outline),
            onPressed: () => context.push('/profile'),
          ),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(140),
          child: Column(
            children: [
              // Status de sincronização
              if (offlineProvider.hasPendingUpdates)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  color: AppTheme.warningColor.withOpacity(0.2),
                  child: Row(
                    children: [
                      Icon(Icons.sync_problem, size: 16, color: AppTheme.warningColor),
                      const SizedBox(width: 8),
                      Text(
                        '${offlineProvider.pendingUpdates} atualização(ões) pendente(s)',
                        style: TextStyle(
                          fontSize: 12,
                          color: AppTheme.warningColor,
                        ),
                      ),
                    ],
                  ),
                ),
              
              // Cards de estatísticas
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    Expanded(
                      child: StatsCard(
                        title: 'Pendentes',
                        count: taskProvider.pendingTasks,
                        color: AppTheme.pendingColor,
                        icon: Icons.schedule,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: StatsCard(
                        title: 'Em Andamento',
                        count: taskProvider.inProgressTasks,
                        color: AppTheme.inProgressColor,
                        icon: Icons.hourglass_empty,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: StatsCard(
                        title: 'Concluídas',
                        count: taskProvider.completedTasks,
                        color: AppTheme.completedColor,
                        icon: Icons.check_circle_outline,
                      ),
                    ),
                  ],
                ),
              ),
              
              // Tabs
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
                  _buildTaskList(taskProvider.getTasksByStatus('em_andamento')),
                  _buildTaskList(taskProvider.completedTasksList),
                ],
              ),
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/reports'),
        icon: const Icon(Icons.analytics_outlined),
        label: const Text('Relatórios'),
      ),
    );
  }

  Widget _buildTaskList(List tasks) {
    if (tasks.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.assignment_outlined,
              size: 64,
              color: AppTheme.textDisabled,
            ),
            const SizedBox(height: 16),
            Text(
              'Nenhuma tarefa encontrada',
              style: TextStyle(
                fontSize: 16,
                color: AppTheme.textSecondary,
              ),
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
