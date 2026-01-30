import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()


def get_secret(key: str, default: str = None) -> str:
    """Obtém secret do Streamlit Cloud ou variável de ambiente."""
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


# Configurações do Banco de Dados
DB_CONFIG = {
    "host": get_secret("DB_HOST", "localhost"),
    "port": get_secret("DB_PORT", "5432"),
    "database": get_secret("DB_NAME", "task_manager"),
    "user": get_secret("DB_USER", "postgres"),
    "password": get_secret("DB_PASSWORD", "postgres"),
}

DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{quote_plus(DB_CONFIG['password'])}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Configurações do Supabase Storage
SUPABASE_URL = get_secret("SUPABASE_URL", "")
SUPABASE_KEY = get_secret("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = get_secret("SUPABASE_SERVICE_KEY", "")
SUPABASE_BUCKET = get_secret("SUPABASE_BUCKET", "task-photos")

# Google Maps API Key
GOOGLE_MAPS_API_KEY = get_secret("GOOGLE_MAPS_API_KEY", "")

# Configurações de Upload
UPLOAD_FOLDER = get_secret("UPLOAD_FOLDER", "uploads")
MAX_FILE_SIZE_GB = float(get_secret("MAX_FILE_SIZE_GB", "1"))
MAX_FILE_SIZE_BYTES = int(MAX_FILE_SIZE_GB * 1024 * 1024 * 1024)
MAX_FILES_PER_TASK = int(get_secret("MAX_FILES_PER_TASK", "10"))
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

# Tipos de Fibra disponíveis
TIPOS_FIBRA = ["F.06", "F.08", "F.12", "Outro"]

# Equipes disponíveis
EQUIPES = ["fusao", "infraestrutura"]

# Roles de usuário
ROLES = ["admin", "user"]
