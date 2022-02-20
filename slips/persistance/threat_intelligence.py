from typing import Optional

from fides.model.aliases import Target
from fides.model.threat_intelligence import SlipsThreatIntelligence
from fides.persistance.threat_intelligence import ThreatIntelligenceDatabase


class SlipsThreatIntelligenceDatabase(ThreatIntelligenceDatabase):
    """Implementation of ThreatIntelligenceDatabase that uses Slips native storage for the TI."""

    def __init__(self, r):
        self.__r = r

    def get_for(self, target: Target) -> Optional[SlipsThreatIntelligence]:
        """Returns threat intelligence for given target or None if there are no data."""
        # TODO: [S] implement this
        raise NotImplemented()
