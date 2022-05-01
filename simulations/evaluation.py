import csv
import math
from dataclasses import dataclass
from typing import Iterable, Optional, Dict

from fides.utils import bound
from simulations.environment import SimulationResult
from simulations.peer import PeerBehavior, behavioral_map


@dataclass
class SimulationEvaluation:
    simulation_id: str

    environment_group: str
    setup_label: str

    avg_target_diff: float
    avg_peers_diff: float
    avg_accumulated_trust: float

    evaluation: float


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
        avg_accumulated_trust=avg_accumulated_trust
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
