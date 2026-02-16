# 📱 Task Manager ISP - App Flutter

App mobile profissional em Flutter para gerenciamento de tarefas de campo para provedores de internet (ISP).

## 🎯 Funcionalidades Implementadas

### ✅ Autenticação
- Login com username/senha
- Persistência de sessão (FlutterSecureStorage)
- Logout seguro
- Integração com Supabase

### 📋 Gerenciamento de Tarefas
- **Dashboard** com estatísticas em tempo real
- **Lista de tarefas** com filtros (Todas, Pendentes, Em Andamento, Concluídas)
- **Detalhes completos** de cada tarefa
- **Atualização de status** em tempo real
- **Prioridades** com indicadores visuais
- **Alertas de prazo** vencido

### 📸 Execução de Tarefas
- Câmera integrada para fotos
- Seleção de múltiplas fotos da galeria
- Upload automático para Supabase Storage
- Campo de observações
- Mudança de status (Pendente → Em Andamento → Concluída)

### 🔔 Notificações
- Push notifications (Firebase Cloud Messaging)
- Notificações in-app
- Badge com contador de não lidas
- Marcar como lida individual ou todas

### 💬 Chat
- Chat em tempo real com gerente
- Interface moderna de mensagens
- Histórico de conversas

### 📊 Relatórios
- Estatísticas detalhadas
- Gráficos de pizza para distribuição de status
- Métricas de produtividade
- Histórico de tarefas concluídas

### 🔄 Modo Offline
- Cache local de tarefas (Hive)
- Sincronização automática quando voltar online
- Indicador de pendências
- Fila de atualizações offline

### 🎨 Interface
- **Material Design 3** profissional
- Tema claro e escuro
- Animações suaves
- Interface responsiva
- Cores corporativas (azul profissional)

## 🛠️ Tecnologias Utilizadas

### Core
- **Flutter SDK** 3.0+
- **Dart** 3.0+

### Backend & Database
- **Supabase Flutter** - Banco de dados e autenticação
- **PostgreSQL** - Banco relacional via Supabase

### State Management
- **Provider** - Gerenciamento de estado reativo

### Navigation
- **GoRouter** - Roteamento declarativo

### Storage
- **Hive** - Cache local para modo offline
- **FlutterSecureStorage** - Armazenamento seguro de credenciais
- **SharedPreferences** - Preferências do usuário

### UI/UX
- **Google Fonts** - Tipografia profissional (Inter)
- **FL Chart** - Gráficos e visualizações
- **Shimmer** - Loading skeletons
- **CachedNetworkImage** - Cache de imagens

### Features
- **Camera** - Captura de fotos
- **ImagePicker** - Seleção de imagens
- **GoogleMapsFlutter** - Mapas e localização
- **Geolocator** - Geolocalização
- **FirebaseMessaging** - Push notifications
- **Connectivity Plus** - Verificação de conectividade

## 📁 Estrutura do Projeto

```
flutter_task_manager/
├── lib/
│   ├── config/
│   │   ├── theme.dart              # Tema e cores
│   │   └── routes.dart             # Configuração de rotas
│   ├── models/
│   │   ├── user.dart               # Modelo de usuário
│   │   ├── task_assignment.dart    # Modelo de tarefa
│   │   ├── notification.dart       # Modelo de notificação
│   │   └── chat_message.dart       # Modelo de mensagem
│   ├── providers/
│   │   ├── auth_provider.dart      # Estado de autenticação
│   │   ├── task_provider.dart      # Estado de tarefas
│   │   ├── notification_provider.dart
│   │   ├── theme_provider.dart
│   │   └── offline_provider.dart
│   ├── services/
│   │   ├── supabase_service.dart   # Integração Supabase
│   │   ├── storage_service.dart    # Armazenamento local
│   │   ├── notification_service.dart
│   │   └── offline_service.dart
│   ├── screens/
│   │   ├── login_screen.dart
│   │   ├── home_screen.dart
│   │   ├── task_detail_screen.dart
│   │   ├── task_execute_screen.dart
│   │   ├── notifications_screen.dart
│   │   ├── profile_screen.dart
│   │   ├── completed_tasks_screen.dart
│   │   ├── chat_screen.dart
│   │   └── reports_screen.dart
│   ├── widgets/
│   │   ├── task_card.dart
│   │   └── stats_card.dart
│   └── main.dart
├── android/
├── ios/
└── pubspec.yaml
```

## 🚀 Como Executar

### Pré-requisitos
```bash
# Flutter SDK instalado
flutter --version  # Deve ser 3.0+

# Dependências do sistema
- Android Studio (para Android)
- Xcode (para iOS - apenas macOS)
- Node.js (para Firebase)
```

### Instalação

1. **Instalar dependências**
```bash
cd /app/flutter_task_manager
flutter pub get
```

2. **Configurar Firebase** (para push notifications)
```bash
# Baixar google-services.json do Firebase Console
# Colocar em: android/app/google-services.json

# Para iOS, baixar GoogleService-Info.plist
# Colocar em: ios/Runner/GoogleService-Info.plist
```

3. **Configurar Google Maps API Key**
```bash
# Android: android/app/src/main/AndroidManifest.xml
<meta-data
    android:name="com.google.android.geo.API_KEY"
    android:value="SUA_API_KEY_AQUI"/>

# iOS: ios/Runner/AppDelegate.swift
GMSServices.provideAPIKey("SUA_API_KEY_AQUI")
```

### Executar no Desenvolvimento

**Android:**
```bash
flutter run -d android
```

**iOS:**
```bash
flutter run -d ios
```

**Web (teste):**
```bash
flutter run -d chrome
```

### Build para Produção

**Android APK:**
```bash
flutter build apk --release
# APK gerado em: build/app/outputs/flutter-apk/app-release.apk
```

**Android App Bundle (Google Play):**
```bash
flutter build appbundle --release
# AAB gerado em: build/app/outputs/bundle/release/app-release.aab
```

**iOS:**
```bash
flutter build ios --release
# Depois, abrir no Xcode para assinar e fazer upload
```

## 🔧 Configuração

### Credenciais Supabase
As credenciais já estão configuradas em `lib/main.dart`:
```dart
await Supabase.initialize(
  url: 'https://ntatkxgsykdnsfrqxwnz.supabase.co',
  anonKey: 'sua_chave_aqui',
);
```

### Temas
Para alterar as cores, edite `lib/config/theme.dart`:
```dart
static const Color primaryColor = Color(0xFF1a73e8); // Azul profissional
```

## 📱 Telas do App

1. **Login** - Autenticação
2. **Home** - Dashboard com lista de tarefas e estatísticas
3. **Detalhes da Tarefa** - Informações completas, mapa, fotos
4. **Executar Tarefa** - Atualizar status, tirar fotos, observações
5. **Notificações** - Lista de notificações com badges
6. **Perfil** - Informações do usuário e configurações
7. **Chat** - Comunicação com gerente
8. **Relatórios** - Estatísticas e gráficos
9. **Tarefas Concluídas** - Histórico

## 🎨 Design System

### Cores Principais
- **Primary**: `#1a73e8` (Azul profissional)
- **Secondary**: `#34A853` (Verde sucesso)
- **Error**: `#EA4335` (Vermelho)
- **Warning**: `#FBBC04` (Amarelo)

### Status
- **Pendente**: Amarelo
- **Em Andamento**: Azul
- **Concluída**: Verde

### Tipografia
- **Fonte**: Inter (Google Fonts)
- **Estilo**: Profissional e limpo

## 🔐 Segurança

- ✅ Credenciais armazenadas com **FlutterSecureStorage**
- ✅ Tokens JWT para sessões
- ✅ Comunicação HTTPS com Supabase
- ✅ Validação de dados no cliente e servidor
- ✅ Upload seguro de fotos

## 📈 Performance

- ✅ Cache de imagens com **CachedNetworkImage**
- ✅ Cache local com **Hive** para modo offline
- ✅ Lazy loading de listas
- ✅ Otimização de builds
- ✅ Sincronização inteligente

## 🐛 Debug

```bash
# Verificar problemas
flutter doctor

# Logs em tempo real
flutter logs

# Limpar cache
flutter clean && flutter pub get
```

## 🚢 Deploy

### Android (Google Play)
1. Criar keystore para assinatura
2. Build do App Bundle: `flutter build appbundle`
3. Upload no Google Play Console

### iOS (App Store)
1. Configurar certificados no Xcode
2. Build: `flutter build ios`
3. Archive e upload via Xcode

## 📝 Credenciais de Teste

Use as credenciais existentes no sistema:
- **Usuário**: `jj.gc` ou `joao.tecnico`
- **Senha**: (conforme cadastrado no sistema)

## 🤝 Integração com Backend

O app se conecta diretamente ao Supabase (PostgreSQL):
- **Tabelas**: `users`, `task_assignments`, `assignment_photos`, `notifications`, `chat_messages`
- **Storage**: Bucket `task-photos`
- **Real-time**: Subscriptions para updates automáticos

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar documentação do Flutter
2. Verificar logs: `flutter logs`
3. Verificar conexão com Supabase

## 🎯 Próximos Passos

- [ ] Assinatura digital na conclusão
- [ ] Reconhecimento de voz para observações
- [ ] IA para otimização de rotas
- [ ] Modo offline avançado com sync inteligente
- [ ] Widget para home screen
- [ ] Deep links para notificações

---

**App Flutter Task Manager ISP v1.0** - Produtividade profissional no campo! 📱✨
