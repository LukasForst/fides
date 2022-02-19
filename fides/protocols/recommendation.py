import math
from typing import List, Optional

from fides.evaluation.recommendation.process import process_new_recommendations
from fides.evaluation.recommendation.selection import select_trustworthy_peers_for_recommendations
from fides.evaluation.service.interaction import Satisfaction, Weight
from fides.messaging.model import PeerRecommendationResponse
from fides.messaging.network_bridge import NetworkBridge
from fides.model.aliases import PeerId
from fides.model.configuration import TrustModelConfiguration
from fides.model.peer import PeerInfo
from fides.model.recommendation import Recommendation
from fides.persistance.trust import TrustDatabase
from fides.protocols.protocol import Protocol
from fides.utils.logger import Logger

logger = Logger(__name__)


class RecommendationProtocol(Protocol):
    """Protocol that is responsible for getting and updating recommendation data."""

    def __init__(self, configuration: TrustModelConfiguration, trust_db: TrustDatabase, bridge: NetworkBridge):
        super().__init__(configuration, trust_db, bridge)
        self.__rec_conf = configuration.recommendations
        self.__trust_db = trust_db
        self.__bridge = bridge

    def get_recommendation_for(self, peer: PeerInfo, recipients: Optional[List[PeerId]] = None):
        """Dispatches recommendation request from the network."""
        if not self.__rec_conf.enabled:
            logger.debug(f"Recommendation protocol is disabled. NOT getting recommendations for Peer {peer.id}.")

        recipients = recipients if recipients else self.__get_recommendation_request_recipients()
        if recipients:
            self.__bridge.send_recommendation_request(recipients=recipients, peer=peer.id)
        else:
            logger.debug(f"No peers are trusted enough to ask them for recommendation!")

    def handle_recommendation_request(self, request_id: str, sender: PeerInfo, subject: PeerId):
        """Handle request for recommendation on given subject."""
        sender_trust = self.__trust_db.get_peer_trust_data(sender)
        # TODO: [+] implement data filtering based on the sender
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
            recommendation = Recommendation(
                competence_belief=0,
                integrity_belief=0,
                service_history_size=0,
                recommendation=0,
                initial_reputation_provided_by_count=0
            )
        self.__bridge.send_recommendation_response(request_id, sender.id, subject, recommendation)

        self.__evaluate_interaction(sender_trust, Satisfaction.OK, Weight.INTELLIGENCE_REQUEST)

    def handle_recommendation_response(self, responses: List[PeerRecommendationResponse]):
        """Handles response from peers with recommendations. Updates all necessary values in db."""
        if len(responses) == 0:
            return
        # TODO: [+] handle cases with multiple subjects
        assert all(responses[0].subject == r.subject for r in responses), \
            "Responses are not for the same subject!"

        config = self.__trust_db.get_model_configuration()
        subject = self.__trust_db.get_peer_trust_data(responses[0].subject)

        recommendations = {r.sender.id: r.recommendation for r in responses}
        trust_matrix = self.__trust_db.get_peers_trust_data(list(recommendations.keys()))

        # check that the data are consistent
        assert len(trust_matrix) == len(responses) == len(recommendations), \
            f'Data are not consistent: TM: {len(trust_matrix)}, RES: {len(responses)}, REC: {len(recommendations)}!'

        # update all recommendations
        updated_matrix = process_new_recommendations(
            configuration=config,
            subject=subject,
            matrix=trust_matrix,
            recommendations=recommendations
        )
        # now store updated matrix
        self.__trust_db.store_peer_trust_matrix(updated_matrix)
        # and dispatch event
        self.__bridge.send_peers_reliability({p.peer_id: p.service_trust for p in updated_matrix.values()})

        # TODO: correct evaluation of the sent data
        interaction_matrix = {p: (Satisfaction.OK, Weight.RECOMMENDATION_RESPONSE) for p in trust_matrix.values()}
        self.__evaluate_interactions(interaction_matrix)

    def __get_recommendation_request_recipients(self) -> List[PeerId]:
        recommenders = []
        require_trusted_peer_count = self.__rec_conf.required_trusted_peers_count
        trusted_peer_threshold = self.__rec_conf.trusted_peer_threshold

        if self.__rec_conf.only_connected:
            recommenders = self.__trust_db.get_connected_peers()

        if self.__rec_conf.only_preconfigured:
            preconfigured_peers = set(p.id for p in self.__configuration.trusted_peers)
            preconfigured_organisations = set(p.id for p in self.__configuration.trusted_organisations)

            if recommenders:
                # if there are already some recommenders it means that only_connected filter is enabled
                # in that case we need to filter those peers and see if they either are on preconfigured
                # list or if they have any organisation
                recommenders = [p for p in recommenders
                                if p.id in preconfigured_peers
                                or preconfigured_organisations.intersection(p.organisations)]
            else:
                # if there are no recommenders, only_preconfigured is disabled, so we select all preconfigured
                # peers and all peers from database that have the organisation
                recommenders = list(preconfigured_peers) \
                               + [p.id for p in
                                  self.__trust_db.get_peers_with_organisations(list(preconfigured_organisations))]
            # if we have only_preconfigured, we do not need to care about minimal trust because we're safe enough
            require_trusted_peer_count = -math.inf
            trusted_peer_threshold = -math.inf

        if not recommenders:
            # if we still don't have any recommenders, we need to fetch some from the database
            recommenders = [p.id for p in
                            self.__trust_db.get_peers_with_geq_recommendation_trust(trusted_peer_threshold)]

        # now we need to get all trust data and sort them by recommendation trust
        candidates = [p for p in self.__trust_db.get_peers_trust_data(recommenders).values()
                      if p.recommendation_trust > trusted_peer_threshold]
        # check if we can proceed
        if len(candidates) < require_trusted_peer_count:
            logger.debug(
                f"Not enough trusted peers! Candidates: {len(candidates)}, requirement: {require_trusted_peer_count}.")
            return []

        # and finally use SORT selection algorithm to pick the correct list of recipients
        return select_trustworthy_peers_for_recommendations(
            data={p.peer_id: p.recommendation_trust for p in candidates},
            max_peers=self.__rec_conf.peers_max_count
        )
