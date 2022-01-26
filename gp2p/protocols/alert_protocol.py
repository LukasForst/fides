from gp2p.messaging.network_bridge import NetworkBridge
from gp2p.model.alert import Alert
from gp2p.model.aliases import Target
from gp2p.model.peer import PeerInfo
from gp2p.model.threat_intelligence import ThreatIntelligence
from gp2p.persistance.trust import TrustDatabase


class AlertProtocol:
    """Protocol that reacts and dispatches alerts."""

    def __init__(self, trust_db: TrustDatabase, bridge: NetworkBridge):
        self.__trust_db = trust_db
        self.__bridge = bridge

    def dispatch_alert(self, target: Target, score: float, confidence: float):
        """Dispatches alert to the network."""
        self.__bridge.send_alert(target, ThreatIntelligence(score=score, confidence=confidence))

    def handle_alert(self, sender: PeerInfo, alert: Alert):
        """Handle alert received from the network."""
        # TODO: implement this
        pass
