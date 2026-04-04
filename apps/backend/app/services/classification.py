import logging
from abc import ABC, abstractmethod

from app.models.schemas import ClassificationResult, ClassificationStatus

logger = logging.getLogger(__name__)


class Classifier(ABC):
    @abstractmethod
    def classify(self, ingredients: list[str]) -> ClassificationResult:
        raise NotImplementedError


class MockRuleBasedClassifier(Classifier):
    _UP_KEYWORDS = (
        "aromatizante",
        "corante",
        "edulcorante",
        "realcador de sabor",
        "xarope",
        "maltodextrina",
        "gordura vegetal hidrogenada",
        "estabilizante",
        "emulsificante",
        "acidulante",
        "conservador",
    )

    def classify(self, ingredients: list[str]) -> ClassificationResult:
        logger.debug(f"Iniciando classificação com {len(ingredients)} ingredientes")
        
        hits = self._find_hits(ingredients)
        hit_count = len(hits)
        logger.debug(f"Palavras-chave encontradas: {hit_count} hits - {hits}")

        if hit_count >= 2:
            status = ClassificationStatus.ALTO_INDICIO
            justification = (
                "Foram identificados ingredientes associados a ultraprocessamento, "
                f"como {', '.join(hits[:3])}."
            )
            logger.info(f"Classificação: ALTO_INDICIO ({hit_count} palavras-chave)")
        elif hit_count == 1:
            status = ClassificationStatus.MEDIO_INDICIO
            justification = (
                "Foi identificado ingrediente associado a ultraprocessamento, "
                f"como {hits[0]}."
            )
            logger.info(f"Classificação: MEDIO_INDICIO ({hit_count} palavra-chave)")
        else:
            status = ClassificationStatus.BAIXO_INDICIO
            justification = (
                "Nao foram identificados ingredientes tipicos de ultraprocessamento "
                "na lista analisada."
            )
            logger.info("Classificação: BAIXO_INDICIO (nenhuma palavra-chave)")

        return ClassificationResult(
            categoria="ultraprocessado",
            status=status,
            justificativa=justification,
        )

    def _find_hits(self, ingredients: list[str]) -> list[str]:
        hits: list[str] = []
        for ingredient in ingredients:
            for keyword in self._UP_KEYWORDS:
                if keyword in ingredient and keyword not in hits:
                    hits.append(keyword)
        return hits
