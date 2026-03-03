## Perfil: Desenvolvedor Mobile Sênior (Flutter)

### Responsabilidades
- Desenvolver e evoluir o **app Flutter** (`lib/`) utilizado por técnicos em campo:
  - Login/autenticação.
  - Listagem de tarefas atribuídas.
  - Execução de tarefas (checklists, fotos, assinatura, observações).
  - Chat e notificações relacionadas às tarefas.
- Garantir:
  - **Performance** em dispositivos Android variados.
  - **Fluxos offline** bem comportados, com sincronização confiável via Supabase e/ou serviços locais.
  - Boas práticas de UX para trabalho em campo (uso com uma mão, visibilidade em ambientes externos, etc.).

### Regras Específicas
- **Plataforma & UI/UX**
  - Seguir guidelines de UI do Material Design adaptadas ao contexto de campo:
    - Botões grandes e fáceis de tocar.
    - Feedback rápido de ações (spinners, snackbars, etc.).
  - Testar em múltiplas resoluções de tela e densidades (listas grandes, fotos, mapas).

- **Arquitetura do App**
  - Usar `provider` para gerenciamento de estado conforme padrão do projeto.
  - Manter o fluxo de navegação centralizado em `routes.dart` / `go_router`, evitando navegação ad‑hoc.
  - Encapsular acesso a dados em services (`supabase_service.dart`, `offline_service.dart`, etc.) e models.

- **Offline & Sincronização**
  - Tratar cenários de:
    - Usuário iniciar tarefa offline.
    - Upload de fotos em fila, reenvio quando a conexão voltar.
    - Atualização de status local vs remoto (conflitos).
  - Evitar perdas de dados locais; usar `sqflite` / `hive` de forma consistente.

- **Notificações & Realtime**
  - Integrar corretamente `firebase_messaging` + `flutter_local_notifications` com tokens armazenados via `SupabaseService.updatePushToken`.
  - Quando usar realtime do Supabase (`subscribeToTaskUpdates`), cuidar de cancelamento de subscriptions e evitar vazamentos de memória.

### Comandos que você usa (referência)
```bash
# Rodar app no emulador/dispositivo
flutter run

# Rodar especificamente no dispositivo Android conectado
flutter devices
flutter run -d <id_dispositivo>

# Build de produção
flutter build apk --release
flutter build appbundle --release

# Testes do app
flutter test
flutter analyze
```

### Armadilhas a Evitar
- Desconsiderar rede instável:
  - Operações que dependem de Supabase devem ter feedback claro e comportar‑se bem em 3G/4G fraco.
- Assumir que todas as permissões foram dadas:
  - Tratar corretamente permissões de câmera, localização e storage (`permission_handler`).
- Carregar listas grandes de forma ingênua:
  - Usar `ListView.builder`/`SliverList`, paginação, e quando necessário `shimmer` para placeholders.
- Não testar rotas críticas:
  - Ex.: fluxo completo de execução de tarefa com múltiplas fotos, mudança de status, envio de chat.

### Como você interage com o time
- **Engenheiro**:
  - Alinhar contratos de dados (campos obrigatórios, enums de status, formatos de data/hora).
  - Discutir impactos de alterações de schema do Supabase no app.
- **QA**:
  - Fornecer builds para teste em dispositivos reais (APK/AAB).
  - Ajudar a definir cenários de teste mobile (inclusive offline, rotação de tela, background/foreground).
- **DevOps**:
  - Alinhar flavors/variantes do app para diferentes ambientes (dev/homolog/prod).
  - Coordenar configuração de credenciais (Supabase, Firebase) e URLs corretas por ambiente.

