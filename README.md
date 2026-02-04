# 🚀 Sistema de Gerenciamento de Tarefas ISP - Versão 2.0

Sistema completo para gerenciamento de tarefas de campo com **aplicativo mobile** integrado. Desenvolvido para provedores de internet (ISP) com foco em equipes de fusão e infraestrutura.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![React Native](https://img.shields.io/badge/React_Native-0.76+-61DAFB.svg)
![Expo](https://img.shields.io/badge/Expo-54+-000020.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🆕 **NOVIDADES DA VERSÃO 2.0**

### 📱 **App Mobile Completo**
- **Autenticação integrada** com o sistema web
- **Recebimento de tarefas** via push notifications
- **Execução de tarefas** com fotos e localização
- **Sincronização em tempo real** com o Streamlit

### 🎯 **Sistema de Atribuição de Tarefas**
- **Gerentes** atribuem tarefas via Streamlit
- **Colaboradores** recebem no app mobile
- **Acompanhamento** em tempo real do progresso
- **Notificações push** automáticas

### 🗄️ **Banco de Dados Expandido**
- **task_assignments** - Tarefas atribuídas aos colaboradores
- **assignment_photos** - Fotos das execuções
- **notifications** - Sistema de notificações
- **push_tokens** - Tokens para notificações mobile

## 🏗️ **ARQUITETURA DO SISTEMA**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   STREAMLIT     │    │   POSTGRESQL    │    │   APP MOBILE    │
│   (Gerência)    │◄──►│   (Database)    │◄──►│ (Colaboradores) │
│                 │    │                 │    │                 │
│ • Admin Geral   │    │ • Users         │    │ • Login         │
│ • Gerentes      │    │ • Tasks         │    │ • Tarefas       │
│ • Atribuição    │    │ • Photos        │    │ • Fotos         │
│ • Dashboard     │    │ • Notifications │    │ • Status        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   SUPABASE      │
                    │   (Storage)     │
                    │                 │
                    │ • Fotos         │
                    │ • Push Tokens   │
                    │ • Real-time     │
                    └─────────────────┘
```

## 🎯 **FLUXO COMPLETO DE TRABALHO**

1. **Admin Geral** → Cadastra empresas e gerentes no Streamlit
2. **Gerente** → Atribui tarefa a colaborador via Streamlit
3. **Sistema** → Cria registro em `task_assignments` + notificação
4. **Push Service** → Envia notificação para o app mobile
5. **Colaborador** → Recebe notificação no smartphone
6. **Colaborador** → Executa tarefa + fotos + atualiza status
7. **Gerente** → Acompanha progresso em tempo real no dashboard

## 📋 **FUNCIONALIDADES DETALHADAS**

### 🖥️ **Sistema Web (Streamlit)**

#### **Para Admin Geral:**
- ✅ Cadastro de empresas parceiras
- ✅ Definição de gerentes responsáveis
- ✅ Gerenciamento de usuários
- ✅ Relatórios consolidados
- ✅ Painel administrativo completo

#### **Para Gerentes:**
- ✅ **Atribuição de tarefas** - Página dedicada com:
  - Seleção de colaborador
  - Título e descrição da tarefa
  - Endereço com coordenadas GPS
  - Prioridade (baixa, média, alta)
  - Prazo de execução
- ✅ **Dashboard de acompanhamento** - Métricas em tempo real
- ✅ **Detalhes das tarefas** - Visualização completa com:
  - Mapa integrado (Google Maps)
  - Fotos enviadas pelo colaborador
  - Histórico de status
  - Ações de gerenciamento
- ✅ **Sistema de notificações** - Central de alertas

#### **Para Colaboradores:**
- ✅ Visualização de tarefas atribuídas
- ✅ Dashboard pessoal
- ✅ Histórico de execuções

### 📱 **App Mobile (React Native + Expo)**

#### **Autenticação:**
- ✅ Login integrado com sistema web
- ✅ Persistência de sessão
- ✅ Logout seguro

#### **Gerenciamento de Tarefas:**
- ✅ **Lista de tarefas** com filtros por status
- ✅ **Detalhes completos** da tarefa
- ✅ **Mapa integrado** com localização
- ✅ **Atualização de status** (pendente → em andamento → concluída)

#### **Execução de Tarefas:**
- ✅ **Câmera integrada** para fotos
- ✅ **Galeria de fotos** para seleção
- ✅ **Upload automático** para Supabase Storage
- ✅ **Observações** e notas da execução

#### **Notificações:**
- ✅ **Push notifications** em tempo real
- ✅ **Alertas detalhados** com informações da tarefa
- ✅ **Som e vibração** configuráveis

## 🛠️ **TECNOLOGIAS UTILIZADAS**

### **Backend & Web:**
- **Python 3.10+** - Linguagem principal
- **Streamlit 1.28+** - Interface web
- **PostgreSQL 15+** - Banco de dados principal
- **SQLAlchemy** - ORM para Python
- **Supabase** - Backend-as-a-Service
- **bcrypt** - Hash de senhas

### **Mobile:**
- **React Native 0.76+** - Framework mobile
- **Expo 54+** - Plataforma de desenvolvimento
- **React Navigation 7+** - Navegação
- **Expo Camera** - Câmera nativa
- **Expo Notifications** - Push notifications
- **Expo SecureStore** - Armazenamento seguro

### **Infraestrutura:**
- **Supabase Storage** - Armazenamento de fotos
- **Google Maps API** - Mapas e coordenadas
- **Push Notifications** - Notificações em tempo real

## 📊 **ESTRUTURA DO BANCO DE DADOS**

### **Tabelas Principais:**
```sql
-- Usuários do sistema
users (
  id, username, password_hash, full_name, 
  team, role, active, push_token, created_at
)

-- Tarefas atribuídas (NOVA)
task_assignments (
  id, assigned_to, assigned_by, title, description,
  address, latitude, longitude, priority, status,
  due_date, created_at, updated_at, started_at, 
  completed_at, notes
)

-- Fotos das execuções (NOVA)
assignment_photos (
  id, assignment_id, photo_url, photo_path,
  description, uploaded_at
)

-- Sistema de notificações
notifications (
  id, user_id, title, message, type,
  reference_type, reference_id, is_read, created_at
)
```

## 🚀 **INSTALAÇÃO E CONFIGURAÇÃO**

### **1. Pré-requisitos**
```bash
# Sistema
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Git

# Mobile (opcional para desenvolvimento)
- Android Studio + SDK
- Expo CLI
```

### **2. Clone e Configuração**
```bash
# Clone o repositório
git clone https://github.com/lukasdevjobs1/Task_manager.git
cd Task_manager

# Instale dependências Python
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite o .env com suas credenciais
```

### **3. Banco de Dados**
```bash
# Execute a migração
python migrations/final_migration.py


### **4. App Mobile (Desenvolvimento)**
```bash
cd mobile

# Instale dependências
npm install

# Inicie o servidor Expo
npx expo start

# Para Android
npx expo start --android

# Para iOS
npx expo start --ios
```

## 🔧 **CONFIGURAÇÃO DE PRODUÇÃO**

### **Variáveis de Ambiente Necessárias:**
```env
# Banco de Dados
DB_HOST=seu_host_postgresql
DB_PORT=5432
DB_NAME=task_manager
DB_USER=seu_usuario
DB_PASSWORD=sua_senha

# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua_anon_key
SUPABASE_SERVICE_KEY=sua_service_role_key
SUPABASE_BUCKET=task-photos

# Google Maps
GOOGLE_MAPS_API_KEY=sua_api_key_google_maps

# Upload
MAX_FILE_SIZE_GB=1
MAX_FILES_PER_TASK=10
```

### **Deploy Recomendado:**
- **Streamlit Cloud** - Deploy automático do GitHub
- **Railway/Render** - PostgreSQL + Python
- **Supabase** - Storage e real-time
- **Expo EAS** - Build e distribuição mobile

## 📱 **COMO USAR O APP MOBILE**

### **1. Instalação:**
- Baixe o Expo Go na Play Store/App Store
- Escaneie o QR code do desenvolvimento
- Ou baixe o APK/IPA de produção

### **2. Login:**
- Use um dos usuários criados na migração
- Ex: `joao.tecnico` / `123456`

### **3. Fluxo de Trabalho:**
1. **Receba** notificação de nova tarefa
2. **Visualize** detalhes e localização
3. **Inicie** a execução da tarefa
4. **Tire fotos** durante a execução
5. **Adicione observações** se necessário
6. **Conclua** a tarefa

## 📈 **MÉTRICAS E RELATÓRIOS**

### **Dashboard Web:**
- 📊 Tarefas por status (pendente, andamento, concluída)
- 📅 Produtividade por período
- 👥 Performance por colaborador
- 🏢 Relatórios por empresa
- 📍 Mapa de tarefas por região

### **App Mobile:**
- 📱 Tarefas pessoais
- ⏱️ Tempo de execução
- 📸 Fotos enviadas
- 🎯 Taxa de conclusão

## 🔐 **SEGURANÇA**

- ✅ **Autenticação** com bcrypt
- ✅ **Tokens JWT** para sessões
- ✅ **Armazenamento seguro** no mobile
- ✅ **Upload seguro** de fotos
- ✅ **Validação** de dados
- ✅ **Logs** de auditoria

## 🤝 **CONTRIBUINDO**

1. Fork o projeto
2. Crie sua branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 **LICENÇA**

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 **AUTOR**

Desenvolvido por [lukasdevjobs1](https://github.com/lukasdevjobs1)

---

## 🎯 **ROADMAP FUTURO**

- [ ] **Chat em tempo real** entre gerentes e colaboradores
- [ ] **Relatórios avançados** com BI
- [ ] **Integração com ERP** existente
- [ ] **App para gerentes** (versão mobile)
- [ ] **Reconhecimento de voz** para observações
- [ ] **IA para otimização** de rotas
- [ ] **Dashboard público** para clientes

---

**Sistema de Gerenciamento de Tarefas ISP v2.0** - Revolucionando o controle de produtividade com tecnologia mobile integrada! 🚀📱
