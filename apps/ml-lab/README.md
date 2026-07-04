# ML Lab - Random Forest Experimental

Este módulo concentra os experimentos de aprendizado de máquina do projeto **Análise Inteligente de Rótulos Alimentares**.

O objetivo do `ml-lab` é apoiar a análise acadêmica do TCC, permitindo treinar, avaliar e comparar uma abordagem experimental com Random Forest.

---

## Papel no Projeto

O Random Forest é **experimental**.

Ele não é a fonte principal da decisão apresentada ao usuário no aplicativo mobile.

A classificação oficial retornada pela API é baseada no motor de regras heurísticas localizado em:

```text
packages/classification_core/
```

O Random Forest pode ser utilizado para:

- comparação com a abordagem baseada em regras;
- geração de métricas para o relatório;
- análise de viabilidade de aprendizado de máquina;
- discussão de limitações;
- fundamentação da seção de testes e resultados.

Não transformar este módulo na fonte oficial da classificação sem aprovação explícita do grupo.

---

## Estrutura Esperada

```text
apps/ml-lab/
  data/
    train.csv
  train_model.py
```

Possíveis saídas de treino:

```text
random_forest.pkl
```

O arquivo de modelo deve ser tratado com cuidado. Caso ele seja necessário em runtime, garantir que a aplicação tenha fallback seguro quando o arquivo não estiver disponível.

---

## Fluxo Experimental

Fluxo conceitual:

```text
Dataset de rótulos/ingredientes
↓
Extração de features
↓
Treinamento do Random Forest
↓
Avaliação experimental
↓
Comparação com regras heurísticas
↓
Discussão no relatório do TCC
```

---

## Relação com o Classification Core

O backend usa o pacote:

```text
packages/classification_core/
```

Esse pacote contém:

- pré-processamento textual;
- extração de features;
- classificação por regras;
- integração experimental com ML;
- geração de explicação amigável.

O `ml-lab` deve servir como ambiente de experimento e apoio acadêmico, não como uma nova arquitetura paralela.

---

## Cuidados de Escopo

Evitar:

- criar pipeline de ML complexo demais para o TCC;
- substituir a classificação por regras sem decisão do grupo;
- adicionar dependências desnecessárias;
- criar modelos difíceis de reproduzir;
- alterar o contrato da API por causa do experimento;
- impactar o funcionamento do aplicativo Android.

Priorizar:

- simplicidade;
- reprodutibilidade;
- métricas fáceis de explicar;
- comparação objetiva com as regras;
- utilidade para o relatório acadêmico.

---

## Possíveis Métricas

Quando houver dataset suficiente, podem ser avaliadas métricas como:

- acurácia;
- precisão;
- revocação;
- F1-score;
- matriz de confusão.

As métricas devem ser apresentadas como evidência experimental, não como garantia absoluta de classificação nutricional.

---

## Regra de Atualização Documental

Atualizar este README somente após alterações reais no módulo experimental.

Se o papel do Random Forest mudar, sincronizar também:

- README raiz;
- `ARCHITECTURE.md`;
- `AGENTS.md`;
- README do backend, se a API for impactada.
