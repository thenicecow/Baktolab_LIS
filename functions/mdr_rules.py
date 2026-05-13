"""Fachliche Regeln und Auswahlwerte fuer das Resistenzmonitoring."""

from __future__ import annotations


Hinweis = tuple[str, str]

UNTERSTUETZTE_KEIME: tuple[str, ...] = (
    "E. coli",
    "S. aureus",
    "Klebsiella pneumoniae",
    "Pseudomonas aeruginosa",
)

_ANTIBIOTIKA_KLASSEN: dict[str, str] = {
    "Meropenem": "Carbapenem",
    "Imipenem": "Carbapenem",
    "Ceftriaxon": "Cephalosporin",
    "Cefepim": "Cephalosporin",
    "Penicillin": "Penicillin",
    "Ciprofloxacin": "Fluorchinolon",
    "Gentamicin": "Aminoglykosid",
}

UNTERSTUETZTE_ANTIBIOTIKA: tuple[str, ...] = tuple(_ANTIBIOTIKA_KLASSEN.keys())

__all__ = (
    "UNTERSTUETZTE_KEIME",
    "UNTERSTUETZTE_ANTIBIOTIKA",
    "classify_rate",
    "antibiotic_class",
    "is_enterobacterales",
    "get_mdr_hints",
)

_ENTEROBACTERALES: frozenset[str] = frozenset({"E. coli", "Klebsiella pneumoniae"})


def classify_rate(rate_pct: float) -> str:
    """Ordnet eine Resistenzrate einer einfachen Fachkategorie zu."""
    if rate_pct < 5:
        return "niedrig (<5 %)"
    if rate_pct <= 10:
        return "mittel (5-10 %)"
    return "hoch (>10 %)"


def antibiotic_class(antibiotic: str) -> str:
    """Liefert die Wirkstoffklasse fuer ein unterstuetztes Antibiotikum."""
    return _ANTIBIOTIKA_KLASSEN.get(antibiotic, "Andere")


def is_enterobacterales(organism: str) -> bool:
    """Prueft, ob ein Keim zur hier beruecksichtigten Gruppe der Enterobacterales gehoert."""
    return organism in _ENTEROBACTERALES


def get_mdr_hints(organism: str, ab_class: str, resistant_n: int) -> list[Hinweis]:
    """Erzeugt einfache fachliche Hinweise fuer relevante Resistenzkonstellationen."""
    hints: list[Hinweis] = []

    if resistant_n <= 0:
        return hints

    if is_enterobacterales(organism) and ab_class == "Carbapenem":
        hints.append(
            (
                "warning",
                "Carbapenem-Resistenz bei Enterobacterales ist besonders relevant. "
                "Bestaetigung, Abklaerung und Hygienemassnahmen gemaess Spitalhygiene-Richtlinien pruefen.",
            )
        )

    if is_enterobacterales(organism) and ab_class == "Cephalosporin":
        hints.append(
            (
                "info",
                "Cephalosporin-Resistenz bei Enterobacterales kann auf ESBL oder AmpC hindeuten. "
                "Interpretation gemaess Spitalhygiene-Richtlinien einordnen.",
            )
        )

    if organism == "S. aureus" and ab_class == "Penicillin":
        hints.append(
            (
                "warning",
                "Penicillin-Resistenz bei S. aureus ist haeufig. "
                "MRSA wird jedoch ueber Oxacillin oder Cefoxitin beurteilt, nicht ueber Penicillin.",
            )
        )

    if organism == "Pseudomonas aeruginosa" and ab_class == "Carbapenem":
        hints.append(
            (
                "warning",
                "Carbapenem-Resistenz bei Pseudomonas aeruginosa kann klinisch relevant sein. "
                "Abklaerung und Therapie nach lokalen Richtlinien pruefen.",
            )
        )

    return hints

