from app.services.classification import MockRuleBasedClassifier


def test_mock_classifier_returns_alto_indicio_with_multiple_hits():
    classifier = MockRuleBasedClassifier()
    result = classifier.classify(
        [
            "acucar",
            "aromatizante artificial",
            "corante caramelo iv",
            "farinha de trigo",
        ]
    )

    assert result.categoria == "ultraprocessado"
    assert result.status.value == "ALTO_INDICIO"
    assert "aromatizante" in result.justificativa


def test_mock_classifier_returns_baixo_indicio_without_hits():
    classifier = MockRuleBasedClassifier()
    result = classifier.classify(["agua", "sal", "farinha de trigo"])

    assert result.status.value == "BAIXO_INDICIO"
