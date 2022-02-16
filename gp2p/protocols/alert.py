from typing import Callable

from gp2p.evaluation.service.interaction import Satisfaction, Weight
from gp2p.messaging.network_bridge import NetworkBridge
from gp2p.model.alert import Alert
from gp2p.model.aliases import Target
from gp2p.model.peer import PeerInfo
from gp2p.model.threat_intelligence import ThreatIntelligence, SlipsThreatIntelligence
from gp2p.model.trust_model_configuration import TrustModelConfiguration
from gp2p.persistance.trust import TrustDatabase
from gp2p.protocols.opinion import OpinionAggregator
from gp2p.protocols.protocol import Protocol
from gp2p.protocols.trust_protocol import TrustProtocol


class AlertProtocol(Protocol):
    """Protocol that reacts and dispatches alerts."""

    def __init__(self,
                 trust_db: TrustDatabase,
                 bridge: NetworkBridge,
                 trust_protocol: TrustProtocol,
                 configuration: TrustModelConfiguration,
                 aggregator: OpinionAggregator,
                 alert_callback: Callable[[SlipsThreatIntelligence], None]
                 ):
        super().__init__(configuration, trust_db, bridge)
        self.__trust_protocol = trust_protocol
        self.__alert_callback = alert_callback
        self.__aggregator = aggregator

    def dispatch_alert(self, target: Target, score: float, confidence: float):
        """Dispatches alert to the network."""
        self.__bridge.send_alert(target, ThreatIntelligence(score=score, confidence=confidence))

    def handle_alert(self, sender: PeerInfo, alert: Alert):
        """Handle alert received from the network."""
        peer_trust = self.__trust_db.get_peer_trust_data(sender.id)

        if peer_trust is None:
            peer_trust = self.__trust_protocol.determine_and_store_initial_trust(sender, get_recommendations=False)
            # TODO: maybe dispatch request to ask fellow peers?

        # aggregate request
        ti = self.__aggregator.evaluate_alert(peer_trust, alert)
        # and dispatch callback
        self.__alert_callback(ti)

        # and update service data
        # TODO: analyse how good was alert and then add assign weight for that
        self.__evaluate_interaction(peer_trust, Satisfaction.OK, Weight.ALERT)
