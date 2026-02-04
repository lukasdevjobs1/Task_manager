# ⚠️ Aviso: Build Local

## Erro Comum

Se você recebeu este erro:
```
CommandError: No Android connected device found, and no emulators could be started automatically.
```

**Isso foi corrigido!** O script agora usa o Gradle diretamente e **NÃO precisa de dispositivo conectado**.

---

## ✅ Solução Aplicada

O script `build-apk-local.bat` foi atualizado para:
- ✅ Usar `gradlew assembleRelease` diretamente
- ✅ **NÃO** tentar instalar no dispositivo
- ✅ Gerar apenas a APK sem precisar de dispositivo/emulador

---

## 🚀 Como Usar Agora

1. Execute: `GERAR_APK_AGORA.bat`
2. Escolha opção **2** (Build Local)
3. Aguarde o build (não precisa de dispositivo!)

---

## 📋 Pré-requisitos para Build Local

- ✅ Node.js instalado
- ✅ Java JDK 17+ instalado
- ✅ Android Studio instalado
- ✅ Android SDK configurado
- ✅ Variável `ANDROID_HOME` configurada
- ❌ **NÃO precisa de dispositivo Android conectado**

---

## 💡 Recomendação

Se você não tem Android Studio configurado, use a **Opção 1 (EAS Build)**:
- ✅ Não precisa de Android Studio
- ✅ Não precisa configurar nada
- ✅ Build na nuvem (mais fácil)

---

## 🔧 Se Ainda Tiver Problemas

### Erro: "Gradle não encontrado"
- Certifique-se de que o `prebuild` foi executado com sucesso
- O diretório `android` deve existir

### Erro: "ANDROID_HOME não definido"
- Configure a variável de ambiente `ANDROID_HOME`
- Exemplo: `C:\Users\SeuUsuario\AppData\Local\Android\Sdk`

### Erro: "Java não encontrado"
- Instale Java JDK 17+
- Configure `JAVA_HOME` ou adicione ao PATH

---

## ✅ Alternativa: EAS Build

Se o build local continuar dando problemas, use o EAS Build:

```bash
cd mobile
build-apk-eas-melhorado.bat
```

É mais fácil e não requer configuração local!

