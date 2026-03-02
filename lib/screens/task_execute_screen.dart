import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import '../providers/task_provider.dart';
import '../providers/auth_provider.dart';
import '../models/task_material.dart';
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
  final ImagePicker _picker = ImagePicker();
  final List<XFile> _photos = [];
  final List<TaskMaterial> _materials = [];
  String _selectedStatus = 'em_andamento';
  bool _isUploading = false;
  String _uploadStatus = '';

  @override
  void dispose() {
    _observationsController.dispose();
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

  Future<void> _uploadPhotos() async {
    if (_photos.isEmpty) return;

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

    if (!mounted) return;

    if (failed > 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('$uploaded fotos enviadas, $failed falharam'),
          backgroundColor: Colors.orange,
        ),
      );
    }
  }

  // ─── Materiais ────────────────────────────────────────────────────────────

  void _showAddMaterialSheet() {
    final nameController = TextEditingController();
    final quantityController = TextEditingController(text: '1');
    final unitController = TextEditingController(text: 'un');
    final formKey = GlobalKey<FormState>();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(
          left: 20,
          right: 20,
          top: 24,
          bottom: MediaQuery.of(ctx).viewInsets.bottom + 24,
        ),
        child: Form(
          key: formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Adicionar Material',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 20),

              // Nome do material
              TextFormField(
                controller: nameController,
                autofocus: true,
                textCapitalization: TextCapitalization.sentences,
                decoration: const InputDecoration(
                  labelText: 'Nome do material *',
                  hintText: 'Ex: Cabo UTP cat6, Conector RJ45...',
                  prefixIcon: Icon(Icons.build_outlined),
                ),
                validator: (v) =>
                    (v == null || v.trim().isEmpty) ? 'Informe o material' : null,
              ),
              const SizedBox(height: 16),

              // Quantidade e unidade na mesma linha
              Row(
                children: [
                  // Quantidade
                  SizedBox(
                    width: 110,
                    child: TextFormField(
                      controller: quantityController,
                      keyboardType: const TextInputType.numberWithOptions(
                          decimal: true),
                      decoration: const InputDecoration(
                        labelText: 'Qtd *',
                      ),
                      validator: (v) {
                        if (v == null || v.trim().isEmpty) return 'Informe';
                        final n = double.tryParse(v.replaceAll(',', '.'));
                        if (n == null || n <= 0) return 'Inválido';
                        return null;
                      },
                    ),
                  ),
                  const SizedBox(width: 12),

                  // Unidade (texto livre)
                  Expanded(
                    child: TextFormField(
                      controller: unitController,
                      textCapitalization: TextCapitalization.none,
                      decoration: const InputDecoration(
                        labelText: 'Unidade',
                        hintText: 'un, m, m², kg...',
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Botões
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.pop(ctx),
                      child: const Text('Cancelar'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        if (!formKey.currentState!.validate()) return;
                        final qty = double.parse(
                            quantityController.text.replaceAll(',', '.'));
                        final unit = unitController.text.trim().isEmpty
                            ? 'un'
                            : unitController.text.trim();
                        setState(() {
                          _materials.add(TaskMaterial(
                            assignmentId: widget.taskId,
                            userId: 0, // preenchido no submit
                            materialName: nameController.text.trim(),
                            quantity: qty,
                            unit: unit,
                            createdAt: DateTime.now(),
                          ));
                        });
                        Navigator.pop(ctx);
                      },
                      child: const Text('Adicionar'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ─── Submit ───────────────────────────────────────────────────────────────

  Future<void> _submitExecution() async {
    setState(() => _isUploading = true);

    // Upload de fotos
    await _uploadPhotos();

    if (!mounted) return;

    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    final taskProvider = Provider.of<TaskProvider>(context, listen: false);
    final userId = authProvider.user?.id ?? 0;

    // Salvar materiais (com userId correto)
    if (_materials.isNotEmpty) {
      setState(() => _uploadStatus = 'Salvando materiais...');
      final materialsWithUser = _materials
          .map((m) => TaskMaterial(
                assignmentId: m.assignmentId,
                userId: userId,
                materialName: m.materialName,
                quantity: m.quantity,
                unit: m.unit,
                createdAt: m.createdAt,
              ))
          .toList();

      await SupabaseService.saveTaskMaterials(
          widget.taskId, userId, materialsWithUser);
    }

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
            Text('Status',
                style: Theme.of(context).textTheme.titleMedium),
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
              onChanged: (value) =>
                  setState(() => _selectedStatus = value!),
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

            // ── Materiais ─────────────────────────────────────────────────
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Materiais Utilizados',
                    style: Theme.of(context).textTheme.titleMedium),
                TextButton.icon(
                  onPressed: _showAddMaterialSheet,
                  icon: const Icon(Icons.add, size: 18),
                  label: const Text('Adicionar'),
                ),
              ],
            ),
            const SizedBox(height: 4),

            if (_materials.isEmpty)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.grey.shade200),
                ),
                child: Row(
                  children: [
                    Icon(Icons.build_outlined,
                        size: 20, color: AppTheme.textDisabled),
                    const SizedBox(width: 10),
                    Text(
                      'Nenhum material adicionado',
                      style: TextStyle(color: AppTheme.textSecondary),
                    ),
                  ],
                ),
              )
            else
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _materials.length,
                separatorBuilder: (_, __) => const Divider(height: 1),
                itemBuilder: (context, index) {
                  final m = _materials[index];
                  return ListTile(
                    contentPadding:
                        const EdgeInsets.symmetric(horizontal: 0),
                    leading: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color:
                            AppTheme.primaryColor.withValues(alpha: 0.1),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.build_outlined,
                          size: 16, color: AppTheme.primaryColor),
                    ),
                    title: Text(m.materialName,
                        style: const TextStyle(fontWeight: FontWeight.w500)),
                    subtitle: Text(m.displayQuantity,
                        style: TextStyle(color: AppTheme.textSecondary)),
                    trailing: IconButton(
                      icon: const Icon(Icons.delete_outline,
                          color: AppTheme.errorColor),
                      onPressed: () =>
                          setState(() => _materials.removeAt(index)),
                    ),
                  );
                },
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
                      style:
                          TextStyle(color: AppTheme.textSecondary)),
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
