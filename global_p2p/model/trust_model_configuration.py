from dataclasses import dataclass


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
