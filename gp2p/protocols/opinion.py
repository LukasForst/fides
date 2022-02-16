from typing import Dict

from gp2p.messaging.model import PeerIntelligenceResponse
from gp2p.model.alert import Alert
from gp2p.model.aliases import PeerId, Target
from gp2p.model.peer_trust_data import PeerTrustData, TrustMatrix
from gp2p.model.threat_intelligence import SlipsThreatIntelligence
from gp2p.model.trust_model_configuration import TrustModelConfiguration


class OpinionAggregator:
    """
    Class responsible for evaluation of the intelligence received from the network.
    """

    def __init__(self, configuration: TrustModelConfiguration):
        self.__configuration = configuration

    def evaluate_alert(self, peer_trust: PeerTrustData, alert: Alert) -> SlipsThreatIntelligence:
        """Evaluates given data about alert and produces aggregated intelligence for Slips."""
        # TODO: implement correct aggregation

        alert_trust = self.__configuration.alert_trust_from_unknown
        alert_trust = max(alert_trust, peer_trust.service_trust)

        score = alert.score
        confidence = alert.confidence * alert_trust
        return SlipsThreatIntelligence(score=score, confidence=confidence, target=alert.target)

    def evaluate_intelligence_response(self,
                                       target: Target,
                                       data: Dict[PeerId, PeerIntelligenceResponse],
                                       trust_matrix: TrustMatrix) -> SlipsThreatIntelligence:
        """Evaluates given threat intelligence report from the network."""
        for peer, response in data.items():
            trust = trust_matrix[peer]
            pass

        # TODO: implement correct aggregation
        return SlipsThreatIntelligence(0, 0, target=target)
