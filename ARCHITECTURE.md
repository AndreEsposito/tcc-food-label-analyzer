# Arquitetura do Sistema

Este documento descreve a arquitetura do sistema desenvolvido no TCC
**Análise Inteligente de Rótulos Alimentares**.

O objetivo do sistema é auxiliar consumidores na identificação de
**indícios de ultraprocessamento em alimentos**, analisando
automaticamente a lista de ingredientes presente em rótulos alimentícios
a partir de imagens.

O sistema utiliza:

-   captura de imagem do rótulo
-   OCR para extração textual
-   pré-processamento dos ingredientes
-   motor de classificação híbrido (regras + machine learning)
-   geração de explicação amigável ao usuário

------------------------------------------------------------------------

# Visão Geral da Arquitetura

Fluxo geral do sistema:

Usuário\
↓\
Aplicativo Mobile\
↓\
API Backend\
↓\
OCR (Google Vision API)\
↓\
Pré-processamento textual\
↓\
Motor de classificação híbrido\
↓\
Resultado da análise\
↓\
Retorno ao aplicativo

A arquitetura foi projetada com **separação clara de
responsabilidades**, permitindo evolução futura e facilitando
manutenção.

------------------------------------------------------------------------

# Componentes da Arquitetura

## 1. Aplicativo Mobile

Responsável pela interface com o usuário.

### Responsabilidades

-   Tela inicial
-   Captura ou upload da imagem do rótulo
-   Envio da imagem para API
-   Exibição da tela de loading
-   Exibição do resultado
-   Tratamento de erros

### Entrada

Imagem do rótulo alimentício.

### Saída

Resultado contendo:

-   classificação do produto
-   explicação amigável

------------------------------------------------------------------------

# 2. API Backend

A API backend atua como **camada central de orquestração** do sistema.

### Responsabilidades

-   receber requisições do aplicativo
-   validar requisições
-   integrar com o serviço de OCR
-   executar o pré-processamento textual
-   acionar o motor de classificação
-   montar a resposta final
-   registrar logs e tratar falhas

------------------------------------------------------------------------

# Endpoint Principal

## Envio de imagem para análise

Endpoint:

POST /analises

Content-Type:

multipart/form-data

### Request

    image: <arquivo da imagem do rótulo>

### Response

``` json
{
  "analiseId": "1a2b3c4d-5678-90ab-cdef-123456789000",
  "status": "CLASSIFICADO",
  "classificacao": {
    "categoria": "ultraprocessado",
    "status": "ALTO_INDICIO",
    "justificativa": "O produto contém ingredientes e aditivos comumente associados a alimentos ultraprocessados, como aromatizantes, corantes e conservantes."
  }
}
```

------------------------------------------------------------------------

# 3. OCR --- Extração de Texto

Responsável por transformar a imagem do rótulo em texto.

### Tecnologia utilizada

Google Vision API.

### Processo

Imagem → OCR → Texto bruto

------------------------------------------------------------------------

# Contrato de Integração com OCR

### Request

``` json
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
    "languageHints": [
      "pt-BR"
    ]
  }
}
```

### Response

``` json
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

------------------------------------------------------------------------

# 4. Pré-processamento Textual

O texto bruto retornado pelo OCR precisa ser tratado antes da análise.

### Responsabilidades

-   limpeza do texto
-   normalização
-   remoção de ruído
-   identificação da lista de ingredientes
-   separação dos ingredientes

### Exemplo

Texto OCR:

INGREDIENTES: açúcar, farinha de trigo, gordura vegetal, aromatizante.

Resultado após pré-processamento:

``` json
[
  "açúcar",
  "farinha de trigo",
  "gordura vegetal",
  "aromatizante"
]
```

------------------------------------------------------------------------

# 5. Motor de Classificação Híbrido

O sistema utiliza duas abordagens complementares.

## 5.1 Módulo de Regras

Baseado em heurísticas.

Analisa ingredientes conhecidos associados a ultraprocessamento.

### Elementos considerados

-   aromatizantes
-   corantes
-   conservantes
-   estabilizantes
-   emulsificantes

Cada ingrediente contribui para um **score de ultraprocessamento**.

------------------------------------------------------------------------

## 5.2 Módulo de Machine Learning (Experimental)

Modelo utilizado:

Random Forest.

### Objetivo

Explorar se técnicas de aprendizado de máquina podem melhorar a
classificação.

### Etapas

-   criação de dataset
-   extração de features
-   treinamento do modelo
-   inferência

------------------------------------------------------------------------

# Consolidação da Classificação

Os resultados dos módulos são consolidados para gerar a decisão final.

O sistema retorna:

-   categoria do produto
-   nível de indício de ultraprocessamento
-   justificativa textual

------------------------------------------------------------------------

# Contrato do Motor de Classificação

### Request

``` json
{
  "analiseId": "1a2b3c4d-5678-90ab-cdef-123456789000",
  "ingredientes": [
    "açúcar",
    "farinha de trigo",
    "gordura vegetal",
    "aromatizante"
  ]
}
```

### Response

``` json
{
  "analiseId": "1a2b3c4d-5678-90ab-cdef-123456789000",
  "classificacao": {
    "categoria": "ultraprocessado",
    "status": "ALTO_INDICIO",
    "justificativa": "O produto contém ingredientes e aditivos comumente associados a alimentos ultraprocessados."
  }
}
```

------------------------------------------------------------------------

# 6. Dados, Testes e Validação

Esse módulo fornece evidências científicas para o TCC.

### Dataset de rótulos

Conjunto de produtos utilizados para testes e validação.

### Base de ingredientes e aditivos

Lista de ingredientes e aditivos associados ao nível de processamento.

### Casos de teste

Produtos utilizados para validar o sistema.

### Métricas

Utilizadas para avaliar:

-   precisão da classificação
-   consistência das regras
-   desempenho do modelo de ML

------------------------------------------------------------------------

# Fluxo Completo do Sistema

1.  Usuário captura ou envia imagem do rótulo
2.  Aplicativo envia requisição para API
3.  API envia imagem para OCR
4.  OCR retorna texto bruto
5.  Texto passa por pré-processamento
6.  Lista de ingredientes é extraída
7.  Ingredientes são enviados ao motor de classificação
8.  Sistema gera classificação e justificativa
9.  API retorna resultado ao aplicativo
10. Aplicativo exibe o resultado ao usuário

------------------------------------------------------------------------

# Princípios de Arquitetura

A arquitetura segue os seguintes princípios:

-   separação de responsabilidades
-   modularidade
-   simplicidade arquitetural
-   explicabilidade das decisões
-   facilidade de manutenção

------------------------------------------------------------------------

# Possíveis Evoluções Futuras

O sistema pode ser expandido para identificar:

-   presença de lactose
-   presença de glúten
-   adequação para dietas veganas
-   recomendações nutricionais

Essas funcionalidades são consideradas **trabalhos futuros** e não fazem
parte do escopo inicial do TCC.
