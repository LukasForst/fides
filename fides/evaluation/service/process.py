from fides.evaluation.service.interaction import Satisfaction, Weight
from fides.evaluation.service.peer_update import update_service_data_for_peer
from fides.model.peer_trust_data import PeerTrustData
from fides.model.service_history import ServiceHistoryRecord
from fides.model.trust_model_configuration import TrustModelConfiguration
from fides.utils.logger import Logger
from fides.utils.time import now

logger = Logger(__name__)


def process_service_interaction(
        configuration: TrustModelConfiguration,
        peer: PeerTrustData,
        satisfaction: Satisfaction,
        weight: Weight
) -> PeerTrustData:
    """Processes given interaction and updates trust data."""
    # we don't update service trust for fixed trust peers
    if peer.has_fixed_trust:
        logger.debug(f"Peer {peer.peer_id} has fixed trust, not modifying.")
        return peer

    return update_service_data_for_peer(
        configuration=configuration,
        peer=peer,
        new_history=peer.service_history + [ServiceHistoryRecord(
            satisfaction=satisfaction.value,
            weight=weight.value,
            timestamp=now()
        )]
    )
