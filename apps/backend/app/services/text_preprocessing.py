import logging
import re
import unicodedata

logger = logging.getLogger(__name__)


class TextPreprocessor:
    _INGREDIENTS_MARKERS = ("ingredientes", "ingrediente")
    _SECTION_STOP_MARKERS = (
        "alergicos",
        "alergênicos",
        "informacao nutricional",
        "informação nutricional",
        "nao contem gluten",
        "não contém glúten",
    )

    def extract_ingredients(self, raw_text: str) -> list[str]:
        logger.debug(f"Iniciando pré-processamento do texto extraído (tamanho: {len(raw_text)} chars)")
        
        if not raw_text or not raw_text.strip():
            logger.warning("Texto vazio recebido")
            return []

        cleaned = self._clean_text(raw_text)
        logger.debug(f"Texto limpo: {len(cleaned)} caracteres")
        logger.debug(f"Texto após limpeza: {cleaned[:200]}...")
        
        section = self._extract_ingredients_section(cleaned)
        if not section:
            logger.warning("Nenhuma seção de ingredientes encontrada")
            return []
        
        logger.debug(f"Seção de ingredientes extraída: {section[:300]}...")
        ingredients = self._split_ingredients(section)
        logger.info(f"Extração concluída: {len(ingredients)} ingredientes")
        logger.debug(f"Ingredientes processados: {ingredients}")
        return ingredients

    def _clean_text(self, text: str) -> str:
        text = text.replace("\n", " ").replace("\r", " ")
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[|_]+", " ", text)
        return text.strip()

    def _extract_ingredients_section(self, text: str) -> str:
        lowered = self._normalize(text)
        marker_positions = [
            lowered.find(marker) for marker in self._INGREDIENTS_MARKERS if marker in lowered
        ]
        if not marker_positions:
            return text

        start = min(marker_positions)
        candidate = text[start:]
        candidate_normalized = self._normalize(candidate)

        colon_index = candidate.find(":")
        if colon_index >= 0:
            candidate = candidate[colon_index + 1 :]
            candidate_normalized = self._normalize(candidate)

        stop_indexes = []
        for marker in self._SECTION_STOP_MARKERS:
            idx = candidate_normalized.find(marker)
            if idx > 0:
                stop_indexes.append(idx)
        if stop_indexes:
            candidate = candidate[: min(stop_indexes)]
        return candidate.strip(" .;-")

    def _split_ingredients(self, text: str) -> list[str]:
        normalized = self._normalize(text)
        normalized = re.sub(r"\bcont[eé]m\b", ",", normalized)
        normalized = re.sub(r"\be\b", ",", normalized)
        normalized = re.sub(r"[.;]", ",", normalized)
        normalized = re.sub(r"[()\[\]{}]", " ", normalized)
        normalized = re.sub(r"[^a-z0-9, %\-]+", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized)
        candidates = [item.strip(" -") for item in normalized.split(",")]
        tokens = [item for item in candidates if item and len(item) > 1]

        deduped: list[str] = []
        seen = set()
        for token in tokens:
            if token not in seen:
                seen.add(token)
                deduped.append(token)
        return deduped

    def _normalize(self, text: str) -> str:
        text = text.lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(char for char in text if not unicodedata.combining(char))
        return text
