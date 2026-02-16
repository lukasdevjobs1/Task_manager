# 🚀 Guia de Configuração Rápida - Flutter Task Manager ISP

## ⚡ Setup Rápido (5 minutos)

### 1. Instalar Flutter SDK

**Windows:**
```bash
# Baixar de: https://flutter.dev/docs/get-started/install/windows
# Extrair e adicionar ao PATH
```

**macOS:**
```bash
brew install flutter
```

**Linux:**
```bash
sudo snap install flutter --classic
```

### 2. Verificar Instalação
```bash
flutter doctor
```

### 3. Instalar Dependências do Projeto
```bash
cd /app/flutter_task_manager
flutter pub get
```

## 📱 Executar no Emulador/Dispositivo

### Android

1. **Instalar Android Studio** e Android SDK
2. **Criar emulador** ou conectar dispositivo físico via USB
3. **Executar:**
```bash
flutter run
```

### iOS (apenas macOS)

1. **Instalar Xcode** da App Store
2. **Abrir simulador:**
```bash
open -a Simulator
```
3. **Executar:**
```bash
flutter run
```

## 🔑 Configurar APIs

### Google Maps API

1. **Obter API Key** em: https://console.cloud.google.com/google/maps-apis
2. **Android** - Editar `android/app/src/main/AndroidManifest.xml`:
```xml
<application>
    ...
    <meta-data
        android:name="com.google.android.geo.API_KEY"
        android:value="SUA_GOOGLE_MAPS_API_KEY"/>
</application>
```

3. **iOS** - Editar `ios/Runner/AppDelegate.swift`:
```swift
import GoogleMaps

@UIApplicationMain
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    GMSServices.provideAPIKey("SUA_GOOGLE_MAPS_API_KEY")
    GeneratedPluginRegistrant.register(with: self)
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}
```

### Firebase (Push Notifications)

1. **Criar projeto** em: https://console.firebase.google.com
2. **Adicionar app Android:**
   - Package name: `com.isp.task_manager`
   - Baixar `google-services.json`
   - Colocar em: `android/app/google-services.json`

3. **Adicionar app iOS:**
   - Bundle ID: `com.isp.taskManager`
   - Baixar `GoogleService-Info.plist`
   - Colocar em: `ios/Runner/GoogleService-Info.plist`

4. **Configurar Android** - Editar `android/build.gradle`:
```gradle
buildscript {
    dependencies {
        classpath 'com.google.gms:google-services:4.3.15'
    }
}
```

5. **Configurar Android** - Editar `android/app/build.gradle`:
```gradle
apply plugin: 'com.google.gms.google-services'
```

## 🔧 Problemas Comuns

### Erro: "Gradle build failed"
```bash
cd android
./gradlew clean
cd ..
flutter clean
flutter pub get
flutter run
```

### Erro: "CocoaPods not installed"
```bash
sudo gem install cocoapods
cd ios
pod install
cd ..
flutter run
```

### Erro: "Flutter SDK not found"
```bash
# Adicionar ao PATH
export PATH="$PATH:`pwd`/flutter/bin"
```

## 📦 Build para Produção

### Android Release APK
```bash
# Gerar APK
flutter build apk --release

# APK estará em:
# build/app/outputs/flutter-apk/app-release.apk
```

### Android App Bundle (Google Play)
```bash
# Gerar AAB
flutter build appbundle --release

# AAB estará em:
# build/app/outputs/bundle/release/app-release.aab
```

### iOS Release
```bash
# Build
flutter build ios --release

# Depois abrir no Xcode:
open ios/Runner.xcworkspace
# Archive → Distribute App → App Store Connect
```

## 🔐 Assinatura de App

### Android - Criar Keystore

```bash
keytool -genkey -v -keystore ~/key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias key
```

Editar `android/key.properties`:
```properties
storePassword=sua_senha
keyPassword=sua_senha
keyAlias=key
storeFile=/caminho/para/key.jks
```

Editar `android/app/build.gradle`:
```gradle
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile file(keystoreProperties['storeFile'])
            storePassword keystoreProperties['storePassword']
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
        }
    }
}
```

## 🧪 Testar no Dispositivo Físico

### Android

1. **Ativar modo desenvolvedor** no Android
2. **Ativar depuração USB**
3. **Conectar via USB**
4. **Verificar conexão:**
```bash
flutter devices
```
5. **Executar:**
```bash
flutter run
```

### iOS

1. **Abrir Xcode:** `ios/Runner.xcworkspace`
2. **Selecionar Team** em Signing & Capabilities
3. **Conectar iPhone via USB**
4. **Confiar no computador** no iPhone
5. **Executar pelo Xcode ou:**
```bash
flutter run
```

## 🌐 Testar no Web (Desenvolvimento)

```bash
flutter run -d chrome
```

## 📊 Performance e Otimização

### Analisar tamanho do app
```bash
flutter build apk --analyze-size
```

### Profile mode (debug de performance)
```bash
flutter run --profile
```

## 🛠️ Comandos Úteis

```bash
# Ver devices disponíveis
flutter devices

# Logs em tempo real
flutter logs

# Limpar cache e reconstruir
flutter clean && flutter pub get && flutter run

# Atualizar dependências
flutter pub upgrade

# Verificar problemas
flutter doctor -v

# Hot reload (durante desenvolvimento)
# Pressione 'r' no terminal

# Hot restart (reiniciar app)
# Pressione 'R' no terminal
```

## 📝 Variáveis de Ambiente

Criar arquivo `.env` (opcional):
```env
SUPABASE_URL=https://ntatkxgsykdnsfrqxwnz.supabase.co
SUPABASE_ANON_KEY=sua_key_aqui
GOOGLE_MAPS_API_KEY=sua_key_aqui
```

## ✅ Checklist de Deploy

- [ ] Testar em Android real
- [ ] Testar em iOS real (se aplicável)
- [ ] Configurar Firebase
- [ ] Configurar Google Maps
- [ ] Criar keystore Android
- [ ] Configurar signing iOS
- [ ] Testar push notifications
- [ ] Testar modo offline
- [ ] Build release e testar
- [ ] Preparar screenshots
- [ ] Preparar descrição da loja

## 🎯 Pronto para Desenvolvimento!

Agora você pode começar a desenvolver e testar o app:

```bash
cd /app/flutter_task_manager
flutter run
```

🚀 Happy coding!
