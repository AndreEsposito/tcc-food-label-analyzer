from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

from packages.classification_core.preprocess import preprocessar
from packages.classification_core.features import extrair_features

DATASET_PATH = Path(__file__).resolve().parent / "datasets" / "train.csv"
MODEL_PATH = Path(__file__).resolve().parent / "models" / "random_forest.pkl"

df = pd.read_csv(DATASET_PATH)

X = []
y = []

for _, row in df.iterrows():
    texto = row["ingredientes"]
    classe = row["classe"]

    texto_processado = preprocessar(texto)
    features = extrair_features(texto_processado)

    X.append(list(features.values()))
    y.append(classe)

modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X, y)

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(modelo, MODEL_PATH)

print("Modelo treinado e salvo com sucesso!")
print(f"Modelo salvo em: {MODEL_PATH}")