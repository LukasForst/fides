import logging
from typing import List, Dict, Callable, Optional

from fides.messaging.model import NetworkMessage, PeerIntelligenceResponse
from fides.model.aliases import Target, Score
from simulations.peer import Peer
from simulations.utils import Click
from tests.load_fides import Fides
from tests.messaging.messages import nl2tl_intelligence_response, serialize, nl2tl_peers_list

logger = logging.getLogger(__name__)


class Environment:

    def run(self):
        pass


class TimeEnvironment:

    def __init__(self,
                 fides: Fides,
                 fides_stream: List[NetworkMessage],
                 other_peers: List[Peer],
                 targets: Dict[Target, Score]
                 ) -> None:
        self._fides = fides
        self._fides_stream = fides_stream
        self._other_peers = other_peers
        self._targets = targets

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
        self._process_fides_messages()

    def _run_for_target(self, epoch: Click, target: Target, baseline: Score):
        tis = [(peer.peer_info, peer.provide_ti(epoch, target, baseline))
               for peer in self._other_peers]  # obtain TI
        # create responses
        responses = [PeerIntelligenceResponse(peer, ti, target) for (peer, ti) in tis if ti is not None]
        # and dispatch message to fides
        self._fides.queue.send_message(serialize(nl2tl_intelligence_response(responses)))
        self._process_fides_messages()

    def _process_fides_messages(self):
        # TODO now react on messages from fides_stream, so execute recommendations
        pass
