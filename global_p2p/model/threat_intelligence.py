from dataclasses import dataclass


@dataclass
class ThreatIntelligence:
    """Representation of peer's opinion on a subject (IP address or domain)."""

    score: float
    """How much is subject malicious or being.
    
    -1 <= score <= 1
    """

    confidence: float
    """How much does peer trust, that score is correct.
    
    0 <= confidence <= 1
    """
