import mimetypes
import os

import requests

# URL do backend. Em desenvolvimento, usar localhost.
# Em produção, substituir pela URL do Render.
# Exemplo Render: https://food-label-analyzer.onrender.com
from config.settings import API_URL

# Trocar para False quando a API estiver acessível
USAR_MOCK = False


def enviar_imagem(caminho_imagem: str) -> dict:
    """
    Envia a imagem para o backend e retorna o resultado normalizado.

    Retorno em caso de sucesso:
    {
        "nova_grupo": int (1–4) ou None quando a análise for inconclusiva,
        "classificacao": str,
        "justificativa": str,
        "ingredientes_detectados": [str, ...]
    }

    Retorno em caso de erro:
    {
        "erro": str
    }
    """
    if USAR_MOCK:
        return _mock_resposta()
    return _chamar_api(caminho_imagem)


def _chamar_api(caminho_imagem: str) -> dict:
    try:
        with open(caminho_imagem, "rb") as f:
            filename = os.path.basename(caminho_imagem) or "rotulo.jpg"
            content_type = mimetypes.guess_type(filename)[0] or "image/jpeg"
            response = requests.post(
                f"{API_URL}/analises",
                files={"imagem": (filename, f, content_type)},
                timeout=20,
            )
        response.raise_for_status()
        return _normalizar_resposta(response.json())

    except requests.exceptions.Timeout:
        return {
            "erro": "O servidor demorou para responder.",
            "detalhe": "Verifique sua conexão e tente novamente.",
            "codigo": 504,
        }
    except requests.exceptions.ConnectionError:
        return {
            "erro": "Sem conexão com o servidor.",
            "detalhe": "Verifique se você está conectado à internet.",
            "codigo": 0,
        }
    except requests.exceptions.HTTPError as e:
        response = e.response
        codigo = response.status_code if response is not None else 0
        detalhe_servidor = _extrair_detalhe_servidor(response)
        return _erro_por_codigo(codigo, detalhe_servidor)
    except Exception as e:
        return {
            "erro": "Erro inesperado.",
            "detalhe": str(e),
            "codigo": -1,
        }


def _extrair_detalhe_servidor(response) -> str:
    if response is None:
        return ""

    try:
        dados = response.json()
    except ValueError:
        return (response.text or "").strip()

    detalhe = dados.get("detail", "")
    if isinstance(detalhe, str):
        return detalhe
    return str(detalhe) if detalhe else ""


def _erro_por_codigo(codigo: int, detalhe_servidor: str = "") -> dict:
    """Mapeia codigos de erro do backend para mensagens amigaveis."""
    if codigo == 400:
        return {
            "erro": "Imagem invalida ou vazia.",
            "detalhe": "Certifique-se de enviar um arquivo de imagem valido (JPG, PNG, etc.).",
            "codigo": 400,
        }
    if codigo == 422:
        return {
            "erro": "Nao foi possivel ler o rotulo.",
            "detalhe": "Tente uma foto mais nitida, bem iluminada e com o rotulo centralizado.",
            "codigo": 422,
        }
    if codigo == 502:
        return {
            "erro": "Servico de leitura indisponivel.",
            "detalhe": "O servico de OCR esta com instabilidade. Tente novamente em instantes.",
            "codigo": 502,
            "detalhe_tecnico": detalhe_servidor,
        }
    if codigo == 504:
        return {
            "erro": "O servico demorou para responder.",
            "detalhe": "O OCR excedeu o tempo limite. Tente novamente.",
            "codigo": 504,
            "detalhe_tecnico": detalhe_servidor,
        }
    if codigo == 404:
        return {
            "erro": "Endpoint da API nao encontrado.",
            "detalhe": "Verifique se a URL do backend e a rota /analises estao corretas.",
            "codigo": 404,
            "detalhe_tecnico": detalhe_servidor,
        }
    if codigo >= 500:
        return {
            "erro": f"Falha interna do servidor ({codigo}).",
            "detalhe": "O backend respondeu com erro. Tente novamente em instantes.",
            "codigo": codigo,
            "detalhe_tecnico": detalhe_servidor,
        }
    return {
        "erro": f"Erro do servidor ({codigo}).",
        "detalhe": "Tente novamente. Se o problema persistir, contate o suporte.",
        "codigo": codigo,
        "detalhe_tecnico": detalhe_servidor,
    }


def _normalizar_resposta(dados: dict) -> dict:
    """
    Converte o contrato do backend para o formato que o ResultScreen consome.

    Backend retorna:
      classificacao.status       -> "ALTO_INDICIO" | "MEDIO_INDICIO" | "BAIXO_INDICIO"
      classificacao.categoria    -> "ultraprocessado"
      classificacao.justificativa -> texto descritivo

    App consome:
      nova_grupo    -> int 2–4 (escala NOVA) ou None
      classificacao -> label legível
      justificativa -> texto descritivo
    """
    try:
        classificacao = dados.get("classificacao", {})
        status_analise = dados.get("status", "CLASSIFICADO")
        status = classificacao.get("status", "")
        categoria = classificacao.get("categoria", "desconhecido")

        _, label = _status_para_nova(status, categoria)
        titulo = classificacao.get("titulo") or label

        nova_grupo_backend = classificacao.get("novaGrupo")
        if nova_grupo_backend in {2, 3, 4}:
            nova_grupo_resposta = nova_grupo_backend
        else:
            # O status BAIXO/MEDIO/ALTO não comprova sozinho um grupo NOVA.
            # Respostas legadas com grupo 1 ou sem novaGrupo são inconclusivas,
            # evitando transformar uma análise antiga genérica em NOVA 2.
            nova_grupo_resposta = None
            if status_analise != "NAO_CLASSIFICADO":
                titulo = "Classificação inconclusiva"
        resultado = {
            "nova_grupo": nova_grupo_resposta,
            "classificacao": titulo,
            "titulo": titulo,
            "resumo": classificacao.get("resumo", ""),
            "justificativa": classificacao.get("justificativa", ""),
            "orientacao": classificacao.get("orientacao", ""),
            "evidencias": classificacao.get("evidencias", []),
            "ingredientes_detectados": classificacao.get("ingredientesDetectados", []),
            "aviso": classificacao.get("aviso", ""),
        }
        if status_analise == "NAO_CLASSIFICADO" or nova_grupo_resposta is None:
            resultado["nao_classificado"] = True
        return resultado
    except Exception:
        return {"erro": "Resposta inesperada do servidor."}


# ──────────────────────────────────────────────────────────────────────────────
# Mapeamento NOVA
# ──────────────────────────────────────────────────────────────────────────────

_MAPA_NOVA = {
    "ALTO_INDICIO":  (4, "Ultraprocessado"),
    "MEDIO_INDICIO": (3, "Alimento processado"),
    "BAIXO_INDICIO": (2, "Ingrediente culinário processado"),
}


def _status_para_nova(status: str, categoria: str) -> tuple[int | None, str]:
    if status in _MAPA_NOVA:
        return _MAPA_NOVA[status]
    # A categoria pública permanece "ultraprocessado" em todos os grupos e,
    # portanto, não sustenta inferência de NOVA quando o status é desconhecido.
    return None, "Classificação inconclusiva"


# ──────────────────────────────────────────────────────────────────────────────
# Mock — remover quando a API estiver integrada
# ──────────────────────────────────────────────────────────────────────────────

def _mock_resposta() -> dict:
    import time
    time.sleep(2)
    return {
        "nova_grupo": 4,
        "classificacao": "Ultraprocessado",
        "titulo": "Ultraprocessado",
        "resumo": "Este produto possui ingredientes comuns em alimentos ultraprocessados.",
        "orientacao": (
            "Vale consumir com atenção e comparar com produtos que tenham uma lista "
            "de ingredientes menor e com nomes mais familiares."
        ),
        "evidencias": [
            {
                "termo": "corante",
                "tipo": "corante",
                "descricao": "Pode indicar uso de substâncias para alterar a aparência do produto.",
            },
            {
                "termo": "aromatizante",
                "tipo": "aromatizante",
                "descricao": "Pode indicar uso de substâncias para alterar ou intensificar o sabor.",
            },
        ],
        "ingredientes_detectados": ["corante", "aromatizante", "maltodextrina"],
        "aviso": (
            "Resultado informativo baseado na lista de ingredientes identificada pelo OCR. "
            "Esta análise não substitui a avaliação de um profissional de nutrição."
        ),
        "justificativa": (
            "O produto foi classificado como ultraprocessado devido à presença de: "
            "corante, aromatizante, glutamato monossódico, maltodextrina."
        ),
    }

