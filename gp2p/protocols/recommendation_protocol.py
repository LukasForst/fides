from typing import List

from gp2p.evaluation.recommendation.process import process_new_recommendations
from gp2p.messaging.model import PeerRecommendationResponse
from gp2p.messaging.network_bridge import NetworkBridge
from gp2p.model.aliases import PeerId
from gp2p.model.peer import PeerInfo
from gp2p.model.recommendation import Recommendation
from gp2p.persistance.trust import TrustDatabase


class RecommendationProtocol:
    """Protocol that is responsible for getting and updating recommendation data."""

    def __init__(self, trust_db: TrustDatabase, bridge: NetworkBridge):
        self.__trust_db = trust_db
        self.__bridge = bridge

    def get_recommendation_for(self, peer: PeerInfo):
        """Dispatches recommendation request from the network."""
        # TODO: implement peers selection according to the SORT protocol
        # TODO: involve peer reliability and trust
        # for now we just ask all of the connected peers for opinion
        connected_peers = [p.id for p in self.__trust_db.get_connected_peers()]
        self.__bridge.send_recommendation_request(recipients=connected_peers, peer=peer.id)

    def handle_recommendation_request(self, request_id: str, sender: PeerInfo, subject: PeerId):
        """Handle request for recommendation on given subject."""
        # TODO: implement data filtering based on the sender
        trust = self.__trust_db.get_peer_trust_data(subject)
        if trust is not None:
            recommendation = Recommendation(
                competence_belief=trust.competence_belief,
                integrity_belief=trust.integrity_belief,
                service_history_size=trust.service_history_size,
                recommendation=trust.reputation,
                initial_reputation_provided_by_count=trust.initial_reputation_provided_by_count
            )
        else:
            # TODO: check if we want to send empty or not send it at all
            recommendation = Recommendation(
                competence_belief=0,
                integrity_belief=0,
                service_history_size=0,
                recommendation=0,
                initial_reputation_provided_by_count=0
            )
        self.__bridge.send_recommendation_response(request_id, sender.id, subject, recommendation)

    def handle_recommendation_response(self, responses: List[PeerRecommendationResponse]):
        """Handles response from peers with recommendations. Updates all necessary values in db."""
        if len(responses) == 0:
            return
        assert all(responses[0].subject == r.subject for r in responses), \
            "Responses are not for the same subject!"

        config = self.__trust_db.get_model_configuration()
        subject = self.__trust_db.get_peer_trust_data(responses[0].subject)

        recommendations = {r.sender.id: r.recommendation for r in responses}
        peers = self.__trust_db.get_peers_trust_data(list(recommendations.keys()))
        trust_matrix = {p.peer_id: p for p in peers}

        # check that the data are consistent
        assert len(trust_matrix) == len(responses) == len(recommendations)

        # update all recommendations
        updated_matrix = process_new_recommendations(
            configuration=config,
            subject=subject,
            matrix=trust_matrix,
            recommendations=recommendations
        )
        # now store updated matrix
        self.__trust_db.store_peer_trust_matrix(updated_matrix)
