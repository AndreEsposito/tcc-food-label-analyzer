# 🍎 TCC - Analisador de Rótulos Alimentícios

Aplicativo mobile para apoio à identificação de indícios de ultraprocessamento em alimentos a partir da análise textual de ingredientes presentes em rótulos.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Objetivos](#objetivos)
- [Funcionalidades](#funcionalidades)
- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [Stack Tecnológico](#stack-tecnológico)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Como Começar](#como-começar)
- [Documentação](#documentação)
- [Equipe](#equipe)

---

## 👀 Visão Geral

Este repositório contém o desenvolvimento de um **Trabalho de Conclusão de Curso (TCC) em Ciência da Computação** que visa criar uma solução prática para auxiliar consumidores na identificação de alimentos ultraprocessados através da análise inteligente da lista de ingredientes presente nos rótulos.

O sistema utiliza:
- 📸 **Captura de imagem** do rótulo do produto
- 🔍 **OCR** (Google Vision API) para extração textual
- 📝 **Processamento textual** para normalização de dados
- 🤖 **Classificação** baseada em regras e aprendizado de máquina
- 💡 **Explicabilidade** - resultados claros e justificados ao usuário

---

## 🎯 Objetivos

O projeto tiene como objetivo principal:

✅ Identificar **indícios de ultraprocessamento** em alimentos com base na análise da lista de ingredientes

Objetivos secundários:
- Criar uma base arquitetural flexível e modular
- Permitir expansão futura para outras categorias de análise
- Gerar evidências científicas para o relatório acadêmico
- Demonstrar aplicação prática de técnicas de computação

---

## ✨ Funcionalidades

### Atual (Escopo do TCC)
- ✅ Captura de imagem de rótulos alimentícios
- ✅ Extração de texto via OCR
- ✅ Pré-processamento e normalização de ingredientes
- ✅ Classificação de indícios de ultraprocessamento
- ✅ Justificativa explicável do resultado

### Trabalhos Futuros
- 🔜 Detecção de lactose
- 🔜 Detecção de glúten
- 🔜 Classificação vegana/vegetariana
- 🔜 Recomendações nutricionais

---

## 🏗️ Arquitetura do Sistema

O sistema é organizado em **domínios funcionais** independentes:

### 📱 Domínio Mobile
- Captura de imagem do rótulo
- Upload da imagem
- Comunicação com API
- Exibição de resultados

### 🔌 Domínio API Backend
- Orquestração central
- Validação de requisições
- Integração com OCR
- Pré-processamento textual
- Integração com motor de classificação
- Montagem de resposta final

### 👁️ Domínio de OCR
- Integração com Google Vision API
- Extração de texto
- Identificação da lista de ingredientes

### 📖 Domínio de Pré-processamento
- Limpeza de texto
- Normalização de termos
- Separação de ingredientes
- Tokenização

### 🤖 Domínio de Classificação
- **Regras**: lista de ingredientes associados ao ultraprocessamento
- **Machine Learning**: modelo Random Forest (experimental)
- Geração de justificativas

### 🧪 Domínio de Dados e Testes
- Coleta de rótulos
- Montagem de dataset
- Rotulagem de dados
- Validação com produtos reais
- Coleta de métricas

---

## 💻 Stack Tecnológico

| Componente | Tecnologia | Status |
|---|---|---|
| **Mobile** | Flutter / Kotlin | Em definição |
| **Backend** | Python | ✅ Em desenvolvimento |
| **API** | FastAPI / Flask | ✅ Em desenvolvimento |
| **OCR** | Google Vision API | ✅ Planejado |
| **ML** | Random Forest / Scikit-learn | 🔜 Em desenvolvimento |
| **Container** | Docker | ✅ Disponível |
| **Versionamento** | Git | ✅ Em uso |
| **Cloud** | AWS (Opcional) | 🔜 Opcional |

---

## 📁 Estrutura do Projeto

```
tcc-food-label-analyzer/
├── apps/                          # Aplicações principais
│   ├── backend/                   # API Backend
│   │   ├── app/
│   │   │   ├── api/              # Endpoints da API
│   │   │   ├── core/             # Lógica central
│   │   │   ├── models/           # Modelos de dados
│   │   │   ├── repositories/     # Acesso a dados
│   │   │   └── services/         # Serviços
│   │   ├── tests/                # Testes
│   │   └── Dockerfile
│   ├── mobile/                    # Aplicativo Mobile
│   └── ml-lab/                    # Laborátório de ML
│
├── packages/                      # Pacotes reutilizáveis
│   ├── classification-core/       # Motor de classificação
│   ├── contracts/                 # Contratos de API
│   ├── ml-core/                   # Core de ML
│   ├── ocr/                       # Integração OCR
│   └── text-processing/           # Pré-processamento textual
│
├── docs/                          # Documentação e arquivos
│   └── arquitetura.drawio         # Diagrama de arquitetura
│
├── infra/                         # Infraestrutura
│   ├── docker/                    # Configurações Docker
│   ├── env/                       # Variáveis de ambiente
│   └── render/                    # Deploy (Render)
│
├── AGENTS.md                      # Guia para agentes de IA
├── ARCHITECTURE.md                # Detalhes de arquitetura
└── README.md                      # Este arquivo
```

---

## 🚀 Como Começar

### Pré-requisitos
- Python 3.8+
- Git
- Docker (opcional)
- Node.js / Flutter SDK (para mobile)

### Backend

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/tcc-food-label-analyzer.git
cd tcc-food-label-analyzer

# Navegue para o backend
cd apps/backend

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python app/main.py
```

### Com Docker

```bash
cd apps/backend
docker build -t tcc-food-label-backend .
docker run -p 8000:8000 tcc-food-label-backend
```

---

## 📚 Documentação

- [AGENTS.md](AGENTS.md) - Guia para agentes de IA e colaboradores
- [ARCHITECTURE.md](ARCHITECTURE.md) - Detalhes técnicos da arquitetura
- [apps/backend/README.md](apps/backend/README.md) - Documentação do backend
- [apps/mobile/README.md](apps/mobile/README.md) - Documentação do mobile
- [apps/ml-lab/README.md](apps/ml-lab/README.md) - Documentação do lab de ML

---

## 👥 Equipe

| Integrante | Responsabilidade |
|---|---|
| **André** | Arquitetura, Backend, OCR e Pré-processamento |
| **Matheus** | Motor de Classificação e Modelo de ML |
| **Leo** | Aplicativo Mobile |
| **Pedro** | Documentação Acadêmica e Relatório |

---

## 📋 Fases do Projeto

1. ✅ Refinamento do projeto
2. ✅ Definição da arquitetura
3. 🔄 Implementação do sistema e prototipação
4. 🔜 Integração e testes
5. 🔜 Montagem da apresentação do TCC
6. 🔜 Preparação da banca

---

## 📝 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

---

## 📞 Contato

Para dúvidas ou sugestões, abra uma issue no repositório.

---

**Desenvolvido como Trabalho de Conclusão de Curso em Ciência da Computação** 🎓
