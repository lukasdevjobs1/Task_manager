import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';
import '../providers/task_provider.dart';
import '../providers/notification_provider.dart';
import '../providers/offline_provider.dart';
import '../config/theme.dart';
import '../widgets/task_card.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final taskProvider = Provider.of<TaskProvider>(context, listen: false);
    final notificationProvider =
        Provider.of<NotificationProvider>(context, listen: false);
    final offlineProvider =
        Provider.of<OfflineProvider>(context, listen: false);

    if (authProvider.user != null) {
      await offlineProvider.checkConnectivity();
      await taskProvider.loadTasks(authProvider.user!.id);
      await notificationProvider.loadNotifications(authProvider.user!.id);
      taskProvider.subscribeToUpdates(authProvider.user!.id);
      if (offlineProvider.isOnline && offlineProvider.hasPendingUpdates) {
        await taskProvider.syncPendingUpdates(authProvider.user!.id);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final taskProvider = Provider.of<TaskProvider>(context);
    final notificationProvider = Provider.of<NotificationProvider>(context);
    final offlineProvider = Provider.of<OfflineProvider>(context);

    final user = authProvider.user;
    final firstName = user?.fullName.split(' ').first ?? 'Técnico';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Início'),
        actions: [
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
                    constraints:
                        const BoxConstraints(minWidth: 18, minHeight: 18),
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
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildWelcomeHeader(
                  context, firstName, taskProvider, offlineProvider),
              _buildStatsSection(context, taskProvider),
              if (!taskProvider.isLoading)
                _buildRecentTasksSection(context, taskProvider),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeHeader(
    BuildContext context,
    String firstName,
    TaskProvider taskProvider,
    OfflineProvider offlineProvider,
  ) {
    final hour = DateTime.now().hour;
    final greeting =
        hour < 12 ? 'Bom dia' : hour < 18 ? 'Boa tarde' : 'Boa noite';
    final activeCount =
        taskProvider.pendingTasks + taskProvider.inProgressTasks;

    return Container(
      width: double.infinity,
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppTheme.primaryColor,
            Color(0xFF1557B0),
          ],
        ),
      ),
      padding: const EdgeInsets.fromLTRB(20, 24, 20, 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!offlineProvider.isOnline)
            Container(
              margin: const EdgeInsets.only(bottom: 14),
              padding:
                  const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: AppTheme.warningColor.withValues(alpha: 0.25),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppTheme.warningColor),
              ),
              child: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.wifi_off, size: 14, color: AppTheme.warningColor),
                  SizedBox(width: 6),
                  Text(
                    'Modo Offline',
                    style: TextStyle(
                        color: AppTheme.warningColor, fontSize: 12),
                  ),
                ],
              ),
            ),
          Text(
            '$greeting, $firstName!',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 26,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            activeCount == 0
                ? 'Tudo em dia. Bom trabalho!'
                : 'Você tem $activeCount tarefa${activeCount > 1 ? 's' : ''} ativa${activeCount > 1 ? 's' : ''}',
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.85),
              fontSize: 15,
            ),
          ),
          if (offlineProvider.hasPendingUpdates) ...[
            const SizedBox(height: 10),
            Row(
              children: [
                const Icon(Icons.sync_problem,
                    size: 14, color: Colors.white70),
                const SizedBox(width: 6),
                Text(
                  '${offlineProvider.pendingUpdates} sincronização(ões) pendente(s)',
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildStatsSection(
      BuildContext context, TaskProvider taskProvider) {
    final total = taskProvider.totalTasks;
    final completed = taskProvider.completedTasks;
    final pending = taskProvider.pendingTasks;
    final inProgress = taskProvider.inProgressTasks;
    final progress = total > 0 ? completed / total : 0.0;
    final percent = (progress * 100).round();

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 20, 16, 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Resumo', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildStatCard(
                  context,
                  'Pendentes',
                  pending,
                  AppTheme.pendingColor,
                  Icons.schedule,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _buildStatCard(
                  context,
                  'Em Andamento',
                  inProgress,
                  AppTheme.inProgressColor,
                  Icons.hourglass_empty,
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _buildStatCard(
                  context,
                  'Concluídas',
                  completed,
                  AppTheme.completedColor,
                  Icons.check_circle_outline,
                ),
              ),
            ],
          ),
          if (total > 0) ...[
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Taxa de conclusão',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                Text(
                  '$percent%',
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.completedColor,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: progress,
                backgroundColor:
                    AppTheme.completedColor.withValues(alpha: 0.15),
                valueColor: const AlwaysStoppedAnimation<Color>(
                    AppTheme.completedColor),
                minHeight: 8,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildStatCard(
    BuildContext context,
    String title,
    int count,
    Color color,
    IconData icon,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 22),
          const SizedBox(height: 6),
          Text(
            '$count',
            style: TextStyle(
                fontSize: 22, fontWeight: FontWeight.bold, color: color),
          ),
          const SizedBox(height: 2),
          Text(
            title,
            style: TextStyle(
                fontSize: 11, color: color, fontWeight: FontWeight.w500),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  Widget _buildRecentTasksSection(
      BuildContext context, TaskProvider taskProvider) {
    final activeTasks = List.from(taskProvider.activeTasks)
      ..sort((a, b) {
        if (a.isOverdue && !b.isOverdue) return -1;
        if (!a.isOverdue && b.isOverdue) return 1;
        return 0;
      });

    if (activeTasks.isEmpty) {
      return Padding(
        padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Tarefas Ativas',
                style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 40),
            Center(
              child: Column(
                children: [
                  Icon(Icons.task_alt,
                      size: 56, color: AppTheme.completedColor),
                  const SizedBox(height: 12),
                  Text(
                    'Nenhuma tarefa ativa no momento',
                    style: TextStyle(color: AppTheme.textSecondary),
                  ),
                ],
              ),
            ),
          ],
        ),
      );
    }

    final displayTasks = activeTasks.take(3).toList();

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Tarefas Ativas',
                  style: Theme.of(context).textTheme.titleLarge),
              TextButton(
                onPressed: () => context.go('/tasks'),
                child: const Text('Ver todas'),
              ),
            ],
          ),
          const SizedBox(height: 4),
          ...displayTasks.map(
            (task) => TaskCard(
              task: task,
              onTap: () => context.push('/task/${task.id}'),
            ),
          ),
        ],
      ),
    );
  }
}
