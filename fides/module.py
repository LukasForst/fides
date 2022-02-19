from fides.messaging.message_handler import MessageHandler
from fides.messaging.network_bridge import NetworkBridge
from fides.messaging.queue import Queue
from fides.model.configuration import load_configuration
from fides.model.threat_intelligence import SlipsThreatIntelligence
from fides.persistance.slips import ThreatIntelligenceDatabase
from fides.persistance.trust import TrustDatabase
from fides.protocols.alert import AlertProtocol
from fides.protocols.opinion import OpinionAggregator
from fides.protocols.peer_list import PeerListUpdateProtocol
from fides.protocols.recommendation import RecommendationProtocol
from fides.protocols.threat_intelligence import ThreatIntelligenceProtocol
from fides.protocols.trust_protocol import TrustProtocol
from fides.utils.logger import LoggerPrintCallbacks, Logger


def initiate():
    # setup logger (for slips add the handler from the module)
    LoggerPrintCallbacks.clear()
    LoggerPrintCallbacks.append(print)

    logger = Logger("TestStartup")

    trust_db = TrustDatabase()
    ti_db = ThreatIntelligenceDatabase()

    config = load_configuration('TODO')
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
