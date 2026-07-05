from typing import Dict, Set
from shared.schemas import NLPFeatures
from .clinical_domains import CONDITION_TO_DOMAIN
from .domain_weights import DOMAIN_RISK_WEIGHTS


def interpret_clinical_domains(nlp: NLPFeatures) -> Dict:
    """
    Converts normalized conditions into domain-level clinical signal.
    """

    domains: Set[str] = set()
    severity_boost = 0.0

    # ----------------------------------
    # 1. Map conditions → domains
    # ----------------------------------
    for cond in nlp.conditions:
        key = cond.lower()
        domain = CONDITION_TO_DOMAIN.get(key)

        if not domain:
            continue

        domains.add(domain)

        # Base weight per domain
        severity_boost += DOMAIN_RISK_WEIGHTS.get(domain, 0.0)

    # ----------------------------------
    # 2. Domain-level amplification
    # ----------------------------------
    DOMAIN_BOOSTS = {
        "cardiac": 0.25,
        "respiratory": 0.20,
        "metabolic": 0.20,
        "mental": 0.15,
        "digestive": 0.15,
    }

    for domain in domains:
        severity_boost += DOMAIN_BOOSTS.get(domain, 0.0)

    # ----------------------------------
    # 3. Family history sensitivity
    # ----------------------------------
    if nlp.family_history:
        severity_boost += 0.10

    # ----------------------------------
    # 4. Age sensitivity
    # ----------------------------------
    if nlp.age >= 60:
        severity_boost += 0.15

    # ----------------------------------
    # 5. Clamp (safety)
    # ----------------------------------
    severity_boost = min(severity_boost, 0.6)

    return {
        "domains": domains,
        "severity_boost": severity_boost,
    }

