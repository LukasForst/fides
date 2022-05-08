import csv
import json
import math
import random
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Iterable, Optional, Dict, Callable, List

from fides.utils import bound
from fides.utils.logger import Logger
from simulations.environment import SimulationResult
from simulations.peer import PeerBehavior, behavioral_map
from simulations.storage import read_simulation, get_file_names

logger = Logger(__name__)


@dataclass
class SimulationEvaluation:
    simulation_id: str

    environment_group: str
    setup_label: str

    avg_target_diff: float
    avg_peers_diff: float
    avg_accumulated_trust: float

    evaluation: float
    env_hardness: float


# (environment_group, (setup_label, evaluation))
SimulationEvaluationMatrix = Dict[str, Dict[str, SimulationEvaluation]]


def create_evaluation_matrix(evaluations: Iterable[Optional[SimulationEvaluation]]) -> SimulationEvaluationMatrix:
    matrix = dict()
    for ev in evaluations:
        if ev is None:
            continue
        labels = matrix.get(ev.environment_group, dict())
        labels[ev.setup_label] = ev
        matrix[ev.environment_group] = labels

    # noinspection PyTypeChecker
    return matrix


HardnessEvaluationMatrix = Dict[str, Dict[float, float]]


def evaluate_hardness_avg_peers_diff(evaluations: Iterable[Optional[SimulationEvaluation]]) \
        -> HardnessEvaluationMatrix:
    return evaluate_hardness(evaluations, lambda ev, current: min(ev.avg_peers_diff, current if current else math.inf))


def evaluate_hardness_avg_target_diff(evaluations: Iterable[Optional[SimulationEvaluation]]) \
        -> HardnessEvaluationMatrix:
    return evaluate_hardness(evaluations, lambda ev, current: min(ev.avg_target_diff, current if current else math.inf))


def evaluate_hardness_avg_accumulated_trust(evaluations: Iterable[Optional[SimulationEvaluation]]) \
        -> HardnessEvaluationMatrix:
    return evaluate_hardness(evaluations,
                             lambda ev, current: max(ev.avg_accumulated_trust, current if current else -math.inf))


def evaluate_hardness_evaluation(evaluations: Iterable[Optional[SimulationEvaluation]]) -> HardnessEvaluationMatrix:
    return evaluate_hardness(evaluations, lambda ev, current: min(ev.evaluation, current if current else math.inf))


def evaluate_hardness(evaluations: Iterable[Optional[SimulationEvaluation]],
                      selector: Callable[[SimulationEvaluation, float], float]) -> HardnessEvaluationMatrix:
    matrix = dict()
    for ev in evaluations:
        if ev is None:
            continue
        hardnesses = matrix.get(ev.setup_label, dict())
        current = hardnesses.get(ev.env_hardness, None)
        hardnesses[ev.env_hardness] = selector(ev, current)
        matrix[ev.setup_label] = hardnesses

    return matrix


def generate_peer_labels_plot(evaluations: Iterable[Optional[SimulationEvaluation]]) -> HardnessEvaluationMatrix:
    matrix = dict()
    for ev in evaluations:
        if ev is None:
            continue

        dis = json.loads(ev.environment_group.split('|')[1])

        cc = matrix.get(ev.setup_label, dict())
        cc[ev.env_hardness] = dis[0] * 100
        matrix[ev.setup_label] = cc

    return matrix


def evaluate_simulation(result: SimulationResult, weight: float = 0.7) -> SimulationEvaluation:
    last_click = max(result.targets_history.keys())

    target_diffs = [abs(result.targets_labels[target] - ti.score)
                    for target, ti in result.targets_history[last_click].items()]
    peer_diffs = [abs(peer_label_to_mean_trust(result.peers_labels[peer]) - trust)
                  for peer, trust in result.peer_trust_history[last_click].items()]

    accumulated_peer_trust = [trust for _, trust in result.peer_trust_history[last_click].items()]

    avg_target_diff = sum(target_diffs) / len(target_diffs)
    avg_peers_diff = sum(peer_diffs) / len(peer_diffs)
    avg_accumulated_trust = sum(accumulated_peer_trust) / len(accumulated_peer_trust)
    return SimulationEvaluation(
        simulation_id=result.simulation_id,
        environment_group=compute_group(result),
        setup_label=compute_label(result),
        avg_target_diff=avg_target_diff,
        avg_peers_diff=avg_peers_diff,
        evaluation=weight * avg_target_diff + (1 - weight) * avg_peers_diff,
        avg_accumulated_trust=avg_accumulated_trust,
        env_hardness=env_hardness(result)
    )


def peer_label_to_mean_trust(b: PeerBehavior) -> float:
    shifted = -1 if b.name in {PeerBehavior.MALICIOUS_PEER.name, PeerBehavior.CONFIDENT_INCORRECT.name} else 1
    scaled_mean = (1 + shifted * behavioral_map[b].score_mean) / 2
    return bound(scaled_mean, 0, 1)


def compute_group(result: SimulationResult) -> str:
    dist = result.simulation_config.peers_distribution
    all_peers = sum(count for _, count in result.simulation_config.peers_distribution.items())
    pretrusted_ratio = result.simulation_config.pre_trusted_peers_count / all_peers

    return f'{pretrusted_ratio}|[{dist[PeerBehavior.CONFIDENT_CORRECT] / all_peers},' \
           f'{dist[PeerBehavior.UNCERTAIN_PEER] / all_peers},' + \
           f'{dist[PeerBehavior.CONFIDENT_INCORRECT] / all_peers},{dist[PeerBehavior.MALICIOUS_PEER] / all_peers}]|' + \
           f'{result.simulation_config.local_slips_acts_as.name}'


def compute_label(result: SimulationResult) -> str:
    e = type(result.simulation_config.evaluation_strategy).__name__
    a = type(result.simulation_config.ti_aggregation_strategy).__name__
    rep = result.simulation_config.initial_reputation
    return f'{e}|{a}|{rep}'


# # Hardness based on accumulated trust
# def env_hardness(result: SimulationResult) -> float:
#     environment_mean_trust = sum(peer_label_to_mean_trust(label) for _, label in result.peers_labels.items())
#     local_slips = peer_label_to_mean_trust(result.simulation_config.local_slips_acts_as)
#     pretrusted_peers = 0.95 * result.simulation_config.pre_trusted_peers_count
#
#     d = environment_mean_trust + local_slips + pretrusted_peers
#     return round(d, 5)

# Hardness based on percentage of confident correct peers in the network
def env_hardness(result: SimulationResult) -> float:
    all_confident_correct_count = sum(
        1 for _, label in result.peers_labels.items() if label == PeerBehavior.CONFIDENT_CORRECT
    )
    all_uncertain_count = sum(
        1 for _, label in result.peers_labels.items() if label == PeerBehavior.UNCERTAIN_PEER
    )
    all_peers = len(result.peers_labels.items())
    conf = (all_confident_correct_count / all_peers) * 10
    unc = all_uncertain_count / all_peers
    return round(conf + unc, 2)


# # Hardness based on discrete values for each behavior
# def env_hardness(result: SimulationResult) -> float:
#     environment_mean_trust = sum(hardness_for_peer_label(label) for _, label in result.peers_labels.items())
#     local_slips = hardness_for_peer_label(result.simulation_config.local_slips_acts_as)
#     pretrusted_peers = 10 * result.simulation_config.pre_trusted_peers_count
#
#     d = environment_mean_trust + local_slips + pretrusted_peers
#     return round(d, 5)


def hardness_for_peer_label(label: PeerBehavior) -> float:
    return {
        PeerBehavior.CONFIDENT_CORRECT.name: 100,
        PeerBehavior.UNCERTAIN_PEER.name: 30,
        PeerBehavior.CONFIDENT_INCORRECT.name: 5,
        PeerBehavior.MALICIOUS_PEER.name: 0
    }[label.name]


# noinspection PyTypeChecker
def matrix_to_csv(file_name: str, matrix: SimulationEvaluationMatrix):
    all_environment_groups = list(matrix.keys())
    all_setup_labels = list(matrix[all_environment_groups[0]].keys())

    with open(file_name, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(
            ['hash', 'pretrusted_ratio', 'behavior_distribution', 'local_slips'] + \
            all_setup_labels + \
            ['best_hash', 'best_evaluation_strategy', 'best_ti_aggregation', 'best_initial_reputation',
             'best_avg_target_diff', 'avg_peers_diff', 'avg_accumulated_trust', 'best_id'])

        for group in all_environment_groups:
            best_eval, best_label = math.inf, None
            row = [group] + group.split('|')
            for label in all_setup_labels:
                val = matrix[group][label]
                row.append(val.evaluation)

                if val.evaluation < best_eval:
                    best_eval, best_label = val.evaluation, label

            best_result = matrix[group][best_label]
            evaluation_strategy, ti_aggregation, initial_reputation = best_result.setup_label.split('|')
            row.extend([best_result.setup_label,
                        evaluation_strategy,
                        ti_aggregation,
                        initial_reputation,
                        best_result.avg_target_diff,
                        best_result.avg_peers_diff,
                        best_result.avg_accumulated_trust,
                        best_result.simulation_id])
            writer.writerow(row)


def read_and_evaluate_all_files(directory: str) -> List[SimulationEvaluation]:
    files = get_file_names(directory)
    logger.info(f'Evaluating {len(files)} simulations...')
    random.shuffle(files)
    with ProcessPoolExecutor() as executor:
        evaluations = executor.map(read_and_evaluate, files)
    logger.info(f'Evaluation finished.')
    return [e for e in evaluations if e]


def read_and_evaluate(file_name: str) -> Optional[SimulationEvaluation]:
    evl = None
    try:
        sim = read_simulation(file_name)
        evl = evaluate_simulation(sim)
    except Exception as ex:
        print(f'Error during processing {file_name} -> {ex}')
    return evl
