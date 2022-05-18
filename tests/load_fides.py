import json
from dataclasses import dataclass
from typing import Union, List, Dict

from dacite import from_dict

from fides.evaluation.ti_aggregation import TIAggregation
from fides.messaging.message_handler import MessageHandler
from fides.messaging.model import NetworkMessage
from fides.messaging.network_bridge import NetworkBridge
from fides.model.aliases import Target
from fides.model.configuration import TrustModelConfiguration
from fides.model.threat_intelligence import SlipsThreatIntelligence
from fides.persistence.threat_intelligence_in_memory import InMemoryThreatIntelligenceDatabase
from fides.persistence.trust_in_memory import InMemoryTrustDatabase
from fides.protocols.alert import AlertProtocol
from fides.protocols.initial_trusl import InitialTrustProtocol
from fides.protocols.opinion import OpinionAggregator
from fides.protocols.peer_list import PeerListUpdateProtocol
from fides.protocols.recommendation import RecommendationProtocol
from fides.protocols.threat_intelligence import ThreatIntelligenceProtocol
from fides.utils.logger import Logger
from tests.load_config import find_config
from tests.messaging.queue import TestQueue

logger = Logger(__name__)


@dataclass
class Fides:
    config: TrustModelConfiguration
    trust_db: InMemoryTrustDatabase
    ti_db: InMemoryThreatIntelligenceDatabase
    queue: TestQueue
    bridge: NetworkBridge
    recommendations: RecommendationProtocol
    trust: InitialTrustProtocol
    peer_list: PeerListUpdateProtocol
    ti_aggregation: TIAggregation
    opinion: OpinionAggregator
    intelligence: ThreatIntelligenceProtocol
    alert: AlertProtocol
    message_handler: MessageHandler

    def listen(self, block: bool = False):
        return self.bridge.listen(self.message_handler, block)


def get_fides(**kwargs) -> Fides:
    """Creates instance of Fides with all dependencies."""

    config = kwargs.get('config', find_config())

    trust_db = kwargs.get('trust_db', InMemoryTrustDatabase(config))
    ti_db = kwargs.get('ti_db', InMemoryThreatIntelligenceDatabase())

    queue = kwargs.get('queue', TestQueue())

    bridge = kwargs.get('bridge', NetworkBridge(queue))

    def default_network_opinion_callback(ti: SlipsThreatIntelligence):
        logger.info(f'Callback: Target: {ti.target}, Score: {ti.score}, Confidence: {ti.confidence}')

    network_opinion_callback = kwargs.get('network_opinion_callback', default_network_opinion_callback)

    recommendations = kwargs.get('recommendations', RecommendationProtocol(config, trust_db, bridge))
    trust = kwargs.get('trust', InitialTrustProtocol(trust_db, config, recommendations))
    peer_list = kwargs.get('peer_list', PeerListUpdateProtocol(trust_db, bridge, recommendations, trust))
    ti_aggregation = kwargs.get('ti_aggregation', config.ti_aggregation_strategy)
    opinion = kwargs.get('opinion', OpinionAggregator(config, ti_db, ti_aggregation))
    ti_evaluation_strategy = kwargs.get('ti_evaluation_strategy', config.interaction_evaluation_strategy)
    intelligence = kwargs.get('intelligence',
                              ThreatIntelligenceProtocol(trust_db, ti_db, bridge, config, opinion, trust,
                                                         ti_evaluation_strategy,
                                                         network_opinion_callback))
    alert = kwargs.get('alert', AlertProtocol(trust_db, bridge, trust, config, opinion, network_opinion_callback))

    def default_on_unknown_message(message: NetworkMessage):
        logger.error('Unknown message received!', message)

    on_unknown_message = kwargs.get('on_unknown_message', default_on_unknown_message)

    def default_on_error(msg: Union[str, NetworkMessage], ex: Exception):
        import sys
        info = sys.exc_info()[2]
        logger.error(f'Error during event handling:\n{info.tb_frame}! {ex}', msg)
        assert False, 'Error during event handling!'

    on_error = kwargs.get('on_error', default_on_error)

    message_handler = kwargs.get('message_handler', MessageHandler(
        on_peer_list_update=peer_list.handle_peer_list_updated,
        on_recommendation_request=recommendations.handle_recommendation_request,
        on_recommendation_response=recommendations.handle_recommendation_response,
        on_alert=alert.handle_alert,
        on_intelligence_request=intelligence.handle_intelligence_request,
        on_intelligence_response=intelligence.handle_intelligence_response,
        on_unknown=on_unknown_message,
        on_error=on_error
    ))
    return Fides(
        config,
        trust_db,
        ti_db,
        queue,
        bridge,
        recommendations,
        trust,
        peer_list,
        ti_aggregation,
        opinion,
        intelligence,
        alert,
        message_handler,
    )


def get_fides_stream(**kwargs) -> (Fides, List[NetworkMessage], Dict[Target, SlipsThreatIntelligence]):
    """Returns fides and list of messages that will be updated when new message comes."""
    messages: List[NetworkMessage] = []
    # noinspection PyTypeChecker
    network_opinions: Dict[Target, SlipsThreatIntelligence] = {}

    def on_network_opinion(ti: SlipsThreatIntelligence):
        network_opinions[ti.target] = ti

    if kwargs.get('network_opinion_callback') is None:
        kwargs['network_opinion_callback'] = on_network_opinion

    f = get_fides(**kwargs)

    def on_message(m: str):
        messages.append(from_dict(data_class=NetworkMessage, data=json.loads(m)))

    f.queue.on_send_called = on_message
    f.listen()
    return f, messages, network_opinions
