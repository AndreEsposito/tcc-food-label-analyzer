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
    # 🔹 Pouco processado (controle)
    "Banana, aveia",
    "Arroz, feijao, sal",
    "Frango, sal, alho",
    "Leite, fermento lacteo",
    "Batata, sal",

    # 🔹 Processado (intermediário)
    "Molho de tomate: tomate, sal, conservante, acidulante",
    "Milho em conserva: milho, agua, sal, conservante",
    "Ervilha em conserva: ervilha, agua, sal, conservante",
    "Requeijao: leite, sal, emulsificante",
    "Molho barbecue: tomate, acucar, acidulante, conservante",

    # 🔹 Ultraprocessado (clássico)
    "Refrigerante: agua, acucar, corante, aromatizante",
    "Salgadinho: milho, oleo, sal, glutamato monossodico, aromatizante",
    "Suco em po: acucar, corante, aromatizante, acidulante",
    "Tempero pronto: sal, glutamato monossodico, corante",
    "Caldo em cubo: sal, gordura vegetal hidrogenada, corante",

    # 🔥 Casos DIFÍCEIS (importante)
    "Iogurte sabor morango: leite, aromatizante, corante",
    "Bebida lactea: leite, acucar, estabilizante",
    "Cereal matinal: milho, acucar, aromatizante",
    "Biscoito simples: farinha, acucar, emulsificante",
    "Chocolate ao leite: acucar, leite, emulsificante",
    "Molho pronto industrial: tomate, acucar, aromatizante",
    "Pao industrial: farinha, acucar, emulsificante, conservante",
    "Hamburguer industrial: carne, gordura vegetal, conservante",
    "Sorvete industrial: leite, acucar, estabilizante, aromatizante",
    "Achocolatado em po: acucar, cacau, aromatizante"
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