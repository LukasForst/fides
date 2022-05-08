from typing import List, Dict, Callable, Optional, Tuple, Set

from fides.messaging.model import NetworkMessage, PeerIntelligenceResponse, PeerRecommendationResponse
from fides.model.aliases import Target, Score, PeerId
from fides.utils.logger import Logger
from simulations.peer import Peer
from simulations.utils import Click
from tests.load_fides import Fides
from tests.messaging.messages import nl2tl_intelligence_response, serialize, nl2tl_peers_list, \
    nl2tl_recommendation_response

logger = Logger(__name__)


class TimeEnvironment:

    def __init__(self,
                 fides: Fides,
                 fides_stream: List[NetworkMessage],
                 other_peers: List[Peer],
                 targets: Dict[Target, Score],
                 enable_messages_processing: bool = False
                 ) -> None:
        self._fides = fides
        self._fides_stream = fides_stream
        self._other_peers = other_peers
        self._targets = targets
        self._enable_messages_processing = enable_messages_processing

    def run(self, simulation_clicks: Click, epoch_callback: Optional[Callable[[Click], None]] = None):
        for epoch in range(simulation_clicks):
            logger.debug(f"Running epoch {epoch}")
            self._run_epoch(epoch)
            logger.debug(f"Epoch {epoch} done")
            if epoch_callback:
                epoch_callback(epoch)

        logger.info("Simulation done!")

    def _run_epoch(self, epoch: Click):
        # each epoch we need to refresh peer list to get new peers that joined
        self._refresh_peer_list(epoch)
        for target, baseline in self._targets.items():
            self._run_for_target(epoch, target, baseline)

    def _refresh_peer_list(self, epoch: Click):
        active_peers = [p.peer_info for p in self._other_peers if p.network_joining_epoch <= epoch]
        self._fides.queue.send_message(serialize(nl2tl_peers_list(active_peers)))
        # now process recommendation responses
        self._process_fides_messages(epoch)

    def _run_for_target(self, epoch: Click, target: Target, baseline: Score):
        tis = [(peer.peer_info, peer.provide_ti(epoch, target, baseline))
               for peer in self._other_peers]  # obtain TI
        # create responses
        responses = [PeerIntelligenceResponse(peer, ti, target) for (peer, ti) in tis if ti is not None]
        # and dispatch message to fides
        self._fides.queue.send_message(serialize(nl2tl_intelligence_response(responses)))
        # now process recommendation responses
        self._process_fides_messages(epoch)

    def _process_fides_messages(self, epoch: Click):
        recommendation_requests: List[Tuple[PeerId, Set[PeerId]]] = [(m.data['payload'], set(m.data['receiver_ids']))
                                                                     for m in self._fides_stream if
                                                                     m.type == 'tl2nl_recommendation_request']
        self._fides_stream.clear()
        baseline_behavior = {p.peer_info.id: p.label for p in self._other_peers}

        for (subject, recommender_ids) in recommendation_requests:
            recommendations = [(p.peer_info, p.provide_recommendation(epoch, subject, baseline_behavior[subject]))
                               for p in self._other_peers if p.peer_info.id in recommender_ids]
            responses = [PeerRecommendationResponse(
                sender=peer_info,
                subject=subject,
                recommendation=recommendation
            ) for (peer_info, recommendation) in recommendations if recommendation]

            self._fides.queue.send_message(serialize(nl2tl_recommendation_response(responses)))
