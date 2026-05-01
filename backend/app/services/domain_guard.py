"""
Guardrails de dominio para el chat de CoolAgent.

Esta capa evita llamadas innecesarias al modelo cuando la consulta es claramente
fuera de refrigeracion general o climatizacion aplicada.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


PROMPT_POLICY_VERSION = "refrigeration-general-v1"

OUT_OF_DOMAIN_RESPONSE = (
    "Solo puedo ayudarte con consultas tecnicas de refrigeracion, "
    "climatizacion aplicada y temas directamente relacionados. "
    "Si tienes una duda sobre neveras, aires acondicionados, camaras "
    "frigorificas, refrigerantes, diagnostico, mantenimiento, electricidad "
    "aplicada o seguridad tecnica, reformulala y con gusto te ayudo."
)

REFRIGERATION_TERMS = {
    "aire acondicionado",
    "aires acondicionados",
    "a/c",
    "ac ",
    "baja presion",
    "bomba de calor",
    "camara frigorifica",
    "camaras frigorificas",
    "carga de refrigerante",
    "chiller",
    "climatizacion",
    "compresor",
    "condensador",
    "congelador",
    "evaporador",
    "filtro secador",
    "fuga",
    "fugas",
    "gas refrigerante",
    "hvac",
    "hvac/r",
    "manifold",
    "nevera",
    "neveras",
    "presion de succion",
    "presion",
    "refrigeracion",
    "refrigerador",
    "refrigerante",
    "r-134a",
    "r-22",
    "r-290",
    "r-32",
    "r-404a",
    "r-407c",
    "r-410a",
    "split",
    "subenfriamiento",
    "superheat",
    "sobrecalentamiento",
    "termostato",
    "valvula de expansion",
    "vitrina",
}

AUXILIARY_TECHNICAL_TERMS = {
    "amperaje",
    "capacitor",
    "continuidad",
    "corriente",
    "diagnostico",
    "epp",
    "herramienta",
    "herramientas",
    "mantenimiento",
    "medicion",
    "medir",
    "multimetro",
    "norma",
    "normativa",
    "ohm",
    "sensor",
    "seguridad",
    "tarjeta",
    "tecnico",
    "voltaje",
}

EQUIPMENT_BRANDS_AND_CODES = {
    "bitzer",
    "carrier",
    "copeland",
    "daikin",
    "danfoss",
    "lg",
    "mitsubishi",
    "samsung",
    "tecumseh",
    "trane",
}

OUT_OF_DOMAIN_TERMS = {
    "abogado",
    "acciones",
    "app",
    "bitcoin",
    "cripto",
    "crypto",
    "dieta",
    "divorcio",
    "dolor",
    "elecciones",
    "finanzas",
    "legal",
    "medicina",
    "medico",
    "politica",
    "programacion",
    "react",
    "software",
    "trading",
    "salud",
}

PROMPT_INJECTION_PATTERNS = (
    r"ignora (tus|las|mis) instrucciones",
    r"olvida (tus|las) instrucciones",
    r"aunque no sea refrigeraci[oó]n",
    r"contesta igual",
    r"act[uú]a como (m[eé]dico|abogado|programador)",
)


@dataclass(frozen=True)
class DomainGuardResult:
    is_allowed: bool
    reason: str
    response: str | None = None
    policy_version: str = PROMPT_POLICY_VERSION


class DomainGuard:
    """Clasificador deterministico para bloquear consultas claramente externas."""

    def evaluate(self, text: str) -> DomainGuardResult:
        normalized = self._normalize(text)

        if not normalized:
            return DomainGuardResult(is_allowed=True, reason="empty_or_whitespace")

        has_refrigeration = self._contains_any(normalized, REFRIGERATION_TERMS)
        has_auxiliary = self._contains_any(normalized, AUXILIARY_TECHNICAL_TERMS)
        has_brand_or_code = self._contains_any(normalized, EQUIPMENT_BRANDS_AND_CODES)
        has_out_of_domain = self._contains_any(normalized, OUT_OF_DOMAIN_TERMS)
        has_prompt_injection = any(
            re.search(pattern, normalized) for pattern in PROMPT_INJECTION_PATTERNS
        )

        if has_prompt_injection:
            return self._blocked("prompt_injection_out_of_domain")

        if has_refrigeration or has_brand_or_code:
            return DomainGuardResult(is_allowed=True, reason="refrigeration_domain")

        if has_auxiliary and not has_out_of_domain:
            return DomainGuardResult(is_allowed=True, reason="technical_auxiliary")

        if has_out_of_domain:
            return self._blocked("clear_out_of_domain")

        # Si no es claramente externo, dejamos pasar para evitar falsos bloqueos.
        return DomainGuardResult(is_allowed=True, reason="ambiguous_allow")

    def _blocked(self, reason: str) -> DomainGuardResult:
        return DomainGuardResult(
            is_allowed=False,
            reason=reason,
            response=OUT_OF_DOMAIN_RESPONSE,
        )

    def _normalize(self, text: str) -> str:
        lowered = text.lower().strip()
        without_accents = "".join(
            char
            for char in unicodedata.normalize("NFD", lowered)
            if unicodedata.category(char) != "Mn"
        )
        return " ".join(without_accents.split())

    def _contains_any(self, text: str, terms: set[str]) -> bool:
        padded = f" {text} "
        return any(term in padded for term in terms)
