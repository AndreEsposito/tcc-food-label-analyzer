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
        "nova_grupo": int (1–4),
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
            response = requests.post(
                f"{API_URL}/analises",
                files={"imagem": f},
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
        codigo = e.response.status_code if e.response else 0
        return _erro_por_codigo(codigo)
    except Exception as e:
        return {
            "erro": "Erro inesperado.",
            "detalhe": str(e),
            "codigo": -1,
        }


def _erro_por_codigo(codigo: int) -> dict:
    """
    Mapeia os códigos de erro do backend para mensagens amigáveis.
    Reflete exatamente o que o analises.py pode retornar.
    """
    if codigo == 400:
        return {
            "erro": "Imagem inválida ou vazia.",
            "detalhe": "Certifique-se de enviar um arquivo de imagem válido (JPG, PNG, etc.).",
            "codigo": 400,
        }
    if codigo == 422:
        return {
            "erro": "Não foi possível ler o rótulo.",
            "detalhe": "Tente uma foto mais nítida, bem iluminada e com o rótulo centralizado.",
            "codigo": 422,
        }
    if codigo == 502:
        return {
            "erro": "Serviço de leitura indisponível.",
            "detalhe": "O serviço de OCR está com instabilidade. Tente novamente em instantes.",
            "codigo": 502,
        }
    if codigo == 504:
        return {
            "erro": "O serviço demorou para responder.",
            "detalhe": "O OCR excedeu o tempo limite. Tente novamente.",
            "codigo": 504,
        }
    return {
        "erro": f"Erro do servidor ({codigo}).",
        "detalhe": "Tente novamente. Se o problema persistir, contate o suporte.",
        "codigo": codigo,
    }


def _normalizar_resposta(dados: dict) -> dict:
    """
    Converte o contrato do backend para o formato que o ResultScreen consome.

    Backend retorna:
      classificacao.status       -> "ALTO_INDICIO" | "MEDIO_INDICIO" | "BAIXO_INDICIO"
      classificacao.categoria    -> "ultraprocessado"
      classificacao.justificativa -> texto descritivo

    App consome:
      nova_grupo    -> int 1–4 (escala NOVA)
      classificacao -> label legível
      justificativa -> texto descritivo
    """
    try:
        classificacao = dados.get("classificacao", {})
        status = classificacao.get("status", "")
        categoria = classificacao.get("categoria", "desconhecido")

        nova_grupo, label = _status_para_nova(status, categoria)
        titulo = classificacao.get("titulo") or label

        return {
            "nova_grupo": classificacao.get("novaGrupo", nova_grupo),
            "classificacao": titulo,
            "titulo": titulo,
            "resumo": classificacao.get("resumo", ""),
            "justificativa": classificacao.get("justificativa", ""),
            "orientacao": classificacao.get("orientacao", ""),
            "evidencias": classificacao.get("evidencias", []),
            "ingredientes_detectados": classificacao.get("ingredientesDetectados", []),
            "aviso": classificacao.get("aviso", ""),
        }
    except Exception:
        return {"erro": "Resposta inesperada do servidor."}


# ──────────────────────────────────────────────────────────────────────────────
# Mapeamento NOVA
# ──────────────────────────────────────────────────────────────────────────────

_MAPA_NOVA = {
    "ALTO_INDICIO":  (4, "Ultraprocessado"),
    "MEDIO_INDICIO": (3, "Alimento processado"),
    "BAIXO_INDICIO": (1, "Baixo processamento"),
}


def _status_para_nova(status: str, categoria: str) -> tuple[int, str]:
    if status in _MAPA_NOVA:
        return _MAPA_NOVA[status]
    # fallback por categoria, caso o status venha diferente do esperado
    if "ultraprocessado" in categoria:
        return 4, "Ultraprocessado"
    if "processado" in categoria:
        return 3, "Alimento processado"
    return 1, "Baixo processamento"


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
