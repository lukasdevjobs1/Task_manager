import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import '../providers/task_provider.dart';
import '../providers/auth_provider.dart';
import '../models/task_assignment.dart';
import '../models/task_material.dart';
import '../services/supabase_service.dart';
import '../config/theme.dart';

enum _ReportPeriod { week, month, quarter }

class ReportsScreen extends StatefulWidget {
  const ReportsScreen({super.key});

  @override
  State<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends State<ReportsScreen> {
  _ReportPeriod _selectedPeriod = _ReportPeriod.month;
  int? _touchedPieIndex;

  int get _periodDays {
    switch (_selectedPeriod) {
      case _ReportPeriod.week:
        return 7;
      case _ReportPeriod.month:
        return 30;
      case _ReportPeriod.quarter:
        return 90;
    }
  }

  String get _periodLabel {
    switch (_selectedPeriod) {
      case _ReportPeriod.week:
        return '7 dias';
      case _ReportPeriod.month:
        return '30 dias';
      case _ReportPeriod.quarter:
        return '90 dias';
    }
  }

  List<TaskAssignment> _filterByPeriod(List<TaskAssignment> tasks) {
    final cutoff =
        DateTime.now().subtract(Duration(days: _periodDays));
    return tasks
        .where((t) => (t.updatedAt ?? t.createdAt).isAfter(cutoff))
        .toList();
  }

  // Retorna contagem de concluídas por dia da semana (últimos 7 dias)
  List<int> _completedByDayOfWeek(List<TaskAssignment> completed) {
    final counts = List.filled(7, 0);
    final now = DateTime.now();
    for (final task in completed) {
      final date = task.updatedAt ?? task.createdAt;
      final diff = now.difference(date).inDays;
      if (diff < 7) {
        // weekday: 1=Mon..7=Sun, index 0=Mon..6=Sun
        final idx = (date.weekday - 1) % 7;
        counts[idx]++;
      }
    }
    return counts;
  }

  @override
  Widget build(BuildContext context) {
    final taskProvider = Provider.of<TaskProvider>(context);
    final authProvider = Provider.of<AuthProvider>(context);
    final allTasks = taskProvider.tasks;
    final periodTasks = _filterByPeriod(allTasks);
    final periodCompleted =
        periodTasks.where((t) => t.isCompleted).toList();
    final periodPending =
        periodTasks.where((t) => t.isPending).toList();
    final periodInProgress =
        periodTasks.where((t) => t.isInProgress).toList();

    final barData = _completedByDayOfWeek(taskProvider.completedTasksList);
    final maxBar = barData.reduce((a, b) => a > b ? a : b).toDouble();

    return Scaffold(
      appBar: AppBar(title: const Text('Relatórios')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Seletor de período
            _buildPeriodSelector(),
            const SizedBox(height: 20),

            // Cards de resumo do período
            Text(
              'Resumo — $_periodLabel',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildStatCard(
                    'Total',
                    periodTasks.length,
                    AppTheme.primaryColor,
                    Icons.assignment_outlined,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _buildStatCard(
                    'Concluídas',
                    periodCompleted.length,
                    AppTheme.completedColor,
                    Icons.check_circle_outline,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _buildStatCard(
                    'Pendentes',
                    periodPending.length,
                    AppTheme.pendingColor,
                    Icons.schedule,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _buildStatCard(
                    'Andamento',
                    periodInProgress.length,
                    AppTheme.inProgressColor,
                    Icons.hourglass_empty,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 28),

            // Gráfico de distribuição (Pizza)
            Text(
              'Distribuição de Status',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),
            _buildPieChart(
              pendingCount: taskProvider.pendingTasks,
              inProgressCount: taskProvider.inProgressTasks,
              completedCount: taskProvider.completedTasks,
            ),

            const SizedBox(height: 28),

            // Gráfico de barras — concluídas por dia da semana
            Text(
              'Concluídas por dia (últimos 7 dias)',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),
            _buildBarChart(barData, maxBar),

            const SizedBox(height: 28),

            // Top materiais utilizados
            if (authProvider.user != null)
              _buildMaterialsSection(context, authProvider.user!.id),

            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildPeriodSelector() {
    return Row(
      children: [
        _buildPeriodChip('7 dias', _ReportPeriod.week),
        const SizedBox(width: 8),
        _buildPeriodChip('30 dias', _ReportPeriod.month),
        const SizedBox(width: 8),
        _buildPeriodChip('90 dias', _ReportPeriod.quarter),
      ],
    );
  }

  Widget _buildPeriodChip(String label, _ReportPeriod value) {
    final isSelected = _selectedPeriod == value;
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      selectedColor: AppTheme.primaryColor,
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : AppTheme.textSecondary,
        fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
        fontSize: 13,
      ),
      onSelected: (_) => setState(() => _selectedPeriod = value),
    );
  }

  Widget _buildStatCard(
      String title, int value, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 18),
          const SizedBox(height: 4),
          Text(
            '$value',
            style: TextStyle(
                fontSize: 20, fontWeight: FontWeight.bold, color: color),
          ),
          const SizedBox(height: 2),
          Text(
            title,
            style: TextStyle(
                color: color, fontWeight: FontWeight.w500, fontSize: 10),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildPieChart({
    required int pendingCount,
    required int inProgressCount,
    required int completedCount,
  }) {
    final total = pendingCount + inProgressCount + completedCount;
    if (total == 0) {
      return const SizedBox(
        height: 120,
        child: Center(child: Text('Sem dados para exibir')),
      );
    }

    final sections = [
      _PieSection(
          label: 'Pendentes',
          count: pendingCount,
          color: AppTheme.pendingColor,
          index: 0),
      _PieSection(
          label: 'Andamento',
          count: inProgressCount,
          color: AppTheme.inProgressColor,
          index: 1),
      _PieSection(
          label: 'Concluídas',
          count: completedCount,
          color: AppTheme.completedColor,
          index: 2),
    ].where((s) => s.count > 0).toList();

    return Row(
      children: [
        // Pizza
        SizedBox(
          height: 160,
          width: 160,
          child: PieChart(
            PieChartData(
              pieTouchData: PieTouchData(
                touchCallback: (event, response) {
                  setState(() {
                    if (!event.isInterestedForInteractions ||
                        response == null ||
                        response.touchedSection == null) {
                      _touchedPieIndex = null;
                    } else {
                      _touchedPieIndex =
                          response.touchedSection!.touchedSectionIndex;
                    }
                  });
                },
              ),
              sections: sections.map((s) {
                final isTouched = _touchedPieIndex == s.index;
                final radius = isTouched ? 70.0 : 60.0;
                final pct = ((s.count / total) * 100).round();
                return PieChartSectionData(
                  value: s.count.toDouble(),
                  title: '$pct%',
                  color: s.color,
                  radius: radius,
                  titleStyle: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                );
              }).toList(),
              centerSpaceRadius: 30,
            ),
          ),
        ),

        const SizedBox(width: 20),

        // Legenda
        Expanded(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: sections
                .map((s) => _buildLegendItem(s.label, s.count, total, s.color))
                .toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildLegendItem(
      String label, int count, int total, Color color) {
    final pct = total > 0 ? ((count / total) * 100).round() : 0;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              label,
              style: const TextStyle(fontSize: 13),
            ),
          ),
          Text(
            '$count ($pct%)',
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBarChart(List<int> data, double maxBar) {
    const days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];
    final maxY = maxBar < 1 ? 4.0 : maxBar + 1;

    return Container(
      height: 200,
      padding: const EdgeInsets.only(top: 8, right: 8),
      child: BarChart(
        BarChartData(
          maxY: maxY,
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            horizontalInterval: maxY > 4 ? (maxY / 4).ceilToDouble() : 1,
            getDrawingHorizontalLine: (value) => FlLine(
              color: Colors.grey.withValues(alpha: 0.15),
              strokeWidth: 1,
            ),
          ),
          borderData: FlBorderData(show: false),
          titlesData: FlTitlesData(
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 28,
                interval: maxY > 4 ? (maxY / 4).ceilToDouble() : 1,
                getTitlesWidget: (value, meta) => Text(
                  '${value.toInt()}',
                  style: TextStyle(
                      fontSize: 11, color: AppTheme.textSecondary),
                ),
              ),
            ),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (value, meta) => Padding(
                  padding: const EdgeInsets.only(top: 6),
                  child: Text(
                    days[value.toInt()],
                    style: TextStyle(
                        fontSize: 11, color: AppTheme.textSecondary),
                  ),
                ),
              ),
            ),
            rightTitles:
                const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles:
                const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          barGroups: List.generate(7, (i) {
            return BarChartGroupData(
              x: i,
              barRods: [
                BarChartRodData(
                  toY: data[i].toDouble(),
                  color: data[i] > 0
                      ? AppTheme.completedColor
                      : AppTheme.completedColor.withValues(alpha: 0.2),
                  width: 20,
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(6),
                    topRight: Radius.circular(6),
                  ),
                ),
              ],
            );
          }),
        ),
      ),
    );
  }

  Widget _buildMaterialsSection(BuildContext context, int userId) {
    return FutureBuilder<List<MaterialSummary>>(
      future: SupabaseService.getUserMaterialsSummary(
        userId,
        periodDays: _periodDays,
      ),
      builder: (context, snapshot) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Materiais Utilizados — $_periodLabel',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 12),
            if (!snapshot.hasData)
              const Center(
                  child: Padding(
                padding: EdgeInsets.all(16),
                child: CircularProgressIndicator(),
              ))
            else if (snapshot.data!.isEmpty)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.grey.shade50,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.grey.shade200),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.build_outlined,
                        color: AppTheme.textDisabled),
                    const SizedBox(width: 10),
                    Text(
                      'Nenhum material no período',
                      style:
                          TextStyle(color: AppTheme.textSecondary),
                    ),
                  ],
                ),
              )
            else
              _buildMaterialsList(context, snapshot.data!),
          ],
        );
      },
    );
  }

  Widget _buildMaterialsList(
      BuildContext context, List<MaterialSummary> materials) {
    // Calcula o total para a barra de progresso relativa
    final maxQty = materials.first.totalQuantity;

    return Column(
      children: materials.take(8).map((m) {
        final pct = maxQty > 0 ? m.totalQuantity / maxQty : 0.0;
        final qtyStr = m.totalQuantity == m.totalQuantity.truncateToDouble()
            ? '${m.totalQuantity.toInt()}'
            : m.totalQuantity.toStringAsFixed(1);

        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Row(
                      children: [
                        const Icon(Icons.build_outlined,
                            size: 14,
                            color: AppTheme.primaryColor),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            m.materialName,
                            style: const TextStyle(
                                fontWeight: FontWeight.w500,
                                fontSize: 14),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Text(
                    '$qtyStr ${m.unit}',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                      color: AppTheme.primaryColor,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '× ${m.timesUsed}',
                    style: TextStyle(
                        fontSize: 11,
                        color: AppTheme.textSecondary),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: pct,
                  backgroundColor:
                      AppTheme.primaryColor.withValues(alpha: 0.1),
                  valueColor: const AlwaysStoppedAnimation<Color>(
                      AppTheme.primaryColor),
                  minHeight: 6,
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}

class _PieSection {
  final String label;
  final int count;
  final Color color;
  final int index;

  const _PieSection({
    required this.label,
    required this.count,
    required this.color,
    required this.index,
  });
}
