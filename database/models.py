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
    Float,
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
    task_assignments = relationship("TaskAssignment", back_populates="company", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="company", cascade="all, delete-orphan")

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
    is_super_admin = Column(Boolean, default=False)  # True apenas para admin geral
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    push_token = Column(String(255), nullable=True)  # Token Expo para push notifications

    # Relacionamentos
    company = relationship("Company", back_populates="users")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    assigned_tasks = relationship(
        "TaskAssignment",
        back_populates="assignee",
        foreign_keys="TaskAssignment.assigned_to",
        cascade="all, delete-orphan",
    )
    created_assignments = relationship(
        "TaskAssignment",
        back_populates="assigner",
        foreign_keys="TaskAssignment.assigned_by",
    )
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

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


class TaskAssignment(Base):
    """Modelo de tarefa atribuída pelo gerente a um usuário de campo."""

    __tablename__ = "task_assignments"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String(300), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(20), nullable=False, default="pending")  # pending, in_progress, completed
    priority = Column(String(20), nullable=False, default="medium")  # low, medium, high, urgent
    due_date = Column(DateTime, nullable=True)
    observations = Column(Text, nullable=True)  # Observações do campo ao concluir
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    company = relationship("Company", back_populates="task_assignments")
    assigner = relationship("User", back_populates="created_assignments", foreign_keys=[assigned_by])
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_to])
    photos = relationship("AssignmentPhoto", back_populates="assignment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TaskAssignment(id={self.id}, title='{self.title}', status='{self.status}')>"


class AssignmentPhoto(Base):
    """Fotos tiradas durante a execução de uma tarefa atribuída."""

    __tablename__ = "assignment_photos"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("task_assignments.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamento
    assignment = relationship("TaskAssignment", back_populates="photos")

    def __repr__(self):
        return f"<AssignmentPhoto(id={self.id}, original_name='{self.original_name}')>"


class Notification(Base):
    """Modelo de notificações in-app."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    type = Column(String(30), nullable=False)  # task_assigned, task_updated, task_completed
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=True)
    reference_id = Column(Integer, nullable=True)  # ID do TaskAssignment relacionado
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relacionamentos
    company = relationship("Company", back_populates="notifications")
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.type}', read={self.read})>"
