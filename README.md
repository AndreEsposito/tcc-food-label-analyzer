# TCC - Food Label Analyzer

Aplicativo para apoiar a identificacao de indicios de ultraprocessamento em alimentos a partir da leitura da lista de ingredientes no rotulo.

## Visao Geral
O projeto segue arquitetura modular com foco academico (TCC) e explicabilidade do resultado.

Fluxo principal:
1. Captura/upload da imagem do rotulo
2. OCR (Google Vision API)
3. Pre-processamento textual
4. Classificacao de indicios de ultraprocessamento
5. Retorno com justificativa

## Status Atual
- Backend FastAPI funcional com endpoint `POST /analises`
- Classificacao rule-based ativa (ML ainda experimental)
- Deploy suportado em Render via `render.yaml`
- Configuracao de credenciais consolidada nos README(s)

## Backend (Resumo)
O backend recebe imagem em `multipart/form-data`, extrai texto com OCR, normaliza ingredientes e retorna classificacao explicavel.

Resposta esperada:
- `categoria`: `ultraprocessado`
- `status`: `ALTO_INDICIO`, `MEDIO_INDICIO` ou `BAIXO_INDICIO`
- `justificativa`: texto com evidencias da decisao

Para setup completo (credenciais, variaveis de ambiente, execucao local e deploy), use o README especifico do backend:
- [apps/backend/README.md](apps/backend/README.md)

## Como Comecar
1. Clone o repositorio
2. Acesse o modulo que deseja executar
3. Siga o README especifico do modulo

Exemplo (backend):
```bash
cd apps/backend
# siga as instrucoes do README do backend
```

## Mapa de Documentacao (README Hub)
Este README da raiz funciona como ponto central. A documentacao detalhada fica nos READMEs especificos:

- [README.md](README.md) - Visao geral do projeto (este arquivo)
- [apps/backend/README.md](apps/backend/README.md) - API, OCR, credenciais, deploy e troubleshooting
- [apps/mobile/README.md](apps/mobile/README.md) - App mobile
- [apps/ml-lab/README.md](apps/ml-lab/README.md) - Experimentos de ML

Documentos de apoio da raiz:
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura macro do sistema
- [AGENTS.md](AGENTS.md) - Guia de colaboracao para agentes e contribuidores

## Escopo do TCC
Foco do trabalho:
- identificar indicios de ultraprocessamento via ingredientes

Possiveis expansoes futuras (fora do escopo inicial):
- deteccao de lactose
- deteccao de gluten
- classificacao vegana/vegetariana
- recomendacoes nutricionais

## Equipe
- Andre: arquitetura, backend, OCR e pre-processamento
- Matheus: classificacao e ML
- Leo: mobile
- Pedro: documentacao academica
