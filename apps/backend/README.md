# Backend - Food Label Analyzer

API FastAPI responsável por receber imagens de rótulos alimentícios, extrair texto por OCR, acionar o motor de classificação e retornar uma explicação amigável sobre indícios de ultraprocessamento.

---

## Fluxo Atual

1. Recebe upload da imagem pelo endpoint `POST /analises`.
2. Valida o arquivo enviado no campo `imagem`.
3. Envia a imagem para OCR com Google Vision API.
4. Recebe o texto extraído do rótulo.
5. Aciona o pipeline de classificação em `packages/classification_core`.
6. Aplica pré-processamento textual.
7. Executa classificação baseada em regras heurísticas.
8. Executa Random Forest como módulo experimental, quando disponível.
9. Gera explicação amigável.
10. Retorna JSON expandido para o aplicativo mobile.

---

## Status

- Backend FastAPI funcional.
- Endpoint principal: `POST /analises`.
- Campo de upload: `imagem`.
- OCR integrado com Google Vision API.
- Classificação rule-based ativa como decisão principal.
- Classificação determinística dos grupos NOVA 2, 3 e 4 e retorno com grupo indeterminado quando os ingredientes não sustentam uma decisão segura.
- Random Forest mantido como recurso experimental/acadêmico.
- Sem persistência em banco.
- Sem autenticação.
- Sem endpoint dedicado de health check; usar `/docs` para validação rápida.

---

## Estrutura

```text
apps/backend/
  app/
    main.py
    api/
      v1/
        analises.py
    models/
      schemas.py
    services/
      analysis_pipeline.py
      ocr.py
  tests/
```

Principais arquivos:

- `app/main.py`: inicialização da API e middlewares.
- `app/api/v1/analises.py`: endpoint `POST /analises`.
- `app/services/analysis_pipeline.py`: orquestração do fluxo OCR → classificação → resposta.
- `app/services/ocr.py`: integração com Google Vision API.
- `app/models/schemas.py`: contratos de entrada/saída.
- `tests/`: testes unitários e de endpoint.

---

## Endpoint Principal

```http
POST /analises
Content-Type: multipart/form-data
```

Entrada:

- campo obrigatório: `imagem`;
- formato: arquivo de imagem;
- tipos aceitos: `image/*` e extensões `.jpg`, `.jpeg`, `.png`, `.bmp`, `.webp`.

> O campo `imagem` faz parte do contrato com o aplicativo mobile. Não renomear sem atualizar o app junto.

---

## Resposta de Sucesso

Exemplo de resposta `200`:

```json
{
  "analiseId": "1a2b3c4d-5678-90ab-cdef-123456789000",
  "status": "CLASSIFICADO",
  "classificacao": {
    "categoria": "ultraprocessado",
    "status": "ALTO_INDICIO",
    "justificativa": "Foram identificados ingredientes associados a ultraprocessamento.",
    "novaGrupo": 4,
    "titulo": "Alto indício de ultraprocessamento",
    "resumo": "Foram encontrados ingredientes associados a alimentos ultraprocessados.",
    "orientacao": "Considere comparar este produto com opções com menor lista de ingredientes.",
    "evidencias": [
      {
        "termo": "aromatizante",
        "tipo": "aditivo",
        "descricao": "Ingrediente frequentemente associado a produtos ultraprocessados."
      }
    ],
    "ingredientesDetectados": [
      "aromatizante",
      "corante"
    ],
    "aviso": "Esta análise possui caráter informativo e não substitui avaliação profissional."
  }
}
```

Campos principais consumidos pelo app:

- `classificacao.categoria`;
- `classificacao.status`;
- `classificacao.justificativa`;
- `classificacao.novaGrupo`;
- `classificacao.titulo`;
- `classificacao.resumo`;
- `classificacao.orientacao`;
- `classificacao.evidencias`;
- `classificacao.ingredientesDetectados`;
- `classificacao.aviso`.

O campo externo `status` pode ser `CLASSIFICADO` ou `NAO_CLASSIFICADO`. `NAO_CLASSIFICADO` é reservado à ausência de ingredientes utilizáveis. Quando ingredientes são identificados sem grupo seguro, o status é `CLASSIFICADO` e `classificacao.novaGrupo` permanece `null`, sem remoção ou renomeação dos demais campos.

`classificacao.novaGrupo` aceita apenas os grupos 2, 3 e 4, ou `null`. O valor legado 1 é rejeitado pelo schema. Após alterações nesse contrato, o serviço no Render precisa ser redeployado; o OpenAPI publicado deve deixar de apresentar `default: 1`.

As regras dos grupos 2 e 3 usam vocabulário fechado e padrões de composição. Foram validadas contra os produtos da aba `Dataset_Produtos`: açúcar/sacarose, sal e azeites são tratados como grupo 2; conservas, queijos simples, geleias e preparações baseadas em alimento com ingredientes culinários são tratadas como grupo 3. `Proteínas lácteas` é normalizado como marcador forte do grupo 4. Leite fermentado simples retorna grupo indeterminado, e manteiga feita de creme de leite exige que o texto OCR também identifique explicitamente o produto como manteiga.

Listas do grupo 3 continuam reconhecíveis quando o OCR perde vírgulas ou quebras de linha. Nesse caso, o backend recompõe os ingredientes apenas por frases do vocabulário controlado e rejeita a recuperação se houver palavras desconhecidas, sem alterar o contrato da API.

Sem o cabeçalho `Ingredientes:`, um termo controlado isolado não sustenta classificação, pois pode ter sido extraído da frente da embalagem. Por exemplo, `açúcar refinado`, `sal` ou `aromatizante` sem estrutura de lista retornam `NAO_CLASSIFICADO` e `novaGrupo: null`; uma lista real de um ingrediente permanece válida quando o cabeçalho é capturado.

---

## Erros Esperados

- `200` com `status = "NAO_CLASSIFICADO"`: OCR sem ingredientes utilizáveis.
- `200` com `status = "CLASSIFICADO"` e `novaGrupo = null`: ingredientes identificados, mas sem grupo NOVA seguro.
- `400`: arquivo inválido ou vazio.
- `422`: reservado para uma falha de ausência de texto propagada por uma implementação alternativa do pipeline.
- `502`: falha de autenticação/serviço OCR.
- `504`: timeout no OCR.

O tratamento de erro deve preservar mensagens compatíveis com o aplicativo mobile.

---

## Papel do Random Forest

O Random Forest é experimental.

Ele pode ser utilizado para:

- comparação acadêmica;
- geração de métricas;
- análise no relatório;
- apoio à validação do motor.

A classificação oficial retornada ao usuário é baseada no motor de regras heurísticas.

Não transformar o Random Forest na fonte principal da decisão final sem decisão explícita do grupo.

Uma falha no pickle ou na inferência experimental não bloqueia o startup nem a resposta heurística oficial.

---

## Configuração de Ambiente

A leitura de configurações ocorre em `app/core/config.py`.

Prioridade do `.env`:

1. `APP_ENV` definido → `.env.{APP_ENV}`;
2. `.env.local`, se existir;
3. `.env.production`, se existir;
4. fallback → `.env.local`.

Variáveis principais:

- `APP_ENV`;
- `DEBUG`;
- `GOOGLE_APPLICATION_CREDENTIALS`;
- `GOOGLE_CREDENTIALS_JSON`;
- `GOOGLE_VISION_TIMEOUT_SECONDS`.

Templates versionados:

- `.env.local.template`;
- `.env.production.template`.

Arquivos sensíveis ignorados no Git:

- `.env.local`;
- `.env.production`;
- `google-credentials.json`.

---

## Credenciais Google Vision

A API suporta duas formas de autenticação.

### 1. Arquivo local para desenvolvimento

No `.env.local`:

```env
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
```

Salvar `google-credentials.json` dentro de `apps/backend/`.

### 2. Variável de ambiente para produção

Usar `GOOGLE_CREDENTIALS_JSON` com:

1. JSON direto; ou
2. JSON em Base64.

Exemplo Base64 no PowerShell:

```powershell
$content = Get-Content apps/backend/google-credentials.json -Raw
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($content))
```

Importante:

- nunca commitar credenciais reais;
- nunca commitar `.env.local` ou `.env.production` com segredos.

---

## Como Rodar Localmente

### 1. Instalar dependências

A partir da raiz do repositório:

```bash
pip install -r apps/requirements.txt
```

### 2. Criar `.env.local`

PowerShell:

```powershell
.\setup-env.ps1
```

Bash:

```bash
./setup-env.sh
```

### 3. Ajustar credenciais

Editar:

```text
apps/backend/.env.local
```

### 4. Subir API

Opção A, a partir da raiz do repositório:

```bash
python -m uvicorn app.main:app --app-dir apps/backend --host localhost --port 8000
```

Opção B, entrando no módulo backend:

```bash
cd apps/backend
python -m uvicorn app.main:app --host localhost --port 8000
```

### 5. Validar

Abrir:

```text
http://localhost:8000/docs
```

---

## Deploy no Render

Este repositório possui `render.yaml` na raiz.

Configuração atual do serviço:

- Runtime: Python 3.12.
- Build: `pip install --upgrade pip setuptools wheel && pip install -r apps/requirements.txt`.
- Start: `cd apps/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`.

Passo a passo:

1. Conectar o repositório no Render como `Web Service`.
2. Confirmar que o `render.yaml` foi detectado.
3. Em `Environment`, adicionar `GOOGLE_CREDENTIALS_JSON`.
4. Fazer deploy.

Validação pós-deploy:

- abrir `<sua-url>.onrender.com/docs`;
- testar `POST /analises` via Swagger;
- testar também pelo app mobile quando possível.

---

## Compatibilidade com Mobile Android

Qualquer alteração no backend deve considerar o aplicativo Kivy rodando no celular.

Preservar:

- endpoint `POST /analises`;
- campo multipart `imagem`;
- formato do JSON de resposta;
- campos usados pela tela de resultado;
- mensagens de erro compatíveis com o app;
- comportamento esperado em ambiente Render.

Não considerar uma alteração segura apenas porque a API roda localmente. O fluxo completo precisa continuar viável no Android:

```text
Mobile Android → Backend → OCR → Classificação → JSON → Mobile Android
```

---

## Troubleshooting Rápido

Build falhou no Render:

- verificar `apps/requirements.txt`;
- verificar logs de build no Render.

Aplicação não sobe no Render:

- verificar se `GOOGLE_CREDENTIALS_JSON` foi configurada corretamente;
- verificar logs do serviço.

Erro `ModuleNotFoundError: No module named 'app'` ao subir local:

- causa: comando executado fora de `apps/backend` sem `--app-dir`;
- correção: usar `--app-dir apps/backend` ou executar dentro de `apps/backend`.

Erro de autenticação OCR:

- revisar permissão da Service Account;
- confirmar Vision API habilitada no projeto Google Cloud;
- validar se a credencial foi lida corretamente.

---

## Observações de Escopo do TCC

Foco atual:

- identificar indícios de ultraprocessamento por ingredientes;
- apresentar resposta explicável;
- validar com exemplos reais.

Ficam para trabalhos futuros:

- glúten;
- lactose;
- classificação vegana/vegetariana;
- recomendações nutricionais;
- histórico de análises;
- login;
- banco de dados.

---

## Regra de Atualização Documental

Atualizações em documentação devem ocorrer apenas depois que a implementação correspondente estiver concluída e validada.

Ao alterar backend, verificar também se README raiz, ARCHITECTURE.md, AGENTS.md e README do mobile precisam ser sincronizados.
