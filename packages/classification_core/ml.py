from pathlib import Path
from functools import lru_cache
import pickle


MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "apps"
    / "ml-lab"
    / "models"
    / "random_forest.pkl"
)


@lru_cache(maxsize=1)
def carregar_modelo():
    with open(MODEL_PATH, "rb") as f:
        modelo = pickle.load(f)
    return modelo


def classificar_ml(features: dict) -> dict:
    try:
        modelo = carregar_modelo()
        entrada = [list(features.values())]
        previsao = modelo.predict(entrada)[0]
        return {"classificacao": previsao, "disponivel": True}
    except Exception as exc:
        # O modelo é apenas comparativo; sua indisponibilidade não pode alterar
        # nem impedir a decisão oficial produzida pelas regras heurísticas.
        return {
            "classificacao": None,
            "disponivel": False,
            "erro": str(exc),
        }
