import json
from dataclasses import asdict
from typing import Dict, List

from global_p2p.messaging.message_handler import MessageHandler
from global_p2p.messaging.model import NetworkMessage, Alert
from global_p2p.messaging.queue import Queue
from global_p2p.model.aliases import PeerId, Target
from global_p2p.model.recommendation_response import Recommendation
from global_p2p.model.threat_intelligence import ThreatIntelligence


class NetworkBridge:
    """
    Class responsible for communication with the network module.

    In order to connect bridge to the queue and start receiving messages,
    execute "listen" method.
    """
    version = 1

    def __init__(self, queue: Queue, handler: MessageHandler):
        self._queue = queue
        self._handler = handler

    def listen(self):
        """Starts messages processing, this method is not blocking."""
        self._queue.listen(lambda message: self._handler.on_message(NetworkMessage(**json.loads(message))))

    def send_intelligence_response(self, request_id: str, target: Target, intelligence: ThreatIntelligence):
        """Shares Intelligence with peer that requested it. request_id comes from the first request."""
        envelope = NetworkMessage(
            type='tl2nl_intelligence_response',
            version=self.version,
            data={
                'request_id': request_id,
                'payload': {'target': target, 'intelligence': intelligence}
            }
        )
        self.__send(envelope)

    def send_intelligence_request(self, target: Target):
        """Requests network intelligence from the network regarding this target."""
        envelope = NetworkMessage(
            type='tl2nl_intelligence_request',
            version=self.version,
            data={'payload': target}
        )
        self.__send(envelope)

    def send_alert(self, target: Target, intelligence: ThreatIntelligence):
        """Broadcasts alert through the network about the target."""
        envelope = NetworkMessage(
            type='tl2nl_alert',
            version=self.version,
            data={
                'payload': Alert(
                    target=target,
                    score=intelligence.score,
                    confidence=intelligence.confidence
                )
            }
        )
        self.__send(envelope)

    def send_recommendation_response(self, request_id: str,
                                     recipient: PeerId,
                                     peer: PeerId,
                                     recommendation: Recommendation):
        """Responds to given request_id to recipient with recommendation on target."""
        envelope = NetworkMessage(
            type='tl2nl_recommendation_response',
            version=self.version,
            data={
                'request_id': request_id,
                'recipient_id': recipient,
                'payload': {'peer': peer, 'recommendation': recommendation}
            }
        )
        self.__send(envelope)

    def send_recommendation_request(self, recipients: List[PeerId], peer: PeerId):
        """Request recommendation from recipients on given peer."""
        envelope = NetworkMessage(
            type='tl2nl_recommendation_request',
            version=self.version,
            data={
                'receiver_ids': recipients,
                'payload': peer
            }
        )
        self.__send(envelope)

    def send_peers_reliability(self, reliability: Dict[PeerId, float]):
        """Sends peer reliability, this message is only for network layer and is not dispatched to the network."""
        data = [{'peer_id': key, 'reliability': value} for key, value in reliability.items()]
        envelope = NetworkMessage(
            type='tl2nl_peers_reliability',
            version=self.version,
            data=data
        )
        self.__send(envelope)

    def __send(self, envelope: NetworkMessage):
        # TODO: error handling
        j = json.dumps(asdict(envelope))
        self._queue.send(j)
