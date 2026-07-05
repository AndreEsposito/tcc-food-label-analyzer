<div align="center">

# 📱 IngreSense — Mobile

**Aplicativo Android para análise de rótulos alimentares**  
Desenvolvido com Kivy · Python 3.10+ · TCC

</div>

---

## Sobre o App

O IngreSense permite que o usuário capture ou selecione a imagem de um rótulo alimentício e receba uma análise explicável sobre possíveis indícios de ultraprocessamento com base na lista de ingredientes.

O app envia a imagem para a API backend, que realiza OCR com Google Vision API, processa o texto extraído, aplica classificação baseada em regras heurísticas e retorna uma resposta amigável para exibição na tela de resultado.

O Random Forest existe no projeto como módulo experimental/acadêmico, mas a decisão principal apresentada ao usuário é baseada no motor de regras.

---

## Stack Mobile

- Python
- Kivy
- Requests
- Plyer
- Buildozer / python-for-android para geração do APK Debug

> O app não utiliza KivyMD, Flutter ou Kotlin.

---

## Estrutura

```text
apps/mobile/Ingresense_app/
│
├── main.py                    # Ponto de entrada da aplicação
├── buildozer.spec             # Configuração de build Android
├── p4a_hooks.py               # Ajustes do Manifest gerado pelo python-for-android
├── android_src/               # Classe Android usada pela camera nativa
│
├── config/
│   └── settings.py            # URL da API
│
├── screens/                   # Lógica de cada tela
│   ├── splash.py              # Tela inicial animada
│   ├── home.py                # Menu principal
│   ├── camera.py              # Captura via camera nativa Android
│   ├── preview.py             # Prévia e confirmação da imagem
│   └── result.py              # Resultado: loading / erro / sucesso
│
├── layouts/                   # UI declarativa em arquivos .kv
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

## Rodando Localmente

### 1. Pré-requisitos

- Python 3.10 ou superior.
- pip atualizado.
- Backend disponível localmente ou no Render.

### 2. Instalar dependências

```bash
pip install kivy requests plyer
```

No Windows, se `pip` não for reconhecido:

```bash
python -m pip install kivy requests plyer
```

### 3. Configurar a URL da API

Abra `config/settings.py` e defina a URL correta.

Desenvolvimento local com backend na mesma máquina:

```python
API_URL = "http://localhost:8000"
```

Produção/Render:

```python
API_URL = "https://tcc-food-label-analyzer.onrender.com"
```

Emulador Android acessando localhost da máquina host:

```python
API_URL = "http://10.0.2.2:8000"
```

> O backend no Render pode demorar cerca de 30 segundos para responder na primeira requisição após período de inatividade no plano free. Se aparecer erro de timeout, tente novamente.

### 4. Rodar o app localmente

```bash
cd apps/mobile/Ingresense_app
python main.py
```

---

## Fluxo de Telas

```text
Splash → Home → Câmera/Galeria → Preview → Resultado
                                               │
                                    ┌──────────┴──────────┐
                                 Sucesso                 Erro
                           Resultado amigável      Mensagem + ação
```

A tela de resultado deve preservar a apresentação amigável da análise, evitando exibir somente dados técnicos.

---

## Integração com o Backend

O serviço `services/api_service.py` realiza:

```http
POST /analises
Content-Type: multipart/form-data
Campo: imagem
```

O campo `imagem` é obrigatório e faz parte do contrato entre mobile e backend.

Não renomear o endpoint, o campo de upload ou a estrutura consumida pela tela de resultado sem atualizar backend e mobile juntos.

---

## Resposta Consumida pelo App

O backend retorna uma resposta expandida. Exemplo resumido:

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

Campos relevantes para a tela:

- `classificacao.status`;
- `classificacao.novaGrupo`;
- `classificacao.titulo`;
- `classificacao.resumo`;
- `classificacao.justificativa`;
- `classificacao.orientacao`;
- `classificacao.evidencias`;
- `classificacao.ingredientesDetectados`;
- `classificacao.aviso`.

Mapeamento conceitual:

| `classificacao.status` | Interpretação no app |
|---|---|
| `ALTO_INDICIO` | Alto indício de ultraprocessamento |
| `MEDIO_INDICIO` | Indício moderado de processamento |
| `BAIXO_INDICIO` | Baixo indício de ultraprocessamento |

---

## Tratamento de Erros

| Código HTTP | Causa | Mensagem esperada ao usuário |
|---|---|---|
| 400 | Arquivo inválido ou vazio | Imagem inválida ou vazia |
| 422 | OCR sem texto extraído | Não foi possível ler o rótulo |
| 502 | Falha no serviço de OCR | Serviço de leitura indisponível |
| 504 | Timeout do OCR | O serviço demorou para responder |
| — | Sem conexão | Sem conexão com o servidor |

---

## Gerando o APK Debug Android

O objetivo deste projeto é gerar somente APK Android Debug para testes manuais.

Não há:

- APK Release;
- AAB;
- assinatura de produção;
- publicação na Play Store.

O build utiliza Buildozer e requer Linux ou WSL.

### 1. Instalar o WSL no Windows

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

Antes de gerar o APK, certifique-se de que `config/settings.py` aponta para o backend acessível pelo celular, preferencialmente no Render:

```python
API_URL = "https://tcc-food-label-analyzer.onrender.com"
```

> Não usar `localhost` em APK instalado no celular físico, pois `localhost` apontará para o próprio aparelho, não para o computador.

### 4. Gerar o APK

```bash
cd apps/mobile/Ingresense_app
buildozer android debug
```

A primeira execução baixa Android SDK/NDK e pode demorar. As execuções seguintes tendem a ser mais rápidas.

O APK gerado ficará em:

```text
apps/mobile/Ingresense_app/bin/*-debug.apk
```
### 5. Gerar pelo GitHub Actions

Também existe um workflow para gerar o APK automaticamente:

1. Abra a aba **Actions** do repositório no GitHub.
2. Selecione **Android Debug APK**.
3. Clique em **Run workflow**.
4. Aguarde a execução terminar.
5. Abra a execução finalizada.
6. Baixe o artifact **ingresense-debug-apk**.
7. Extraia o arquivo `.zip`; dentro dele estará o APK Debug.

O workflow publica apenas o artifact do APK Debug e não cria release.

### 6. Instalar no celular

Transfira o APK para o celular via USB, Google Drive ou outro meio.

Pode ser necessário habilitar **Instalar de fontes desconhecidas** nas configurações do Android.

Passo geral:

1. Copie o APK para o aparelho.
2. Abra o APK pelo app **Meus Arquivos**, navegador ou Google Drive.
3. Quando o Android bloquear a instalação, toque em **Configurações**.
4. Habilite **Permitir desta fonte** para o app usado.
5. Volte ao APK e confirme **Instalar**.

---

## Cuidados ao Alterar o Mobile

Ao alterar o app, preservar:

- fluxo de telas existente;
- integração com `POST /analises`;
- campo multipart `imagem`;
- consumo do JSON expandido;
- mensagens de erro amigáveis;
- compatibilidade com execução em celular Android;
- compatibilidade com Buildozer.

Não considerar uma alteração segura apenas porque o app roda localmente no computador.

O fluxo completo abaixo deve continuar funcionando:

```text
Mobile Android → Backend → OCR → Classificação → JSON → Mobile Android
```

---

## Observações

- Para testes sem backend, usar mock somente quando essa estratégia já estiver prevista no código.
- Para emulador Android acessando localhost da máquina host, usar `API_URL = "http://10.0.2.2:8000"`.
- Para celular físico, usar uma URL acessível pelo aparelho, como a URL do Render ou IP da rede local configurado corretamente.
- A resposta ao usuário deve manter linguagem amigável e caráter informativo.

---

## Regra de Atualização Documental

Atualizar este README somente depois que alterações de implementação no app estiverem concluídas e validadas.

Sempre que o contrato com o backend mudar, atualizar também:

- README raiz;
- `ARCHITECTURE.md`;
- `apps/backend/README.md`;
- `AGENTS.md`, quando houver impacto nas diretrizes dos agentes.
