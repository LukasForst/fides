from typing import Dict

from fides.evaluation.dovecot import Dovecot, PeerReport
from fides.messaging.model import PeerIntelligenceResponse
from fides.model.alert import Alert
from fides.model.aliases import PeerId, Target
from fides.model.configuration import TrustModelConfiguration
from fides.model.peer_trust_data import PeerTrustData, TrustMatrix
from fides.model.threat_intelligence import SlipsThreatIntelligence
from fides.persistance.threat_intelligence import ThreatIntelligenceDatabase


class OpinionAggregator:
    """
    Class responsible for evaluation of the intelligence received from the network.
    """

    # TODO: [!] check if we really need to get the reporter_ti or not

    def __init__(self,
                 configuration: TrustModelConfiguration,
                 ti_db: ThreatIntelligenceDatabase,
                 dovecot: Dovecot):
        self.__configuration = configuration
        self.__ti_db = ti_db
        self.__dovecot = dovecot

    def evaluate_alert(self, peer_trust: PeerTrustData, alert: Alert) -> SlipsThreatIntelligence:
        """Evaluates given data about alert and produces aggregated intelligence for Slips."""

        alert_trust = max(self.__configuration.alert_trust_from_unknown, peer_trust.service_trust)
        score = alert.score
        confidence = alert.confidence * alert_trust
        return SlipsThreatIntelligence(score=score, confidence=confidence, target=alert.target)

    def evaluate_intelligence_response(self,
                                       target: Target,
                                       data: Dict[PeerId, PeerIntelligenceResponse],
                                       trust_matrix: TrustMatrix) -> SlipsThreatIntelligence:
        """Evaluates given threat intelligence report from the network."""
        reports = [PeerReport(report_ti=ti.intelligence,
                              reporter_trust=trust_matrix[peer_id],
                              reporter_ti=self.__ti_db.get_for(ti.sender.ip) if ti.sender.ip else None
                              ) for peer_id, ti in data.items()]
        # use Dovecot to aggregate opinion from the reports
        ti = self.__dovecot.assemble_peer_opinion(reports)
        return SlipsThreatIntelligence(score=ti.score, confidence=ti.confidence, target=target)
