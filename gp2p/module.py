from gp2p.messaging.message_handler import MessageHandler
from gp2p.messaging.network_bridge import NetworkBridge
from gp2p.messaging.queue import Queue
from gp2p.model.threat_intelligence import SlipsThreatIntelligence
from gp2p.model.trust_model_configuration import TrustModelConfiguration
from gp2p.persistance.slips import ThreatIntelligenceDatabase
from gp2p.persistance.trust import TrustDatabase
from gp2p.protocols.alert import AlertProtocol
from gp2p.protocols.opinion import OpinionAggregator
from gp2p.protocols.peer_list import PeerListUpdateProtocol
from gp2p.protocols.recommendation import RecommendationProtocol
from gp2p.protocols.threat_intelligence import ThreatIntelligenceProtocol
from gp2p.protocols.trust_protocol import TrustProtocol
from gp2p.utils.logger import LoggerPrintCallbacks, Logger


def initiate():
    # setup logger (for slips add the handler from the module)
    LoggerPrintCallbacks.clear()
    LoggerPrintCallbacks.append(print)

    logger = Logger("TestStartup")

    trust_db = TrustDatabase()
    ti_db = ThreatIntelligenceDatabase()

    config = TrustModelConfiguration(1, 1, 1, [], 0)
    trust_db.store_model_configuration(config)

    queue = Queue()

    bridge = NetworkBridge(queue)

    def network_opinion_callback(ti: SlipsThreatIntelligence):
        logger.info(f'Callback: Target: {ti.target}, Score: {ti.score}, Confidence: {ti.confidence}')

    recommendations = RecommendationProtocol(config, trust_db, bridge)
    trust = TrustProtocol(trust_db, config, recommendations)
    peer_list = PeerListUpdateProtocol(trust_db, bridge, recommendations, trust)
    opinion = OpinionAggregator(config)
    intelligence = ThreatIntelligenceProtocol(trust_db, ti_db, bridge, config, opinion, network_opinion_callback)
    alert = AlertProtocol(trust_db, bridge, trust, config, opinion, network_opinion_callback)

    # TODO: now connect alert to the queue receiving data from blocking module
    message_handler = MessageHandler(
        on_peer_list_update=peer_list.handle_peer_list_updated,
        on_recommendation_request=recommendations.handle_recommendation_request,
        on_recommendation_response=recommendations.handle_recommendation_response,
        on_alert=alert.handle_alert,
        on_intelligence_request=intelligence.handle_intelligence_request,
        on_intelligence_response=intelligence.handle_intelligence_response,
    )

    bridge.listen(message_handler)
