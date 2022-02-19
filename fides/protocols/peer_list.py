from typing import List

from fides.messaging.network_bridge import NetworkBridge
from fides.model.peer import PeerInfo
from fides.persistance.trust import TrustDatabase
from fides.protocols.recommendation import RecommendationProtocol
from fides.protocols.trust_protocol import TrustProtocol


class PeerListUpdateProtocol:
    """Protocol handling situations when peer list was updated."""

    def __init__(self,
                 trust_db: TrustDatabase,
                 bridge: NetworkBridge,
                 recommendation_protocol: RecommendationProtocol,
                 trust_protocol: TrustProtocol
                 ):
        self.__trust_db = trust_db
        self.__bridge = bridge
        self.__recommendation_protocol = recommendation_protocol
        self.__trust_protocol = trust_protocol

    def handle_peer_list_updated(self, peers: List[PeerInfo]):
        """Processes updated peer list."""
        # first store them in the database
        self.__trust_db.store_connected_peers_list(peers)
        # and now find their trust metrics to send it to the network module
        trust_data = self.__trust_db.get_peers_trust_data([p.id for p in peers])
        # if we don't have data for all peers that means that there are some new peers
        # we need to establish initial trust for them
        if len(trust_data) != len(peers):
            known_peers = trust_data.keys()
            new_trusts = []
            for peer in [p for p in peers if p.id not in known_peers]:
                # this stores trust in database as well, do not get recommendations because at this point
                # we don't have correct peer list in database
                peer_trust = self.__trust_protocol.determine_and_store_initial_trust(peer, get_recommendations=False)
                new_trusts.append(peer_trust)
                # TODO: add logic when to get recommendations
                # get recommendations for this peer
                self.__recommendation_protocol.get_recommendation_for(peer, list(known_peers))
            # send only updated trusts to the network layer
            self.__bridge.send_peers_reliability({p.peer_id: p.service_trust for p in new_trusts})
        # now set update peer list in database
        self.__trust_db.store_connected_peers_list(peers)
