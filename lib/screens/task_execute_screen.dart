import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import '../providers/task_provider.dart';
import '../providers/auth_provider.dart';
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
  List<XFile> _photos = [];
  String _selectedStatus = 'em_andamento';

  @override
  void dispose() {
    _observationsController.dispose();
    super.dispose();
  }

  Future<void> _takePicture() async {
    final photo = await _picker.pickImage(source: ImageSource.camera);
    if (photo != null) {
      setState(() => _photos.add(photo));
    }
  }

  Future<void> _pickFromGallery() async {
    final photos = await _picker.pickMultiImage();
    setState(() => _photos.addAll(photos));
  }

  Future<void> _submitExecution() async {
    final taskProvider = Provider.of<TaskProvider>(context, listen: false);
    
    final success = await taskProvider.updateTaskStatus(
      widget.taskId,
      _selectedStatus,
      observations: _observationsController.text,
    );

    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Tarefa atualizada com sucesso!')),
      );
      context.pop();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Erro ao atualizar tarefa'), backgroundColor: Colors.red),
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
            // Status
            const Text('Status:', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _selectedStatus,
              decoration: const InputDecoration(border: OutlineInputBorder()),
              items: const [
                DropdownMenuItem(value: 'em_andamento', child: Text('Em Andamento')),
                DropdownMenuItem(value: 'concluida', child: Text('Concluída')),
              ],
              onChanged: (value) => setState(() => _selectedStatus = value!),
            ),
            const SizedBox(height: 24),

            // Fotos
            const Text('Fotos:', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Row(
              children: [
                ElevatedButton.icon(
                  onPressed: _takePicture,
                  icon: const Icon(Icons.camera_alt),
                  label: const Text('Câmera'),
                ),
                const SizedBox(width: 8),
                OutlinedButton.icon(
                  onPressed: _pickFromGallery,
                  icon: const Icon(Icons.photo_library),
                  label: const Text('Galeria'),
                ),
              ],
            ),
            if (_photos.isNotEmpty) ...[
              const SizedBox(height: 16),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: _photos.map((photo) => Image.asset(photo.path, width: 80, height: 80, fit: BoxFit.cover)).toList(),
              ),
            ],
            const SizedBox(height: 24),

            // Observações
            const Text('Observações:', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            TextField(
              controller: _observationsController,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Adicione observações sobre a execução...',
              ),
              maxLines: 5,
            ),
            const SizedBox(height: 32),

            // Botão salvar
            SizedBox(
              height: 50,
              child: ElevatedButton(
                onPressed: _submitExecution,
                child: const Text('Salvar Execução', style: TextStyle(fontSize: 16)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
