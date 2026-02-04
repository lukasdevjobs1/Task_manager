// Adicionar função para registrar token push
export const registerPushToken = async (userId, token) => {
  try {
    const { data, error } = await supabase
      .from('users')
      .update({ push_token: token })
      .eq('id', userId)
      .select();

    if (error) {
      throw error;
    }

    return data[0];
  } catch (error) {
    console.error('Erro ao registrar token push:', error);
    throw error;
  }
};

const API_BASE_URL = 'http://192.168.1.4:5000';

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

export const getAssignmentDetail = async (assignmentId) => {
  try {
    const { data, error } = await supabase
      .from('task_assignments')
      .select(`
        *,
        assigned_by_user:assigned_by(full_name),
        photos:assignment_photos(*)
      `)
      .eq('id', assignmentId)
      .single();

    if (error) {
      throw error;
    }

    return data;
  } catch (error) {
    console.error('Erro ao buscar detalhes da tarefa:', error);
    throw error;
  }
};

export const updateAssignmentStatus = async (assignmentId, status, observations = null) => {
  try {
    // Mapear status do app para API
    const statusMap = {
      'pending': 'pendente',
      'in_progress': 'em_andamento', 
      'completed': 'concluida'
    };
    
    const apiStatus = statusMap[status] || status;
    
    const updateData = { 
      status: apiStatus,
      updated_at: new Date().toISOString()
    };

    if (apiStatus === 'em_andamento') {
      updateData.started_at = new Date().toISOString();
    } else if (apiStatus === 'concluida') {
      updateData.completed_at = new Date().toISOString();
    }

    if (observations) {
      updateData.notes = observations;
    }

    const { data, error } = await supabase
      .from('task_assignments')
      .update(updateData)
      .eq('id', assignmentId)
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

export const updateTaskStatus = async (taskId, status, notes = null) => {
  return updateAssignmentStatus(taskId, status, notes);
};

export const uploadAssignmentPhotos = async (assignmentId, photos) => {
  try {
    const uploadedPhotos = [];
    
    for (const photo of photos) {
      const fileName = `task_${assignmentId}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}.jpg`;
      
      // Criar FormData para upload
      const formData = new FormData();
      formData.append('file', {
        uri: photo.uri,
        type: photo.type || 'image/jpeg',
        name: photo.fileName || fileName,
      });

      const { data: uploadData, error: uploadError } = await supabase.storage
        .from('task-photos')
        .upload(fileName, formData);

      if (uploadError) {
        console.error('Erro no upload:', uploadError);
        continue;
      }

      // Obter URL pública
      const { data: urlData } = supabase.storage
        .from('task-photos')
        .getPublicUrl(fileName);

      // Salvar no banco
      const { data, error } = await supabase
        .from('assignment_photos')
        .insert({
          assignment_id: assignmentId,
          photo_url: urlData.publicUrl,
          photo_path: fileName,
          original_name: photo.fileName || fileName,
        })
        .select();

      if (!error && data) {
        uploadedPhotos.push(data[0]);
      }
    }
    
    return uploadedPhotos;
  } catch (error) {
    console.error('Erro ao fazer upload das fotos:', error);
    throw error;
  }
};

export const getPhotoPublicUrl = (filePath) => {
  if (!filePath) return null;
  const { data } = supabase.storage
    .from('task-photos')
    .getPublicUrl(filePath);
  return data.publicUrl;
};

export const uploadTaskPhoto = async (taskId, photoUri, description = '') => {
  return uploadAssignmentPhotos(taskId, [{ uri: photoUri, fileName: `photo_${Date.now()}.jpg` }]);
};