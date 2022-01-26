from typing import List

from gp2p.messaging.network_bridge import NetworkBridge
from gp2p.model.peer import PeerInfo
from gp2p.persistance.trust import TrustDatabase


class PeerListUpdateProtocol:
    """Protocol handling situations when peer list was updated."""

    def __init__(self, trust_db: TrustDatabase, bridge: NetworkBridge):
        self.__trust_db = trust_db
        self.__bridge = bridge

    def peer_list_updated(self, peers: List[PeerInfo]):
        """Processes updated peer list."""
        # first store them in the database
        self.__trust_db.store_connected_peers_list(peers)
        # and now find their trust metrics to send it to the network module
        trust_data = self.__trust_db.get_peers_trust_data([p.id for p in peers])
        # now let's check if we have all data for all peers
        if len(trust_data) == len(peers):
            # if so, we just pass back trust data
            reliability = {p.peer_id: p.service_trust for p in trust_data}
            self.__bridge.send_peers_reliability(reliability)
        else:
            # however, in case when we don't have all data, we're seeing new peers
            # TODO: implement this
            pass
