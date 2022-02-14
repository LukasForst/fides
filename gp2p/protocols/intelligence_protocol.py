from gp2p.messaging.network_bridge import NetworkBridge
from gp2p.model.trust_model_configuration import TrustModelConfiguration
from gp2p.persistance.trust import TrustDatabase


class ThreatIntelligenceProtocol:
    def __init__(self,
                 trust_db: TrustDatabase,
                 bridge: NetworkBridge,
                 configuration: TrustModelConfiguration,
                 ):
        self.__trust_db = trust_db
        self.__bridge = bridge
        self.__configuration = configuration
