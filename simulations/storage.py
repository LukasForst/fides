import json
from dataclasses import asdict
from typing import Dict

from fides.model.aliases import Target, PeerId
from fides.model.threat_intelligence import SlipsThreatIntelligence
from simulations.setup import SimulationConfiguration
from simulations.utils import Click


def store_simulation_result(
        file_name: str,
        configuration: SimulationConfiguration,
        peer_trust_history: Dict[Click, Dict[PeerId, float]],
        targets_history: Dict[Click, Dict[Target, SlipsThreatIntelligence]]):
    time = list(peer_trust_history.keys())
    history_data = {}
    for click in time:
        history_data[click] = {
            'peers_trust': peer_trust_history[click],
            'targets': {target: asdict(ti) for target, ti in targets_history[click].items()}
        }

    data = {
        'configuration': _serialize_configuration(configuration),
        'data': history_data
    }
    with open(file_name, "w+") as f:
        f.write(json.dumps(data))


def _serialize_configuration(cfg: SimulationConfiguration) -> Dict:
    return {
        'benign_targets': cfg.benign_targets,
        'malicious_targets': cfg.malicious_targets,
        'peers_distribution': {behavior.name: count for behavior, count in cfg.peers_distribution.items()},
        'malicious_peers_lie_about_targets': cfg.malicious_peers_lie_about_targets,
        'simulation_length': cfg.simulation_length,
        'malicious_peers_lie_since': cfg.malicious_peers_lie_since,
        'service_history_size': cfg.service_history_size,
        'pre_trusted_peers_count': cfg.pre_trusted_peers_count,
        'initial_reputation': cfg.initial_reputation,
        'evaluation_strategy': type(cfg.evaluation_strategy).__name__,
        'ti_aggregation_strategy': type(cfg.ti_aggregation_strategy).__name__,
        'local_slips_acts_as': cfg.local_slips_acts_as.name,
        'new_peers_join_between': f'{cfg.new_peers_join_between[0]}, {cfg.new_peers_join_between[1][0]},'
                                  f' {cfg.new_peers_join_between[1][1]}' if cfg.new_peers_join_between else None,
        'recommendation_setup': asdict(cfg.recommendation_setup) if cfg.recommendation_setup else None
    }
