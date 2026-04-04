# Guia: Deploy no Render

Este documento descreve como fazer deploy da aplicação Food Label Analyzer no Render.

---

## 📋 Pré-requisitos

- ✅ Código versionado no GitHub
- ✅ `requirements.txt` atualizado (backend)
- ✅ `.env.production.template` configurado
- ✅ Conta no Render (gratuita)

---

## 🚀 Passo 1: Criar Conta no Render

1. Acesse [render.com](https://render.com)
2. Clique em **Sign Up**
3. Escolha **Sign up with GitHub** (recomendado)
4. Autorize Render a acessar seus repositórios

---

## 📱 Passo 2: Conectar Repositório GitHub

1. No Render Dashboard, clique em **New +**
2. Selecione **Web Service**
3. Clique em **Connect a repository**
4. Selecione o repositório `tcc-food-label-analyzer`
5. Clique em **Connect**

---

## ⚙️ Passo 3: Configurar Web Service

### Nome e Plano

```
Name: food-label-analyzer-api
Environment: Python 3
Region: Ohio (ou mais próximo)
Branch: main
Build Command: (deixe em branco por enquanto)
Start Command: (deixe em branco por enquanto)
Plan: Free
```

### Build & Start Commands

Na página de criação do service:

**Build Command:**
```bash
cd apps/backend && pip install -r requirements.txt
```

**Start Command:**
```bash
cd apps/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 🔐 Passo 4: Configurar Variáveis de Ambiente

1. Após criar o Web Service, vá para **Environment**
2. Clique em **Add Environment Variable** para cada variável:

### Variáveis Necessárias

| Key | Value |
|-----|-------|
| `APP_ENV` | `production` |
| `DEBUG` | `false` |
| `GOOGLE_VISION_TIMEOUT_SECONDS` | `15` |
| `GOOGLE_CREDENTIALS_JSON` | `(seu JSON aqui)` |

### Como Preencher `GOOGLE_CREDENTIALS_JSON`

**Opção 1: JSON Direto (Simples)**

1. Abra seu arquivo `google-credentials.json` local
2. Copie TODO o conteúdo (é um JSON grande)
3. Cole no value do Render:

```
Key: GOOGLE_CREDENTIALS_JSON
Value: {"type":"service_account","project_id":"...","private_key":"...","client_email":"...",...}
```

**Opção 2: Base64 (Se tiver problemas de caracteres)**

1. No terminal, encode o arquivo:
   ```bash
   # macOS/Linux
   cat apps/backend/google-credentials.json | base64 -w 0
   
   # Windows PowerShell
   $content = Get-Content apps/backend/google-credentials.json -Raw
   [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($content))
   ```

2. Cole a string em Base64:
   ```
   Key: GOOGLE_CREDENTIALS_JSON
   Value: eyJ0eXBlIjoic2VydmljZV9hY2NvdW50IiwicHJvamVjdF9pZCI6Ii4uLiIsLi4ufQ==
   ```

3. O código já decodifica automaticamente!

---

## 🎯 Passo 5: Deploy

Depois de salvar as variáveis:

1. Clique em **Deploy** (ou **Re-deploy**)
2. Acompanhe o build nos logs:
   ```
   Starting build...
   Installing dependencies...
   Running start command...
   ```

3. Quando terminar, seu app estará em:
   ```
   https://food-label-analyzer-api.onrender.com
   ```

---

## ✅ Verificar Deploy

### URL da API

```
https://food-label-analyzer-api.onrender.com/docs
```

(FastAPI cria documentação automática Swagger)

### Testar Endpoint

```bash
curl https://food-label-analyzer-api.onrender.com/health

# Ou via Python
import requests
response = requests.get("https://food-label-analyzer-api.onrender.com/health")
print(response.json())
```

### Ver Logs

No Render Dashboard:
- Clique no seu service
- Vá para **Logs**
- Veja logs em tempo real

---

## 🔄 Atualizações Futuras

Depois do deploy inicial, as atualizações são automáticas:

```bash
# Faça mudanças locais
git add .
git commit -m "Fix: melhorias na API"
git push origin main

# Render detecta e faz deploy automaticamente!
```

---

## 🆘 Troubleshooting

### Erro: "Build failed"

**Causa**: `requirements.txt` não encontrado ou faltam dependências

**Solução**:
```bash
# Verifique se exists
ls apps/backend/requirements.txt

# Gere se não existir
cd apps/backend
pip freeze > requirements.txt
```

### Erro: "Application failed to start"

**Causa**: Credenciais não configuradas ou JWT inválido

**Solução**:
1. Verifique logs no Render
2. Confirme `GOOGLE_CREDENTIALS_JSON` foi salva
3. Se for Base64, verifique se decodifica corretamente:
   ```python
   import base64
   decoded = base64.b64decode("seu_base64_aqui").decode("utf-8")
   print(decoded)  # Deve ser JSON válido
   ```

### App fica "In Progress" por muito tempo

**Causa**: Build está lento (normal)

**Solução**:
- Primeira build leva 3-5 min
- Builds posteriores são mais rápidas
- Se tomar 10+ min, verifique erros nos logs

### Erro: "500 Internal Server Error"

**Causa**: Credenciais inválidas ou Google Vision API retornou erro

**Solução**:
1. Teste localmente com a mesma credencial
2. Verifique se API está habilitada no Google Cloud
3. Revise logs detalhados

---

## 📝 Configuração do `render.yaml` (Opcional)

Para automatizar ainda mais, você pode criar um arquivo `render.yaml` no repo:

```yaml
services:
  - type: web
    name: food-label-analyzer-api
    env: python
    region: ohio
    startCommand: cd apps/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
    buildCommand: cd apps/backend && pip install -r requirements.txt
    plan: free
    envVars:
      - key: APP_ENV
        value: production
      - key: DEBUG
        value: "false"
      - key: GOOGLE_VISION_TIMEOUT_SECONDS
        value: "15"
      - key: GOOGLE_CREDENTIALS_JSON
        sync: false
```

Depois, no Render, ao criar o service, ele detecta automaticamente!

---

## 🎉 Pronto!

Sua aplicação está no ar! 

### Próximas etapas:

1. **Teste a API**:
   ```bash
   curl https://food-label-analyzer-api.onrender.com/docs
   ```

2. **Integre com app mobile** (Leo) - use a URL do Render

3. **Configure CI/CD** (opcional):
   - GitHub Actions para testar antes de deploy
   - Webhook do Render para notificações

---

## 📚 Referências

- [Render Docs - Python](https://render.com/docs/deploy-python)
- [Render Docs - Environment Variables](https://render.com/docs/environment-variables)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Google Cloud - Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
