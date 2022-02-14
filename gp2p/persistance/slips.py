from typing import Optional

from gp2p.model.aliases import Target
from gp2p.model.threat_intelligence import ThreatIntelligence


class ThreatIntelligenceDatabase:
    """Database that stores threat intelligence data."""

    def get_for(self, target: Target) -> Optional[ThreatIntelligence]:
        """Returns threat intelligence for given target or None if there are no data."""
        # TODO: implement this
        raise NotImplemented()
