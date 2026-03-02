## Projeto: Sistema de Tarefas ISP

### Visão Geral do Produto
Aplicação completa de gerenciamento de tarefas de campo para provedores de internet (ISP), composta por:
- **App Flutter** usado pelos técnicos em campo (mobile, com suporte offline e sincronização).
- **Painel Web (Streamlit)** usado por gestores/administradores para cadastro, acompanhamento e análise das tarefas.
- **Backend de dados** baseado em **Supabase (Postgres, Storage, Realtime)**, scripts Python e integrações externas (notificações, mapas, etc.).

### Stack Tecnológica do Projeto
- **Mobile (principal):**
  - Flutter 3 (Dart null‑safe)
  - `provider` + `go_router`
  - `supabase_flutter` (auth, storage, realtime)
  - Offline: `sqflite`, `hive`, `hive_flutter`
  - Notificações: `firebase_core`, `firebase_messaging`, `flutter_local_notifications`
  - Maps & localização: `google_maps_flutter`, `geolocator`, `geocoding`
  - Outras libs importantes: `dio`, `shared_preferences`, `flutter_secure_storage`, `image_picker`, `camera`, `fl_chart`, etc.

- **Painel Web / Ferramentas internas:**
  - Python 3
  - Streamlit (`app.py`) como UI principal administrativa
  - Módulos em `auth/`, `views/`, `utils/`, `database/`

- **Backend / Dados:**
  - Supabase (Postgres, Row Level Security, Storage, Realtime)
  - Scripts e migrações Python (diretórios `migrations/`, `database/`, `fix_users.py`, etc.)

- **Infraestrutura:**
  - Variáveis de ambiente via `.env` e `config.py`
  - Implantação do painel Streamlit (servidor próprio / plataforma PaaS)
  - Push notifications via Firebase Cloud Messaging

### Estrutura de Repositório (alto nível)
/
├── `lib/`                     # App Flutter (mobile principal)
├── `auth/`, `views/`, `utils/`, `database/`  # Módulos Python do painel/admin
├── `migrations/`              # Scripts e migrações de banco
├── `uploads/`                 # Arquivos enviados (fotos, anexos, etc.)
├── `.claude/team/`            # Perfis dos agents (VOCÊ ESTÁ AQUI)
├── `.claude/commands/`        # Comandos de orquestração (ex: reunião de time)
└── `CLAUDE.md`                # Este arquivo (visão geral para todos os agents)

### Regras Gerais do Time de Agents
1. **Commits**
   - Usar **conventional commits** sempre que possível: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`.
   - Descrever **o porquê** da mudança, não só o que foi alterado.

2. **Branches e Pull Requests**
   - Toda funcionalidade relevante deve ser desenvolvida em **branch dedicada**.
   - Cada PR deve:
     - Explicar o contexto e a motivação.
     - Listar mudanças principais (Flutter, Python, Supabase, etc.).
     - Incluir **checklist de testes** realizados (mobile, web, scripts).
   - Idealmente, todo PR precisa de revisão de **pelo menos 2 perfis** (ex: `ENGENHEIRO` + `QA`, ou `MOBILE` + `DEVOPS`).

3. **Comunicação entre Agents**
   - Sempre que uma decisão impactar múltiplas áreas (ex: mudança no modelo de dados Supabase que afeta Flutter e Streamlit):
     - Engenheiro deve alinhar com **Mobile** e **QA**.
     - Se envolver ambiente, variáveis ou deploy, envolver **DevOps**.
   - Use o comando `/reuniao-time` (ver `.claude/commands/reuniao-time.md`) para alinhar decisões maiores.

4. **Documentação**
   - Toda decisão técnica relevante (mudança de schema, fluxo crítico de autenticação, políticas offline/sync, push notifications) deve ser registrada em:
     - `docs/decisions/` (quando existir) ou
     - Em um arquivo Markdown específico referenciado pelo PR.
   - O **contrato de API/Supabase** consumido pelo app Flutter e pelo painel deve ser descrito minimamente (tabelas, colunas importantes, regras de RLS, triggers).

5. **Qualidade e Testes**
   - Nenhuma mudança crítica em:
     - Autenticação/login,
     - Fluxo de tarefas (criação/atribuição/conclusão),
     - Sincronização offline/online,
     - Notificações push,
     Pode ser feita **sem plano de testes** acordado com o perfil **QA**.
   - Manter scripts de teste executáveis de forma simples (por exemplo, via `Makefile`, `taskfile`, ou comandos documentados em `README`/`CLAUDE.md`).

6. **Segurança e Dados**
   - Nunca commitar **secrets**: chaves Supabase, Firebase, senhas, etc. Devem ficar em `.env` ou providers seguros.
   - Cuidado com dados sensíveis de usuários (endereços, fotos, localização). Sempre seguir boas práticas de LGPD.

### Time Virtual de Agents
Os perfis detalhados do time estão em `.claude/team/`:
- `ENGINEER.md` – Engenheiro de Software Sênior (Flutter + Python + Supabase).
- `QA.md` – Engenheiro de Qualidade (testes Flutter, Python, fluxo de tarefas).
- `DEVOPS.md` – Responsável por ambientes, variáveis, deploy e observabilidade.
- `MOBILE.md` – Desenvolvedor Mobile Sênior focado no app Flutter.

Use também o comando de orquestração em `.claude/commands/reuniao-time.md` para alinhar as perspectivas dos quatro perfis ao planejar uma tarefa maior.

