from typing import Optional

from fides.model.aliases import Target, ConfidentialityLevel
from fides.model.threat_intelligence import ThreatIntelligence


class ThreatIntelligenceDatabase:
    """Database that stores threat intelligence data."""

    def get_for(self, target: Target) -> Optional[ThreatIntelligence, ConfidentialityLevel]:
        """Returns threat intelligence for given target or None if there are no data."""
        # TODO: implement this
        raise NotImplemented()
