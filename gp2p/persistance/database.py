from typing import List, Optional

from gp2p.messaging.model import PeerInfo
from gp2p.model.aliases import PeerId, Target
from gp2p.model.peer_trust_data import PeerTrustData
from gp2p.model.threat_intelligence import ThreatIntelligence
from gp2p.model.trust_model_configuration import TrustModelConfiguration


class TrustDatabase:
    """Class responsible for persisting data for trust model."""

    def store_model_configuration(self, configuration: TrustModelConfiguration):
        """Stores trust model configuration."""
        raise NotImplemented()

    def get_model_configuration(self) -> Optional[TrustModelConfiguration]:
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

    def get_peer_trust_data(self, peer_id: PeerId) -> Optional[PeerTrustData]:
        """Returns trust data for given peer ID, if no data are found, returns None."""
        raise NotImplemented()

    def cache_network_opinion(self, target: Target, intelligence: ThreatIntelligence):
        """Caches aggregated opinion on given target."""
        raise NotImplemented()

    def get_cached_network_opinion(self, target: Target) -> Optional[ThreatIntelligence]:
        """Returns cached network opinion. Checks cache time and returns None if data expired."""
        raise NotImplemented()
