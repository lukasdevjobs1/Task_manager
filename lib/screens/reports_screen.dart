import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../providers/task_provider.dart';
import '../config/theme.dart';

class ReportsScreen extends StatelessWidget {
  const ReportsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final taskProvider = Provider.of<TaskProvider>(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Relatórios e Estatísticas')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Resumo Geral', style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 16),

            // Cards de estatísticas
            Row(
              children: [
                Expanded(
                  child: _buildStatCard('Total', taskProvider.totalTasks, AppTheme.primaryColor),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildStatCard('Concluídas', taskProvider.completedTasks, AppTheme.completedColor),
                ),
              ],
            ),
            const SizedBox(height: 32),

            // Gráfico de pizza
            Text('Distribuição de Status', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: PieChart(
                PieChartData(
                  sections: [
                    PieChartSectionData(
                      value: taskProvider.pendingTasks.toDouble(),
                      title: '${taskProvider.pendingTasks}',
                      color: AppTheme.pendingColor,
                      radius: 60,
                    ),
                    PieChartSectionData(
                      value: taskProvider.inProgressTasks.toDouble(),
                      title: '${taskProvider.inProgressTasks}',
                      color: AppTheme.inProgressColor,
                      radius: 60,
                    ),
                    PieChartSectionData(
                      value: taskProvider.completedTasks.toDouble(),
                      title: '${taskProvider.completedTasks}',
                      color: AppTheme.completedColor,
                      radius: 60,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Legendas
            _buildLegendItem('Pendentes', AppTheme.pendingColor),
            _buildLegendItem('Em Andamento', AppTheme.inProgressColor),
            _buildLegendItem('Concluídas', AppTheme.completedColor),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, int value, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Text(
            '$value',
            style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: color),
          ),
          const SizedBox(height: 4),
          Text(title, style: TextStyle(color: color, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  Widget _buildLegendItem(String label, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Container(
            width: 16,
            height: 16,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
          const SizedBox(width: 8),
          Text(label),
        ],
      ),
    );
  }
}
