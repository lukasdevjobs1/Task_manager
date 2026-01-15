from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    Numeric,
    ForeignKey,
    BigInteger,
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Company(Base):
    """Modelo de empresa/organização para multi-tenant."""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company(name='{self.name}', slug='{self.slug}')>"


class User(Base):
    """Modelo de usuário do sistema."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    team = Column(String(20), nullable=False)  # 'fusao' ou 'infraestrutura'
    role = Column(String(20), nullable=False, default="user")  # 'admin' ou 'user'
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    company = relationship("Company", back_populates="users")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username='{self.username}', company_id={self.company_id})>"


class Task(Base):
    """Modelo de tarefa/atividade de campo."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Informações gerais
    empresa = Column(String(100), nullable=False)
    bairro = Column(String(100), nullable=False)

    # Atividades em Caixa de Emenda
    abertura_caixa_emenda = Column(Boolean, default=False)
    fechamento_caixa_emenda = Column(Boolean, default=False)

    # Atividades em CTO
    abertura_cto = Column(Boolean, default=False)
    fechamento_cto = Column(Boolean, default=False)

    # Atividades em Rozeta
    abertura_rozeta = Column(Boolean, default=False)
    fechamento_rozeta = Column(Boolean, default=False)

    # Quantidades
    qtd_cto = Column(Integer, default=0)
    qtd_caixa_emenda = Column(Integer, default=0)

    # Fibra
    tipo_fibra = Column(String(20))  # 'F.06', 'F.08', 'F.12', 'Outro'
    fibra_lancada = Column(Numeric(10, 2), default=0)  # metros

    # Observações
    observacoes = Column(Text)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relacionamentos
    company = relationship("Company", back_populates="tasks")
    user = relationship("User", back_populates="tasks")
    photos = relationship("TaskPhoto", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task(id={self.id}, company_id={self.company_id}, empresa='{self.empresa}')>"


class TaskPhoto(Base):
    """Modelo para fotos associadas às tarefas."""

    __tablename__ = "task_photos"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # tamanho em bytes
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamento
    task = relationship("Task", back_populates="photos")

    def __repr__(self):
        return f"<TaskPhoto(id={self.id}, original_name='{self.original_name}')>"
