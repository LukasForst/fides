from dataclasses import dataclass
from typing import List, Optional

from fides.evaluation.ti_aggregation import TIAggregation
from fides.evaluation.ti_evaluation import TIEvaluation
from fides.model.aliases import PeerId
from fides.model.configuration import TrustedEntity, TrustModelConfiguration, RecommendationsConfiguration

Click = int
"""Measure of time."""


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


def build_config(setup: FidesSetup) -> TrustModelConfiguration:
    return TrustModelConfiguration(
        privacy_levels=[],
        confidentiality_thresholds=[],
        data_default_level=0,
        initial_reputation=setup.default_reputation,
        service_history_max_size=setup.service_history_max_size,
        recommendations=setup.recommendations_setup if setup.recommendations_setup else RecommendationsConfiguration(
            enabled=False,
            only_connected=False,
            only_preconfigured=False,
            required_trusted_peers_count=0,
            trusted_peer_threshold=0,
            peers_max_count=1000,
            history_max_size=1000
        ),
        alert_trust_from_unknown=1.0,
        trusted_peers=[TrustedEntity(p.peer_id, f"Pre-trusted peer {p.peer_id}", p.trust, p.enforce_trust, 1.0)
                       for p in setup.pretrusted_peers],
        trusted_organisations=[],
        network_opinion_cache_valid_seconds=100000,
        interaction_evaluation_strategy=setup.evaluation_strategy,
        ti_aggregation_strategy=setup.ti_aggregation_strategy
    )
