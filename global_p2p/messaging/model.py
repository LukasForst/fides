from dataclasses import dataclass
from typing import List, Any

from global_p2p.model.aliases import PeerId, Target
from global_p2p.model.recommendation_response import Recommendation
from global_p2p.model.threat_intelligence import ThreatIntelligence

"""
Model data coming from the Redis queue - 
communication layer between network and trust layer.
"""


@dataclass
class PeerInfo:
    id: PeerId
    organisations: List[str]


@dataclass
class Alert:
    target: Target
    score: float
    confidence: float


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
