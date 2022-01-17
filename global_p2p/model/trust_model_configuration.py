from dataclasses import dataclass


@dataclass
class TrustModelConfiguration:
    service_history_max_size: int
    """Maximal size of Service History.
    
    In model's notation sh_max.
    """
