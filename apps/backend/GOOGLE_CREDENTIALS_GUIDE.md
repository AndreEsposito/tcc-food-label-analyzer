# Guia: Gerenciamento de Ambientes e Credenciais

Este documento explica como gerenciar configurações e credenciais do Google Vision API em diferentes ambientes usando **templates seguro para versionamento**.

---

## 🔒 Estratégia de Segurança: Templates + .gitignore

O projeto usa uma abordagem **template-based** que permite versionamento seguro:

### Arquivos Versionados (Seguros - Sem Credenciais)

```
✅ .env.local.template       → Template com placeholders
✅ .env.production.template  → Template com placeholders
```

### Arquivos Ignorados pelo Git (Credenciais Reais)

```
❌ .env.local
❌ .env.production
❌ google-credentials.json
```

**Benefício**: Documentação de estrutura versionada, credenciais protegidas!

---

## 📍 Ambientes Suportados

A aplicação suporta dois ambientes:

| Ambiente | Template | Uso |
|----------|----------|-----|
| **local** | `.env.local.template` | Desenvolvimento na máquina local |
| **production** | `.env.production.template` | Servidor em produção (Render, AWS, etc) |

---

## ⚡ Setup Rápido (Primeira Vez)

### Linux/macOS

```bash
cd tcc-food-label-analyzer/

# Executar script de setup
./setup-env.sh

# Configurar credenciais
cd apps/backend
nano .env.local
```

### Windows (PowerShell)

```powershell
cd tcc-food-label-analyzer\

# Executar script de setup
.\setup-env.ps1

# Configurar credenciais
cd apps/backend
notepad .env.local
```

---

## 🔧 Como a Aplicação Escolhe o .env

A aplicação detecta automaticamente qual arquivo `.env` carregar:

### Ordem de Prioridade

1. **Variável de ambiente `APP_ENV`** (se definida)
   ```bash
   export APP_ENV=production
   # Carrega: .env.production
   ```

2. **Detecção automática** (se `APP_ENV` não estiver definida)
   - Verifica se `.env.local` existe → usa `.env.local`
   - Caso contrário, verifica `.env.production`

---

## 📋 Estrutura dos Arquivos `.env`

### `.env.local` (Desenvolvimento)

Criada a partir de `.env.local.template`:

```env
APP_ENV=local
DEBUG=true
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
GOOGLE_VISION_TIMEOUT_SECONDS=10
```

### `.env.production` (Produção)

Criada a partir de `.env.production.template`:

```env
APP_ENV=production
DEBUG=false
GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'
GOOGLE_VISION_TIMEOUT_SECONDS=15
```

---

## 🚀 Setup: Desenvolvimento Local

### 1. Clonar e Executar Setup

```bash
git clone <repo>
cd tcc-food-label-analyzer/
./setup-env.sh  # Cria .env.local a partir do template
```

### 2. Obter Credenciais do Google Cloud

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie/abra um projeto
3. Ative a API **Cloud Vision API**
4. Crie uma **Service Account**
5. Baixe a chave em formato JSON

### 3. Configurar .env.local

```bash
cd apps/backend

# Edite com seu editor favorito
nano .env.local

# Preencha:
# GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
# (Já pré-configurado no template)
```

### 4. Colocar Credenciais

```bash
# Copie o arquivo JSON obtido do Google Cloud
cp ~/Downloads/google-credentials.json ./google-credentials.json

# Verifique se está seguro em .gitignore
cat ../.gitignore | grep google-credentials
```

### 5. Executar

```bash
python -m uvicorn app.main:app
# Carrega .env.local automaticamente
```

---

## 🌐 Deploy no Render

### Opção 1: Usar Variáveis de Ambiente (Recomendado)

Render carrega variáveis diretamente, sem precisar de `.env.production`:

1. Acesse [Render Dashboard](https://dashboard.render.com/)
2. Vá para **Environment**
3. Adicione cada variável:

```
APP_ENV              → production
DEBUG                → false
GOOGLE_CREDENTIALS_JSON → {"type":"service_account",...}
GOOGLE_VISION_TIMEOUT_SECONDS → 15
DATABASE_URL         → postgresql://...
SECRET_KEY           → <gerar novo>
```

4. Deploy normalmente

### Opção 2: Usar .env.production (Alternativo)

Se preferir usar arquivo `.env.production` local no Render:

```bash
# Criar a partir do template
cp .env.production.template .env.production

# Editar com suas credenciais
nano .env.production

# Comitar (OU usar como variável de ambiente)
git add .env.production
git commit -m "Configure production environment"
```

⚠️ **Cuidado**: Se commitar, certifique-se de que credenciais não sensíveis.

---

## 🔐 Segurança

### ✅ Melhores Práticas

- ✅ Use templates versionados (`.template`)
- ✅ Nunca commite arquivos `.env` reais
- ✅ Nunca commite `google-credentials.json`
- ✅ Use variáveis de ambiente em produção (Render, AWS, etc)
- ✅ Revise permissões da Service Account (mínimo necessário)
- ✅ Gere `SECRET_KEY` com `secrets.token_urlsafe(32)`

### ❌ O Que Evitar

- ❌ Commitar `.env.local` ou `.env.production` reais
- ❌ Commitar credenciais do Google Cloud
- ❌ Usar mesma `SECRET_KEY` em dev e prod
- ❌ Deixar `DEBUG=true` em produção
- ❌ Compartilhar arquivos `.env` em repositórios

---

## ⚙️ Como a Configuração Funciona (Internamente)

O arquivo `app/core/config.py` implementa a detecção automática:

```python
def _get_env_file() -> str:
    """Detecta e retorna o arquivo .env apropriado"""
    app_env = os.getenv("APP_ENV", "").lower()
    
    if app_env:
        return f".env.{app_env}"  # .env.production, .env.local, etc
    
    # Detecção automática
    if Path(".env.local").exists():
        return ".env.local"
    elif Path(".env.production").exists():
        return ".env.production"
    
    return ".env.local"  # Padrão: desenvolvimento
```

---

## ❓ Troubleshooting

### Erro: `.env.local` não encontrado

**Causa**: Script de setup não foi executado.

**Solução**:
```bash
# Linux/macOS
./setup-env.sh

# Windows
.\setup-env.ps1

# Ou manualmente
cp apps/backend/.env.local.template apps/backend/.env.local
```

### Erro: `Credenciais não configuradas`

**Causa**: `google-credentials.json` não está no lugar certo.

**Solução**:
```bash
cd apps/backend
ls -la google-credentials.json  # Verificar se existe
cat .env.local | grep GOOGLE    # Verificar configuração
```

### Erro: `Invalid JSON in GOOGLE_CREDENTIALS_JSON`

**Causa**: JSON foi corrompido ao colar.

**Solução**:
1. Valide o JSON: [jsonlint.com](https://www.jsonlint.com/)
2. Copie novamente com cuidado
3. Teste com um JSON simples primeiro

---

## 📚 Arquivos Relevantes

- [setup-env.sh](../../setup-env.sh) — Script de setup (Linux/macOS)
- [setup-env.ps1](../../setup-env.ps1) — Script de setup (Windows)
- [app/core/config.py](./app/core/config.py) — Detecção de ambientes
- [.env.local.template](./.env.local.template) — Template desenvolvimento
- [.env.production.template](./.env.production.template) — Template produção
- [.env.example](./.env.example) — Referência rápida

---

## 📖 Referências

- [Pydantic Settings - Multiple Environments](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Render - Environment Variables](https://render.com/docs/environment-variables)
- [Google Cloud - Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [Python dotenv](https://github.com/theskumar/python-dotenv)

---

## 🔧 Como a Aplicação Escolhe o .env

A aplicação detecta automaticamente qual arquivo `.env` carregar:

### Ordem de Prioridade

1. **Variável de ambiente `APP_ENV`** (se definida)
   ```bash
   export APP_ENV=production
   # Carrega: .env.production
   ```

2. **Detecção automática** (se `APP_ENV` não estiver definida)
   - Verifica se `.env.local` existe → usa `.env.local`
   - Caso contrário, verifica `.env.production`
   - Fallback: `.env` genérico

### Exemplos

**Desenvolvimento Local:**
```bash
# Não precisa definir APP_ENV
# A aplicação busca .env.local automaticamente

python -m uvicorn app.main:app
# Carrega: .env.local
```

**Produção no Render:**
```bash
# Defina no painel do Render
APP_ENV=production

# ou via linha de comando
export APP_ENV=production
python -m uvicorn app.main:app
# Carrega: .env.production
```

---

## 📋 Estrutura dos Arquivos `.env`

### `.env.local` (Desenvolvimento)

```env
APP_ENV=local
DEBUG=true
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
GOOGLE_VISION_TIMEOUT_SECONDS=10
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=dev-secret-key
```

**Notas:**
- Use arquivo JSON local de credenciais
- `DEBUG=true` para logs detalhados
- Database SQLite para simplicidade

### `.env.production` (Produção)

```env
APP_ENV=production
DEBUG=false
GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'
GOOGLE_VISION_TIMEOUT_SECONDS=15
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=your-production-secret-key
```

**Notas:**
- Credenciais via variável (JSON ou Base64)
- `DEBUG=false` 
- Database externo recomendado

---

## 🚀 Setup: Desenvolvimento Local

### 1. Obter Credenciais do Google Cloud

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie/abra um projeto
3. Ative a API **Cloud Vision API**
4. Crie uma **Service Account**
5. Baixe a chave em formato JSON

### 2. Salvar Localmente

```bash
cd apps/backend

# Coloque o arquivo JSON obtido
# Verifique se está em .gitignore
cat .gitignore | grep google-credentials.json
```

Arquivo deve estar no `.gitignore`:
```
google-credentials.json
```

### 3. Usar `.env.local`

O arquivo `.env.local` já está pronto. Basta executar:

```bash
cd apps/backend
python -m uvicorn app.main:app
```

A aplicação carregará `.env.local` automaticamente.

---

## 🌐 Deploy no Render

### Passo 1: Preparar Credenciais

Você tem **2 opções**:

#### Opção A: JSON String Direto (Simples)

```bash
# Copie TODO o conteúdo de google-credentials.json
cat google-credentials.json
```

Resultado (exemplo):
```json
{"type":"service_account","project_id":"my-project","private_key":"...","client_email":"...","...":"..."}
```

#### Opção B: Base64 (Se JSON tiver caracteres especiais)

```bash
# macOS/Linux
cat google-credentials.json | base64 -w 0

# Windows PowerShell
$content = Get-Content google-credentials.json -Raw
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($content))
```

### Passo 2: Adicionar Variáveis no Render

1. Acesse seu projeto no [Render Dashboard](https://dashboard.render.com/)
2. Vá para a aba **Environment**
3. Clique em **Add Environment Variable**

**Variável 1:**
```
Key: APP_ENV
Value: production
```

**Variável 2 (Opção A - JSON Direto):**
```
Key: GOOGLE_CREDENTIALS_JSON
Value: {"type":"service_account","project_id":"..."}
```

**Variável 2 (Opção B - Base64):**
```
Key: GOOGLE_CREDENTIALS_JSON
Value: eyJ0eXBlIjoic2VydmljZV9hY2NvdW50Iiw...
```

### Passo 3: Fazer Deploy

```bash
git push render main
```

Render detectará `APP_ENV=production` e carregará automaticamente `.env.production`.

---

## 🔐 Segurança

### ✅ Melhores Práticas

- ✅ Nunca commite `google-credentials.json`
- ✅ Nunca commite `.env.local` ou `.env.production`  
- ✅ Use variáveis de ambiente em produção
- ✅ Revise permissões da Service Account (mínimo necessário)
- ✅ Use HTTPS em produção
- ✅ Gere `SECRET_KEY` com `secrets.token_urlsafe(32)`

### ❌ O Que Evitar

- ❌ Commitar credenciais no GitHub
- ❌ Usar mesma `SECRET_KEY` em dev e prod
- ❌ Deixar `DEBUG=true` em produção
- ❌ Compartilhar arquivos `.env` em repositórios públicos

---

## ⚙️ Como a Configuração Funciona (Internamente)

O arquivo `app/core/config.py` implementa a detecção automática:

```python
def _get_env_file() -> str:
    """Detecta e retorna o arquivo .env apropriado"""
    app_env = os.getenv("APP_ENV", "").lower()
    
    if app_env:
        return f".env.{app_env}"  # .env.production, .env.local, etc
    
    # Detecção automática
    if Path(".env.local").exists():
        return ".env.local"
    elif Path(".env.production").exists():
        return ".env.production"
    
    return ".env"  # Fallback
```

---

## ❓ Troubleshooting

### Erro: `Credenciais não configuradas`

**Causa**: Nenhum arquivo `.env` foi encontrado ou `GOOGLE_CREDENTIALS_JSON` está vazio.

**Solução**:
```bash
# Local
ls -la .env.local
cat .env.local | grep GOOGLE

# Render - Verificar logs
```

### Erro: `Invalid JSON in GOOGLE_CREDENTIALS_JSON`

**Causa**: JSON foi corrompido ao colar ou Base64 não foi decodificado corretamente.

**Solução**:
1. Valide o JSON: [jsonlint.com](https://www.jsonlint.com/)
2. Se usar Base64, decodifique e valide
3. Copie novamente com cuidado

### A aplicação carrega `.env.production` quando deveria carregar `.env.local`

**Causa**: `APP_ENV` pode estar definida no seu shell.

**Solução**:
```bash
# Verifique
echo $APP_ENV

# Limpe (se necessário)
unset APP_ENV
```

---

## 📚 Arquivos Relevantes

- [app/core/config.py](./app/core/config.py) — Detecção de ambientes
- [.env.example](./.env.example) — Exemplo de configuração
- [.env.local](./.env.local) — Desenvolvimento
- [.env.production](./.env.production) — Produção
- [GOOGLE_CREDENTIALS_GUIDE.md](./GOOGLE_CREDENTIALS_GUIDE.md) — Este arquivo

---

## 📖 Referências

- [Pydantic Settings - Multiple Environments](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Render - Environment Variables](https://render.com/docs/environment-variables)
- [Google Cloud - Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [Python dotenv](https://github.com/theskumar/python-dotenv)

---

## 🔧 Como a Aplicação Escolhe o .env

A aplicação detecta automaticamente qual arquivo `.env` carregar:

### Ordem de Prioridade

1. **Variável de ambiente `APP_ENV`** (se definida)
   ```bash
   export APP_ENV=production
   # Carrega: .env.production
   ```

2. **Detecção automática** (se `APP_ENV` não estiver definida)
   - Verifica se `.env.local` existe → usa `.env.local`
   - Caso contrário, verifica `.env.production`
   - Fallback: `.env` genérico

### Exemplos

**Desenvolvimento Local:**
```bash
# Não precisa definir APP_ENV
# A aplicação busca .env.local automaticamente

python -m uvicorn app.main:app
# Carrega: .env.local
```

**Produção no Render:**
```bash
# Defina no painel do Render
APP_ENV=production

# ou via linha de comando
export APP_ENV=production
python -m uvicorn app.main:app
# Carrega: .env.production
```

---

## 📋 Estrutura dos Arquivos `.env`

### `.env.local` (Desenvolvimento)

```env
APP_ENV=local
DEBUG=true
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
GOOGLE_VISION_TIMEOUT_SECONDS=10
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=dev-secret-key
```

**Notas:**
- Use arquivo JSON local de credenciais
- `DEBUG=true` para logs detalhados
- Database SQLite para simplicidade

### `.env.production` (Produção)

```env
APP_ENV=production
DEBUG=false
GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'
GOOGLE_VISION_TIMEOUT_SECONDS=15
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=your-production-secret-key
```

**Notas:**
- Credenciais via variável (JSON ou Base64)
- `DEBUG=false` 
- Database externo recomendado

### `.env.staging` (Testes)

Similar ao `.env.production`, mas com URLs de staging.

---

## 🚀 Setup: Desenvolvimento Local

### 1. Obter Credenciais do Google Cloud

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie/abra um projeto
3. Ative a API **Cloud Vision API**
4. Crie uma **Service Account**
5. Baixe a chave em formato JSON

### 2. Salvar Localmente

```bash
cd apps/backend

# Coloque o arquivo JSON obtido
# Verifique se está em .gitignore
cat .gitignore | grep google-credentials.json
```

Arquivo deve estar no `.gitignore`:
```
google-credentials.json
```

### 3. Usar `.env.local`

O arquivo `.env.local` já está pronto. Basta executar:

```bash
cd apps/backend
python -m uvicorn app.main:app
```

A aplicação carregará `.env.local` automaticamente.

---

## 🌐 Deploy no Render

### Passo 1: Preparar Credenciais

Você tem **2 opções**:

#### Opção A: JSON String Direto (Simples)

```bash
# Copie TODO o conteúdo de google-credentials.json
cat google-credentials.json
```

Resultado (exemplo):
```json
{"type":"service_account","project_id":"my-project","private_key":"...","client_email":"...","...":"..."}
```

#### Opção B: Base64 (Se JSON tiver caracteres especiais)

```bash
# macOS/Linux
cat google-credentials.json | base64 -w 0

# Windows PowerShell
$content = Get-Content google-credentials.json -Raw
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($content))
```

### Passo 2: Adicionar Variáveis no Render

1. Acesse seu projeto no [Render Dashboard](https://dashboard.render.com/)
2. Vá para a aba **Environment**
3. Clique em **Add Environment Variable**

**Variável 1:**
```
Key: APP_ENV
Value: production
```

**Variável 2 (Opção A - JSON Direto):**
```
Key: GOOGLE_CREDENTIALS_JSON
Value: {"type":"service_account","project_id":"..."}
```

**Variável 2 (Opção B - Base64):**
```
Key: GOOGLE_CREDENTIALS_JSON
Value: eyJ0eXBlIjoic2VydmljZV9hY2NvdW50Iiw...
```

### Passo 3: Fazer Deploy

```bash
git push render main
```

Render detectará `APP_ENV=production` e carregará automaticamente `.env.production`.

---

## 🔐 Segurança

### ✅ Melhores Práticas

- ✅ Nunca commite `google-credentials.json`
- ✅ Nunca commite `.env.local` ou `.env.production`  
- ✅ Use variáveis de ambiente em produção
- ✅ Revise permissões da Service Account (mínimo necessário)
- ✅ Use HTTPS em produção
- ✅ Gere `SECRET_KEY` com `secrets.token_urlsafe(32)`

### ❌ O Que Evitar

- ❌ Commitar credenciais no GitHub
- ❌ Usar mesma `SECRET_KEY` em dev e prod
- ❌ Deixar `DEBUG=true` em produção
- ❌ Compartilhar arquivos `.env` em repositórios públicos

---

## ⚙️ Como a Configuração Funciona (Internamente)

O arquivo `app/core/config.py` implementa a detecção automática:

```python
def _get_env_file() -> str:
    """Detecta e retorna o arquivo .env apropriado"""
    app_env = os.getenv("APP_ENV", "").lower()
    
    if app_env:
        return f".env.{app_env}"  # .env.production, .env.local, etc
    
    # Detecção automática
    if Path(".env.local").exists():
        return ".env.local"
    elif Path(".env.production").exists():
        return ".env.production"
    
    return ".env"  # Fallback
```

---

## ❓ Troubleshooting

### Erro: `Credenciais não configuradas`

**Causa**: Nenhum arquivo `.env` foi encontrado ou `GOOGLE_CREDENTIALS_JSON` está vazio.

**Solução**:
```bash
# Local
ls -la .env.local
cat .env.local | grep GOOGLE

# Render - Verificar logs
```

### Erro: `Invalid JSON in GOOGLE_CREDENTIALS_JSON`

**Causa**: JSON foi corrompido ao colar ou Base64 não foi decodificado corretamente.

**Solução**:
1. Valide o JSON: [jsonlint.com](https://www.jsonlint.com/)
2. Se usar Base64, decodifique e valide
3. Copie novamente com cuidado

### A aplicação carrega `.env.production` quando deveria carregar `.env.local`

**Causa**: `APP_ENV` pode estar definida no seu shell.

**Solução**:
```bash
# Verifique
echo $APP_ENV

# Limpe (se necessário)
unset APP_ENV
```

---

## 📚 Arquivos Relevantes

- [app/core/config.py](./app/core/config.py) — Detecção de ambientes
- [.env.example](./.env.example) — Exemplo de configuração
- [.env.local](./.env.local) — Desenvolvimento
- [.env.production](./.env.production) — Produção
- [GOOGLE_CREDENTIALS_GUIDE.md](./GOOGLE_CREDENTIALS_GUIDE.md) — Este arquivo

---

## 📖 Referências

- [Pydantic Settings - Multiple Environments](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Render - Environment Variables](https://render.com/docs/environment-variables)
- [Google Cloud - Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [Python dotenv](https://github.com/theskumar/python-dotenv)


