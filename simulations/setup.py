from fides.model.configuration import TrustModelConfiguration, RecommendationsConfiguration, TrustedEntity
from simulations.model import FidesSetup


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
