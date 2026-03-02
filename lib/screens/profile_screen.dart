import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';
import '../providers/task_provider.dart';
import '../providers/theme_provider.dart';
import '../models/user.dart';
import '../models/task_material.dart';
import '../services/supabase_service.dart';
import '../config/theme.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final taskProvider = Provider.of<TaskProvider>(context);
    final themeProvider = Provider.of<ThemeProvider>(context);
    final user = authProvider.user;

    final total = taskProvider.totalTasks;
    final completed = taskProvider.completedTasks;
    final overdue = taskProvider.overdueTasks;
    final completionRate =
        total > 0 ? ((completed / total) * 100).round() : 0;

    // Concluídas neste mês
    final now = DateTime.now();
    final completedThisMonth = taskProvider.completedTasksList.where((t) {
      final date = t.updatedAt ?? t.createdAt;
      return date.year == now.year && date.month == now.month;
    }).length;

    return Scaffold(
      appBar: AppBar(title: const Text('Perfil')),
      body: ListView(
        children: [
          // Header com gradiente
          _buildProfileHeader(context, user),

          const SizedBox(height: 8),

          // Seção Desempenho
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
            child: Text(
              'Meu Desempenho',
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
          const SizedBox(height: 12),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                Expanded(
                  child: _buildMetricCard(
                    context,
                    label: 'Este mês',
                    value: '$completedThisMonth',
                    subtitle: 'concluídas',
                    icon: Icons.calendar_today,
                    color: AppTheme.primaryColor,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _buildMetricCard(
                    context,
                    label: 'Taxa',
                    value: '$completionRate%',
                    subtitle: 'de conclusão',
                    icon: Icons.pie_chart_outline,
                    color: AppTheme.completedColor,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _buildMetricCard(
                    context,
                    label: 'Em atraso',
                    value: '$overdue',
                    subtitle: 'tarefas',
                    icon: Icons.warning_amber_outlined,
                    color: overdue > 0
                        ? AppTheme.errorColor
                        : AppTheme.textSecondary,
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // Materiais do mês
          if (user != null)
            FutureBuilder<List<MaterialSummary>>(
              future: SupabaseService.getUserMaterialsSummary(user.id,
                  periodDays: 30),
              builder: (context, snapshot) {
                if (!snapshot.hasData || snapshot.data!.isEmpty) {
                  return const SizedBox.shrink();
                }
                final materials = snapshot.data!;
                final totalItems = materials.fold<double>(
                    0, (sum, m) => sum + m.totalQuantity);
                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Materiais este mês',
                              style:
                                  Theme.of(context).textTheme.titleMedium),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: AppTheme.primaryColor
                                  .withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              '${totalItems % 1 == 0 ? totalItems.toInt() : totalItems.toStringAsFixed(1)} itens',
                              style: const TextStyle(
                                fontSize: 12,
                                color: AppTheme.primaryColor,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: materials.take(8).map((m) {
                          final qty = m.totalQuantity == m.totalQuantity.truncateToDouble()
                              ? '${m.totalQuantity.toInt()}'
                              : m.totalQuantity.toStringAsFixed(1);
                          return Chip(
                            avatar: const Icon(Icons.build_outlined,
                                size: 14),
                            label: Text(
                              '${m.materialName} · $qty ${m.unit}',
                              style: const TextStyle(fontSize: 12),
                            ),
                            backgroundColor:
                                AppTheme.primaryColor.withValues(alpha: 0.07),
                          );
                        }).toList(),
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],
                );
              },
            ),

          const Divider(indent: 16, endIndent: 16),

          // Informações do usuário
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
            child: Text(
              'Informações',
              style: Theme.of(context).textTheme.titleMedium,
            ),
          ),
          ListTile(
            leading: const Icon(Icons.badge_outlined),
            title: const Text('Usuário'),
            subtitle: Text('@${user?.username ?? 'N/A'}'),
          ),
          ListTile(
            leading: const Icon(Icons.business_outlined),
            title: const Text('Empresa'),
            subtitle: Text(user?.companyName ?? 'N/A'),
          ),
          ListTile(
            leading: const Icon(Icons.group_outlined),
            title: const Text('Equipe'),
            subtitle:
                Text(user?.team.toUpperCase() ?? 'N/A'),
          ),

          const Divider(indent: 16, endIndent: 16),

          // Configurações
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
            child: Text(
              'Configurações',
              style: Theme.of(context).textTheme.titleMedium,
            ),
          ),
          ListTile(
            leading: const Icon(Icons.dark_mode_outlined),
            title: const Text('Tema Escuro'),
            trailing: Switch(
              value: themeProvider.themeMode == ThemeMode.dark,
              onChanged: (value) {
                themeProvider.setThemeMode(
                    value ? ThemeMode.dark : ThemeMode.light);
              },
            ),
          ),

          const Divider(indent: 16, endIndent: 16),

          // Ações
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
            child: Text(
              'Histórico',
              style: Theme.of(context).textTheme.titleMedium,
            ),
          ),
          ListTile(
            leading: const Icon(Icons.history),
            title: const Text('Tarefas Concluídas'),
            subtitle: Text('$completed tarefas no total'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => context.push('/completed-tasks'),
          ),

          const Divider(indent: 16, endIndent: 16),

          // Logout
          ListTile(
            leading:
                const Icon(Icons.logout, color: AppTheme.errorColor),
            title: const Text(
              'Sair',
              style: TextStyle(color: AppTheme.errorColor),
            ),
            onTap: () async {
              final confirmed = await showDialog<bool>(
                context: context,
                builder: (ctx) => AlertDialog(
                  title: const Text('Sair do app'),
                  content: const Text('Deseja realmente sair?'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(ctx, false),
                      child: const Text('Cancelar'),
                    ),
                    TextButton(
                      onPressed: () => Navigator.pop(ctx, true),
                      child: const Text(
                        'Sair',
                        style: TextStyle(color: AppTheme.errorColor),
                      ),
                    ),
                  ],
                ),
              );
              if (confirmed == true && context.mounted) {
                await authProvider.logout();
                if (context.mounted) context.go('/login');
              }
            },
          ),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildProfileHeader(BuildContext context, User? user) {
    final initials = user?.fullName != null && user!.fullName.isNotEmpty
        ? user.fullName
            .trim()
            .split(' ')
            .where((w) => w.isNotEmpty)
            .take(2)
            .map((w) => w[0].toUpperCase())
            .join()
        : 'U';

    return Container(
      width: double.infinity,
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [AppTheme.primaryColor, Color(0xFF1557B0)],
        ),
      ),
      padding: const EdgeInsets.fromLTRB(24, 28, 24, 32),
      child: Column(
        children: [
          CircleAvatar(
            radius: 44,
            backgroundColor: Colors.white.withValues(alpha: 0.25),
            child: Text(
              initials,
              style: const TextStyle(
                fontSize: 30,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ),
          const SizedBox(height: 14),
          Text(
            user?.fullName ?? '',
            style: const TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            '@${user?.username ?? ''}',
            style: TextStyle(
              fontSize: 14,
              color: Colors.white.withValues(alpha: 0.8),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricCard(
    BuildContext context, {
    required String label,
    required String value,
    required String subtitle,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 10),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.25)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(height: 6),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: TextStyle(
              fontSize: 10,
              color: color,
              fontWeight: FontWeight.w600,
            ),
            textAlign: TextAlign.center,
          ),
          Text(
            subtitle,
            style: TextStyle(
              fontSize: 10,
              color: color.withValues(alpha: 0.75),
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
