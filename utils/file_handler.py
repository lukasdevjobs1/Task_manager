"""
Gerenciamento de upload e download de fotos.
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import UPLOAD_FOLDER, MAX_FILE_SIZE_BYTES, MAX_FILES_PER_TASK, ALLOWED_EXTENSIONS
from database.connection import SessionLocal
from database.models import TaskPhoto


def get_upload_folder() -> str:
    """Retorna o caminho absoluto da pasta de uploads."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_path = os.path.join(base_dir, UPLOAD_FOLDER)
    os.makedirs(upload_path, exist_ok=True)
    return upload_path


def allowed_file(filename: str) -> bool:
    """Verifica se o arquivo tem extensão permitida."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(original_name: str) -> str:
    """Gera um nome de arquivo único mantendo a extensão original."""
    ext = original_name.rsplit(".", 1)[1].lower() if "." in original_name else "jpg"
    unique_id = uuid.uuid4().hex[:12]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{unique_id}.{ext}"


def save_uploaded_files(
    uploaded_files: list, task_id: int
) -> tuple[bool, str, List[dict]]:
    """
    Salva os arquivos enviados no sistema de arquivos e registra no banco.

    Args:
        uploaded_files: Lista de arquivos do Streamlit file_uploader
        task_id: ID da tarefa associada

    Returns:
        (sucesso, mensagem, lista de fotos salvas)
    """
    if not uploaded_files:
        return True, "Nenhum arquivo para salvar.", []

    # Validações
    if len(uploaded_files) > MAX_FILES_PER_TASK:
        return (
            False,
            f"Máximo de {MAX_FILES_PER_TASK} fotos permitidas por tarefa.",
            [],
        )

    upload_folder = get_upload_folder()
    saved_photos = []
    session = SessionLocal()

    try:
        for file in uploaded_files:
            # Validar extensão
            if not allowed_file(file.name):
                return (
                    False,
                    f"Arquivo '{file.name}' tem formato inválido. Use JPG, JPEG ou PNG.",
                    [],
                )

            # Validar tamanho
            file_size = file.size
            if file_size > MAX_FILE_SIZE_BYTES:
                return (
                    False,
                    f"Arquivo '{file.name}' excede o tamanho máximo de 1GB.",
                    [],
                )

            # Gerar nome único e salvar arquivo
            unique_name = generate_unique_filename(file.name)
            file_path = os.path.join(upload_folder, unique_name)

            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

            # Registrar no banco
            photo = TaskPhoto(
                task_id=task_id,
                file_path=unique_name,
                original_name=file.name,
                file_size=file_size,
            )
            session.add(photo)
            saved_photos.append(
                {
                    "file_path": unique_name,
                    "original_name": file.name,
                    "file_size": file_size,
                }
            )

        session.commit()
        return True, f"{len(saved_photos)} foto(s) salva(s) com sucesso.", saved_photos

    except Exception as e:
        session.rollback()
        # Limpar arquivos já salvos em caso de erro
        for photo in saved_photos:
            try:
                os.remove(os.path.join(upload_folder, photo["file_path"]))
            except:
                pass
        return False, f"Erro ao salvar fotos: {str(e)}", []
    finally:
        session.close()


def get_task_photos(task_id: int) -> List[dict]:
    """Retorna lista de fotos de uma tarefa."""
    session = SessionLocal()
    try:
        photos = session.query(TaskPhoto).filter(TaskPhoto.task_id == task_id).all()
        return [
            {
                "id": p.id,
                "file_path": p.file_path,
                "original_name": p.original_name,
                "file_size": p.file_size,
                "uploaded_at": p.uploaded_at,
                "full_path": os.path.join(get_upload_folder(), p.file_path),
            }
            for p in photos
        ]
    finally:
        session.close()


def delete_task_photos(task_id: int) -> tuple[bool, str]:
    """Remove todas as fotos de uma tarefa."""
    session = SessionLocal()
    try:
        photos = session.query(TaskPhoto).filter(TaskPhoto.task_id == task_id).all()
        upload_folder = get_upload_folder()

        for photo in photos:
            # Remove arquivo físico
            file_path = os.path.join(upload_folder, photo.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
            # Remove registro do banco
            session.delete(photo)

        session.commit()
        return True, f"{len(photos)} foto(s) removida(s)."
    except Exception as e:
        session.rollback()
        return False, f"Erro ao remover fotos: {str(e)}"
    finally:
        session.close()


def get_photo_path(filename: str) -> Optional[str]:
    """Retorna o caminho completo de uma foto."""
    full_path = os.path.join(get_upload_folder(), filename)
    if os.path.exists(full_path):
        return full_path
    return None


def format_file_size(size_bytes: int) -> str:
    """Formata o tamanho do arquivo para exibição."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
