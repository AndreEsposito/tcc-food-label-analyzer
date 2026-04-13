from pathlib import Path
import sys
import pickle

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

from packages.classification_core.pipeline import classificar
from packages.classification_core.preprocess import preprocessar
from packages.classification_core.features import extrair_features

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "random_forest.pkl"

with open(MODEL_PATH, "rb") as f:
    modelo = pickle.load(f)

exemplos = [
    "Tomate, sal",
    "Molho de tomate: tomate, sal, conservante",
    "Leite fermentado: leite, estabilizante",
    "Refrigerante: agua, acucar, corante, aromatizante",
    "Salgadinho: milho, oleo, sal, glutamato monossodico, aromatizante",
    "Doce diet: agua, edulcorante, sucralose, conservante",
    "Biscoito recheado: farinha, acucar, aromatizante, emulsificante"
]

for texto in exemplos:
    resultado_regras = classificar(texto)
    classe_regras = resultado_regras["classificacao"]

    texto_processado = preprocessar(texto)
    features = extrair_features(texto_processado)
    entrada = [list(features.values())]
    classe_ia = modelo.predict(entrada)[0]

    print("\n" + "=" * 60)
    print("Texto:", texto)
    print("Regras:", classe_regras)
    print("IA:", classe_ia)

    if classe_regras == classe_ia:
        print("Resultado: CONCORDAM")
    else:
        print("Resultado: DIVERGÊNCIA")