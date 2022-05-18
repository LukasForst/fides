from typing import Callable

from fides.evaluation.service.interaction import Weight, SatisfactionLevels
from fides.messaging.network_bridge import NetworkBridge
from fides.model.alert import Alert
from fides.model.aliases import Target
from fides.model.configuration import TrustModelConfiguration
from fides.model.peer import PeerInfo
from fides.model.threat_intelligence import ThreatIntelligence, SlipsThreatIntelligence
from fides.persistence.trust import TrustDatabase
from fides.protocols.initial_trusl import InitialTrustProtocol
from fides.protocols.opinion import OpinionAggregator
from fides.protocols.protocol import Protocol


class AlertProtocol(Protocol):
    """Protocol that reacts and dispatches alerts."""

    def __init__(self,
                 trust_db: TrustDatabase,
                 bridge: NetworkBridge,
                 trust_protocol: InitialTrustProtocol,
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
        self._bridge.send_alert(target, ThreatIntelligence(score=score, confidence=confidence))

    def handle_alert(self, sender: PeerInfo, alert: Alert):
        """Handle alert received from the network."""
        peer_trust = self._trust_db.get_peer_trust_data(sender.id)

        if peer_trust is None:
            peer_trust = self.__trust_protocol.determine_and_store_initial_trust(sender, get_recommendations=False)
            # TODO: [?] maybe dispatch request to ask fellow peers?

        # aggregate request
        ti = self.__aggregator.evaluate_alert(peer_trust, alert)
        # and dispatch callback
        self.__alert_callback(ti)

        # and update service data
        self._evaluate_interaction(peer_trust, SatisfactionLevels.Ok, Weight.ALERT)
