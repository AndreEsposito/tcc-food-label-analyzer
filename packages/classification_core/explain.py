def gerar_explicacao(classificacao: str, ingredientes_detectados: list) -> str:
    if not ingredientes_detectados:
        return "Não foram identificados ingredientes críticos na lista analisada."

    ingredientes = ", ".join(ingredientes_detectados)

    if classificacao == "ultraprocessado":
        return f"O produto foi classificado como ultraprocessado devido à presença de: {ingredientes}."

    if classificacao == "processado":
        return f"O produto foi classificado como processado devido à presença de: {ingredientes}."

    return "O produto apresenta baixo nível de processamento."