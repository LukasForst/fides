from dataclasses import dataclass
from typing import List

from gp2p.model.aliases import PeerId, OrganisationId


@dataclass
class PeerInfo:
    """Identification data of a single peer in the network."""

    id: PeerId
    """Unique identification of a peer in the network."""

    organisations: List[OrganisationId]
    """List of organization that signed public key of this peer.
    According to the protocol, these are organizations that trust the peer.
    """
