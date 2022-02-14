from gp2p.messaging.message_handler import MessageHandler
from gp2p.messaging.network_bridge import NetworkBridge
from gp2p.messaging.queue import Queue
from gp2p.model.trust_model_configuration import TrustModelConfiguration
from gp2p.persistance.slips import ThreatIntelligenceDatabase
from gp2p.persistance.trust import TrustDatabase
from gp2p.protocols.alert_protocol import AlertProtocol
from gp2p.protocols.peer_list_updated_protocol import PeerListUpdateProtocol
from gp2p.protocols.recommendation_protocol import RecommendationProtocol
from gp2p.protocols.trust_protocol import TrustProtocol


def initiate():
    trust_db = TrustDatabase()
    ti_db = ThreatIntelligenceDatabase()

    config = TrustModelConfiguration(1, 1, 1, [])
    trust_db.store_model_configuration(config)

    queue = Queue()

    bridge = NetworkBridge(queue)

    recommendations = RecommendationProtocol(trust_db, bridge)
    trust = TrustProtocol(trust_db, config, recommendations)
    peer_list = PeerListUpdateProtocol(trust_db, bridge, recommendations, trust)
    alert = AlertProtocol(trust_db, bridge)
    # TODO: now connect alert to the queue receiving data from blocking module
    message_handler = MessageHandler(
        on_peer_list_update=peer_list.peer_list_updated,
        on_recommendation_request=recommendations.handle_recommendation_request,
        on_recommendation_response=recommendations.handle_recommendation_response,
        on_alert=alert.handle_alert,  # TODO
        on_intelligence_request=None,  # TODO
        on_intelligence_response=None,  # TODO
    )

    bridge.listen(message_handler)
