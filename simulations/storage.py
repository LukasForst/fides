import json
from dataclasses import asdict

from dacite import from_dict

# noinspection PyUnresolvedReferences
from fides.evaluation.ti_aggregation import *
# noinspection PyUnresolvedReferences
from fides.evaluation.ti_evaluation import *
from fides.model.configuration import RecommendationsConfiguration
from fides.model.threat_intelligence import SlipsThreatIntelligence
from simulations.environment import SimulationResult
from simulations.peer import PeerBehavior
from simulations.setup import SimulationConfiguration


def store_simulation_result(
        file_name: str,
        result: SimulationResult
):
    time = list(result.peer_trust_history.keys())
    history_data = {}
    for click in time:
        history_data[click] = {
            'peers_trust': result.peer_trust_history[click],
            'targets': {target: asdict(ti) for target, ti in result.targets_history[click].items()}
        }

    data = {
        'id': result.simulation_id,
        'configuration': _serialize_configuration(result.simulation_config),
        'data': history_data,
        'targets_labels': result.targets_labels,
        'peers_labels': {peer_id: behavior.name for peer_id, behavior in result.peers_labels.items()}
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


def read_simulation(file_name: str) -> SimulationResult:
    with open(file_name, 'r') as f:
        data = json.load(f)
    new_peers_join_between = data['configuration']['new_peers_join_between']
    if new_peers_join_between:
        count, start, end = new_peers_join_between.split(', ')
        new_peers_join_between = count, (start, end)
    peer_trust_history = {}
    targets = {}
    for click, events in data['data'].items():
        peer_trust_history[int(click)] = events['peers_trust']
        targets[int(click)] = {target: from_dict(data_class=SlipsThreatIntelligence, data=ti)
                               for target, ti in events['targets'].items()}

    return SimulationResult(
        simulation_id=file_name.split('/')[-1].replace('.json', ''),
        simulation_config=SimulationConfiguration(
            benign_targets=data['configuration']['benign_targets'],
            malicious_targets=data['configuration']['malicious_targets'],
            peers_distribution={PeerBehavior[behavior_name]: count for behavior_name, count in
                                data['configuration']['peers_distribution'].items()},
            malicious_peers_lie_about_targets=data['configuration']['malicious_peers_lie_about_targets'],
            simulation_length=data['configuration']['simulation_length'],
            malicious_peers_lie_since=data['configuration']['malicious_peers_lie_since'],
            service_history_size=data['configuration']['service_history_size'],
            pre_trusted_peers_count=data['configuration']['pre_trusted_peers_count'],
            initial_reputation=data['configuration']['initial_reputation'],
            evaluation_strategy=globals()[data['configuration']['evaluation_strategy']](),
            ti_aggregation_strategy=globals()[data['configuration']['ti_aggregation_strategy']](),
            local_slips_acts_as=PeerBehavior[data['configuration']['local_slips_acts_as']],
            new_peers_join_between=new_peers_join_between,
            recommendation_setup=from_dict(data_class=RecommendationsConfiguration, data=d)
            if (d := data['configuration']['recommendation_setup']) else None
        ),
        peer_trust_history=peer_trust_history,
        targets_history=targets,
        targets_labels=data['targets_labels'],
        peers_labels={peer_id: PeerBehavior[behavior_name] for peer_id, behavior_name in data['peers_labels'].items()}
    )
