from dataclasses import dataclass

from fides.utils import bound
from simulations.environment import SimulationResult
from simulations.peer import PeerBehavior, behavioral_map


@dataclass
class SimulationEvaluation:
    simulation_id: str
    simulation_group: str

    accumulated_target_diff: float
    accumulated_peers_diff: float
    accumulated_peer_trust: float


def evaluate_simulation(result: SimulationResult) -> SimulationEvaluation:
    last_click = max(result.targets_history.keys())

    target_diffs = [abs(result.targets_labels[target] - ti.score)
                    for target, ti in result.targets_history[last_click].items()]
    peer_diffs = [abs(peer_label_to_mean_trust(result.peers_labels[peer]) - trust)
                  for peer, trust in result.peer_trust_history[last_click].items()]
    peer_trusts = [trust for _, trust in result.peer_trust_history[last_click].items()]

    return SimulationEvaluation(
        simulation_id=result.simulation_id,
        simulation_group=compute_group(result),
        accumulated_target_diff=sum(target_diffs),
        accumulated_peers_diff=sum(peer_diffs),
        accumulated_peer_trust=sum(peer_trusts),
    )


def peer_label_to_mean_trust(b: PeerBehavior) -> float:
    shifted = -1 if b.name in {PeerBehavior.MALICIOUS_PEER.name, PeerBehavior.CONFIDENT_INCORRECT.name} else 1
    scaled_mean = (1 + shifted * behavioral_map[b].score_mean) / 2
    return bound(scaled_mean, 0, 1)


def compute_group(result: SimulationResult) -> str:
    dist = result.simulation_config.peers_distribution
    all_peers = sum(count for _, count in result.simulation_config.peers_distribution.items())
    pretrusted_ratio = result.simulation_config.pre_trusted_peers_count / all_peers

    return f'{pretrusted_ratio}[{dist[PeerBehavior.CONFIDENT_CORRECT] / all_peers},{dist[PeerBehavior.UNCERTAIN_PEER] / all_peers},' + \
           f'{dist[PeerBehavior.CONFIDENT_INCORRECT] / all_peers},{dist[PeerBehavior.MALICIOUS_PEER] / all_peers}]' + \
           f'{result.simulation_config.local_slips_acts_as.name}'
