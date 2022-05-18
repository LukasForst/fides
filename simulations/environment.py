import random
import uuid
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Tuple

from fides.model.aliases import Target, Score, PeerId
from fides.model.configuration import TrustModelConfiguration
from fides.model.threat_intelligence import SlipsThreatIntelligence
from fides.persistence.threat_intelligence import ThreatIntelligenceDatabase
from fides.utils.logger import Logger
from simulations.generators import generate_targets, generate_peers
from simulations.model import SimulationConfiguration, PreTrustedPeer, FidesSetup, SimulationResult
from simulations.peer import LocalSlipsTIDb, PeerBehavior, Peer, behavioral_map
from simulations.setup import build_config
from simulations.storage import store_simulation_result
from simulations.time_environment import TimeEnvironment
from simulations.utils import print_only_error_warn, Click
from tests.load_fides import get_fides_stream

logger = Logger(__name__)


def execute_all_parallel_simulation_configurations(configs: List[SimulationConfiguration], output_folder: str):
    sims_number = len(configs)
    logger.warn(f"About to execute: {sims_number} of simulations.")
    enumerated_sims = [(idx, sims_number, output_folder, sim) for idx, sim in enumerate(configs, start=1)]
    with ProcessPoolExecutor() as executor:
        executor.map(execute_parallel_simulation_configuration, enumerated_sims)
    logger.warn(f"Executed {sims_number} simulations.")


def execute_parallel_simulation_configuration(i: Tuple[int, int, str, SimulationConfiguration]):
    try:
        print_only_error_warn()
        idx, total_simulations, folder_with_results, configuration = i
        percentage_done = round((idx / total_simulations) * 100)
        result = generate_and_run(configuration)
        store_simulation_result(f'{folder_with_results}/{result.simulation_id}.json', result)
        logger.warn(f'{idx}/{total_simulations} - {percentage_done}% - done with ID {result.simulation_id}')
    except Exception as ex:
        logger.error("Error during execution", ex)


def generate_and_run(simulation_config: SimulationConfiguration) -> SimulationResult:
    targets = generate_targets(benign=simulation_config.benign_targets, malicious=simulation_config.malicious_targets)
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
        cfg = simulation_config.new_peers_join_between
        late_joining_peers = [p for p in other_peers
                              if cfg.peers_selector(p)][:cfg.number_of_peers_joining_late]
        for peer in late_joining_peers:
            peer.network_joining_epoch = random.randint(cfg.start_joining, cfg.stop_joining)

    peer_trust_history, targets_history = run_simulation(
        config=config,
        local_ti_db=ti_db,
        targets=targets,
        other_peers=other_peers,
        simulation_time=simulation_config.simulation_length
    )
    peers_labels = {p.peer_info.id: p.label for p in other_peers}
    return SimulationResult(str(uuid.uuid4()), simulation_config, peer_trust_history, targets_history, targets,
                            peers_labels)


def run_simulation(
        config: TrustModelConfiguration,
        local_ti_db: ThreatIntelligenceDatabase,
        targets: Dict[Target, Score],
        other_peers: List[Peer],
        simulation_time: Click
) -> (Dict[Click, Dict[PeerId, float]], Dict[Click, Dict[Target, SlipsThreatIntelligence]]):
    fides, stream, ti = get_fides_stream(config=config, ti_db=local_ti_db)

    env = TimeEnvironment(fides=fides, fides_stream=stream, other_peers=other_peers, targets=targets,
                          enable_messages_processing=config.recommendations.enabled)

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
