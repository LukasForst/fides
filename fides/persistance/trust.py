from typing import List, Optional, Union

from fides.messaging.model import PeerInfo
from fides.model.aliases import PeerId, Target
from fides.model.peer_trust_data import PeerTrustData, TrustMatrix
from fides.model.threat_intelligence import ThreatIntelligence
from fides.model.trust_model_configuration import TrustModelConfiguration


class TrustDatabase:
    """Class responsible for persisting data for trust model."""

    def store_model_configuration(self, configuration: TrustModelConfiguration):
        """Stores trust model configuration."""
        raise NotImplemented()

    def get_model_configuration(self) -> TrustModelConfiguration:
        """Returns current trust model configuration if set."""
        raise NotImplemented()

    def store_connected_peers_list(self, current_peers: List[PeerInfo]):
        """Stores list of peers that are directly connected to the Slips."""
        raise NotImplemented()

    def get_connected_peers(self) -> List[PeerInfo]:
        """Returns list of peers that are directly connected to the Slips."""
        raise NotImplemented()

    def store_peer_trust_data(self, trust_data: PeerTrustData):
        """Stores trust data for given peer - overwrites any data if existed."""
        raise NotImplemented()

    def store_peer_trust_matrix(self, trust_matrix: TrustMatrix):
        """Stores trust matrix."""
        for peer in trust_matrix.values():
            self.store_peer_trust_data(peer)

    def get_peer_trust_data(self, peer: Union[PeerId, PeerInfo]) -> Optional[PeerTrustData]:
        """Returns trust data for given peer ID, if no data are found, returns None."""
        raise NotImplemented()

    def get_peers_trust_data(self, peer_ids: List[Union[PeerId, PeerInfo]]) -> TrustMatrix:
        """Return trust data for each peer from peer_ids."""
        return {peer_id: self.get_peer_trust_data(peer_id) for peer_id in peer_ids}

    def cache_network_opinion(self, target: Target, intelligence: ThreatIntelligence):
        """Caches aggregated opinion on given target."""
        raise NotImplemented()

    def get_cached_network_opinion(self, target: Target) -> Optional[ThreatIntelligence]:
        """Returns cached network opinion. Checks cache time and returns None if data expired."""
        raise NotImplemented()
