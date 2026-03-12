import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../providers/task_provider.dart';
import '../models/task_assignment.dart';
import '../config/theme.dart';
import '../widgets/task_card.dart';

enum _PeriodFilter { week, month, all }

class CompletedTasksScreen extends StatefulWidget {
  const CompletedTasksScreen({super.key});

  @override
  State<CompletedTasksScreen> createState() => _CompletedTasksScreenState();
}

class _CompletedTasksScreenState extends State<CompletedTasksScreen> {
  _PeriodFilter _selectedPeriod = _PeriodFilter.month;

  List<TaskAssignment> _filterByPeriod(List<TaskAssignment> tasks) {
    final now = DateTime.now();
    return tasks.where((task) {
      final date = task.updatedAt ?? task.createdAt;
      switch (_selectedPeriod) {
        case _PeriodFilter.week:
          return date.isAfter(now.subtract(const Duration(days: 7)));
        case _PeriodFilter.month:
          return date.isAfter(now.subtract(const Duration(days: 30)));
        case _PeriodFilter.all:
          return true;
      }
    }).toList()
      ..sort((a, b) {
        final dateA = a.updatedAt ?? a.createdAt;
        final dateB = b.updatedAt ?? b.createdAt;
        return dateB.compareTo(dateA);
      });
  }

  @override
  Widget build(BuildContext context) {
    final taskProvider = Provider.of<TaskProvider>(context);
    final filtered = _filterByPeriod(taskProvider.completedTasksList);

    return Scaffold(
      appBar: AppBar(title: const Text('Tarefas Concluídas')),
      body: Column(
        children: [
          // Filtros de período
          Container(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
            child: Row(
              children: [
                _buildFilterChip('Esta semana', _PeriodFilter.week),
                const SizedBox(width: 8),
                _buildFilterChip('Este mês', _PeriodFilter.month),
                const SizedBox(width: 8),
                _buildFilterChip('Tudo', _PeriodFilter.all),
              ],
            ),
          ),

          // Contador
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
            child: Row(
              children: [
                Text(
                  '${filtered.length} tarefa${filtered.length != 1 ? 's' : ''} concluída${filtered.length != 1 ? 's' : ''}',
                  style: TextStyle(
                    color: AppTheme.textSecondary,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),

          // Lista
          Expanded(
            child: filtered.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                    itemCount: filtered.length,
                    itemBuilder: (context, index) => TaskCard(
                      task: filtered[index],
                      onTap: () => context.push('/task/${filtered[index].id}'),
                    ),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String label, _PeriodFilter value) {
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

  Widget _buildEmptyState() {
    String message;
    switch (_selectedPeriod) {
      case _PeriodFilter.week:
        message = 'Nenhuma tarefa concluída\nnesta semana';
        break;
      case _PeriodFilter.month:
        message = 'Nenhuma tarefa concluída\nneste mês';
        break;
      case _PeriodFilter.all:
        message = 'Nenhuma tarefa concluída\nainda';
        break;
    }

    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.history, size: 64, color: AppTheme.textDisabled),
          const SizedBox(height: 16),
          Text(
            message,
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16, color: AppTheme.textSecondary),
          ),
        ],
      ),
    );
  }
}
