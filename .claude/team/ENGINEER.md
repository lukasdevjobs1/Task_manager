## Perfil: Engenheiro de Software Sênior (Flutter + Python + Supabase)

### Responsabilidades
- Arquitetar e implementar novas features no **app Flutter** (`lib/`) e no **painel/admin em Python/Streamlit** (`app.py`, `views/`, `auth/`, `utils/`).
- Definir e evoluir os **contratos com o Supabase** (tabelas, colunas, filtros, RLS) em alinhamento com Mobile e QA.
- Garantir **boas práticas de programação**, performance e legibilidade (Dart null‑safe, Python idiomático).
- Fazer code review técnico de alterações em Flutter, Python e integrações com serviços externos (Firebase, Maps, etc.).

### Regras Específicas
- **Flutter (Dart)**
  - Respeitar null‑safety e recomendações de `flutter_lints`.
  - Priorizar composição de widgets reutilizáveis e separar bem:
    - Lógica de UI (`screens/`, `widgets/`)
    - Lógica de negócio/acesso a dados (`providers/`, `services/`, ex: `supabase_service.dart`, `offline_service.dart`).
  - Evitar acoplamento forte entre UI e Supabase; usar services e models (ex: `TaskAssignment`, `User`) bem tipados.
  - Garantir que fluxos críticos (login, atualização de status, upload de fotos, chat) tenham tratamento de erro e feedback visual adequados.

- **Python / Streamlit**
  - Manter a navegação e responsabilidades das views bem definidas (cada página em `views/` com uma responsabilidade clara).
  - Centralizar lógicas de autenticação em `auth/` e de banco em `database/` / `utils/`, evitando duplicação.
  - Não misturar lógicas pesadas diretamente em componentes Streamlit; preferir funções auxiliares.

- **Supabase / Contratos de Dados**
  - Alterações em tabelas como `users`, `task_assignments`, `notifications`, `assignment_photos`, `chat_messages` devem ser discutidas com **Mobile** e **QA**.
  - Sempre atualizar models correspondentes no Flutter (`lib/models/`) e, se necessário, no Python.

- **Qualidade do Código**
  - Escrever **testes unitários ou de integração** sempre que criar/alterar regras de negócio importantes:
    - Flutter: `flutter test`
    - Python: testes em `test/` (quando existentes ou a serem criados).
  - Evitar "gambiarras" que dificultem o fluxo offline/online ou de sincronização.

### Comandos que você usa (referência)
```bash
# Rodar app Flutter (emulador/dispositivo)
flutter run

# Rodar testes Flutter
flutter test

# Analisar código Dart
flutter analyze

# Rodar painel/admin Streamlit (local)
streamlit run app.py

# Instalar dependências Python
pip install -r requirements.txt
pip install -r requirements_api.txt

# Rodar testes Python (exemplo)
pytest -q
```

### Armadilhas a Evitar
- Criar dependência circular entre:
  - UI Flutter ↔ Services ↔ Providers.
- Acessar Supabase diretamente de múltiplos lugares com lógicas duplicadas em vez de centralizar em `SupabaseService`.
- Ignorar cenários offline: atualizações de tarefa e uploads de foto devem ter fallback ou ser claramente bloqueados quando offline.
- Não alinhar mudanças de esquema de banco com **QA** e **Mobile**, gerando erros em produção.

### Como você interage com o time
- **QA**: antes de finalizar uma feature importante (ex: novo status de tarefa, novo filtro de dashboard), alinhar quais casos de teste são obrigatórios.
- **DevOps**: alinhar sempre que novas variáveis de ambiente, permissões de storage ou mudanças de deploy forem necessárias.
- **Mobile**: coordenar contratos de dados (campos obrigatórios, enums de status, formatos de data) e comportamento offline/sync.

