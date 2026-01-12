# Sistema de Gerenciamento de Tarefas ISP

Sistema web para registro e acompanhamento de tarefas de campo de equipes de fusão e infraestrutura de provedores de internet.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Funcionalidades

- **Autenticação segura** - Login com hash bcrypt
- **Registro de tarefas** - Formulário completo para atividades de campo
- **Upload de fotos** - Até 10 fotos por tarefa (máx. 1GB cada)
- **Dashboard interativo** - Métricas por usuário, mês e ano com gráficos
- **Painel administrativo** - Gerenciamento de usuários
- **Exportação de relatórios** - PDF e Excel

## Campos do Registro de Tarefas

| Campo | Descrição |
|-------|-----------|
| Empresa | Nome da empresa cliente |
| Bairro | Localização do serviço |
| Caixa de Emenda | Abertura/Fechamento + Quantidade |
| CTO | Abertura/Fechamento + Quantidade |
| Rozeta | Abertura/Fechamento |
| Tipo de Fibra | F.06, F.08, F.12, Outro |
| Fibra Lançada | Metros de fibra instalada |
| Observações | Detalhes adicionais |
| Fotos | Registro fotográfico (obrigatório) |

## Tecnologias

- **Backend:** Python 3.10+
- **Frontend:** Streamlit
- **Banco de dados:** PostgreSQL
- **ORM:** SQLAlchemy
- **Autenticação:** bcrypt
- **Gráficos:** Plotly
- **Exportação:** ReportLab (PDF), OpenPyXL (Excel)

## Estrutura do Projeto

```
task_manager/
├── app.py                    # Aplicação principal
├── config.py                 # Configurações
├── requirements.txt          # Dependências
├── .env.example              # Template de variáveis de ambiente
├── database/
│   ├── connection.py         # Conexão PostgreSQL
│   ├── models.py             # Modelos SQLAlchemy
│   └── init_db.py            # Inicialização do banco
├── auth/
│   └── authentication.py     # Sistema de autenticação
├── pages/
│   ├── login.py              # Página de login
│   ├── register_task.py      # Formulário de tarefas
│   ├── dashboard.py          # Dashboard de métricas
│   └── admin.py              # Painel administrativo
├── utils/
│   ├── file_handler.py       # Upload de fotos
│   └── export.py             # Exportação PDF/Excel
└── uploads/                  # Armazenamento de fotos
```

## Instalação

### Pré-requisitos

- Python 3.10+
- PostgreSQL 15+
- Docker (opcional)

### 1. Clone o repositório

```bash
git clone https://github.com/lukasdevjobs1/Task_manager.git
cd Task_manager
```

### 2. Crie o ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=task_manager
DB_USER=postgres
DB_PASSWORD=sua_senha
```

### 5. Configure o banco de dados

#### Opção A: PostgreSQL local

```sql
CREATE DATABASE task_manager;
```

#### Opção B: Docker

```bash
docker run -d \
  --name task_manager_postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=task_manager \
  -p 5432:5432 \
  postgres:15-alpine
```

### 6. Inicialize o banco de dados

```bash
python database/init_db.py
```

### 7. Execute a aplicação

```bash
streamlit run app.py
```

Acesse: **http://localhost:8501**

## Credenciais Padrão

| Usuário | Senha | Perfil |
|---------|-------|--------|
| admin | admin123 | Administrador |

> **Importante:** Altere a senha após o primeiro login!

## Deploy

### Variáveis de Ambiente Necessárias

```env
DB_HOST=seu_host
DB_PORT=5432
DB_NAME=task_manager
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE_GB=1
MAX_FILES_PER_TASK=10
```

### Plataformas Recomendadas

- **Streamlit Cloud** - Deploy gratuito direto do GitHub
- **Railway** - Suporte a PostgreSQL + Python
- **Render** - Free tier disponível
- **Heroku** - Com add-on PostgreSQL

## Screenshots

### Login
Tela de autenticação segura com validação de credenciais.

### Registro de Tarefas
Formulário completo para registro de atividades de campo com upload de fotos.

### Dashboard
Visualização de métricas com gráficos interativos e filtros por período.

### Painel Admin
Gerenciamento de usuários com opções de criar, ativar/desativar e alterar senhas.

## Equipes

O sistema suporta duas equipes:

- **Fusão** - Equipe de fusão de fibra óptica
- **Infraestrutura** - Equipe de infraestrutura de rede

## API de Dados

### Modelo de Usuário

```python
{
    "id": int,
    "username": str,
    "full_name": str,
    "team": "fusao" | "infraestrutura",
    "role": "admin" | "user",
    "active": bool,
    "created_at": datetime
}
```

### Modelo de Tarefa

```python
{
    "id": int,
    "user_id": int,
    "empresa": str,
    "bairro": str,
    "abertura_caixa_emenda": bool,
    "fechamento_caixa_emenda": bool,
    "abertura_cto": bool,
    "fechamento_cto": bool,
    "abertura_rozeta": bool,
    "fechamento_rozeta": bool,
    "qtd_cto": int,
    "qtd_caixa_emenda": int,
    "tipo_fibra": str,
    "fibra_lancada": float,
    "observacoes": str,
    "created_at": datetime
}
```

## Contribuindo

1. Fork o projeto
2. Crie sua branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Autor

Desenvolvido por [lukasdevjobs1](https://github.com/lukasdevjobs1)

---

**Sistema de Gerenciamento de Tarefas ISP** - Facilitando o controle de produtividade de equipes de campo.
