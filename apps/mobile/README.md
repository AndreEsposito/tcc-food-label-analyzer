<div align="center">

# 📱 IngreSense — Mobile

**Aplicativo Android para análise de rótulos alimentares**  
Desenvolvido com [Kivy](https://kivy.org/) · Python 3.10+ · TCC 2025

</div>

---

## Sobre o app

O IngreSense permite que qualquer pessoa fotografe o rótulo de um produto e saiba instantaneamente o nível de processamento segundo a **classificação NOVA** — a escala mais reconhecida internacionalmente para identificação de ultraprocessados.

O app envia a imagem para a API backend, que realiza OCR + classificação rule-based e retorna o resultado com justificativa. O app exibe o grupo NOVA, o que ele significa e o que o usuário deve fazer com essa informação.

---

## Estrutura

```
apps/mobile/Ingresense_app/
│
├── main.py                    # Ponto de entrada da aplicação
├── buildozer.spec             # Configuração de build Android
│
├── config/
│   └── settings.py            # URL da API (trocar para produção antes do APK)
│
├── screens/                   # Lógica de cada tela
│   ├── splash.py              # Tela inicial animada
│   ├── home.py                # Menu principal
│   ├── camera.py              # Captura via câmera ou galeria
│   ├── preview.py             # Prévia e confirmação da imagem
│   └── result.py              # Resultado: loading / erro / sucesso
│
├── layouts/                   # UI declarativa (arquivos .kv)
│   ├── splash.kv
│   ├── home.kv
│   ├── camera.kv
│   ├── preview.kv
│   └── result.kv
│
├── services/
│   └── api_service.py         # Integração com POST /analises
│
├── utils/
│   └── image_utils.py
│
└── assets/
    └── images/                # Ícones e imagens da UI
```

---

## Rodando localmente

### 1. Pré-requisitos

- Python 3.10 ou superior
- pip atualizado

### 2. Instalar dependências

```bash
pip install kivy requests plyer
```

> No Windows, se `pip` não for reconhecido:
> ```bash
> python -m pip install kivy requests plyer
> ```

### 3. Configurar a URL da API

Abra `config/settings.py` e defina a URL correta:

```python
# Desenvolvimento local (backend rodando na sua máquina)
API_URL = "http://localhost:8000"

# Produção (Render)
API_URL = "https://tcc-food-label-analyzer.onrender.com"
```

> ⚠️ O backend no Render pode demorar ~30 segundos para responder na primeira requisição após período de inatividade (plano free). Se aparecer erro de timeout, basta tentar novamente.

### 4. Rodar o app

```bash
cd apps/mobile/Ingresense_app
python main.py
```

---

## Fluxo de telas

```
Splash → Home → Câmera/Galeria → Preview → Resultado
                                               │
                                    ┌──────────┴──────────┐
                                 Sucesso                 Erro
                              (4 cards NOVA)        (título + dica
                                                   + tentar novamente)
```

---

## Integração com o backend

O serviço `api_service.py` realiza `POST /analises` enviando a imagem como `multipart/form-data`.

A resposta do backend é normalizada para o formato consumido pela tela de resultado:

| `classificacao.status` (backend) | `nova_grupo` (app) | Exibição            |
|----------------------------------|--------------------|---------------------|
| `ALTO_INDICIO`                   | 4                  | Ultraprocessado     |
| `MEDIO_INDICIO`                  | 3                  | Alimento processado |
| `BAIXO_INDICIO`                  | 1                  | Baixo processamento |

### Tratamento de erros

| Código HTTP | Causa                        | Mensagem ao usuário                     |
|-------------|------------------------------|-----------------------------------------|
| 400         | Arquivo inválido ou vazio    | Imagem inválida ou vazia                |
| 422         | OCR sem texto extraído       | Não foi possível ler o rótulo           |
| 502         | Falha no serviço de OCR      | Serviço de leitura indisponível         |
| 504         | Timeout do OCR               | O serviço demorou para responder        |
| —           | Sem conexão                  | Sem conexão com o servidor              |

---

## Gerando o APK Debug (Android)

O objetivo deste projeto e gerar somente APK Android Debug para testes manuais.
Nao ha APK Release, AAB, assinatura de producao ou publicacao na Play Store.

O arquivo `apps/mobile/Ingresense_app/buildozer.spec` fixa o
`python-for-android` em `v2024.01.21`, uma versao compativel com
`kivy==2.3.0`.

O build utiliza [Buildozer](https://buildozer.readthedocs.io/) e **requer Linux ou WSL**.

### 1. Instalar o WSL (Windows)

Abra o PowerShell como administrador:

```powershell
wsl --install
```

Reinicie o PC. O Ubuntu será instalado automaticamente.

### 2. Instalar dependências no Ubuntu/WSL

```bash
sudo apt update && sudo apt install -y \
  git zip unzip openjdk-17-jdk python3-pip \
  autoconf libtool pkg-config zlib1g-dev \
  libncurses5-dev libncursesw5-dev cmake \
  libffi-dev libssl-dev

python3 -m pip install --user --break-system-packages \
  "Cython==0.29.37" "buildozer==1.6.0"

export PATH="$HOME/.local/bin:$PATH"
export PIP_BREAK_SYSTEM_PACKAGES=1
```

### 3. Configurar a URL de produção

Antes de gerar o APK, certifique-se que `config/settings.py` aponta para o Render:

```python
API_URL = "https://tcc-food-label-analyzer.onrender.com"
```

### 4. Gerar o APK

```bash
cd apps/mobile/Ingresense_app
buildozer android debug
```

> A primeira execução baixa o Android SDK e NDK (~1 GB) e pode demorar entre 20 e 40 minutos. As execuções seguintes são muito mais rápidas.

O APK gerado estara em `bin/ingresense-1.0.0-arm64-v8a_armeabi-v7a-debug.apk`
ou em outro arquivo `bin/*-debug.apk`, conforme as arquiteturas configuradas.

### 5. Gerar pelo GitHub Actions

Tambem existe um workflow para gerar o APK automaticamente:

1. Abra a aba **Actions** do repositorio no GitHub.
2. Selecione **Android Debug APK**.
3. Clique em **Run workflow**.
4. Aguarde a execucao terminar.
5. Abra a execucao finalizada e baixe o artifact **ingresense-debug-apk**.
6. Extraia o arquivo `.zip`; dentro dele estara o APK Debug.

O workflow publica apenas o artifact do APK Debug e nao cria release.

### 6. Instalar no celular

Transfira o APK para o celular via USB ou qualquer meio e instale. Pode ser necessário habilitar **"Instalar de fontes desconhecidas"** nas configurações do Android.

No Samsung Galaxy S25+, o caminho pode variar conforme o app usado para abrir o
arquivo. Em geral:

1. Copie o APK para o aparelho.
2. Abra o APK pelo app **Meus Arquivos**, navegador ou Google Drive.
3. Quando o Android bloquear a instalacao, toque em **Configuracoes**.
4. Habilite **Permitir desta fonte** para o app usado.
5. Volte ao APK e confirme **Instalar**.

---

## Observações

- O campo `justificativa` retornado pelo backend é exibido diretamente na tela de resultado
- Para testes sem o backend, defina `USAR_MOCK = True` em `services/api_service.py`
- Para emulador Android acessando localhost da máquina host, use `API_URL = "http://10.0.2.2:8000"`
