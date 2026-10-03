import importlib.util
import json
from pathlib import Path

import pytest

from app.api.v1.deps import get_analysis_pipeline
from app.main import app
from app.services.analysis_pipeline import AnalysisPipeline
from packages.classification_core.pipeline import classificar


ROOT = Path(__file__).resolve().parents[3]
CASOS = json.loads((Path(__file__).parent / "fixtures/nova_20_rotulos.json").read_text(encoding="utf-8"))["casos"]


class TranscribedOCR:
    """Retorna uma transcrição humana, sem chamar o Google Vision."""

    def __init__(self, text):
        self.text = text

    def extract_text(self, image_bytes):
        return self.text


@pytest.mark.parametrize("caso", CASOS, ids=lambda caso: f"imagem-{caso['imagem']:02d}")
def test_reference_labels_through_rules_api_and_mobile(client, monkeypatch, caso):
    # Cada caso percorre o core, a API real (OCR simulado) e o consumidor mobile.
    result = classificar(caso["texto"])
    assert result["nova_grupo"] == caso["nova_grupo"]
    assert result["status_analise"] == caso["status"]
    pipeline = AnalysisPipeline(TranscribedOCR(caso["texto"]))
    app.dependency_overrides[get_analysis_pipeline] = lambda: pipeline
    response = client.post("/analises", files={"imagem": ("rotulo.jpg", b"stub-image", "image/jpeg")})
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == caso["status"]
    assert payload["classificacao"]["novaGrupo"] == caso["nova_grupo"]

    # Carrega apenas o serviço HTTP do mobile; não exige Kivy nem Android.
    mobile = ROOT / "apps/mobile/Ingresense_app"
    monkeypatch.syspath_prepend(str(mobile))
    spec = importlib.util.spec_from_file_location("mobile_reference_api_service", mobile / "services/api_service.py")
    service = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(service)
    normalized = service._normalizar_resposta(payload)
    assert normalized["nova_grupo"] == caso["nova_grupo"]
    if caso["imagem"] == 10:
        assert normalized["grupo_indeterminado"] is True
        assert normalized["ingredientes_detectados"] == ["creatina monohidratada"]
    elif caso["nova_grupo"] is None:
        assert normalized["nao_classificado"] is True
    else:
        assert "nao_classificado" not in normalized
        assert payload["classificacao"]["evidencias"]
    if caso["imagem"] == 3:
        assert payload["classificacao"]["ingredientesDetectados"] == []
        assert "denominação" in normalized["aviso"]


@pytest.mark.parametrize("texto, grupo", [
    ("Ingredientes: aveia em flocos finos.", 1),
    ("Ingredientes: leite UHT desnatado, enzima lactase, estabilizante citrato de sódio.", 1),
    ("Ingredientes: leite integral e fermento lácteo.", 1),
    ("Ingredientes: aveia em flocos, aroma natural.", 4),
    ("Ingredientes: leite semidesnatado, lactase, citrato de sódio e aromatizante.", 4),
    ("Ingredientes: leite integral, fermento lácteo e emulsificante lecitina.", 4),
    ("Ingredientes: leite integral e açúcar.", 3),
    ("Ingredientes: aveia em flocos, ingrediente desconhecido.", None),
    ("Ingredientes: leite integral, lactase, estabilizante desconhecido.", None),
    ("Ingredientes: leite integral, estabilizante.", None),
    ("Ingredientes: leite integral, citrato de sódio e ingrediente desconhecido.", None),
    ("Ingredientes: leite integral, fermento lácteo e citrato de sódio.", None),
    ("Ingredientes: creatina monohidratada.", None),
    ("Ingredientes: óleo de soja, antioxidante ingrediente desconhecido.", None),
    ("Manteiga. Ingredientes: creme de leite desconhecido e sal.", None),
    ("Ingredientes: creme de leite e cloreto de sódio (sal).", None),
    ("Ingredientes: 100 azeite virgem extra.", None),
    ("Ingredientes: milho verde e salmoura (água, sal e ingrediente desconhecido).", None),
    ("Ingredientes: água, açúcar e caramelo E-150d.", 4),
    ("Ingredientes: açúcar, emulsificante lecitina de soja.", 4),
    ("Ingredientes do macarrão: farinha de trigo, água e sal. Ingredientes do tempero em pó: glutamato monossódico.", 4),
])
def test_controlled_recipes_do_not_hide_markers_or_unknown_components(texto, grupo):
    result = classificar(texto)
    assert result["status_analise"] == "CLASSIFICADO"
    assert result["nova_grupo"] == grupo


@pytest.mark.parametrize("texto", [
    "Açúcar refinado especial",  # Denominação isolada ainda é insuficiente.
    "Biscoito\nAçúcar refinado especial\nPeso Líq. 1kg",
    "Mistura com canela\nAçúcar refinado especial\nPeso Líq. 1kg",
    "Açúcar refinado especial\nPeso Líq. 1kg\nIngredientes: ingrediente desconhecido",
    "Açúcar refinado especial\nPeso Líq. 1kg\nINFORMAÇÃO NUTRICIONAL Porção 30g",
])
def test_front_label_exception_does_not_override_composition_or_nutritional_table(texto):
    assert classificar(texto)["nova_grupo"] is None
