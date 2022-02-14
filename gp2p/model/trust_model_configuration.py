from dataclasses import dataclass
from typing import List

from gp2p.model.aliases import OrganisationId


@dataclass
class TrustedOrganisation:
    identifier: OrganisationId
    """Unique identifier for the organisation."""

    trust: float
    """Initial trust for the organisation.

    If, "enforce_trust = false" this value will change during time as the instance has more interactions with
    organisation nodes. If "enforce_trust = true", the trust for all peers from this organisation will remain 
    the same. 
    """
    enforce_trust: bool
    """If true, organisation nodes will have always initial trust."""


@dataclass
class TrustModelConfiguration:
    service_history_max_size: int
    """Maximal size of Service History.
    
    In model's notation sh_max.
    """

    recommending_peers_max_count: int
    """Maximal count of peers that are asked to give recommendations on a peer.
    
    In model's notation η_max.
    """

    recommendation_history_max_size: int
    """Maximal size of Recommendation History.
    
    In model's notation rh_max.
    """

    trusted_organisations: List[TrustedOrganisation]
    """List of preconfigured organisations."""
