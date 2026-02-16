import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../providers/task_provider.dart';
import '../widgets/task_card.dart';

class CompletedTasksScreen extends StatelessWidget {
  const CompletedTasksScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final taskProvider = Provider.of<TaskProvider>(context);
    final completedTasks = taskProvider.completedTasksList;

    return Scaffold(
      appBar: AppBar(title: const Text('Tarefas Concluídas')),
      body: completedTasks.isEmpty
          ? const Center(child: Text('Nenhuma tarefa concluída'))
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: completedTasks.length,
              itemBuilder: (context, index) {
                return TaskCard(
                  task: completedTasks[index],
                  onTap: () => context.push('/task/${completedTasks[index].id}'),
                );
              },
            ),
    );
  }
}
