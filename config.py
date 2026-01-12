import os
from dotenv import load_dotenv

load_dotenv()

# Configurações do Banco de Dados
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "task_manager"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}

DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Configurações de Upload
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
MAX_FILE_SIZE_GB = float(os.getenv("MAX_FILE_SIZE_GB", "1"))
MAX_FILE_SIZE_BYTES = int(MAX_FILE_SIZE_GB * 1024 * 1024 * 1024)
MAX_FILES_PER_TASK = int(os.getenv("MAX_FILES_PER_TASK", "10"))
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

# Tipos de Fibra disponíveis
TIPOS_FIBRA = ["F.06", "F.08", "F.12", "Outro"]

# Equipes disponíveis
EQUIPES = ["fusao", "infraestrutura"]

# Roles de usuário
ROLES = ["admin", "user"]
