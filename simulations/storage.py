import json
from dataclasses import asdict
from os import listdir
from os.path import join, isfile

from dacite import from_dict

# noinspection PyUnresolvedReferences
from fides.evaluation.ti_aggregation import *
# noinspection PyUnresolvedReferences
from fides.evaluation.ti_evaluation import *
from fides.model.configuration import RecommendationsConfiguration
from fides.model.threat_intelligence import SlipsThreatIntelligence
from simulations.environment import SimulationResult
from simulations.model import SimulationConfiguration, NewPeersJoiningLater
from simulations.peer import PeerBehavior


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
        'new_peers_join_between': _serialize_peers_joining_late(cfg.new_peers_join_between),
        'recommendation_setup': asdict(cfg.recommendation_setup) if cfg.recommendation_setup else None
    }


def read_simulation(file_name: str) -> SimulationResult:
    with open(file_name, 'r') as f:
        data = json.load(f)
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
            new_peers_join_between=_deserialize_peers_joining_late(data['configuration']['new_peers_join_between']),
            recommendation_setup=from_dict(data_class=RecommendationsConfiguration, data=d)
            if (d := data['configuration']['recommendation_setup']) else None
        ),
        peer_trust_history=peer_trust_history,
        targets_history=targets,
        targets_labels=data['targets_labels'],
        peers_labels={peer_id: PeerBehavior[behavior_name] for peer_id, behavior_name in data['peers_labels'].items()}
    )


def _serialize_peers_joining_late(cfg: Optional[NewPeersJoiningLater]) -> Optional[dict]:
    if cfg is None:
        return None
    return {
        'number_of_peers_joining_late': cfg.number_of_peers_joining_late,
        'start_joining': cfg.start_joining,
        'stop_joining': cfg.stop_joining
    }


def _deserialize_peers_joining_late(d: dict) -> Optional[NewPeersJoiningLater]:
    if d is None:
        return None

    def default_selector(x):
        raise Exception('Can not deserialize peers selector! Do not replay serialized data.')

    return NewPeersJoiningLater(
        number_of_peers_joining_late=d['number_of_peers_joining_late'],
        start_joining=d['start_joining'],
        stop_joining=d['stop_joining'],
        peers_selector=default_selector
    )


def get_file_names(directory: str) -> List[str]:
    return [join(directory, f) for f in listdir(directory) if
            isfile(join(directory, f)) and not f.startswith('.') and f.endswith('.json')]
