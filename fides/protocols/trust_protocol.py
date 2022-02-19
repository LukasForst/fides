from fides.evaluation.service.interaction import Satisfaction, Weight
from fides.evaluation.service.process import process_service_interaction
from fides.model.peer import PeerInfo
from fides.model.peer_trust_data import PeerTrustData, trust_data_prototype
from fides.model.trust_model_configuration import TrustModelConfiguration
from fides.persistance.trust import TrustDatabase
from fides.protocols.recommendation import RecommendationProtocol
from fides.utils.logger import Logger

logger = Logger(__name__)


class TrustProtocol:
    def __init__(self,
                 trust_db: TrustDatabase,
                 configuration: TrustModelConfiguration,
                 recommendation_protocol: RecommendationProtocol
                 ):
        self.__trust_db = trust_db
        self.__configuration = configuration
        self.__recommendation_protocol = recommendation_protocol

    def determine_and_store_initial_trust(self, peer: PeerInfo, get_recommendations: bool = False) -> PeerTrustData:
        """Determines initial trust and stores that value in database.

        Returns trust data before the recommendation protocol is executed.
        """
        logger.debug(f"Determining trust for peer {peer.id}", peer)

        existing_trust = self.__trust_db.get_peer_trust_data(peer.id)
        if existing_trust is not None:
            logger.debug(f"There's an existing trust for peer {peer.id}: ST: {existing_trust.service_trust}")
            return existing_trust

        # now we know that this is a new peer
        trust = trust_data_prototype(peer)
        # add values that are inherited from the organisation
        peers_orgs = [org for org in self.__configuration.trusted_organisations if org.identifier in peer.organisations]
        if peers_orgs:
            logger.debug(f"Peer {peer.id} has known organisations.", peers_orgs)
            trust.initial_reputation_provided_by_count = len(peers_orgs)
            # select organisation that has the highest trust
            leading_organisation = max(peers_orgs, key=lambda org: org.trust)
            logger.debug(f"Main organisation selected, computing trust", leading_organisation)

            # TODO check which believes / trust metrics can we set as well
            trust.reputation = max(trust.reputation, leading_organisation.trust)
            trust.recommendation_trust = trust.reputation
            # process interaction and assign all others values
            trust = process_service_interaction(configuration=self.__configuration,
                                                peer=trust,
                                                satisfaction=Satisfaction.OK,
                                                weight=Weight.FIRST_ENCOUNTER
                                                )
            logger.debug(f"New trust for peer:", trust)
            # if we need to enforce that the peer has the same trust during the runtime,
            # we need to set service trust as well
            if leading_organisation.enforce_trust:
                trust.has_fixed_trust = True
                trust.service_trust = trust.reputation
                # and we will be satisfied with all interactions equally
                trust.integrity_belief = 1
                trust.competence_belief = 1
                logger.debug(f"Enforced trust, leaving service trust to: {trust.service_trust}.")

        if trust.reputation == 0 and get_recommendations:
            logger.debug("Getting recommendations.")
            self.__recommendation_protocol.get_recommendation_for(trust.info)

        # now we save the trust to the database as we have everything we need
        self.__trust_db.store_peer_trust_data(trust)
        return trust
