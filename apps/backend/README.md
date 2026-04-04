# Backend - Food Label Analyzer

API FastAPI para analisar rotulos de alimentos a partir de imagem.

Fluxo atual:
1. Upload da imagem
2. OCR (Google Vision)
3. Pre-processamento do texto
4. Classificacao rule-based
5. Retorno com justificativa

Status:
- Rule-based ativo
- Sem persistencia em banco
- Sem endpoint de health check (apenas `/docs` para validacao rapida)

## Estrutura
- `app/main.py`: inicializacao da API e middlewares.
- `app/api/v1/analises.py`: endpoint `POST /analises`.
- `app/services/analysis_pipeline.py`: orquestracao do fluxo.
- `app/services/ocr.py`: integracao Google Vision.
- `app/services/text_preprocessing.py`: limpeza/normalizacao de ingredientes.
- `app/services/classification.py`: classificacao por regras.
- `app/models/schemas.py`: contratos de entrada/saida.
- `tests/`: testes unitarios e de endpoint.

## Endpoint
`POST /analises`

Entrada:
- `multipart/form-data`
- Campo `imagem`
- Tipos aceitos: `image/*` e extensoes `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`

Resposta (200):
```json
{
  "analiseId": "1a2b3c4d-5678-90ab-cdef-123456789000",
  "status": "CLASSIFICADO",
  "classificacao": {
    "categoria": "ultraprocessado",
    "status": "ALTO_INDICIO",
    "justificativa": "Foram identificados ingredientes associados a ultraprocessamento, como aromatizante, corante."
  }
}
```

Erros esperados:
- `400`: arquivo invalido ou vazio
- `422`: OCR sem texto extraido
- `502`: falha de autenticacao/servico OCR
- `504`: timeout no OCR

## Configuracao de Ambiente
Leitura em `app/core/config.py`.

Prioridade do `.env`:
1. `APP_ENV` definido -> `.env.{APP_ENV}`
2. `.env.local` (se existir)
3. `.env.production` (se existir)
4. fallback -> `.env.local`

Variaveis principais:
- `APP_ENV`
- `DEBUG`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `GOOGLE_CREDENTIALS_JSON` (JSON direto ou Base64)
- `GOOGLE_VISION_TIMEOUT_SECONDS`

Templates versionados:
- `.env.local.template`
- `.env.production.template`

Arquivos sensiveis (ignorados no Git):
- `.env.local`
- `.env.production`
- `google-credentials.json`

## Credenciais Google Vision
A API suporta 2 formas:

1. Arquivo local (desenvolvimento)
- No `.env.local`, usar:
```env
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
```
- Salvar `google-credentials.json` dentro de `apps/backend/`

2. Variavel de ambiente (producao)
- Usar `GOOGLE_CREDENTIALS_JSON` com:
1. JSON direto, ou
2. JSON em Base64

Exemplo Base64 (PowerShell):
```powershell
$content = Get-Content apps/backend/google-credentials.json -Raw
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($content))
```

Importante:
- Nunca commitar credenciais reais
- Nunca commitar `.env.local`/`.env.production` com segredos

## Como rodar local
1. Instalar dependencias
```bash
pip install -r apps/backend/requirements.txt
```

2. Criar `.env.local`
```powershell
.\setup-env.ps1
```
ou
```bash
./setup-env.sh
```

3. Ajustar credenciais no `apps/backend/.env.local`

4. Subir API
```bash
cd apps/backend
python -m uvicorn app.main:app --host localhost --port 8000
```

5. Validar
- Swagger: `http://localhost:8000/docs`

## Deploy no Render
Este repositorio ja possui `render.yaml` na raiz.

Configuracao atual do service:
- Runtime: Python 3.12
- Build: `cd apps/backend && pip install --upgrade pip setuptools wheel && pip install -r requirements.txt`
- Start: `cd apps/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`

Passo a passo:
1. Conectar o repo no Render como `Web Service`
2. Confirmar que o `render.yaml` foi detectado
3. Em `Environment`, adicionar `GOOGLE_CREDENTIALS_JSON` (JSON ou Base64)
4. Fazer deploy

Validacao pos-deploy:
- Abrir `<sua-url>.onrender.com/docs`
- Testar `POST /analises` via Swagger

## Troubleshooting rapido
Build falhou:
- Verificar `apps/backend/requirements.txt`
- Verificar logs de build no Render

Aplicacao nao sobe no Render:
- Verificar se `GOOGLE_CREDENTIALS_JSON` foi configurada corretamente
- Verificar logs do servico

Erro de autenticacao OCR:
- Revisar permissao da Service Account
- Confirmar Vision API habilitada no projeto Google Cloud

## Observacoes de escopo (TCC)
- Foco atual: identificar indicios de ultraprocessamento por ingredientes
- Expansoes (gluten/lactose/veg) ficam para trabalhos futuros
- Priorizar simplicidade, modularidade e explicabilidade
