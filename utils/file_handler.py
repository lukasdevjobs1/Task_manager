"""
Gerenciamento de upload e download de fotos usando Supabase Storage.
"""

import uuid
from datetime import datetime
from typing import List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    SUPABASE_URL,
    SUPABASE_KEY,
    SUPABASE_SERVICE_KEY,
    SUPABASE_BUCKET,
    MAX_FILE_SIZE_BYTES,
    MAX_FILES_PER_TASK,
    ALLOWED_EXTENSIONS,
)
from database.connection import SessionLocal
from database.models import TaskPhoto

# Clientes Supabase (inicializados sob demanda)
_supabase_client = None
_supabase_service_client = None


def get_supabase_client():
    """Retorna o cliente Supabase (anon key) para leitura."""
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError(
                "SUPABASE_URL e SUPABASE_KEY devem estar configurados. "
                "Verifique o arquivo secrets.toml ou variáveis de ambiente."
            )
        from supabase import create_client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client


def get_supabase_service_client():
    """Retorna o cliente Supabase com service_role key para operações server-side (upload/delete).
    Isso contorna as políticas de RLS que bloqueiam a anon key."""
    global _supabase_service_client
    if _supabase_service_client is None:
        key = SUPABASE_SERVICE_KEY or SUPABASE_KEY
        if not SUPABASE_URL or not key:
            raise ValueError(
                "SUPABASE_URL e SUPABASE_SERVICE_KEY (ou SUPABASE_KEY) devem estar configurados."
            )
        from supabase import create_client
        _supabase_service_client = create_client(SUPABASE_URL, key)
    return _supabase_service_client


def allowed_file(filename: str) -> bool:
    """Verifica se o arquivo tem extensão permitida."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(original_name: str, company_id: int = None) -> str:
    """
    Gera um nome de arquivo único mantendo a extensão original.
    Inclui company_id no path para organização.
    """
    ext = original_name.rsplit(".", 1)[1].lower() if "." in original_name else "jpg"
    unique_id = uuid.uuid4().hex[:12]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if company_id:
        return f"company_{company_id}/{timestamp}_{unique_id}.{ext}"
    return f"{timestamp}_{unique_id}.{ext}"


def get_content_type(filename: str) -> str:
    """Retorna o content-type baseado na extensão do arquivo."""
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
    content_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
    }
    return content_types.get(ext, "application/octet-stream")


def save_uploaded_files(
    uploaded_files: list, task_id: int, company_id: int = None
) -> tuple[bool, str, List[dict]]:
    """
    Salva os arquivos enviados no Supabase Storage e registra no banco.

    Args:
        uploaded_files: Lista de arquivos do Streamlit file_uploader
        task_id: ID da tarefa associada
        company_id: ID da empresa (para organização de pastas)

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

    saved_photos = []
    session = SessionLocal()

    try:
        supabase = get_supabase_service_client()

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

            # Gerar nome único
            unique_name = generate_unique_filename(file.name, company_id)
            content_type = get_content_type(file.name)

            # Ler conteúdo do arquivo
            file_content = file.getvalue()

            # Upload para Supabase Storage (usando service_role key para bypass RLS)
            response = supabase.storage.from_(SUPABASE_BUCKET).upload(
                path=unique_name,
                file=file_content,
                file_options={"content-type": content_type}
            )

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
        # Limpar arquivos já salvos no Supabase em caso de erro
        try:
            supabase = get_supabase_service_client()
            for photo in saved_photos:
                supabase.storage.from_(SUPABASE_BUCKET).remove([photo["file_path"]])
        except:
            pass
        return False, f"Erro ao salvar fotos: {str(e)}", []
    finally:
        session.close()


def get_task_photos(task_id: int) -> List[dict]:
    """Retorna lista de fotos de uma tarefa com URLs públicas."""
    session = SessionLocal()
    try:
        photos = session.query(TaskPhoto).filter(TaskPhoto.task_id == task_id).all()
        result = []

        for p in photos:
            photo_data = {
                "id": p.id,
                "file_path": p.file_path,
                "original_name": p.original_name,
                "file_size": p.file_size,
                "uploaded_at": p.uploaded_at,
                "public_url": get_photo_url(p.file_path),
            }
            result.append(photo_data)

        return result
    finally:
        session.close()


def get_photo_url(file_path: str, expires_in: int = 3600) -> Optional[str]:
    """
    Retorna a URL pública ou assinada de uma foto no Supabase Storage.

    Args:
        file_path: Caminho do arquivo no bucket
        expires_in: Tempo de expiração em segundos (padrão: 1 hora)

    Returns:
        URL da foto ou None em caso de erro
    """
    try:
        supabase = get_supabase_client()
        # Gera URL assinada (funciona para buckets privados e públicos)
        response = supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(
            path=file_path,
            expires_in=expires_in
        )
        return response.get("signedURL") or response.get("signedUrl")
    except Exception as e:
        print(f"Erro ao gerar URL da foto: {e}")
        return None


def get_public_url(file_path: str) -> str:
    """
    Retorna a URL pública direta de uma foto (para buckets públicos).

    Args:
        file_path: Caminho do arquivo no bucket

    Returns:
        URL pública da foto
    """
    try:
        supabase = get_supabase_client()
        response = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(file_path)
        return response
    except Exception as e:
        print(f"Erro ao gerar URL pública: {e}")
        return ""


def delete_task_photos(task_id: int) -> tuple[bool, str]:
    """Remove todas as fotos de uma tarefa do Supabase Storage e banco."""
    session = SessionLocal()
    try:
        photos = session.query(TaskPhoto).filter(TaskPhoto.task_id == task_id).all()

        if not photos:
            return True, "Nenhuma foto para remover."

        # Coletar paths para deletar
        file_paths = [photo.file_path for photo in photos]

        # Remover do Supabase Storage (usando service_role key para bypass RLS)
        try:
            supabase = get_supabase_service_client()
            supabase.storage.from_(SUPABASE_BUCKET).remove(file_paths)
        except Exception as e:
            print(f"Aviso: Erro ao remover arquivos do storage: {e}")

        # Remover registros do banco
        for photo in photos:
            session.delete(photo)

        session.commit()
        return True, f"{len(photos)} foto(s) removida(s)."
    except Exception as e:
        session.rollback()
        return False, f"Erro ao remover fotos: {str(e)}"
    finally:
        session.close()


def delete_single_photo(photo_id: int) -> tuple[bool, str]:
    """Remove uma única foto pelo ID."""
    session = SessionLocal()
    try:
        photo = session.query(TaskPhoto).filter(TaskPhoto.id == photo_id).first()

        if not photo:
            return False, "Foto não encontrada."

        file_path = photo.file_path

        # Remover do Supabase Storage (usando service_role key para bypass RLS)
        try:
            supabase = get_supabase_service_client()
            supabase.storage.from_(SUPABASE_BUCKET).remove([file_path])
        except Exception as e:
            print(f"Aviso: Erro ao remover arquivo do storage: {e}")

        # Remover registro do banco
        session.delete(photo)
        session.commit()

        return True, "Foto removida com sucesso."
    except Exception as e:
        session.rollback()
        return False, f"Erro ao remover foto: {str(e)}"
    finally:
        session.close()


def download_photo(file_path: str) -> Optional[bytes]:
    """
    Faz download do conteúdo de uma foto do Supabase Storage.

    Args:
        file_path: Caminho do arquivo no bucket

    Returns:
        Conteúdo do arquivo em bytes ou None em caso de erro
    """
    try:
        supabase = get_supabase_client()
        response = supabase.storage.from_(SUPABASE_BUCKET).download(file_path)
        return response
    except Exception as e:
        print(f"Erro ao baixar foto: {e}")
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


def ensure_bucket_exists() -> bool:
    """
    Verifica se o bucket existe e tenta criar se não existir.
    Retorna True se o bucket está disponível.
    """
    try:
        supabase = get_supabase_service_client()
        # Listar buckets existentes
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]

        if SUPABASE_BUCKET not in bucket_names:
            # Criar bucket (público para facilitar acesso às imagens)
            supabase.storage.create_bucket(
                SUPABASE_BUCKET,
                options={"public": True}
            )
            print(f"Bucket '{SUPABASE_BUCKET}' criado com sucesso.")

        return True
    except Exception as e:
        print(f"Erro ao verificar/criar bucket: {e}")
        return False
