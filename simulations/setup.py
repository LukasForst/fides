from dataclasses import dataclass
from typing import Dict, Optional, Callable

from fides.evaluation.ti_aggregation import TIAggregation
from fides.evaluation.ti_evaluation import TIEvaluation
from fides.model.configuration import RecommendationsConfiguration
from simulations.peer import PeerBehavior, Peer
from simulations.utils import Click


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
