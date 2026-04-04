from app.services.text_preprocessing import TextPreprocessor


def test_extract_ingredients_from_common_ocr_text():
    text = """
    INFORMACOES GERAIS
    INGREDIENTES: Acucar, farinha de trigo, Gordura vegetal hidrogenada,
    Aromatizante e Corante. ALERGICOS: contem gluten.
    """
    preprocessor = TextPreprocessor()

    ingredients = preprocessor.extract_ingredients(text)

    assert "acucar" in ingredients
    assert "farinha de trigo" in ingredients
    assert "gordura vegetal hidrogenada" in ingredients
    assert "aromatizante" in ingredients
    assert "corante" in ingredients
    assert all("alergicos" not in item for item in ingredients)


def test_extract_ingredients_handles_empty_text():
    preprocessor = TextPreprocessor()
    assert preprocessor.extract_ingredients("   ") == []
