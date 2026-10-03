# Validação das regras NOVA com 20 rótulos

Esta regressão usa transcrições manuais de trechos legíveis do documento `20 imagens para testes.pdf`, fornecido para o TCC. Os testes não chamam Google Vision, não comparam pixels e não medem acurácia de reconhecimento de imagens. As classificações esperadas reproduzem a tabela de referência discutida com o responsável pelo projeto.

## Casos de referência

| Imagem | Produto identificado | NOVA esperada | Evidência usada no teste |
|---|---|---|---|
| 01 | rosto | ? | Sem lista utilizável. |
| 02 | tela do Google | ? | Sem lista utilizável. |
| 03 | açúcar refinado | 2 | Denominação + peso líquido; ingredientes não lidos. |
| 04 | atum | 3 | Composição transcrita do rótulo. |
| 05 | aveia | 1 | Composição transcrita do rótulo. |
| 06 | azeite | 2 | Composição transcrita do rótulo. |
| 07 | biscoito Oreo | 4 | Composição transcrita do rótulo. |
| 08 | cebola empanada | 4 | Composição transcrita do rótulo. |
| 09 | Coca-Cola Original | 4 | Composição transcrita do rótulo. |
| 10 | creatina pura | ? | Ingredientes lidos; regra não determina NOVA. |
| 11 | extrato de tomate | 3 | Composição transcrita do rótulo. |
| 12 | iogurte natural | 1 | Composição transcrita do rótulo. |
| 13 | bebida em cápsulas KitKat | 4 | Composição transcrita do rótulo. |
| 14 | biscoito maizena de chocolate | 4 | Composição transcrita do rótulo. |
| 15 | manteiga com sal | 2 | Inclui o título da página identificando manteiga. |
| 16 | milho em conserva | 3 | Composição transcrita do rótulo. |
| 17 | macarrão instantâneo com tempero | 4 | Composição transcrita do rótulo. |
| 18 | achocolatado Nescau | 4 | Composição transcrita do rótulo. |
| 19 | leite zero lactose | 1 | Composição transcrita do rótulo. |
| 20 | sardinha | 3 | Composição transcrita do rótulo. |

Distribuição: NOVA 1 = 3; NOVA 2 = 3; NOVA 3 = 4; NOVA 4 = 7; indeterminada = 3. “?” não é um quinto grupo NOVA. Nos casos 01 e 02, a API retorna `NAO_CLASSIFICADO`; na creatina pura, retorna `CLASSIFICADO`, `novaGrupo: null` e ingredientes identificados.

A imagem 13 é uma bebida em cápsulas KitKat Dolce Gusto, não uma barra de chocolate. A marca não entra em nenhuma regra. O arquivo de referência armazena produto e número somente para rastreabilidade dos testes.

## Mudanças nas regras

- Grupo 1: receitas fechadas de aveia, leite e iogurte natural. Inclui a lista de culturas lácteas transcrita e auxiliares explicitamente reconhecidos do leite, como lactase, citrato e fosfatos de sódio. Uma palavra desconhecida impede a classificação por essas receitas. A lista de auxiliares do leite não se aplica automaticamente ao iogurte.
- Grupo 2: variantes de azeite virgem extra, declaração explícita `100%`, e manteiga com creme de leite e cloreto de sódio/sal quando o texto completo identifica o produto como manteiga. Auxiliares desconhecidos não são descartados.
- Grupo 3: milho verde com salmoura de água e sal, nome botânico da soja na composição do atum, sardinhas sem pele/espinha e óleo comestível. Qualificadores reconhecidos são expressões controladas; parênteses não são removidos genericamente porque podem conter subingredientes relevantes.
- Grupo 4: prioridade aos marcadores fortes, incluindo aromas naturais adicionados, emulsificantes/lecitina, soro de leite, dextrose, goma guar e E-150d. A regra antiga que aceitava “aroma natural de endro” como grupo 3 foi corrigida: endro como tempero culinário e aroma adicionado exigem tratamentos distintos.
- Extração: cabeçalhos `Ingredientes:`, `Ingredients:` e `INGR.:`; terminações por alergênicos com ou sem acento, lactose, instruções de conservação e texto nutricional; preservação da composição do macarrão e do tempero. A tabela nutricional fora da lista não invalida um ingrediente desconhecido, como creatina.
- API/mobile: `novaGrupo` aceita 1–4 ou `null`; NOVA 1 tem explicação e configuração visual próprias. O status BAIXO/MÉDIO/ALTO, sozinho, não determina NOVA. O endpoint `POST /analises`, o campo `imagem` e os demais campos JSON permanecem.
- Random Forest: continua experimental, sem novo treino ou alteração do vetor de características. Os testes não comprovam a qualidade de seu modelo binário; indisponibilidade do modelo não impede a resposta heurística.

## Identificação do produto e limites do recorte

A imagem 03 mostra a frente da embalagem de açúcar, sem lista de ingredientes. A exceção exige denominação de açúcar refinado em uma linha e peso líquido explícito, sem cabeçalho de ingredientes, tabela nutricional, marcadores fortes ou termos incompatíveis. A resposta registra “denominação do produto” nas evidências, conserva `ingredientesDetectados: []` e explica que a composição não foi lida. Uma lista presente nunca é substituída por essa exceção. Outras denominações de produtos não são classificadas por marca ou aparência.

Na imagem 15, “manteiga com sal” está no título da página do documento. A lista visível na fotografia contém apenas creme de leite e cloreto de sódio (sal). O teste inclui esse título explicitamente; um recorte contendo somente a lista continua indeterminado. Para obter NOVA 2 com a foto real, o texto OCR precisa também identificar o produto como manteiga. O sistema atual faz análise textual, sem um modelo visual de reconhecimento de produtos.

A creatina monohidratada pura continua com grupo indeterminado e ingredientes preservados. A existência de uma lista legível e a ausência de marcadores fortes não autorizam sua promoção automática a NOVA 1.

## Reprodução dos testes

Na raiz do repositório, em PowerShell:

```powershell
$env:PYTHONPATH = "$PWD;$PWD\apps\backend"
python -m pytest apps/backend/tests apps/mobile/Ingresense_app/tests -q -p no:cacheprovider
```

Em Linux/macOS:

```sh
PYTHONPATH=.:apps/backend python -m pytest apps/backend/tests apps/mobile/Ingresense_app/tests -q -p no:cacheprovider
```

Resultado observado nesta alteração: **169 testes aprovados**, incluindo os 20 casos através do core, endpoint FastAPI com OCR simulado e normalizador HTTP do mobile, além de casos negativos de componentes desconhecidos, aditivos e recortes insuficientes. Houve um aviso de depreciação preexistente do status HTTP 422; nenhum teste falhou. A execução local usou Python 3.13 e as bibliotecas disponíveis no ambiente; não substitui execução no ambiente de deploy com as versões fixadas em `apps/requirements.txt`.

Dados: [nova_20_rotulos.json](../apps/backend/tests/fixtures/nova_20_rotulos.json). Teste de integração: [test_nova_reference_labels.py](../apps/backend/tests/test_nova_reference_labels.py).

Não foram executados Google Vision sobre as 20 imagens, build APK ou teste em dispositivo Android. Nenhum serviço foi redeployado. Após revisão da alteração, a validação com OCR real deve registrar separadamente o texto extraído, divergências da transcrição e resultado NOVA; o teste no celular deve verificar upload, selo NOVA 1, NOVA ? e mensagens de nova captura.

## Referências de classificação

- NUPENS/USP. [Aprenda a classificar alimentos](https://nupens.fsp.usp.br/aprenda-a-classificar-alimentos/). Referência para os grupos e para o tratamento contextual de estabilizadores do leite UHT.
- Monteiro CA et al. (2019). [Ultra-processed foods: what they are and how to identify them](https://doi.org/10.1017/S1368980018003762). Public Health Nutrition, 22(5), 936–941. Referência para identificação de marcadores industriais e aditivos cosméticos.

O conjunto fechado de 20 exemplos é uma regressão de comportamento. Ele não constitui amostra independente de validação científica nem sustenta uma taxa geral de acerto.
