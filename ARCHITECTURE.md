# Arquitetura do Sistema

Este documento descreve a arquitetura real do sistema desenvolvido no TCC **Análise Inteligente de Rótulos Alimentares**.

O objetivo do sistema é auxiliar consumidores na identificação de **indícios de ultraprocessamento em alimentos**, analisando automaticamente a lista de ingredientes presente em rótulos alimentícios a partir de imagens.

A arquitetura atual prioriza:

- simplicidade;
- modularidade;
- separação de responsabilidades;
- explicabilidade da classificação;
- compatibilidade entre backend e aplicativo mobile Android;
- viabilidade acadêmica para um TCC de graduação.

---

## 1. Visão Geral da Arquitetura

Fluxo real do sistema:

```text
Usuário
↓
Aplicativo Mobile em Kivy
↓
Captura ou seleção da imagem do rótulo
↓
POST /analises
multipart/form-data com campo "imagem"
↓
Backend FastAPI
↓
Google Vision API
↓
Pré-processamento textual
↓
Motor de classificação
  ├── regras heurísticas
  └── Random Forest experimental
↓
Camada de explicação amigável
↓
Resposta JSON expandida
↓
Tela de resultado no aplicativo mobile
```

A decisão oficial apresentada ao usuário é baseada no **motor de regras heurísticas**. O Random Forest permanece como módulo experimental para comparação, validação acadêmica e discussão no relatório.

---

## 2. Estrutura Modular do Repositório

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

## 3. Componentes da Arquitetura

### 3.1 Aplicativo Mobile

O aplicativo mobile é desenvolvido com **Python + Kivy** e tem como objetivo oferecer uma interface simples para envio de imagens e visualização do resultado.

Responsabilidades:

- exibir tela inicial;
- permitir captura ou seleção da imagem do rótulo;
- exibir prévia da imagem;
- enviar a imagem para a API;
- exibir tela de carregamento;
- apresentar resultado amigável;
- tratar erros de comunicação e processamento;
- preservar compatibilidade com execução em dispositivo Android.

Entrada:

```text
Imagem do rótulo alimentício.
```

Saída:

```text
Resultado amigável exibido ao usuário.
```

Fluxo de telas:

```text
Splash → Home → Câmera/Galeria → Preview → Resultado
```

---

### 3.2 API Backend

A API backend é desenvolvida com **FastAPI** e atua como camada central de orquestração.

Responsabilidades:

- receber requisições do aplicativo mobile;
- validar a imagem enviada;
- integrar com o serviço de OCR;
- acionar o pipeline de classificação;
- montar a resposta final;
- retornar dados compatíveis com o app;
- tratar erros de forma segura.

Tecnologias principais:

- Python;
- FastAPI;
- Uvicorn;
- Pydantic.

---

### 3.3 OCR e Extração Textual

O OCR é responsável por transformar a imagem do rótulo em texto bruto.

Tecnologia utilizada:

```text
Google Vision API
```

Responsabilidades:

- receber a imagem enviada pelo backend;
- realizar detecção de texto;
- retornar o texto extraído;
- permitir que o backend identifique a lista de ingredientes.

Processo:

```text
Imagem → Google Vision API → Texto bruto
```

---

### 3.4 Pré-processamento Textual

O pré-processamento transforma o texto bruto extraído pelo OCR em uma forma utilizável pelo motor de classificação.

Responsabilidades:

- limpar o texto;
- normalizar caracteres e termos;
- reduzir ruídos da leitura;
- identificar trecho de ingredientes;
- separar ingredientes;
- preparar features para classificação.

Exemplo:

Texto OCR:

```text
INGREDIENTES: açúcar, farinha de trigo, gordura vegetal, aromatizante.
```

Saída esperada:

```json
[
  "açúcar",
  "farinha de trigo",
  "gordura vegetal",
  "aromatizante"
]
```

---

### 3.5 Motor de Classificação

O motor de classificação fica em `packages/classification_core`.

Fluxo interno:

```text
Texto extraído
↓
Pré-processamento
↓
Extração de features
↓
Classificação por regras
↓
Random Forest experimental, quando disponível
↓
Geração de explicação amigável
↓
Resultado consolidado
```

#### 3.5.1 Classificação baseada em regras

A classificação principal do sistema é baseada em regras heurísticas.

Ela considera ingredientes e padrões associados ao ultraprocessamento, como:

- aromatizantes;
- corantes;
- conservantes;
- estabilizantes;
- emulsificantes;
- gordura vegetal;
- xarope;
- outros aditivos e termos recorrentes.

A saída da classificação por regras é utilizada como decisão oficial retornada ao usuário.

A ordem determinística é:

1. validar se há lista de ingredientes suficiente;
2. identificar grupo 2 por famílias culinárias fechadas e auxiliares permitidos;
3. identificar grupo 4 por marcadores fortes de formulação;
4. identificar grupo 3 por alimento-base reconhecível combinado com ingredientes culinários;
5. retornar `NOVA ?` com os ingredientes detectados quando nenhuma regra de grupo for sustentada.

Resultados sem ingredientes preservam a resposta existente com `status = "NAO_CLASSIFICADO"`, `novaGrupo = null`, evidências vazias e orientação para nova captura. Quando a lista contém ingredientes, mas nenhuma regra define o grupo com segurança, o resultado usa `status = "CLASSIFICADO"`, mantém `novaGrupo = null`, devolve os ingredientes como itens identificados e é apresentado no mobile como `NOVA ?`. Os grupos 2, 3 e 4 mapeiam, respectivamente, para `BAIXO_INDICIO`, `MEDIO_INDICIO` e `ALTO_INDICIO`.

Na ausência do cabeçalho de ingredientes, um único termo controlado não é considerado uma lista suficiente: ele pode ser apenas o nome ou um destaque da frente da embalagem. Assim, textos isolados como `açúcar refinado`, `sal` ou `aromatizante` permanecem inconclusivos; listas de um ingrediente continuam classificáveis quando o OCR captura o cabeçalho `Ingredientes:`.

O vocabulário controlado dos grupos 2 e 3 cobre sinônimos e composições observados no dataset acadêmico, incluindo sacarose de cana, azeites refinado/virgem, queijos com quimosina, geleias com pectina e suco de limão, vegetais acidificados, pescados e leguminosas com temperos culinários. Entre os marcadores fortes do grupo 4, a normalização também reconhece `proteínas lácteas` como `proteina lactea`, evitando o falso resultado indeterminado observado no produto P011. Contextos ambíguos preservam os ingredientes e retornam `NOVA ?`: creme de leite só sustenta manteiga do grupo 2 quando o texto completo identifica explicitamente o produto, e leite fermentado simples não é suficiente para grupo 3.

Quando o OCR remove pontuação e quebras de linha, o motor tenta recuperar os componentes do grupo 3 com uma segmentação gulosa pelo termo controlado mais longo. A recuperação não ignora conteúdo desconhecido: se restar qualquer palavra fora do vocabulário, a composição não é classificada por essa estratégia. Isso preserva o caráter conservador sem depender obrigatoriamente das vírgulas do rótulo.

#### 3.5.2 Random Forest experimental

O Random Forest é uma abordagem complementar e experimental.

Ele pode ser utilizado para:

- análise acadêmica;
- comparação de resultados;
- geração de métricas;
- discussão no relatório;
- apoio à validação do projeto.

O Random Forest não deve ser tratado como fonte principal da decisão final sem decisão explícita do grupo.

O vetor experimental legado é preservado para manter compatibilidade com o pickle atual. Falhas no carregamento ou na inferência são registradas como indisponibilidade experimental e não interrompem a classificação heurística.

---

### 3.6 Camada de Explicação Amigável

A explicação amigável transforma a saída técnica da classificação em uma resposta compreensível para usuários comuns.

Ela deve gerar informações como:

- título;
- resumo;
- justificativa;
- orientação;
- evidências encontradas;
- ingredientes detectados;
- aviso informativo.

O objetivo é evitar uma resposta puramente técnica e tornar a análise útil para o consumidor.

---

## 4. Endpoint Principal

### 4.1 Envio de imagem para análise

```http
POST /analises
Content-Type: multipart/form-data
Campo do arquivo: imagem
```

O campo do arquivo deve permanecer como `imagem`, pois o aplicativo mobile depende desse contrato.

### 4.2 Exemplo de resposta

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

---

## 5. Contrato de Integração com OCR

O backend utiliza a Google Vision API para detecção de texto.

Formato conceitual da requisição enviada ao serviço de OCR:

```json
{
  "image": {
    "content": "BASE64_DA_IMAGEM"
  },
  "features": [
    {
      "type": "TEXT_DETECTION"
    }
  ],
  "imageContext": {
    "languageHints": ["pt-BR"]
  }
}
```

Formato conceitual da resposta:

```json
{
  "textAnnotations": [
    {
      "description": "INGREDIENTES: açúcar, farinha..."
    }
  ],
  "fullTextAnnotation": {
    "text": "INGREDIENTES: açúcar, farinha..."
  }
}
```

---

## 6. Dados, Testes e Validação

Este domínio fornece evidências científicas para o TCC.

Responsabilidades:

- coleta de rótulos;
- definição de casos de teste;
- validação com produtos reais;
- comparação entre resultados esperados e obtidos;
- avaliação das limitações do OCR;
- análise do comportamento das regras;
- análise experimental do Random Forest.

Essas evidências devem sustentar principalmente os capítulos de desenvolvimento, testes, resultados, limitações e trabalhos futuros.

---

## 7. Compatibilidade Mobile e Android

Qualquer alteração arquitetural deve preservar o fluxo completo no aplicativo Android.

Não basta a API funcionar localmente. O sistema deve continuar compatível com:

- app Kivy;
- Buildozer;
- empacotamento Android;
- comunicação HTTP entre app e backend;
- upload de imagem no campo `imagem`;
- contrato JSON esperado pela tela de resultado;
- execução real em celular.

Fluxo que deve ser preservado:

```text
Mobile Android
↓
Backend
↓
OCR
↓
Classificação
↓
Explicação amigável
↓
Resposta JSON
↓
Mobile Android
```

---

## 8. Princípios de Arquitetura

A arquitetura segue os seguintes princípios:

- separação de responsabilidades;
- modularidade;
- baixo acoplamento;
- simplicidade arquitetural;
- explicabilidade das decisões;
- preservação de funcionalidades existentes;
- compatibilidade entre backend e mobile;
- viabilidade para TCC.

Evitar:

- refatorações amplas sem necessidade;
- criação de camadas desnecessárias;
- inclusão de tecnologias fora do escopo;
- mudanças que funcionem apenas localmente;
- alterações que quebrem o funcionamento no Android.

---

## 9. Escopo Atual e Evoluções Futuras

Faz parte do escopo atual:

- análise de rótulos por imagem;
- OCR com Google Vision API;
- pré-processamento textual;
- classificação de indícios de ultraprocessamento;
- explicação amigável;
- Random Forest experimental;
- validação com produtos reais.

São trabalhos futuros:

- detecção de lactose;
- detecção de glúten;
- classificação vegana;
- classificação vegetariana;
- recomendações nutricionais personalizadas;
- login;
- histórico de análises;
- banco de dados;
- painel administrativo.

---

## 10. Regra de Atualização Documental

A documentação deve ser atualizada somente após a implementação correspondente estar concluída e validada.

Ordem correta:

1. implementar a mudança solicitada;
2. garantir que nada além do solicitado foi alterado;
3. validar compatibilidade entre backend, mobile e Android;
4. atualizar documentação técnica impactada;
5. atualizar documentação acadêmica impactada, quando necessário.

Este documento deve refletir o sistema real, não uma arquitetura idealizada.
