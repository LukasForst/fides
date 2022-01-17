from dataclasses import dataclass
from typing import List, Dict, Any

from global_p2p.model.aliases import PeerId


@dataclass
class Peer:
    """Identification data of a single peer in the network."""

    peer_id: PeerId
    """Unique identification of a peer in the network."""

    organizations: List[str]
    """List of organization that signed public key of this peer.
    
    According to the protocol, these are organizations that trust the peer.
    """

    metadata: Dict[str, Any]
    """Metadata that this peer provided during connection."""
