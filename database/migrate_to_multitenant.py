"""
Script de migração para multi-tenant.
Adiciona a tabela companies e atualiza users/tasks com company_id.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database.connection import engine, SessionLocal
from database.models import Base, Company, User, Task


def migrate():
    """Executa a migração para multi-tenant."""
    print("=" * 50)
    print("Iniciando migração para multi-tenant...")
    print("=" * 50)

    session = SessionLocal()

    try:
        # 1. Criar tabela companies se não existir
        print("\n1. Verificando/criando tabela companies...")
        Base.metadata.create_all(bind=engine)
        print("   Tabela companies OK")

        # 2. Verificar se já existe empresa padrão
        print("\n2. Verificando empresa padrão...")
        company = session.query(Company).filter(Company.slug == "empresa-padrao").first()

        if not company:
            print("   Criando empresa padrão...")
            company = Company(
                name="Empresa Padrão",
                slug="empresa-padrao",
                active=True,
            )
            session.add(company)
            session.commit()
            print("   Empresa padrão criada com ID:", company.id)
        else:
            print("   Empresa padrão já existe com ID:", company.id)

        # 3. Verificar se coluna company_id existe em users
        print("\n3. Atualizando usuários existentes...")
        try:
            # Tentar atualizar usuários sem company_id
            result = session.execute(
                text("UPDATE users SET company_id = :company_id WHERE company_id IS NULL"),
                {"company_id": company.id}
            )
            session.commit()
            print(f"   {result.rowcount} usuário(s) atualizado(s)")
        except Exception as e:
            print(f"   Aviso: {e}")
            session.rollback()

        # 4. Atualizar tarefas existentes
        print("\n4. Atualizando tarefas existentes...")
        try:
            result = session.execute(
                text("UPDATE tasks SET company_id = :company_id WHERE company_id IS NULL"),
                {"company_id": company.id}
            )
            session.commit()
            print(f"   {result.rowcount} tarefa(s) atualizada(s)")
        except Exception as e:
            print(f"   Aviso: {e}")
            session.rollback()

        print("\n" + "=" * 50)
        print("Migração concluída com sucesso!")
        print("=" * 50)

    except Exception as e:
        session.rollback()
        print(f"\nErro durante migração: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    migrate()
