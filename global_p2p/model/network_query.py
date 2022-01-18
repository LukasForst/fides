from dataclasses import dataclass
from enum import Enum
from typing import List, Union

from global_p2p.model.aliases import IP, Domain, PeerId
from global_p2p.model.recommendation_response import RecommendationResponse
from global_p2p.model.threat_intelligence import ThreatIntelligence
from global_p2p.utils.time import Time


class QueryType(Enum):
    """Identification of the query."""

    THREAT_INTELLIGENCE = "THREAT_INTELLIGENCE"
    """Threat intelligence request - requesting data about some IP/Domain."""

    RECOMMENDATION_REQUEST = "RECOMMENDATION_REQUEST"
    """Recommendation Request - requesting peer k to send recommendation about j."""


@dataclass
class NetworkQueryResponse:
    """Represents response from the peer."""

    responding_peer_id: PeerId
    """Peer ID that sent this response."""

    received_at: Time
    """Time when was the response received."""


@dataclass
class ThreatIntelligenceQueryResponse(NetworkQueryResponse):
    """Network response on QueryType.THREAT_INTELLIGENCE."""
    intelligence: ThreatIntelligence


@dataclass
class RecommendationQueryResponse(NetworkQueryResponse):
    """Network response on QueryType.RECOMMENDATION_REQUEST."""
    recommendation: RecommendationResponse


@dataclass
class NetworkQuery:
    """Represents a single network query - request from Trust Model to the network."""

    query_id: str
    """Unique identification of the query."""

    type: QueryType
    """Type of the query.
     
     Threat Intelligence when requesting data about subject, 
     Recommendation request when getting recommendations from peer.
     """

    dispatched: Time
    """When was this query dispatched."""

    recipients: List[PeerId]
    """What peers should receive the message and should response."""

    expected_response_by: Time
    """Timeout when the query will be finished."""

    subject: Union[IP, Domain, PeerId]
    """Subject of the query.
    
    IP Address or Domain in case of threat intelligence,
    PeerId in case of recommendation request.
    """

    responses: Union[ThreatIntelligenceQueryResponse, RecommendationQueryResponse]
    """Responses received from the network."""
