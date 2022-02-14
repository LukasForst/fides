from gp2p.model.peer import PeerInfo
from gp2p.model.peer_trust_data import PeerTrustData
from gp2p.model.trust_model_configuration import TrustModelConfiguration
from gp2p.persistance.trust import TrustDatabase
from gp2p.protocols.recommendation_protocol import RecommendationProtocol


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
        existing_trust = self.__trust_db.get_peer_trust_data(peer.id)
        if existing_trust is not None:
            return existing_trust

        # now we know that this is a new peer
        trust = PeerTrustData(
            info=peer,
            service_trust=0,
            reputation=0,
            recommendation_trust=0,
            competence_belief=0,
            integrity_belief=0,
            initial_reputation_provided_by_count=0,
            service_history=[],
            recommendation_history=[]
        )
        # add values that are inherited from the organisation
        peers_orgs = [org for org in self.__configuration.trusted_organisations if org.identifier in peer.organisations]
        if peers_orgs:
            trust.initial_reputation_provided_by_count = len(peers_orgs)
            # select organisation that has the highest trust
            leading_organisation = max(peers_orgs, key=lambda org: org.trust)
            # TODO check which believes / trust metrics can we set as well
            trust.reputation = max(trust.reputation, leading_organisation.trust)
            trust.recommendation_trust = trust.reputation
            # if we need to enforce that the peer has the same trust during the runtime,
            # we need to set service trust as well
            if leading_organisation.enforce_trust:
                trust.service_trust = trust.reputation
                # and we will be satisfied with all interactions equally
                trust.integrity_belief = 1
                trust.competence_belief = 1

        if trust.reputation == 0 and get_recommendations:
            self.__recommendation_protocol.get_recommendation_for(trust.info)

        # now we save the trust to the database as we have everything we need
        self.__trust_db.store_peer_trust_data(trust)
        return trust
