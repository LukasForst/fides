from typing import List, Callable

from gp2p.evaluation.service.interaction import Satisfaction, Weight
from gp2p.messaging.model import PeerIntelligenceResponse
from gp2p.messaging.network_bridge import NetworkBridge
from gp2p.model.aliases import Target
from gp2p.model.peer import PeerInfo
from gp2p.model.threat_intelligence import ThreatIntelligence, SlipsThreatIntelligence
from gp2p.model.trust_model_configuration import TrustModelConfiguration
from gp2p.persistance.slips import ThreatIntelligenceDatabase
from gp2p.persistance.trust import TrustDatabase
from gp2p.protocols.opinion import OpinionAggregator
from gp2p.protocols.protocol import Protocol


class ThreatIntelligenceProtocol(Protocol):
    """Class handling threat intelligence requests and responses."""

    def __init__(self,
                 trust_db: TrustDatabase,
                 ti_db: ThreatIntelligenceDatabase,
                 bridge: NetworkBridge,
                 configuration: TrustModelConfiguration,
                 aggregator: OpinionAggregator,
                 network_opinion_callback: Callable[[SlipsThreatIntelligence], None]
                 ):
        super().__init__(configuration, trust_db, bridge)
        self.__ti_db = ti_db
        self.__aggregator = aggregator
        self.__network_opinion_callback = network_opinion_callback

    def request_data(self, target: Target):
        """Requests network opinion on given target."""
        self.__bridge.send_intelligence_request(target)

    def handle_intelligence_request(self, request_id: str, sender: PeerInfo, target: Target):
        """Handles intelligence request."""
        peer_trust = self.__trust_db.get_peer_trust_data(sender.id)
        # TODO: implement privacy filter - what we can send and what needs to be filtered
        ti = self.__ti_db.get_for(target)
        # TODO: how to properly handle that? we need to send something
        if ti is None:
            ti = ThreatIntelligence(score=0, confidence=0)

        # and respond with data we have
        self.__bridge.send_intelligence_response(request_id, target, ti)
        self.__evaluate_interaction(peer_trust,
                                    Satisfaction.OK if ti.confidence else Satisfaction.UNSURE,
                                    Weight.INTELLIGENCE_REQUEST)

    def handle_intelligence_response(self, responses: List[PeerIntelligenceResponse]):
        """Handles intelligence responses."""
        trust_matrix = self.__trust_db.get_peers_trust_data([r.sender.id for r in responses])
        assert len(trust_matrix) == len(responses), 'We need to have trust data for all peers that sent the response.'
        target = {r.target for r in responses}
        assert len(target) == 1, 'Responses should be for a single target.'
        target = target.pop()

        # now everything is checked, so we aggregate it and get the threat intelligence
        r = {r.sender.id: r for r in responses}
        ti = self.__aggregator.evaluate_intelligence_response(target, r, trust_matrix)

        self.__network_opinion_callback(ti)

        # TODO: correct evaluation of the sent data
        interaction_matrix = {p: (Satisfaction.OK, Weight.INTELLIGENCE_DATA_REPORT) for p in trust_matrix.values()}
        self.__evaluate_interactions(interaction_matrix)
