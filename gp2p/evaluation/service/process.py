from typing import Any

from gp2p.model.peer_trust_data import PeerTrustData, TrustMatrix
from gp2p.model.trust_model_configuration import TrustModelConfiguration


def process_service_interaction(
        configuration: TrustModelConfiguration,
        subject: PeerTrustData,
        matrix: TrustMatrix,
        interaction: Any
) -> TrustMatrix:
    pass
