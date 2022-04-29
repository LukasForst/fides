import random
from typing import List, Dict, Tuple

from fides.model.aliases import Target, Score, PeerId
from fides.model.configuration import TrustModelConfiguration
from fides.model.threat_intelligence import SlipsThreatIntelligence
from fides.persistance.threat_intelligence import ThreatIntelligenceDatabase
from fides.utils.logger import Logger
from simulations.generators import generate_targets, generate_peers
from simulations.peer import LocalSlipsTIDb, PeerBehavior, Peer, behavioral_map
from simulations.setup import SimulationConfiguration
from simulations.time_environment import TimeEnvironment
from simulations.utils import build_config, FidesSetup, Click, PreTrustedPeer
from tests.load_fides import get_fides_stream

logger = Logger(__name__)


def generate_and_run(simulation_config: SimulationConfiguration) -> Tuple[
    TrustModelConfiguration, Dict[Click, Dict[PeerId, float]], Dict[Click, Dict[Target, SlipsThreatIntelligence]]
]:
    targets = generate_targets(being=simulation_config.being_targets, malicious=simulation_config.malicious_targets)
    malicious_lie_about = list(targets.keys())
    random.shuffle(malicious_lie_about)
    malicious_lie_about = malicious_lie_about[: int(len(targets) * simulation_config.malicious_peers_lie_about_targets)]

    other_peers = generate_peers(
        service_history_size=simulation_config.service_history_size,
        recommendation_history_size=simulation_config.service_history_size,
        distribution=simulation_config.peers_distribution,
        malicious_lie_about=malicious_lie_about,
        malicious_start_lie_at=simulation_config.malicious_peers_lie_since
    )

    ti_db = LocalSlipsTIDb(
        target_baseline=targets,
        behavior=behavioral_map[simulation_config.local_slips_acts_as]
    )
    config = build_config(FidesSetup(
        default_reputation=simulation_config.initial_reputation,
        pretrusted_peers=[PreTrustedPeer(p.peer_info.id, 0.95)
                          for p in other_peers if p.label == PeerBehavior.CONFIDENT_CORRECT
                          ][:simulation_config.pre_trusted_peers_count],
        evaluation_strategy=simulation_config.evaluation_strategy,
        ti_aggregation_strategy=simulation_config.ti_aggregation_strategy,
        service_history_max_size=simulation_config.service_history_size,
        recommendations_setup=simulation_config.recommendation_setup
    ))

    random.shuffle(other_peers)
    if simulation_config.new_peers_join_between:
        late_joining_peers_count, (start_joining, stop_joining) = simulation_config.new_peers_join_between
        pretrusted_peers_ids = {p.id for p in config.trusted_peers}
        late_joining_peers = [p for p in other_peers
                              if p.peer_info.id not in pretrusted_peers_ids][:late_joining_peers_count]
        for peer in late_joining_peers:
            peer.network_joining_epoch = random.randint(start_joining, stop_joining)

    peer_trust_history, targets_history = run_simulation(
        config=config,
        local_ti_db=ti_db,
        targets=targets,
        other_peers=other_peers,
        simulation_time=simulation_config.simulation_length
    )
    return config, peer_trust_history, targets_history


def run_simulation(
        config: TrustModelConfiguration,
        local_ti_db: ThreatIntelligenceDatabase,
        targets: Dict[Target, Score],
        other_peers: List[Peer],
        simulation_time: Click
) -> (Dict[Click, Dict[PeerId, float]], Dict[Click, Dict[Target, SlipsThreatIntelligence]]):
    fides, stream, ti = get_fides_stream(config=config, ti_db=local_ti_db)

    env = TimeEnvironment(fides=fides, fides_stream=stream, other_peers=other_peers, targets=targets)

    peer_trust_history: Dict[Click, Dict[PeerId, float]] = {}
    targets_history: Dict[Click, Dict[Target, SlipsThreatIntelligence]] = {}

    def epoch_callback(click: Click):
        peer_trust_history[click] = {}
        targets_history[click] = {}

        for peer in other_peers:
            maybe_trust = fides.trust_db.get_peer_trust_data(peer.peer_info.id)

            peer_trust_history[click][peer.peer_info.id] = maybe_trust.service_trust if maybe_trust else None

        for target in targets.keys():
            targets_history[click][target] = ti[target]

    env.run(simulation_time, epoch_callback=epoch_callback)

    return peer_trust_history, targets_history
