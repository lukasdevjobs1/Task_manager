import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import '../providers/task_provider.dart';
import '../services/supabase_service.dart';
import '../config/theme.dart';

class TaskExecuteScreen extends StatefulWidget {
  final int taskId;

  const TaskExecuteScreen({super.key, required this.taskId});

  @override
  State<TaskExecuteScreen> createState() => _TaskExecuteScreenState();
}

class _TaskExecuteScreenState extends State<TaskExecuteScreen> {
  final _observationsController = TextEditingController();
  final _abertCxEmendaController = TextEditingController(text: '0');
  final _abertCtoController = TextEditingController(text: '0');
  final _abertRozetaController = TextEditingController(text: '0');
  final _qtdCtoController = TextEditingController(text: '0');
  final _qtdCxEmendaController = TextEditingController(text: '0');
  final _fibraLancadaController = TextEditingController(text: '0');
  final ImagePicker _picker = ImagePicker();
  final List<XFile> _photos = [];
  String _selectedStatus = 'em_andamento';
  bool _isUploading = false;
  String _uploadStatus = '';

  @override
  void dispose() {
    _observationsController.dispose();
    _abertCxEmendaController.dispose();
    _abertCtoController.dispose();
    _abertRozetaController.dispose();
    _qtdCtoController.dispose();
    _qtdCxEmendaController.dispose();
    _fibraLancadaController.dispose();
    super.dispose();
  }

  // ─── Fotos ────────────────────────────────────────────────────────────────

  Future<void> _takePicture() async {
    final photo = await _picker.pickImage(source: ImageSource.camera);
    if (photo != null) setState(() => _photos.add(photo));
  }

  Future<void> _pickFromGallery() async {
    final photos = await _picker.pickMultiImage();
    setState(() => _photos.addAll(photos));
  }

  Future<bool> _uploadPhotos() async {
    if (_photos.isEmpty) return true;

    setState(() {
      _isUploading = true;
      _uploadStatus = 'Enviando fotos...';
    });

    int uploaded = 0;
    int failed = 0;

    for (int i = 0; i < _photos.length; i++) {
      setState(() {
        _uploadStatus = 'Enviando foto ${i + 1} de ${_photos.length}...';
      });

      try {
        final file = File(_photos[i].path);
        final bytes = await file.readAsBytes();
        final result = await SupabaseService.uploadTaskPhoto(
          widget.taskId,
          _photos[i].path,
          bytes.toList(),
        );
        if (result != null) {
          uploaded++;
        } else {
          failed++;
        }
      } catch (e) {
        failed++;
      }
    }

    setState(() {
      _isUploading = false;
      _uploadStatus = '';
    });

    if (!mounted) return false;

    if (failed > 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('$uploaded fotos enviadas, $failed falharam'),
          backgroundColor: Colors.orange,
        ),
      );
      return false;
    }

    return true;
  }

  // ─── Helper campo numérico ────────────────────────────────────────────────

  Widget _buildNumericField(String label, TextEditingController controller) {
    return TextFormField(
      controller: controller,
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
      decoration: InputDecoration(
        labelText: label,
        isDense: true,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      ),
    );
  }

  // ─── Submit ───────────────────────────────────────────────────────────────

  Future<void> _submitExecution() async {
    setState(() => _isUploading = true);

    // Upload de fotos
    final photosOk = await _uploadPhotos();

    if (!mounted) return;

    // Se houver fotos e alguma falhou, perguntar se quer continuar
    if (!photosOk && _selectedStatus == 'concluida') {
      final continuar = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('Falha no envio de fotos'),
          content: const Text(
            'Algumas fotos não foram enviadas.\n\nDeseja finalizar a tarefa mesmo assim?',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Cancelar'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.pop(ctx, true),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.orange),
              child: const Text('Finalizar mesmo assim'),
            ),
          ],
        ),
      );

      if (continuar != true) {
        setState(() => _isUploading = false);
        return;
      }
    }

    if (!mounted) return;

    final taskProvider = Provider.of<TaskProvider>(context, listen: false);

    // Salvar dados técnicos ISP
    setState(() => _uploadStatus = 'Salvando dados técnicos...');
    await SupabaseService.updateTaskTechnicalData(
      widget.taskId,
      aberturaFechamentoCxEmenda:
          int.tryParse(_abertCxEmendaController.text) ?? 0,
      aberturaFechamentoCto: int.tryParse(_abertCtoController.text) ?? 0,
      aberturaFechamentoRozeta:
          int.tryParse(_abertRozetaController.text) ?? 0,
      quantidadeCto: int.tryParse(_qtdCtoController.text) ?? 0,
      quantidadeCxEmenda: int.tryParse(_qtdCxEmendaController.text) ?? 0,
      fibraLancada:
          double.tryParse(_fibraLancadaController.text.replaceAll(',', '.')) ??
              0,
    );

    setState(() {
      _isUploading = false;
      _uploadStatus = '';
    });

    if (!mounted) return;

    final success = await taskProvider.updateTaskStatus(
      widget.taskId,
      _selectedStatus,
      observations: _observationsController.text,
    );

    setState(() => _isUploading = false);

    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Tarefa atualizada com sucesso!')),
      );
      context.pop();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Erro ao atualizar tarefa'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Executar Tarefa')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // ── Status ────────────────────────────────────────────────────
            Text('Status', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _selectedStatus,
              decoration: const InputDecoration(
                prefixIcon: Icon(Icons.flag_outlined),
              ),
              items: const [
                DropdownMenuItem(
                  value: 'em_andamento',
                  child: Text('Em Andamento'),
                ),
                DropdownMenuItem(
                  value: 'concluida',
                  child: Text('Concluída'),
                ),
              ],
              onChanged: (value) => setState(() => _selectedStatus = value!),
            ),
            const SizedBox(height: 24),

            // ── Fotos ─────────────────────────────────────────────────────
            Text('Fotos', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _takePicture,
                    icon: const Icon(Icons.camera_alt),
                    label: const Text('Câmera'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _pickFromGallery,
                    icon: const Icon(Icons.photo_library),
                    label: const Text('Galeria'),
                  ),
                ),
              ],
            ),
            if (_photos.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: _photos.asMap().entries.map((entry) {
                  final index = entry.key;
                  final photo = entry.value;
                  return Stack(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.file(
                          File(photo.path),
                          width: 80,
                          height: 80,
                          fit: BoxFit.cover,
                        ),
                      ),
                      Positioned(
                        top: 0,
                        right: 0,
                        child: GestureDetector(
                          onTap: () =>
                              setState(() => _photos.removeAt(index)),
                          child: Container(
                            decoration: const BoxDecoration(
                              color: Colors.red,
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(Icons.close,
                                size: 18, color: Colors.white),
                          ),
                        ),
                      ),
                    ],
                  );
                }).toList(),
              ),
            ],

            const SizedBox(height: 24),

            // ── Dados Técnicos da OS ───────────────────────────────────────
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.primaryColor.withValues(alpha: 0.05),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                    color: AppTheme.primaryColor.withValues(alpha: 0.3)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.cable_outlined,
                          color: AppTheme.primaryColor, size: 20),
                      const SizedBox(width: 8),
                      Text(
                        'Dados Técnicos da OS',
                        style: Theme.of(context)
                            .textTheme
                            .titleMedium
                            ?.copyWith(color: AppTheme.primaryColor),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Table(
                    columnWidths: const {
                      0: FlexColumnWidth(),
                      1: FlexColumnWidth(),
                    },
                    children: [
                      TableRow(children: [
                        Padding(
                          padding: const EdgeInsets.only(right: 6, bottom: 12),
                          child: _buildNumericField(
                              'Abert./Fech. Cx Emenda',
                              _abertCxEmendaController),
                        ),
                        Padding(
                          padding: const EdgeInsets.only(left: 6, bottom: 12),
                          child: _buildNumericField(
                              'Abert./Fech. CTO', _abertCtoController),
                        ),
                      ]),
                      TableRow(children: [
                        Padding(
                          padding: const EdgeInsets.only(right: 6, bottom: 12),
                          child: _buildNumericField(
                              'Abert./Fech. Rozeta', _abertRozetaController),
                        ),
                        Padding(
                          padding: const EdgeInsets.only(left: 6, bottom: 12),
                          child: _buildNumericField(
                              'Qtd CTO', _qtdCtoController),
                        ),
                      ]),
                      TableRow(children: [
                        Padding(
                          padding: const EdgeInsets.only(right: 6),
                          child: _buildNumericField(
                              'Qtd Cx de Emenda', _qtdCxEmendaController),
                        ),
                        Padding(
                          padding: const EdgeInsets.only(left: 6),
                          child: _buildNumericField(
                              'Fibra Lançada (m)', _fibraLancadaController),
                        ),
                      ]),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // ── Observações ───────────────────────────────────────────────
            Text('Observações',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            TextField(
              controller: _observationsController,
              decoration: const InputDecoration(
                hintText: 'Adicione observações sobre a execução...',
                prefixIcon: Icon(Icons.notes_outlined),
              ),
              maxLines: 4,
            ),

            const SizedBox(height: 32),

            // Status de upload
            if (_isUploading && _uploadStatus.isNotEmpty) ...[
              Row(
                children: [
                  const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  const SizedBox(width: 8),
                  Text(_uploadStatus,
                      style: TextStyle(color: AppTheme.textSecondary)),
                ],
              ),
              const SizedBox(height: 16),
            ],

            // Botão salvar
            SizedBox(
              height: 50,
              child: ElevatedButton(
                onPressed: _isUploading ? null : _submitExecution,
                child: _isUploading
                    ? const SizedBox(
                        width: 24,
                        height: 24,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Text('Salvar Execução',
                        style: TextStyle(fontSize: 16)),
              ),
            ),

            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}
