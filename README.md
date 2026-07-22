# TCC - Food Label Analyzer

Aplicativo mobile para apoiar a identificação de indícios de ultraprocessamento em alimentos a partir da leitura da lista de ingredientes presente em rótulos alimentícios.

Este projeto faz parte de um Trabalho de Conclusão de Curso em Ciência da Computação e tem caráter informativo, educativo e acadêmico. A solução não substitui avaliação profissional de nutricionistas ou órgãos reguladores.

---

## Visão Geral

O sistema segue uma arquitetura modular com foco em simplicidade, explicabilidade e viabilidade para TCC.

Fluxo principal:

1. Usuário captura ou seleciona uma imagem do rótulo no aplicativo mobile.
2. O app envia a imagem para o backend via `POST /analises`.
3. A API FastAPI recebe a imagem em `multipart/form-data`, no campo `imagem`.
4. O backend envia a imagem para OCR com Google Vision API.
5. O texto extraído passa por pré-processamento textual.
6. O motor de classificação analisa os ingredientes.
7. A classificação oficial é gerada por regras heurísticas.
8. O Random Forest é mantido como módulo experimental/acadêmico.
9. A API retorna um JSON expandido com classificação e explicação amigável.
10. O app exibe o resultado ao usuário.

---

## Status Atual

- Backend FastAPI funcional.
- Endpoint principal: `POST /analises`.
- Campo de upload: `imagem`.
- OCR integrado com Google Vision API.
- Classificação rule-based ativa como decisão principal.
- Regras determinísticas para grupos NOVA 2, 3 e 4, com `NOVA ?` quando os ingredientes são identificados sem evidência suficiente para definir o grupo.
- Random Forest mantido como abordagem experimental.
- Resposta amigável expandida para o app mobile.
- App mobile desenvolvido com Python + Kivy.
- Geração de APK Debug Android via Buildozer/GitHub Actions.
- Deploy da API suportado em Render.
- Sem banco de dados, login, histórico de análises ou painel administrativo.

---

## Stack Tecnológica Real

### Mobile

- Python
- Kivy
- Buildozer / python-for-android
- Requests

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic

### OCR

- Google Vision API

### Classificação e IA Experimental

- Scikit-learn
- Random Forest experimental
- Pandas, quando necessário para treino/análise

### Infraestrutura

- Render

### Versionamento

- Git
- GitHub

> O projeto não utiliza atualmente Flutter, Kotlin, KivyMD, Docker, AWS, banco de dados ou autenticação.

---

## Estrutura do Repositório

```text
apps/
  backend/
    app/
      api/
      models/
      services/
    tests/

  mobile/
    Ingresense_app/
      main.py
      config/
      layouts/
      screens/
      services/
      buildozer.spec

  ml-lab/
    data/
    train_model.py

packages/
  classification_core/
    pipeline.py
    preprocessing.py
    feature_extractor.py
    rule_based.py
    ml.py
    explanation_generator.py
```

---

## Backend (Resumo)

O backend recebe uma imagem, extrai texto via OCR, aciona o pipeline de classificação e retorna uma resposta amigável para o app.

Endpoint principal:

```http
POST /analises
Content-Type: multipart/form-data
Campo: imagem
```

Resposta esperada, em formato resumido:

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
    "ingredientesDetectados": ["aromatizante"],
    "aviso": "Esta análise possui caráter informativo e não substitui avaliação profissional."
  }
}
```

Para setup completo, credenciais, variáveis de ambiente, execução local e deploy, consulte:

- [apps/backend/README.md](apps/backend/README.md)

Quando o OCR não identifica ingredientes, a API mantém o mesmo JSON, retorna `status: "NAO_CLASSIFICADO"` e `classificacao.novaGrupo: null`; o aplicativo orienta uma nova captura. Quando há ingredientes identificados, mas nenhuma regra permite definir o grupo com segurança, a API retorna `status: "CLASSIFICADO"`, preserva `classificacao.novaGrupo: null` e o aplicativo apresenta o resultado como `NOVA ?`, junto dos itens encontrados.

O aplicativo só exibe um grupo numérico quando o backend envia explicitamente `novaGrupo` como 2, 3 ou 4. Respostas sem grupo que contenham ingredientes identificados são exibidas como `NOVA ?`; respostas sem grupo e sem ingredientes permanecem no fluxo de nova tentativa.

---

## Mobile (Resumo)

O app mobile é desenvolvido com Kivy e possui fluxo de uso simples:

```text
Splash → Home → Câmera/Galeria → Preview → Resultado
```

O aplicativo consome o endpoint `POST /analises`, enviando a imagem no campo `imagem`, e exibe os campos de explicação amigável retornados pelo backend.

Para instruções de execução local, configuração da URL da API e geração do APK Debug Android, consulte:

- [apps/mobile/README.md](apps/mobile/README.md)

---

## Como Começar

1. Clone o repositório.
2. Acesse o módulo desejado.
3. Siga o README específico do módulo.

Exemplo para o backend:

```bash
cd apps/backend
# siga as instruções do README do backend
```

Exemplo para o app mobile:

```bash
cd apps/mobile/Ingresense_app
# siga as instruções do README do mobile
```

---

## APK Debug Android

O projeto gera apenas APK Android Debug para testes manuais. Não há APK Release, AAB, assinatura de produção ou publicação na Play Store.

Para gerar automaticamente pelo GitHub Actions:

1. Abra a aba **Actions** do repositório no GitHub.
2. Selecione o workflow **Android Debug APK**.
3. Clique em **Run workflow**.
4. Ao terminar, abra a execução e baixe o artifact **ingresense-debug-apk**.
5. Extraia o `.zip` baixado.
6. Transfira o arquivo `*-debug.apk` para o Android.
7. Habilite instalação por fontes desconhecidas, se necessário.
8. Instale o APK no celular.

Para gerar localmente, use Linux ou WSL:

```bash
cd apps/mobile/Ingresense_app
buildozer android debug
```

O APK local fica em:

```text
apps/mobile/Ingresense_app/bin/*-debug.apk
```

---

## Regra de Documentação

A documentação deve refletir a implementação existente.

Em alterações futuras, a ordem correta é:

1. implementar a mudança solicitada;
2. validar que o backend, mobile e fluxo Android continuam funcionando;
3. garantir que nada além do solicitado foi alterado;
4. somente depois atualizar README, ARCHITECTURE.md, AGENTS.md ou demais documentos impactados.

---

## Mapa de Documentação

- [README.md](README.md) — visão geral do projeto.
- [AGENTS.md](AGENTS.md) — guia operacional para agentes, Codex e colaboradores.
- [ARCHITECTURE.md](ARCHITECTURE.md) — arquitetura macro e fluxo técnico do sistema.
- [apps/backend/README.md](apps/backend/README.md) — API, OCR, credenciais, deploy e troubleshooting.
- [apps/mobile/README.md](apps/mobile/README.md) — app mobile, execução local, integração e APK Android.
- [apps/ml-lab/README.md](apps/ml-lab/README.md) — experimentos com Random Forest.

---

## Escopo do TCC

Faz parte do escopo atual:

- identificação de indícios de ultraprocessamento via ingredientes;
- OCR de rótulos alimentícios;
- classificação baseada em regras;
- Random Forest experimental;
- explicação amigável ao usuário;
- validação com exemplos reais.

Fica como trabalho futuro:

- detecção de lactose;
- detecção de glúten;
- classificação vegana/vegetariana;
- recomendações nutricionais personalizadas;
- login;
- histórico de análises;
- banco de dados;
- painel administrativo.

---

## Equipe

- André: liderança, arquitetura, backend, cloud e IA.
- Leo: mobile, redes e DevOps.
- Matheus: documentação, ABNT e IA.
- Pedro: escrita acadêmica e documentação.
