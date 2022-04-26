from dataclasses import dataclass
from typing import Dict

from fides.evaluation.ti_aggregation import TIAggregation
from fides.evaluation.ti_evaluation import TIEvaluation
from simulations.peer import PeerBehavior
from simulations.utils import Click


@dataclass
class SimulationConfiguration:
    being_targets: int
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
