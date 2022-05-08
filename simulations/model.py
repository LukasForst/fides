from dataclasses import dataclass
from typing import Dict, Callable
from typing import List, Optional

from fides.evaluation.ti_aggregation import TIAggregation
from fides.evaluation.ti_evaluation import TIEvaluation
from fides.model.aliases import PeerId, Target, Score
from fides.model.configuration import RecommendationsConfiguration
from fides.model.threat_intelligence import SlipsThreatIntelligence
from simulations.peer import PeerBehavior, Peer
from simulations.utils import Click


@dataclass
class PreTrustedPeer:
    peer_id: PeerId
    trust: float
    enforce_trust: bool = True


@dataclass
class FidesSetup:
    default_reputation: float
    pretrusted_peers: List[PreTrustedPeer]
    evaluation_strategy: TIEvaluation
    ti_aggregation_strategy: TIAggregation

    recommendations_setup: Optional[RecommendationsConfiguration] = None
    service_history_max_size: int = 100


@dataclass
class NewPeersJoiningLater:
    number_of_peers_joining_late: int
    start_joining: Click
    stop_joining: Click
    peers_selector: Callable[[Peer], bool]


@dataclass
class SimulationConfiguration:
    benign_targets: int
    malicious_targets: int
    peers_distribution: Dict[PeerBehavior, int]
    malicious_peers_lie_about_targets: float  # percentage
    simulation_length: Click
    malicious_peers_lie_since: Click
    service_history_size: Click
    pre_trusted_peers_count: int
    initial_reputation: float
    evaluation_strategy: TIEvaluation
    ti_aggregation_strategy: TIAggregation
    local_slips_acts_as: PeerBehavior
    new_peers_join_between: Optional[NewPeersJoiningLater] = None
    recommendation_setup: Optional[RecommendationsConfiguration] = None


@dataclass
class SimulationResult:
    simulation_id: str
    simulation_config: SimulationConfiguration
    peer_trust_history: Dict[Click, Dict[PeerId, float]]
    targets_history: Dict[Click, Dict[Target, SlipsThreatIntelligence]]
    targets_labels: Dict[Target, Score]
    peers_labels: Dict[PeerId, PeerBehavior]
