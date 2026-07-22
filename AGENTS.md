# AGENTS.md

Guia operacional para agentes de IA, Codex e colaboradores humanos do projeto de TCC **Análise Inteligente de Rótulos Alimentares**.

Este arquivo define o contexto acadêmico, a arquitetura real do sistema, a stack efetivamente utilizada, os contratos principais e as regras de manutenção do projeto. O objetivo é permitir que qualquer agente de IA compreenda rapidamente o estado atual da aplicação e contribua de forma segura, conservadora e coerente com o escopo do TCC.

---

# 1. Contexto do Projeto

Este repositório contém o desenvolvimento de um **Trabalho de Conclusão de Curso (TCC) em Ciência da Computação**.

O objetivo do projeto é desenvolver um **aplicativo mobile para apoio à identificação de indícios de ultraprocessamento em alimentos por meio da análise textual da lista de ingredientes presente nos rótulos alimentícios**.

O sistema permite que o usuário capture ou selecione uma imagem de um rótulo, envie essa imagem para processamento, extraia o texto por OCR, analise os ingredientes e receba uma resposta compreensível sobre possíveis indícios de ultraprocessamento.

O foco desta versão é:

- captura ou seleção de imagem de rótulo alimentício;
- extração textual com OCR;
- pré-processamento dos ingredientes;
- classificação baseada em regras heurísticas;
- uso experimental de Random Forest para fins acadêmicos/comparativos;
- geração de explicação amigável para o usuário final;
- validação com exemplos reais de produtos.

Funcionalidades como detecção de lactose, glúten, classificação vegana/vegetariana e recomendações nutricionais personalizadas são consideradas **trabalhos futuros** e não fazem parte do escopo principal atual.

---

# 2. Regra Fundamental: Implementação Antes da Documentação

> **A documentação deve refletir a implementação existente, nunca o contrário.**

Sempre que uma alteração funcional, técnica ou arquitetural for solicitada, o agente deve seguir obrigatoriamente esta ordem:

1. entender a solicitação;
2. analisar a arquitetura atual do projeto;
3. implementar as mudanças solicitadas no código;
4. validar que a implementação ficou consistente;
5. garantir que nada além do solicitado foi alterado;
6. atualizar testes, quando necessário;
7. somente depois atualizar a documentação técnica ou acadêmica impactada.

Durante uma tarefa em andamento, é aceitável que a documentação fique temporariamente desatualizada. Porém, nenhuma tarefa deve ser considerada concluída enquanto a documentação impactada não estiver sincronizada com a implementação final.

Não atualizar README, ARCHITECTURE.md, diagramas, relatório ou qualquer outro documento antes de concluir e validar a implementação solicitada.

---

# 3. Fluxo Geral Real do Sistema

Fluxo atual da aplicação:

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

O sistema deve preservar clareza, modularidade, explicabilidade e viabilidade acadêmica.

---

# 4. Stack Tecnológica Real

Esta é a stack efetivamente utilizada no projeto. Não assumir outras tecnologias como parte ativa da implementação.

## Mobile

- Python
- Kivy
- Buildozer / python-for-android para empacotamento Android
- Requests para comunicação HTTP com o backend

## Backend

- Python
- FastAPI
- Uvicorn
- Pydantic

## OCR

- Google Vision API

## Classificação e IA Experimental

- Python
- Scikit-learn
- Random Forest experimental
- Pandas quando necessário para treino/análise de dados

## Infraestrutura

- Render para hospedagem da API

## Versionamento

- Git
- GitHub

## Tecnologias que não devem ser assumidas

Não assumir que o projeto utiliza atualmente:

- Flutter;
- Kotlin;
- KivyMD;
- Docker;
- AWS;
- banco de dados;
- autenticação de usuários;
- armazenamento persistente de análises.

Essas tecnologias só devem ser propostas se houver solicitação explícita e justificativa clara de viabilidade para o TCC.

---

# 5. Estrutura Arquitetural do Repositório

A arquitetura atual é organizada de forma modular.

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

packages/
  classification_core/
    pipeline.py
    preprocessing.py
    feature_extractor.py
    rule_based.py
    ml.py
    explanation_generator.py

apps/ml-lab/
  data/
  train_model.py
```

## 5.1 Backend

Responsável por orquestrar o fluxo principal da análise.

Responsabilidades:

- expor a API HTTP;
- receber imagem enviada pelo app;
- validar arquivo recebido;
- chamar o serviço de OCR;
- acionar o pipeline de classificação;
- montar a resposta compatível com o contrato da API;
- tratar erros de forma segura.

## 5.2 Mobile

Responsável pela interação com o usuário.

Responsabilidades:

- exibir tela inicial;
- permitir captura ou seleção de imagem;
- enviar imagem para a API;
- exibir tela de carregamento;
- apresentar resultado amigável;
- tratar erros de comunicação e processamento;
- preservar compatibilidade com execução em dispositivo Android.

## 5.3 Classification Core

Responsável pela lógica de análise textual e classificação.

Responsabilidades:

- pré-processar texto extraído do OCR;
- extrair características dos ingredientes;
- aplicar regras heurísticas;
- executar modelo Random Forest de forma experimental, quando disponível;
- gerar explicação amigável;
- retornar estrutura consolidada para o backend.

## 5.4 ML Lab

Área experimental para treino, validação e análise do modelo Random Forest.

O conteúdo deste módulo serve principalmente para fins acadêmicos, comparação de resultados e documentação do TCC.

---

# 6. Contrato Atual da API

## 6.1 Endpoint Principal

```http
POST /analises
Content-Type: multipart/form-data
Campo do arquivo: imagem
```

O aplicativo mobile deve enviar a imagem usando o campo `imagem`.

Não renomear este endpoint, o campo do arquivo ou a estrutura da resposta sem atualizar todas as camadas impactadas.

## 6.2 Resposta Esperada

Formato geral da resposta:

```json
{
  "analiseId": "1a2b3c4d-5678-90ab-cdef-123456789000",
  "status": "CLASSIFICADO",
  "classificacao": {
    "categoria": "ultraprocessado",
    "status": "ALTO_INDICIO",
    "justificativa": "O produto contém ingredientes e aditivos comumente associados a alimentos ultraprocessados.",
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
      "corante",
      "gordura vegetal"
    ],
    "aviso": "Esta análise possui caráter informativo e não substitui avaliação profissional."
  }
}
```

O contrato pode evoluir, mas qualquer mudança deve preservar compatibilidade com o aplicativo mobile ou atualizar explicitamente o app junto com o backend.

O campo externo `status` admite `CLASSIFICADO` e `NAO_CLASSIFICADO`. `NAO_CLASSIFICADO` é reservado aos casos em que nenhum ingrediente utilizável foi identificado. Quando há ingredientes, mas nenhuma regra define o grupo com segurança, o resultado permanece `CLASSIFICADO`, `novaGrupo` é `null` e o mobile apresenta `NOVA ?`; os demais campos da estrutura permanecem presentes. Para resultados com grupo definido, a precedência oficial é: grupo 2 (família culinária fechada e auxiliares permitidos), grupo 4 (marcadores fortes) e grupo 3 (alimento-base com ingredientes culinários). O campo interno `classificacao.status` preserva `BAIXO_INDICIO`, `MEDIO_INDICIO` e `ALTO_INDICIO`.

O valor `novaGrupo = 1` pertence ao contrato legado e não é válido no escopo atual. O schema aceita somente 2, 3, 4 ou `null`; o mobile converte respostas legadas pelo status interno e nunca deve exibir grupo 1.

As regras controladas devem preservar as seguintes distinções validadas pelo dataset acadêmico:

- grupo 2 reconhece sinônimos explícitos de açúcar/sacarose, sal, óleos, azeites e manteiga;
- manteiga baseada em creme de leite exige contexto textual explícito de que o produto é manteiga;
- grupo 3 aceita combinações controladas de conservas, queijos simples, geleias, frutas em calda e preparações com temperos culinários;
- leite com fermento lácteo, sem outro critério de processamento do grupo 3, não deve ser promovido automaticamente;
- vocabulário adicional nunca pode prevalecer sobre marcadores fortes do grupo 4.

Como o OCR pode remover vírgulas e quebras de linha, o grupo 3 possui uma recuperação determinística por termos controlados. Ela segmenta o texto normalizado pelo termo mais longo e só é aceita quando todas as palavras pertencem ao vocabulário conhecido; qualquer palavra residual impede a atribuição do grupo 3, mas os ingredientes detectados continuam sendo retornados com `novaGrupo = null`.

---

# 7. Papel da Classificação e do Random Forest

A classificação oficial apresentada ao usuário é baseada principalmente no **motor de regras heurísticas**.

O Random Forest possui papel **experimental e acadêmico**. Ele pode ser utilizado para:

- comparação de resultados;
- avaliação técnica;
- geração de métricas;
- discussão no relatório;
- apoio à análise do motor de classificação.

Não transformar o Random Forest na fonte oficial da decisão final sem aprovação explícita do grupo.

Não remover o módulo experimental sem solicitação explícita, pois ele sustenta parte dos objetivos acadêmicos do projeto.

Falhas de carregamento ou inferência do modelo experimental não devem impedir o startup da API nem a resposta produzida pelas regras heurísticas.

---

# 8. Camada de Explicação Amigável

A resposta ao usuário não deve ser apenas técnica.

O sistema deve apresentar uma explicação compreensível, com linguagem acessível e caráter informativo.

A camada de explicação amigável deve priorizar:

- título claro;
- resumo objetivo;
- justificativa compreensível;
- orientação prática;
- evidências encontradas;
- lista de ingredientes relevantes;
- aviso de caráter informativo.

Evitar respostas excessivamente técnicas, frias ou baseadas apenas em score interno.

O objetivo do projeto é ajudar o consumidor a interpretar melhor a lista de ingredientes, não apenas exibir uma classificação bruta.

---

# 9. Regras para Alterações de Código

Ao implementar qualquer solicitação neste projeto, o agente deve atuar com extrema cautela, preservando a estabilidade da aplicação.

## 9.1 Alterar Apenas o Solicitado

- Não realizar refatorações desnecessárias.
- Não reestruturar a arquitetura sem solicitação explícita.
- Não renomear arquivos, classes, funções, endpoints ou diretórios apenas por preferência.
- Não alterar contratos públicos da API sem necessidade.
- Não modificar telas, fluxos ou comportamentos já existentes que não façam parte da solicitação.
- Não adicionar dependências sem necessidade clara.
- Não substituir tecnologias já utilizadas por alternativas não solicitadas.

## 9.2 Preservar Funcionalidades Existentes

Antes de alterar qualquer componente, analisar seus impactos sobre o restante do sistema.

Assuma que toda funcionalidade existente está em uso no projeto e deve ser preservada.

O agente deve ser zeloso e conservador:

- preferir alterações pequenas e localizadas;
- evitar mudanças colaterais;
- não mexer em funcionalidades já em funcionamento;
- preservar comportamento existente sempre que a solicitação não pedir mudança;
- garantir que a correção não quebre fluxos já implementados.

## 9.3 Garantir que Nada Além do Pedido Foi Alterado

Após concluir qualquer ajuste, o agente deve revisar as mudanças e confirmar que:

- apenas os arquivos necessários foram modificados;
- apenas o comportamento solicitado foi alterado;
- nenhuma funcionalidade existente foi removida;
- nenhum fluxo funcional foi impactado sem necessidade;
- nenhum contrato foi quebrado;
- nenhuma alteração oportunista foi incluída.

Se uma melhoria adicional for identificada, ela deve ser registrada como sugestão separada, não implementada automaticamente.

## 9.4 Preservar Compatibilidade Entre Módulos

Toda alteração deve manter compatibilidade entre:

- aplicativo mobile;
- API Backend;
- OCR;
- motor de classificação;
- camada de explicação amigável;
- contrato JSON;
- fluxo completo da aplicação.

Nenhum módulo deve ser alterado de forma isolada sem verificar impacto nos demais.

---

# 10. Compatibilidade Mobile e Android

Este projeto possui um aplicativo mobile em Kivy destinado à execução em dispositivos Android.

Ao realizar alterações, o agente deve preservar não apenas a execução local do backend ou do app em ambiente de desenvolvimento, mas também o funcionamento completo no celular.

Antes de considerar uma tarefa concluída, verificar se as mudanças continuam compatíveis com:

- Buildozer;
- empacotamento Android;
- permissões necessárias para câmera/galeria, quando aplicável;
- comunicação HTTP entre mobile e backend;
- upload de imagens;
- endpoint `POST /analises`;
- campo `imagem` no multipart;
- resposta JSON consumida pelo app;
- exibição correta da tela de resultado;
- tratamento de erros no dispositivo móvel.

Nunca assumir que uma alteração é segura apenas porque o backend executa localmente.

O fluxo abaixo deve permanecer íntegro:

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

# 11. Diretrizes para Codex e Agentes de IA

Ao trabalhar neste repositório, o agente deve se comportar como um engenheiro de manutenção cuidadoso, não como alguém tentando redesenhar o projeto inteiro.

## 11.1 Antes de Implementar

- Ler os arquivos relevantes antes de alterar código.
- Entender o fluxo atual.
- Identificar o menor conjunto de mudanças necessário.
- Verificar se a alteração impacta backend, mobile, contrato JSON ou relatório.
- Em caso de dúvida, preferir a solução mais simples e conservadora.

## 11.2 Durante a Implementação

- Reutilizar componentes existentes.
- Reutilizar `packages/classification_core` para lógica de classificação.
- Reutilizar schemas existentes quando possível.
- Preservar endpoint `POST /analises`.
- Preservar campo `imagem` no upload multipart.
- Preservar resposta amigável consumida pelo mobile.
- Evitar duplicação de lógica.
- Evitar grandes refatorações.
- Evitar alterações cosméticas fora do escopo.

## 11.3 Depois da Implementação

- Conferir se o que foi pedido foi atendido.
- Conferir se nada além do pedido foi alterado.
- Conferir se o backend continua compatível com o app mobile.
- Conferir se o app continua compatível com Android.
- Atualizar documentação somente após a implementação estar finalizada.
- Registrar riscos ou pontos pendentes quando não for possível validar algo completamente.

---

# 12. Fases do Projeto

O projeto segue fases estruturadas:

1. Refinamento do projeto;
2. Definição da arquitetura;
3. Prototipação;
4. Implementação do sistema;
5. Integração e testes;
6. Escrita final do TCC;
7. Preparação da banca.

Sempre considerar em qual fase o projeto está antes de propor mudanças estruturais.

O desenvolvimento ocorre principalmente em mini sprints de 1 ou 2 semanas, com objetivo, tarefas, responsáveis e entregáveis esperados.

Quando apropriado, verificar:

> O grupo já definiu as tarefas da próxima sprint?

---

# 13. Responsabilidades da Equipe

| Integrante | Domínio principal | Responsabilidades |
|---|---|---|
| André (líder) | Arquitetura, backend, cloud e IA | Arquitetura do sistema, backend, OCR, pré-processamento, integração, infraestrutura e decisões técnicas |
| Leo | Mobile, redes e DevOps | Aplicativo mobile, fluxo de telas, integração com API, apoio em execução/deploy |
| Matheus | ABNT, documentação e IA | Motor de classificação, regras, Random Forest experimental, apoio na documentação técnica/acadêmica |
| Pedro | Escrita acadêmica e documentação | Relatório, revisão textual, organização acadêmica, preparação da banca |

---

# 14. Escopo do Projeto

O foco principal do TCC é identificar **indícios de ultraprocessamento em alimentos com base na análise textual da lista de ingredientes**.

Faz parte do escopo atual:

- aplicativo mobile simples e funcional;
- envio de imagem de rótulo;
- OCR com Google Vision API;
- pré-processamento textual;
- classificação por regras;
- Random Forest experimental;
- explicação amigável;
- validação com exemplos reais.

Não faz parte do escopo atual:

- identificação de lactose;
- identificação de glúten;
- classificação vegana;
- classificação vegetariana;
- recomendações nutricionais personalizadas;
- login de usuários;
- histórico de análises;
- banco de dados;
- painel administrativo;
- arquitetura complexa de produção.

Ideias fora do escopo devem ser classificadas como melhoria futura, trabalho futuro ou extensão do projeto.

---

# 15. Diretrizes de Engenharia

Priorizar:

- simplicidade;
- modularidade;
- clareza arquitetural;
- separação de responsabilidades;
- explicabilidade;
- baixo risco de regressão;
- compatibilidade entre backend e mobile;
- viabilidade acadêmica.

Evitar:

- complexidade excessiva;
- dependências desnecessárias;
- refatorações amplas;
- mudanças não solicitadas;
- pipelines de ML complexos demais;
- tecnologias difíceis de manter no prazo do TCC;
- alterações que funcionem apenas localmente e quebrem no Android.

Sempre que uma solução parecer complexa demais, questionar:

> Essa complexidade é realmente necessária para este TCC?

Se não for, propor alternativa mais simples.

---

# 16. Riscos do Projeto

Riscos relevantes:

- complexidade excessiva;
- alteração indevida de funcionalidade já funcionando;
- quebra de compatibilidade entre backend e mobile;
- funcionamento local sem funcionamento no celular;
- dificuldades com OCR;
- ausência ou limitação de dataset;
- Random Forest com papel maior do que o necessário;
- atraso no desenvolvimento;
- documentação desalinhada da implementação.

Ao identificar risco, sugerir mitigação simples e viável.

---

# 17. Coerência Acadêmica

O desenvolvimento do software deve manter coerência com:

- problema de pesquisa;
- hipótese;
- objetivo geral;
- objetivos específicos;
- metodologia;
- modelo oficial de TCC da universidade;
- estrutura do relatório;
- evidências de teste e validação.

A implementação deve gerar material suficiente para capítulos como:

- revisão bibliográfica;
- tecnologias utilizadas;
- planejamento do programa;
- arquitetura da solução;
- funcionamento da aplicação;
- testes e resultados;
- limitações;
- trabalhos futuros.

A escrita acadêmica deve ser impessoal, clara, referenciada e coerente com a implementação real.

---

# 18. Checklist Obrigatório Antes de Finalizar Tarefa

Antes de considerar qualquer tarefa concluída, confirmar:

- [ ] Apenas o que foi solicitado foi alterado.
- [ ] Nenhuma funcionalidade existente foi modificada sem necessidade.
- [ ] Nenhuma refatoração fora do escopo foi feita.
- [ ] O fluxo completo continua funcionando.
- [ ] Os contratos JSON permanecem compatíveis.
- [ ] O backend continua compatível com o aplicativo mobile.
- [ ] O aplicativo continua apto para execução em dispositivos Android.
- [ ] Não foram adicionadas dependências desnecessárias.
- [ ] A arquitetura existente foi preservada.
- [ ] O endpoint `POST /analises` foi preservado, salvo solicitação explícita.
- [ ] O campo multipart `imagem` foi preservado, salvo solicitação explícita.
- [ ] A explicação amigável continua sendo retornada.
- [ ] A documentação não foi atualizada antes da implementação.
- [ ] Após finalizar a implementação, a documentação impactada foi sincronizada com o código.

---

# 19. Objetivo Final do Projeto

Este projeto não visa apenas criar um software funcional.

Ele deve também:

- demonstrar aplicação prática de técnicas de computação;
- produzir resultados analisáveis;
- gerar evidências científicas;
- sustentar um relatório acadêmico consistente;
- apresentar uma solução compreensível para usuários comuns;
- manter escopo viável para um TCC de graduação.

Portanto, agentes devem considerar simultaneamente engenharia de software, experiência do usuário, viabilidade técnica e coerência acadêmica.
