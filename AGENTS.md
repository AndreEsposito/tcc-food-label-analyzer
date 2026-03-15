# AGENTS.md

Guia para agentes de IA e colaboradores do projeto de TCC.

Este arquivo define o **contexto do projeto, arquitetura, responsabilidades e diretrizes de desenvolvimento**, para que qualquer agente de IA ou colaborador humano consiga compreender rapidamente o sistema e contribuir de forma consistente.

---

# 1. Contexto do Projeto

Este repositório contém o desenvolvimento de um **Trabalho de Conclusão de Curso (TCC) em Ciência da Computação**.

O objetivo inicial do projeto é desenvolver **um aplicativo mobile que auxilia consumidores na identificação de alimentos ultraprocessados, analisando a lista de ingredientes presente nos rótulos alimentícios**.  
A arquitetura do sistema será modular, permitindo que, futuramente, sejam incorporadas outras categorias de análise, como detecção de lactose, glúten, classificação vegana/vegetariana e recomendações nutricionais.  
Assim, o projeto visa criar uma base flexível para expandir as funcionalidades conforme novas necessidades ou pesquisas acadêmicas.

O sistema utiliza:

- captura de imagem do rótulo do produto
- OCR para extração textual
- processamento do texto
- classificação baseada em regras e aprendizado de máquina
- retorno explicável ao usuário

A proposta baseia-se no pré-projeto acadêmico do TCC. :contentReference[oaicite:4]{index=4}

---

# 2. Fluxo Geral do Sistema

Fluxo simplificado da aplicação:

Usuário  
↓  
Aplicativo Mobile  
↓  
Envio da imagem do rótulo  
↓  
Backend API  
↓  
OCR (Google Vision API)  
↓  
Pré-processamento textual  
↓  
Motor de classificação  
↓  
Resultado com explicação  
↓  
Retorno para o aplicativo

O sistema deve priorizar **clareza, modularidade e explicabilidade do resultado**.

---

# 3. Arquitetura do Sistema

A arquitetura é organizada em **domínios funcionais**, seguindo a estrutura definida para o projeto. :contentReference[oaicite:5]{index=5}

---

## 3.1 Domínio Mobile

Responsável pela interação com o usuário.

Funções principais:

- captura de imagem do rótulo
- upload da imagem
- comunicação com API
- exibição do resultado
- exibição da justificativa da classificação
- tratamento de erros

---

## 3.2 Domínio API Backend

Camada central de orquestração.

Responsabilidades:

- receber requisição do aplicativo
- validar requisições
- integrar com OCR
- acionar pré-processamento textual
- acionar motor de classificação
- montar resposta final
- retornar resultado ao aplicativo

Entrada:

Content-Type: multipart/form-data

Saída:

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

---

## 3.3 Domínio de OCR

Responsável por extrair texto da imagem.

Tecnologia principal:

Google Vision API.

Responsabilidades:

- envio da imagem ao OCR
- recebimento do texto extraído
- identificação da lista de ingredientes

Entrada:

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

Saída:

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

---

## 3.4 Domínio de Pré-processamento Textual

Transforma o texto bruto em dados estruturados.

Responsabilidades:

- limpeza do texto
- remoção de ruído
- normalização
- separação da lista de ingredientes
- padronização de termos
- tokenização simples

Entrada:

INGREDIENTES: açúcar, farinha de trigo, gordura vegetal, aromatizante.

Saída:

``` json
[
  "açúcar",
  "farinha de trigo",
  "gordura vegetal",
  "aromatizante"
]
```

---

## 3.5 Domínio de Classificação

Coração lógico do sistema.

Utiliza duas abordagens complementares.

### Classificação baseada em regras

- lista de ingredientes associados ao ultraprocessamento e futuramente outras categorias
- pesos e critérios
- score de processamento
- geração de justificativa

### Classificação baseada em Machine Learning

Modelo experimental:

Random Forest.

Responsabilidades:

- preparação do dataset
- engenharia de features
- treinamento
- inferência

Entrada:

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

Saída:

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

---

## 3.6 Domínio de Dados, Testes e Validação

Suporte científico ao TCC.

Responsabilidades:

- coleta de rótulos
- montagem do dataset
- rotulagem de dados
- definição de casos de teste
- validação com produtos reais
- coleta de métricas

Esse domínio fornece **evidências para o relatório acadêmico**.

---

# 4. Fases do Projeto

O projeto segue fases estruturadas. :contentReference[oaicite:6]{index=6}

1. Refinamento do projeto  
2. Definição da arquitetura  
3. Implementação do sistema e prototipação
4. Integração e testes  
5. Montagem da apresentação do TCC  
6. Preparação da banca

Relatório acadêmico deve ser desenvolvido **paralelamente ao desenvolvimento do software**, garantindo coerência entre a implementação e a estrutura do relatório.

Agentes devem considerar **em qual fase o projeto se encontra antes de propor mudanças estruturais**.

---

# 5. Organização em Sprints

O desenvolvimento ocorre principalmente **nos finais de semana**.

As sprints devem ter duração de **1 ou 2 semanas**.

Cada sprint deve definir:

- objetivo
- tarefas
- responsáveis
- entregáveis esperados

Sempre que possível, verificar:

"O grupo já definiu as tarefas da próxima sprint?"

---

# 6. Stack Tecnológica Inicial

Tecnologias consideradas para o projeto:

Mobile

- Flutter ou Kotlin

Backend

- Python

OCR

- Google Vision API

Machine Learning

- Random Forest

Cloud (opcional)

- AWS

Versionamento

- Git

Agentes devem priorizar **soluções simples e viáveis para um projeto acadêmico**.

---

# 7. Responsabilidades da Equipe

| Integrante | Responsabilidade |
|---|---|
| André (líder) | Arquitetura, backend, integração com OCR e pré-processamento |
| Matheus | Motor de classificação e modelo de ML |
| Leo | Aplicativo mobile |
| Pedro | Documentação acadêmica e relatório |

---

# 8. Diretrizes de Engenharia

Ao contribuir para o projeto:

Priorizar:

- simplicidade
- modularidade
- clareza arquitetural
- separação de responsabilidades
- explicabilidade do sistema
- viabilidade acadêmica

Evitar:

- complexidade excessiva
- dependências desnecessárias
- pipelines de ML complexos demais
- tecnologias difíceis de implementar no prazo do TCC.

---

# 9. Riscos do Projeto

Possíveis riscos:

- complexidade excessiva
- dificuldades na implementação da IA
- problemas na integração com OCR
- falta de dataset
- atraso no desenvolvimento

Quando identificar um risco, agentes devem sugerir **alternativas mais simples e viáveis**.

---

# 10. Escopo do Projeto

O foco principal do TCC é:

identificar **indícios de ultraprocessamento em alimentos com base na análise da lista de ingredientes**.

Outras análises podem ser consideradas **trabalhos futuros**, como:

- detecção de lactose
- detecção de glúten
- classificação vegana/vegetariana
- recomendações nutricionais

Essas funcionalidades **não fazem parte do escopo inicial do TCC**.

---

# 11. Coerência Acadêmica

O desenvolvimento do software deve sempre manter coerência com:

- objetivos do TCC
- metodologia do trabalho
- estrutura acadêmica exigida pela universidade

A implementação deve permitir gerar evidências para capítulos como:

- metodologia
- arquitetura do sistema
- experimentos
- resultados.

O projeto deve manter alinhamento com o modelo acadêmico de relatório. :contentReference[oaicite:7]{index=7}

---

# 12. Objetivo Final do Projeto

Este projeto não visa apenas criar um software funcional.

Ele também deve:

- demonstrar aplicação prática de técnicas de computação
- produzir resultados analisáveis
- gerar evidências científicas
- sustentar um relatório acadêmico consistente

Portanto, agentes devem considerar **tanto a engenharia de software quanto a coerência científica do projeto**.
