# 🎨 Guia para Adicionar Logo do App

## 📋 Arquivos Necessários

Você precisa criar 4 imagens a partir da logo "ISP Tasks":

### 1. **icon.png** (1024x1024px)
- Ícone principal do app
- Fundo transparente ou sólido
- Formato: PNG
- Localização: `mobile/assets/icon.png`

### 2. **adaptive-icon.png** (1024x1024px)
- Ícone adaptativo para Android
- Apenas o símbolo WiFi + check (sem texto)
- Fundo transparente
- Localização: `mobile/assets/adaptive-icon.png`

### 3. **splash.png** (1284x2778px)
- Tela de abertura
- Logo centralizada
- Fundo branco ou gradiente
- Localização: `mobile/assets/splash.png`

### 4. **favicon.png** (48x48px)
- Ícone para web
- Versão pequena da logo
- Localização: `mobile/assets/favicon.png`

## 🎨 Especificações da Logo

Com base na imagem fornecida:
- **Cores principais:**
  - Azul escuro: #003366 (ISP)
  - Azul claro: #5B9BD5 (Tasks)
  - Gradiente WiFi: Verde/Azul (#7FD8BE → #5B9BD5)
  - Check: Verde claro (#9FD356)

## 🛠️ Como Criar os Ícones

### Opção 1: Usar Ferramenta Online
1. Acesse: https://www.appicon.co/
2. Upload da logo original
3. Gere todos os tamanhos automaticamente
4. Baixe e extraia para `mobile/assets/`

### Opção 2: Usar Figma/Photoshop
1. Abra a logo original
2. Redimensione para cada tamanho
3. Exporte como PNG
4. Salve em `mobile/assets/`

### Opção 3: Usar ImageMagick (Linha de comando)
```bash
# Instalar ImageMagick
# Windows: https://imagemagick.org/script/download.php

# Criar icon.png (1024x1024)
magick logo_original.png -resize 1024x1024 icon.png

# Criar adaptive-icon.png (1024x1024, sem texto)
magick logo_simbolo.png -resize 1024x1024 adaptive-icon.png

# Criar splash.png (1284x2778)
magick -size 1284x2778 xc:white logo_original.png -gravity center -composite splash.png

# Criar favicon.png (48x48)
magick logo_original.png -resize 48x48 favicon.png
```

## 📁 Estrutura Final

```
mobile/
└── assets/
    ├── icon.png          (1024x1024)
    ├── adaptive-icon.png (1024x1024)
    ├── splash.png        (1284x2778)
    └── favicon.png       (48x48)
```

## ✅ Checklist

- [ ] Criar icon.png (1024x1024)
- [ ] Criar adaptive-icon.png (1024x1024)
- [ ] Criar splash.png (1284x2778)
- [ ] Criar favicon.png (48x48)
- [ ] Colocar todos em `mobile/assets/`
- [ ] Verificar se app.json aponta para os arquivos corretos
- [ ] Fazer build novamente

## 🚀 Após Adicionar as Imagens

```bash
cd mobile

# Limpar cache
npx expo start -c

# Fazer build
eas build --platform android --profile preview
```

## 💡 Dicas

1. **Adaptive Icon:** Use apenas o símbolo WiFi + check, sem texto
2. **Splash Screen:** Centralize a logo com bastante espaço ao redor
3. **Cores:** Mantenha o gradiente azul/verde da logo original
4. **Qualidade:** Use PNG com alta resolução
5. **Fundo:** Adaptive icon deve ter fundo transparente

## 🎯 Recomendação Rápida

Se você tem a logo em alta resolução:
1. Salve como `icon.png` (1024x1024)
2. Copie para `adaptive-icon.png`
3. Use ferramenta online para gerar splash
4. Redimensione para favicon

Depois execute:
```bash
eas build --platform android --profile preview
```
