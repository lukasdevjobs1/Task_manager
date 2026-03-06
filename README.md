# Task Manager ISP

Sistema completo de **gerenciamento de tarefas de campo para provedores de internet (ISP)**, composto por:

- **App Mobile Flutter** — utilizado pelos técnicos em campo
- **Painel Web (Streamlit)** — para gestores acompanharem operações em tempo real
- **Backend Supabase** — Postgres, Storage e Realtime

---

## Capturas de tela

### App Mobile

| Perfil / Métricas | Lista de Materiais utilizados | Home / Dashboard |
|:---:|:---:|:---:|
| ![Home](assets/images/2026-03-04%20at%2013.47.06.jpeg) | ![Tarefas](assets/images/2026-03-04%20at%2019.38.10.jpeg) | ![Executar](assets/images/2026-03-05%20at%2000.45.21.jpeg) |

| Gerenciamento de  Tarefas |
|:---:|
| ![Perfil](assets/images/2026-03-05%20at%2000.45.52.jpeg) |

### Dashboard Mobile

![Dashboard Web](assets/images/Captura%20de%20tela%202026-03-01%20153218.png)

---

## Funcionalidades

### App Mobile (Flutter)

- **Autenticação segura**
  - Login com usuário/senha integrado ao Supabase
  - Armazenamento seguro de credenciais com `FlutterSecureStorage`

- **Gestão de tarefas de campo**
  - Listagem com abas: Todas / Pendentes / Em Andamento / Concluídas
  - Detalhes completos da OS com endereço, descrição e prioridade
  - Atualização de status: pendente → em andamento → concluída

- **Execução de tarefa com dados técnicos ISP**
  - Registro de: Abertura/Fechamento de Cx Emenda, CTO e Rozeta
  - Quantidade de CTOs e Caixas de Emenda instaladas
  - Metragem de fibra lançada
  - Upload de fotos com detecção automática de formato (JPG, PNG, WebP, HEIC)
  - Retry automático de upload (3 tentativas com backoff)
  - Bloqueio de finalização se o upload de fotos falhar, com diálogo de confirmação

- **Materiais utilizados**
  - Registro de materiais por tarefa (nome, quantidade, unidade)
  - Histórico de materiais no perfil e relatórios

- **Mapas e localização**
  - Abertura direta no Google Maps a partir do endereço ou coordenadas GPS
  - Integração com `geolocator` e `geocoding`

- **Relatórios**
  - Filtros por 7, 30 e 90 dias
  - Gráfico de distribuição de status (pizza)
  - Gráfico de tarefas concluídas por dia (barras — últimos 7 dias)
  - Resumo de materiais utilizados no período

- **Notificações**
  - Push via Firebase Cloud Messaging
  - Notificações locais com badge na navegação

- **Modo offline**
  - Cache com `Hive` para uso sem conexão
  - Sincronização automática ao reconectar

- **Chat**
  - Comunicação em tempo real entre técnico e gestor via Supabase Realtime ( ainda em desenvolvimento )

---

### Painel Web (Streamlit)

- **Dashboard interativo**
  - KPIs: total de tarefas, concluídas, em andamento, pendentes
  - Métricas ISP agregadas: Qtd CTOs, Qtd Cx Emenda, Fibra Lançada (m), Abert./Fech. Cx Emenda, Abert./Fech. CTO, Abert./Fech. Rozeta
  - Filtro por empresa (apenas empresas ativas) e período
  - Gráficos interativos por empresa e por técnico (Plotly)
  - Aba de desempenho por técnico e aba de materiais

- **Tarefas Concluídas**
  - Listagem com filtro por data e colaborador
  - 7 métricas ISP no topo (quantidade + abertura/fechamento)
  - Detalhes de cada tarefa: dados técnicos, materiais da tabela `task_materials`, fotos

- **Gerenciamento de tarefas**
  - Criação e atribuição de tarefas
  - Caixa da empresa (tarefas sem técnico atribuído)
  - Visualização e reatribuição de tarefas

- **Multi-empresa com grupos**
  - Gestores veem apenas empresas ativas do seu grupo
  - Empresas inativas não interferem nas métricas

- **Administração (Super Admin)**
  - Gestão de empresas e usuários
  - Ativação/desativação de contas

---

## Stack técnica

### Mobile
| Camada | Tecnologia |
|---|---|
| Framework | Flutter 3 / Dart (null-safe) |
| Estado | Provider |
| Navegação | go_router |
| Backend | supabase_flutter |
| Offline | Hive + sqflite |
| Notificações | Firebase Messaging + flutter_local_notifications |
| Mapas | google_maps_flutter + geolocator + geocoding |
| Gráficos | fl_chart |
| Câmera | camera + image_picker |
| HTTP | dio |

### Web / Backend
| Camada | Tecnologia |
|---|---|
| Painel web | Python + Streamlit |
| Banco de dados | Supabase (PostgreSQL) |
| Storage | Supabase Storage |
| Realtime | Supabase Realtime |
| Gráficos web | Plotly |

---

## Modelo de dados principal

```
companies         → empresas (multi-tenant)
users             → técnicos e gestores por empresa
task_assignments  → OSs com dados técnicos ISP, status, fotos
task_materials    → materiais utilizados por tarefa
assignment_photos → fotos vinculadas às OSs
notifications     → notificações push
chat_messages     → mensagens técnico ↔ gestor
```

Views Supabase:
- `vw_technician_materials_summary` — resumo de materiais por técnico/mês
- `vw_technician_performance` — tarefas + materiais para cálculo de bonificação

---

## Como executar

### App Mobile

```bash
# Instalar dependências
flutter pub get

# Rodar em debug
flutter run

# Build release APK
flutter build apk --release
# APK: build/app/outputs/flutter-apk/app-release.apk
```

### Painel Web

```bash
# Instalar dependências Python
pip install -r requirements.txt

# Rodar localmente
streamlit run app.py
```

O painel web também está hospedado no **Streamlit Cloud** com deploy automático via push no `main`.

---

## Configuração

### Supabase (Mobile)

Configure em `lib/main.dart`:
```dart
await Supabase.initialize(
  url: 'SUA_URL_SUPABASE',
  anonKey: 'SUA_ANON_KEY',
);
```

### Firebase (Push Notifications)

- Android: `android/app/google-services.json`
- iOS: `ios/Runner/GoogleService-Info.plist`
  
---

## Estrutura do projeto

```
task_manager/
├── lib/                        # App Flutter
│   ├── config/                 # Tema e rotas
│   ├── models/                 # TaskAssignment, User, TaskMaterial...
│   ├── providers/              # Auth, Task, Notification, Offline
│   ├── screens/                # Telas do app
│   ├── services/               # SupabaseService (upload, API)
│   └── widgets/                # Componentes reutilizáveis
├── views/                      # Painel web Streamlit
│   ├── dashboard_supabase.py   # Dashboard principal
│   ├── completed_tasks_manager.py
│   ├── task_management.py
│   └── ...
├── database/                   # Conexão e queries Supabase (web)
├── migrations/                 # SQLs para aplicar no Supabase
├── assets/
│   └── images/                 # Screenshots e imagens do README
└── app.py                      # Entrada do painel web
```

---

## Segurança

- Credenciais armazenadas com `FlutterSecureStorage`
- RLS (Row Level Security) ativo em todas as tabelas do Supabase
- Políticas por empresa (multi-tenant isolado)
- Comunicação exclusivamente via HTTPS

---

**Task Manager ISP v1.0** — Gestão de campo completa para provedores de internet.
