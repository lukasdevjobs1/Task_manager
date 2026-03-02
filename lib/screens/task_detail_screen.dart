import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:url_launcher/url_launcher.dart';
import '../providers/task_provider.dart';
import '../config/theme.dart';

class TaskDetailScreen extends StatelessWidget {
  final int taskId;

  const TaskDetailScreen({super.key, required this.taskId});

  /// Abre o app de mapas nativo com a localização da tarefa.
  /// Prioridade: coordenadas GPS → endereço como fallback.
  Future<void> _openMaps(BuildContext context,
      {double? lat, double? lng, String? address, String? title}) async {
    Uri? uri;

    if (lat != null && lng != null) {
      // Coordenadas GPS disponíveis
      final label = Uri.encodeComponent(title ?? 'Tarefa');
      uri = Uri.parse('geo:$lat,$lng?q=$lat,$lng($label)');
    } else if (address != null && address.isNotEmpty) {
      // Fallback: busca pelo endereço
      final query = Uri.encodeComponent(address);
      uri = Uri.parse('https://maps.google.com/?q=$query');
    }

    if (uri == null) return;

    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      // Fallback universal via Google Maps web
      if (address != null && address.isNotEmpty) {
        final webUri =
            Uri.parse('https://www.google.com/maps/search/?q=${Uri.encodeComponent(address)}');
        if (await canLaunchUrl(webUri)) {
          await launchUrl(webUri, mode: LaunchMode.externalApplication);
          return;
        }
      }
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Não foi possível abrir o maps')),
        );
      }
    }
  }

  void _showFullImage(BuildContext context, String imageUrl) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        backgroundColor: Colors.transparent,
        child: Stack(
          children: [
            Center(
              child: InteractiveViewer(
                child: CachedNetworkImage(
                  imageUrl: imageUrl,
                  fit: BoxFit.contain,
                  placeholder: (context, url) =>
                      const CircularProgressIndicator(),
                  errorWidget: (context, url, error) => const Icon(
                    Icons.error,
                    color: Colors.white,
                    size: 48,
                  ),
                ),
              ),
            ),
            Positioned(
              top: 0,
              right: 0,
              child: IconButton(
                icon: const Icon(Icons.close, color: Colors.white, size: 30),
                onPressed: () => Navigator.of(context).pop(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final taskProvider = Provider.of<TaskProvider>(context);
    final task = taskProvider.getTaskById(taskId);

    if (task == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Detalhes da Tarefa')),
        body: const Center(child: Text('Tarefa não encontrada')),
      );
    }

    final hasLocation =
        task.latitude != null || (task.address != null && task.address!.isNotEmpty);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Detalhes da Tarefa'),
        actions: [
          IconButton(
            icon: const Icon(Icons.chat_outlined),
            onPressed: () =>
                context.push('/task/$taskId/chat?title=${task.title}'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Título e status
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Text(
                    task.title,
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                ),
                const SizedBox(width: 12),
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: AppTheme.getStatusColor(task.status)
                        .withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    task.statusDisplay,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.getStatusColor(task.status),
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // Empresa
            if (task.empresaNome != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: _buildInfoRow(
                  context,
                  icon: Icons.business_outlined,
                  color: AppTheme.textSecondary,
                  child: Text(
                    task.empresaNome!,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ),
              ),

            // Descrição
            if (task.description != null && task.description!.isNotEmpty) ...[
              Text(task.description!,
                  style: Theme.of(context).textTheme.bodyLarge),
              const SizedBox(height: 16),
            ],

            // Localização com botão de maps
            if (task.address != null && task.address!.isNotEmpty) ...[
              _buildInfoRow(
                context,
                icon: Icons.location_on_outlined,
                color: AppTheme.inProgressColor,
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        task.address!,
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 8),
            ],

            // Botão Abrir no Maps
            if (hasLocation) ...[
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () => _openMaps(
                    context,
                    lat: task.latitude,
                    lng: task.longitude,
                    address: task.address,
                    title: task.title,
                  ),
                  icon: const Icon(Icons.map_outlined),
                  label: const Text('Abrir no Maps'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: AppTheme.inProgressColor,
                    side: const BorderSide(color: AppTheme.inProgressColor),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],

            // Prioridade e vencimento
            Row(
              children: [
                Icon(
                  Icons.flag_outlined,
                  size: 16,
                  color: AppTheme.getPriorityColor(task.priority),
                ),
                const SizedBox(width: 6),
                Text(
                  task.priorityDisplay,
                  style: TextStyle(
                    fontSize: 13,
                    color: AppTheme.getPriorityColor(task.priority),
                    fontWeight: FontWeight.w500,
                  ),
                ),
                if (task.dueDate != null) ...[
                  const SizedBox(width: 20),
                  Icon(
                    task.isOverdue
                        ? Icons.warning_amber_rounded
                        : Icons.calendar_today_outlined,
                    size: 16,
                    color: task.isOverdue
                        ? AppTheme.errorColor
                        : AppTheme.textSecondary,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    'Vence: ${_formatDate(task.dueDate!)}',
                    style: TextStyle(
                      fontSize: 13,
                      color: task.isOverdue
                          ? AppTheme.errorColor
                          : AppTheme.textSecondary,
                    ),
                  ),
                ],
              ],
            ),

            const SizedBox(height: 20),
            const Divider(),
            const SizedBox(height: 12),

            // Fotos
            if (task.photos != null && task.photos!.isNotEmpty) ...[
              Text(
                'Fotos (${task.photos!.length})',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 10),
              SizedBox(
                height: 120,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: task.photos!.length,
                  itemBuilder: (context, index) {
                    final photo = task.photos![index];
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: GestureDetector(
                        onTap: () =>
                            _showFullImage(context, photo.photoUrl),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: CachedNetworkImage(
                            imageUrl: photo.photoUrl,
                            width: 120,
                            height: 120,
                            fit: BoxFit.cover,
                            placeholder: (context, url) => Container(
                              width: 120,
                              height: 120,
                              color: Colors.grey[300],
                              child: const Center(
                                child: CircularProgressIndicator(
                                    strokeWidth: 2),
                              ),
                            ),
                            errorWidget: (context, url, error) => Container(
                              width: 120,
                              height: 120,
                              color: Colors.grey[300],
                              child: const Icon(Icons.broken_image),
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 20),
              const Divider(),
              const SizedBox(height: 12),
            ],

            // Materiais utilizados
            if (task.materials != null && task.materials!.isNotEmpty) ...[
              Text(
                'Materiais utilizados',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 10),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: task.materials!.map((m) {
                  return Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryColor.withValues(alpha: 0.08),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                          color: AppTheme.primaryColor
                              .withValues(alpha: 0.3)),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.build_outlined,
                            size: 14, color: AppTheme.primaryColor),
                        const SizedBox(width: 6),
                        Text(
                          '${m.materialName} · ${m.displayQuantity}',
                          style: const TextStyle(
                            fontSize: 13,
                            color: AppTheme.primaryColor,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 20),
              const Divider(),
              const SizedBox(height: 12),
            ],

            // Observações
            if (task.observations != null &&
                task.observations!.isNotEmpty) ...[
              Text(
                'Observações',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.backgroundColor,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                      color: Colors.grey.shade300),
                ),
                child: Text(
                  task.observations!,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ),
              const SizedBox(height: 20),
            ],

            // Dados Técnicos ISP (somente leitura, aparece se algum campo > 0)
            Builder(builder: (context) {
              final hasTech =
                  (task.aberturaFechamentoCxEmenda ?? 0) > 0 ||
                  (task.aberturaFechamentoCto ?? 0) > 0 ||
                  (task.aberturaFechamentoRozeta ?? 0) > 0 ||
                  (task.quantidadeCto ?? 0) > 0 ||
                  (task.quantidadeCxEmenda ?? 0) > 0 ||
                  (task.fibraLancada ?? 0) > 0;
              if (!hasTech) return const SizedBox.shrink();
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Dados Técnicos',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 10),
                  if ((task.aberturaFechamentoCxEmenda ?? 0) > 0)
                    _buildInfoRow(context,
                        icon: Icons.cable_outlined,
                        color: AppTheme.textSecondary,
                        child: Text(
                            'Abert./Fech. Cx Emenda: ${task.aberturaFechamentoCxEmenda}')),
                  if ((task.aberturaFechamentoCto ?? 0) > 0)
                    _buildInfoRow(context,
                        icon: Icons.cable_outlined,
                        color: AppTheme.textSecondary,
                        child: Text(
                            'Abert./Fech. CTO: ${task.aberturaFechamentoCto}')),
                  if ((task.aberturaFechamentoRozeta ?? 0) > 0)
                    _buildInfoRow(context,
                        icon: Icons.cable_outlined,
                        color: AppTheme.textSecondary,
                        child: Text(
                            'Abert./Fech. Rozeta: ${task.aberturaFechamentoRozeta}')),
                  if ((task.quantidadeCto ?? 0) > 0)
                    _buildInfoRow(context,
                        icon: Icons.device_hub_outlined,
                        color: AppTheme.textSecondary,
                        child: Text('Qtd CTO: ${task.quantidadeCto}')),
                  if ((task.quantidadeCxEmenda ?? 0) > 0)
                    _buildInfoRow(context,
                        icon: Icons.device_hub_outlined,
                        color: AppTheme.textSecondary,
                        child:
                            Text('Qtd Cx de Emenda: ${task.quantidadeCxEmenda}')),
                  if ((task.fibraLancada ?? 0) > 0)
                    _buildInfoRow(context,
                        icon: Icons.straighten_outlined,
                        color: AppTheme.textSecondary,
                        child: Text(
                            'Fibra Lançada: ${task.fibraLancada!.toStringAsFixed(2)} m')),
                  const SizedBox(height: 20),
                  const Divider(),
                  const SizedBox(height: 12),
                ],
              );
            }),

            // Botão Executar (só para tarefas não concluídas)
            if (!task.isCompleted) ...[
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () =>
                      context.push('/task/$taskId/execute'),
                  icon: const Icon(Icons.play_arrow),
                  label: const Text('Executar Tarefa'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(BuildContext context,
      {required IconData icon,
      required Color color,
      required Widget child}) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 18, color: color),
        const SizedBox(width: 8),
        Expanded(child: child),
      ],
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year}';
  }
}
