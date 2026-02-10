// Adicionar função para registrar token push
export const registerPushToken = async (userId, token) => {
  try {
    const { data, error } = await supabase
      .from("users")
      .update({ push_token: token })
      .eq("id", userId)
      .select();

    if (error) {
      throw error;
    }

    return data[0];
  } catch (error) {
    console.error("Erro ao registrar token push:", error);
    throw error;
  }
};

const API_BASE_URL = "https://tarefasprovedor.streamlit.app/admin";

import { supabase } from "../config/supabase";

export const getMyAssignments = async (userId) => {
  try {
    console.log("Buscando tarefas para usuário:", userId);

    const { data, error } = await supabase
      .from("task_assignments")
      .select(
        `
        *,
        assigned_by_user:users!assigned_by(full_name),
        photos:assignment_photos(*)
      `
      )
      .eq("assigned_to", userId)
      .order("created_at", { ascending: false });

    if (error) {
      console.error("Erro Supabase ao buscar tarefas:", error);
      throw new Error(`Erro no banco: ${error.message}`);
    }

    console.log("Tarefas encontradas:", data?.length || 0);
    return data || [];
  } catch (error) {
    console.error("Erro ao buscar tarefas:", error);
    throw error;
  }
};

export const getAssignmentDetail = async (assignmentId) => {
  try {
    const { data, error } = await supabase
      .from("task_assignments")
      .select(
        `
        *,
        assigned_by_user:assigned_by(full_name),
        photos:assignment_photos(*)
      `
      )
      .eq("id", assignmentId)
      .single();

    if (error) {
      throw error;
    }

    return data;
  } catch (error) {
    console.error("Erro ao buscar detalhes da tarefa:", error);
    throw error;
  }
};

export const updateAssignmentMaterials = async (assignmentId, materials) => {
  try {
    const { data, error } = await supabase
      .from("task_assignments")
      .update({
        materials: materials,
        updated_at: new Date().toISOString(),
      })
      .eq("id", assignmentId)
      .select();

    if (error) {
      console.error("Erro Supabase ao atualizar materiais:", error);
      throw new Error(`Erro no banco: ${error.message}`);
    }

    if (!data || data.length === 0) {
      throw new Error("Tarefa não encontrada");
    }

    return data[0];
  } catch (error) {
    console.error("Erro ao atualizar materiais:", error);
    throw error;
  }
};

export const updateAssignmentStatus = async (
  assignmentId,
  status,
  observations = null
) => {
  try {
    // Mapear status do app para API
    const statusMap = {
      pending: "pendente",
      in_progress: "em_andamento",
      completed: "concluida",
    };

    const apiStatus = statusMap[status] || status;

    const updateData = {
      status: apiStatus,
      updated_at: new Date().toISOString(),
    };

    if (apiStatus === "em_andamento") {
      updateData.started_at = new Date().toISOString();
    } else if (apiStatus === "concluida") {
      updateData.completed_at = new Date().toISOString();
    }

    if (observations) {
      updateData.notes = observations;
    }

    console.log("Tentando atualizar tarefa:", { assignmentId, updateData });

    const { data, error } = await supabase
      .from("task_assignments")
      .update(updateData)
      .eq("id", assignmentId)
      .select();

    console.log("Resposta Supabase:", { data, error });

    if (error) {
      console.error("Erro Supabase:", error);
      throw new Error(`Erro no banco: ${error.message}`);
    }

    if (!data || data.length === 0) {
      throw new Error("Tarefa não encontrada");
    }

    return data[0];
  } catch (error) {
    console.error("Erro ao atualizar status da tarefa:", error);
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
      const fileName = `task_${assignmentId}_${Date.now()}_${Math.random()
        .toString(36)
        .substr(2, 9)}.jpg`;

      // Converter URI para blob para upload no Supabase
      const response = await fetch(photo.uri);
      const blob = await response.blob();

      const { data: uploadData, error: uploadError } = await supabase.storage
        .from("task-photos")
        .upload(fileName, blob, {
          contentType: photo.type || "image/jpeg",
          upsert: false,
        });

      if (uploadError) {
        console.error("Erro no upload:", uploadError);
        throw new Error(`Erro no upload: ${uploadError.message}`);
      }

      // Obter URL pública
      const { data: urlData } = supabase.storage
        .from("task-photos")
        .getPublicUrl(fileName);

      // Salvar no banco
      const { data, error } = await supabase
        .from("assignment_photos")
        .insert({
          assignment_id: assignmentId,
          photo_url: urlData.publicUrl,
          photo_path: fileName,
          original_name: photo.fileName || fileName,
          uploaded_at: new Date().toISOString(),
        })
        .select();

      if (error) {
        console.error("Erro ao salvar foto no banco:", error);
        throw new Error(`Erro ao salvar foto: ${error.message}`);
      }

      if (data && data.length > 0) {
        uploadedPhotos.push(data[0]);
      }
    }

    return uploadedPhotos;
  } catch (error) {
    console.error("Erro ao fazer upload das fotos:", error);
    throw error;
  }
};

export const getPhotoPublicUrl = (filePath) => {
  if (!filePath) return null;
  const { data } = supabase.storage.from("task-photos").getPublicUrl(filePath);
  return data.publicUrl;
};

export const uploadTaskPhoto = async (taskId, photoUri, description = "") => {
  return uploadAssignmentPhotos(taskId, [
    { uri: photoUri, fileName: `photo_${Date.now()}.jpg` },
  ]);
};
