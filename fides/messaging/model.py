from dataclasses import dataclass
from typing import Any

from fides.model.aliases import PeerId, Target
from fides.model.peer import PeerInfo
from fides.model.recommendation import Recommendation
from fides.model.threat_intelligence import ThreatIntelligence

"""
Model data coming from the Redis queue - 
communication layer between network and trust layer.
"""


@dataclass
class NetworkMessage:
    type: str
    version: int
    data: Any


@dataclass
class PeerRecommendationResponse:
    sender: PeerInfo
    subject: PeerId
    recommendation: Recommendation


@dataclass
class PeerIntelligenceResponse:
    sender: PeerInfo
    intelligence: ThreatIntelligence
    target: Target
