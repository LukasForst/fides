from dataclasses import dataclass

from fides.model.aliases import Target


@dataclass
class Alert:
    """Alert that was broadcast on the network."""

    target: Target
    """Target that """

    score: float
    """Score of the alert. See ThreatIntelligence.score."""

    confidence: float
    """Confidence of the alert. See ThreatIntelligence.confidence."""
