from dataclasses import dataclass

from global_p2p.model.aliases import PeerId
from global_p2p.model.recommendation_history import RecommendationHistory
from global_p2p.model.service_history import ServiceHistory


@dataclass
class TrustData:
    """Trust data related to given peer - in model's notation "peer_id" is actually "j"."""

    peer_id: PeerId
    """ID of the peer these data are for."""

    service_trust: float
    """Service Trust Metric.
    
    Semantic meaning is basically "trust" - how much does current peer trust peer "j" about quality of service.
    In model's notation st_ij.
    
    0 <= service_trust <= 1
    """

    reputation: float
    """Reputation Metric.
    
    The reputation metric measures a stranger’s trustworthiness based on recommendations.
    In model's notation r_ij.
    
    0 <= reputation <= 1
    """

    recommendation_trust: float
    """Recommendation Trust Metric.
    
    How much does the peer trust that reputation is correct.
    In model's notation rt_ij.
    
    0 <= recommendation_trust <= 1
    """

    initial_reputation_provided_by_count: int
    """How many peers provided recommendation during initial calculation of reputation.
    
    In model's notation η_ij.
    """

    service_history: ServiceHistory
    """History of interactions, in model's notation SH_ij."""

    @property
    def service_history_size(self):
        """Size of the history, in model's notation sh_ij."""
        return len(self.service_history)

    recommendation_history: RecommendationHistory
    """History of recommendation, in model's notation RH_ij."""

    @property
    def recommendation_history_size(self):
        """Size of the recommendation history, in model's notation rh_ij."""
        return len(self.recommendation_history)
