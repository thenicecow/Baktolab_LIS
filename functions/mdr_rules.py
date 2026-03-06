# mdr = multi-drug resistance

from typing import List, Tuple

Hint = Tuple[str, str]
def classify_rate(rate_pct: float) -> str:
    if rate_pct < 5:
        return "🟢 niedrig (<5%)"
    if rate_pct <= 10:
        return "🟠 mittel (5–10%)"
    return "🔴 hoch (>10%)"


def antibiotic_class(antibiotic: str) -> str:
    if antibiotic in ["Meropenem", "Imipenem"]:
        return "Carbapenem"
    if antibiotic in ["Ceftriaxon", "Cefepim"]:
        return "Cephalosporin"
    if antibiotic in ["Penicillin"]:
        return "Penicillin"
    return "Other"


def is_enterobacterales(organism: str) -> bool:
    return organism in ["E. coli", "Klebsiella pneumoniae"]


def get_mdr_hints(organism: str, ab_class: str, resistant_n: int) -> List[Hint]:
 
    hints: List[Hint] = []

    if resistant_n <= 0:
        return hints

    if is_enterobacterales(organism) and ab_class == "Carbapenem":
        hints.append((
            "warning",
            "Carbapenem-Resistenz bei Enterobacterales ist besonders relevant.  "
            "Bestätigung/Abklärung und Hygienemassnahmen gemäss Spitalhygiene-Richtlinien prüfen."
        ))

    if is_enterobacterales(organism) and ab_class == "Cephalosporin":
        hints.append((
            "info",
            "Cephalosporin-Resistenz bei Enterobacterales kann auf ESBL/AmpC hindeuten. "
            "Interpretation gemäss Spitalhygiene-Richtlinien."
        ))

    if organism == "S. aureus" and ab_class == "Penicillin":
        hints.append((
            "warning",
            "Penicillin-Resistenz bei S. aureus ist häufig. "
            "MRSA wird jedoch über Oxacillin/Cefoxitin beurteilt (nicht über Penicillin)."
        ))

    if organism == "Pseudomonas aeruginosa" and ab_class == "Carbapenem":
        hints.append((
            "warning",
            "Carbapenem-Resistenz bei Pseudomonas aeruginosa kann klinisch relevant sein (z. B. CRPA). "
            "Abklärung und Therapie gemäss Spitalhygiene prüfen."
        ))

    return hints