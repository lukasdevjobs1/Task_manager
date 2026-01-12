"""
Script para inicializar o banco de dados.
Cria todas as tabelas e o usuário admin padrão.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import engine, SessionLocal
from database.models import Base, User
import bcrypt


def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_tables():
    """Cria todas as tabelas no banco de dados."""
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")


def create_default_admin():
    """Cria o usuário admin padrão se não existir."""
    session = SessionLocal()
    try:
        # Verifica se já existe um admin
        admin = session.query(User).filter(User.username == "admin").first()
        if admin:
            print("Usuário admin já existe.")
            return

        # Cria o admin padrão
        admin_user = User(
            username="admin",
            password_hash=hash_password("admin123"),
            full_name="Administrador",
            team="fusao",
            role="admin",
            active=True,
        )
        session.add(admin_user)
        session.commit()
        print("Usuário admin criado com sucesso!")
        print("  Username: admin")
        print("  Senha: admin123")
        print("  IMPORTANTE: Altere a senha após o primeiro login!")
    except Exception as e:
        session.rollback()
        print(f"Erro ao criar admin: {e}")
        raise
    finally:
        session.close()


def init_database():
    """Inicializa o banco de dados completo."""
    print("=" * 50)
    print("Inicializando banco de dados...")
    print("=" * 50)

    create_tables()
    create_default_admin()

    print("=" * 50)
    print("Banco de dados inicializado com sucesso!")
    print("=" * 50)


if __name__ == "__main__":
    init_database()
