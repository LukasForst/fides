from gp2p.evaluation.service.interaction import Satisfaction, Weight
from gp2p.evaluation.service.peer_update import update_service_data_for_peer
from gp2p.model.peer_trust_data import PeerTrustData
from gp2p.model.service_history import ServiceHistoryRecord
from gp2p.model.trust_model_configuration import TrustModelConfiguration
from gp2p.utils.time import now


def process_service_interaction(
        configuration: TrustModelConfiguration,
        peer: PeerTrustData,
        satisfaction: Satisfaction,
        weight: Weight
) -> PeerTrustData:
    """Processes given interaction and updates trust data."""
    return update_service_data_for_peer(
        configuration=configuration,
        peer=peer,
        new_history=peer.service_history + [ServiceHistoryRecord(
            satisfaction=satisfaction.value,
            weight=weight.value,
            timestamp=now()
        )]
    )
