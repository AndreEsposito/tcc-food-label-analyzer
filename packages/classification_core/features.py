ULTRAPROCESSADOS = [
    "corante",
    "caramelo iv",
    "ins 150d",
    "aromatizante",
    "aroma artificial",
    "aroma identico ao natural",
    "glutamato monossodico",
    "realcador de sabor",
    "maltodextrina",
    "xarope de glicose",
    "xarope de milho",
    "edulcorante",
    "aspartame",
    "sucralose",
    "acesulfame de potassio",
    "ciclamato",
    "sacarina",
    "gordura vegetal hidrogenada",
    "extrato de levedura"
]

PROCESSADOS = [
    "conservante",
    "benzoato de sodio",
    "sorbato de potassio",
    "emulsificante",
    "estabilizante",
    "espessante",
    "acidulante",
    "antiumectante",
    "antioxidante"
]


def extrair_features(texto: str) -> dict:
    features = {}

    for ingrediente in ULTRAPROCESSADOS:
        features[ingrediente] = int(ingrediente in texto)

    for ingrediente in PROCESSADOS:
        features[ingrediente] = int(ingrediente in texto)

    return features