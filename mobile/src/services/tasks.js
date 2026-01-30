import { supabase } from '../config/supabase';

export const getMyTasks = async (userId) => {
  try {
    const { data, error } = await supabase
      .from('task_assignments')
      .select(`
        *,
        assigned_by_user:assigned_by(full_name),
        photos:assignment_photos(*)
      `)
      .eq('assigned_to', userId)
      .order('created_at', { ascending: false });

    if (error) {
      throw error;
    }

    return data || [];
  } catch (error) {
    console.error('Erro ao buscar tarefas:', error);
    throw error;
  }
};

export const updateTaskStatus = async (taskId, status, notes = null) => {
  try {
    const updateData = { 
      status,
      updated_at: new Date().toISOString()
    };

    if (status === 'em_andamento') {
      updateData.started_at = new Date().toISOString();
    } else if (status === 'concluida') {
      updateData.completed_at = new Date().toISOString();
    }

    if (notes) {
      updateData.notes = notes;
    }

    const { data, error } = await supabase
      .from('task_assignments')
      .update(updateData)
      .eq('id', taskId)
      .select();

    if (error) {
      throw error;
    }

    return data[0];
  } catch (error) {
    console.error('Erro ao atualizar status da tarefa:', error);
    throw error;
  }
};

export const uploadTaskPhoto = async (taskId, photoUri, description = '') => {
  try {
    // Upload da foto para o Supabase Storage
    const fileName = `task_${taskId}_${Date.now()}.jpg`;
    const formData = new FormData();
    formData.append('file', {
      uri: photoUri,
      type: 'image/jpeg',
      name: fileName,
    });

    const { data: uploadData, error: uploadError } = await supabase.storage
      .from('task-photos')
      .upload(fileName, formData);

    if (uploadError) {
      throw uploadError;
    }

    // Obter URL pública da foto
    const { data: urlData } = supabase.storage
      .from('task-photos')
      .getPublicUrl(fileName);

    // Salvar referência no banco
    const { data, error } = await supabase
      .from('assignment_photos')
      .insert({
        assignment_id: taskId,
        photo_url: urlData.publicUrl,
        photo_path: fileName,
        description: description,
      })
      .select();

    if (error) {
      throw error;
    }

    return data[0];
  } catch (error) {
    console.error('Erro ao fazer upload da foto:', error);
    throw error;
  }
};