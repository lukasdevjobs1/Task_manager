# 📸 Correção: Câmera e Galeria

## ✅ Alterações Implementadas

### 1. **Upload Simplificado**
- Removida conversão Base64 (causava erros)
- Salva URI diretamente no banco
- Atualização imediata da lista de fotos

### 2. **Tratamento de Erros**
- Try-catch em todas as funções
- Mensagens de erro detalhadas
- Validação de permissões

### 3. **Permissões Android Atualizadas**
```json
"permissions": [
  "CAMERA",
  "READ_EXTERNAL_STORAGE",
  "WRITE_EXTERNAL_STORAGE",
  "READ_MEDIA_IMAGES"
]
```

### 4. **Plugin expo-image-picker Configurado**
- Mensagens de permissão personalizadas
- Configuração correta para Android/iOS

## 🚀 Como Testar

### 1. Reinstalar Dependências
```bash
cd mobile
npm install expo-image-picker
```

### 2. Fazer Novo Build
```bash
eas build --platform android --profile preview
```

### 3. Testar no App
1. Abra uma tarefa
2. Clique em "Câmera" ou "Galeria"
3. Conceda permissões quando solicitado
4. Tire/selecione uma foto
5. Verifique se aparece na lista

## 🐛 Troubleshooting

### Galeria não abre:
```bash
# Verificar se o plugin está instalado
npm list expo-image-picker

# Reinstalar se necessário
npm install expo-image-picker@~17.0.10
```

### Câmera não funciona:
- Verifique se o dispositivo tem câmera
- Conceda permissões manualmente em Configurações > Apps > Tarefas ISP

### Fotos não salvam:
- Verifique conexão com Supabase
- Cheque logs: `npx expo start`
- Valide tabela `assignment_photos` no banco

## 📋 Checklist

- [x] Upload simplificado (sem base64)
- [x] Permissões atualizadas
- [x] Plugin expo-image-picker configurado
- [x] Tratamento de erros
- [ ] Reinstalar dependências
- [ ] Fazer novo build
- [ ] Testar câmera
- [ ] Testar galeria
- [ ] Validar salvamento

## 🔧 Comandos Rápidos

```bash
# Limpar e reinstalar
cd mobile
rm -rf node_modules
npm install

# Build
eas build --platform android --profile preview

# Ou build local para teste rápido
npx expo run:android
```

## 📱 Teste Manual

1. **Câmera:**
   - Abrir tarefa
   - Clicar "Câmera"
   - Permitir acesso
   - Tirar foto
   - Confirmar
   - Verificar se aparece

2. **Galeria:**
   - Abrir tarefa
   - Clicar "Galeria"
   - Permitir acesso
   - Selecionar foto
   - Confirmar
   - Verificar se aparece

3. **Salvamento:**
   - Adicionar 2-3 fotos
   - Clicar "Salvar"
   - Voltar e reabrir tarefa
   - Verificar se fotos persistiram

## ✅ Resultado Esperado

- ✅ Câmera abre normalmente
- ✅ Galeria abre e mostra fotos
- ✅ Fotos aparecem na lista imediatamente
- ✅ Fotos são salvas no banco
- ✅ Fotos persistem após reabrir tarefa
- ✅ Gerente vê fotos no Streamlit

---

**Status:** ✅ Pronto para novo build e teste
