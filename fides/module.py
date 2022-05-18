from typing import Union

from fides.messaging.message_handler import MessageHandler
from fides.messaging.model import NetworkMessage
from fides.messaging.network_bridge import NetworkBridge
from fides.messaging.queue_in_memory import InMemoryQueue
from fides.model.configuration import load_configuration
from fides.model.threat_intelligence import SlipsThreatIntelligence
from fides.persistence.threat_intelligence_in_memory import InMemoryThreatIntelligenceDatabase
from fides.persistence.trust_in_memory import InMemoryTrustDatabase
from fides.protocols.alert import AlertProtocol
from fides.protocols.initial_trusl import InitialTrustProtocol
from fides.protocols.opinion import OpinionAggregator
from fides.protocols.peer_list import PeerListUpdateProtocol
from fides.protocols.recommendation import RecommendationProtocol
from fides.protocols.threat_intelligence import ThreatIntelligenceProtocol
from fides.utils.logger import LoggerPrintCallbacks, Logger

if __name__ == '__main__':
    # setup logger (for slips add the handler from the module)
    LoggerPrintCallbacks.clear()
    LoggerPrintCallbacks.append(print)
    logger = Logger("TestStartup")

    config = load_configuration('../fides.conf.yml')

    trust_db = InMemoryTrustDatabase(config)
    ti_db = InMemoryThreatIntelligenceDatabase()

    queue = InMemoryQueue()

    bridge = NetworkBridge(queue)


    def network_opinion_callback(ti: SlipsThreatIntelligence):
        logger.info(f'Callback: Target: {ti.target}, Score: {ti.score}, Confidence: {ti.confidence}')


    recommendations = RecommendationProtocol(config, trust_db, bridge, )
    trust = InitialTrustProtocol(trust_db, config, recommendations)
    peer_list = PeerListUpdateProtocol(trust_db, bridge, recommendations, trust)
    opinion = OpinionAggregator(config, ti_db, config.ti_aggregation_strategy)

    intelligence = ThreatIntelligenceProtocol(trust_db, ti_db, bridge, config, opinion, trust,
                                              config.interaction_evaluation_strategy, network_opinion_callback)
    alert = AlertProtocol(trust_db, bridge, trust, config, opinion, network_opinion_callback)


    def on_unknown_message(message: NetworkMessage):
        logger.error('Unknown message received!', message)


    def on_error(msg: Union[str, NetworkMessage], ex: Exception):
        logger.error(f'Error during event handling! {ex}', msg)


    message_handler = MessageHandler(
        on_peer_list_update=peer_list.handle_peer_list_updated,
        on_recommendation_request=recommendations.handle_recommendation_request,
        on_recommendation_response=recommendations.handle_recommendation_response,
        on_alert=alert.handle_alert,
        on_intelligence_request=intelligence.handle_intelligence_request,
        on_intelligence_response=intelligence.handle_intelligence_response,
        on_unknown=on_unknown_message,
        on_error=on_error
    )

    bridge.listen(message_handler)
