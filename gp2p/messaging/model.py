from dataclasses import dataclass
from typing import Any

from gp2p.model.aliases import PeerId, Target
from gp2p.model.peer import PeerInfo
from gp2p.model.recommendation import Recommendation
from gp2p.model.threat_intelligence import ThreatIntelligence

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
    peer: PeerId
    recommendation: Recommendation


@dataclass
class PeerIntelligenceResponse:
    sender: PeerInfo
    intelligence: ThreatIntelligence
    target: Target
