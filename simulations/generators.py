import random
from typing import Dict, List

from fides.model.aliases import Target, Score
from fides.model.peer import PeerInfo
from fides.utils.logger import Logger
from simulations.model import SimulationConfiguration
from simulations.peer import PeerBehavior, Peer, ConfidentCorrectPeer, UncertainPeer, ConfidentIncorrectPeer, \
    MaliciousPeer
from simulations.utils import Click

logger = Logger(__name__)


def generate_simulations(evaluation_strategies, gaining_trust_periods, initial_reputations, local_slips_acts_ass,
                         malicious_peers_lie_abouts, malicious_targets, peers_count, peers_distribution,
                         pre_trusted_peers, service_history_sizes, simulation_lengths, targets,
                         ti_aggregation_strategies):
    ns = len(peers_count) * len(peers_distribution) * len(pre_trusted_peers) * len(targets) * \
         len(malicious_targets) * len(malicious_peers_lie_abouts) * \
         len(gaining_trust_periods) * len(simulation_lengths) * len(service_history_sizes) * \
         len(evaluation_strategies) * len(ti_aggregation_strategies) * \
         len(initial_reputations) * len(local_slips_acts_ass)
    logger.warn(f'Number of combinations for parameters: {ns}')
    simulations = []
    for peer_count in peers_count:
        for distribution in peers_distribution:
            p_distribution = {
                PeerBehavior.CONFIDENT_CORRECT: round(distribution[0] * peer_count),
                PeerBehavior.UNCERTAIN_PEER: round(distribution[1] * peer_count),
                PeerBehavior.CONFIDENT_INCORRECT: round(distribution[2] * peer_count),
                PeerBehavior.MALICIOUS_PEER: round(distribution[3] * peer_count)
            }
            p_distribution[PeerBehavior.UNCERTAIN_PEER] = \
                peer_count - p_distribution[PeerBehavior.CONFIDENT_CORRECT] - \
                p_distribution[PeerBehavior.CONFIDENT_INCORRECT] - \
                p_distribution[PeerBehavior.MALICIOUS_PEER]
            for pre_trusted_peer in pre_trusted_peers:
                if pre_trusted_peer > distribution[0]:
                    continue
                for target in targets:
                    for malicious_target in malicious_targets:
                        malicious_targets_count = int(target * malicious_target)
                        benign_targets_count = target - malicious_targets_count
                        for malicious_peers_lie_about in malicious_peers_lie_abouts:
                            for gaining_trust_period in gaining_trust_periods:
                                for simulation_length in simulation_lengths:
                                    for service_history_size in service_history_sizes:
                                        for evaluation_strategy in evaluation_strategies:
                                            for ti_aggregation_strategy in ti_aggregation_strategies:
                                                for initial_reputation in initial_reputations:
                                                    for local_slips_acts_as in local_slips_acts_ass:
                                                        simulation_configuration = SimulationConfiguration(
                                                            benign_targets=benign_targets_count,
                                                            malicious_targets=malicious_targets_count,
                                                            malicious_peers_lie_about_targets=malicious_peers_lie_about,
                                                            peers_distribution=p_distribution,
                                                            simulation_length=simulation_length,
                                                            malicious_peers_lie_since=gaining_trust_period,
                                                            service_history_size=service_history_size,
                                                            pre_trusted_peers_count=round(
                                                                peer_count * pre_trusted_peer),
                                                            initial_reputation=initial_reputation,
                                                            local_slips_acts_as=local_slips_acts_as,
                                                            evaluation_strategy=evaluation_strategy,
                                                            ti_aggregation_strategy=ti_aggregation_strategy,
                                                        )
                                                        simulations.append(simulation_configuration)
    random.shuffle(simulations)
    return simulations


def generate_peers_distributions() -> List[List[float]]:
    # [CONFIDENT_CORRECT, UNCERTAIN_PEER, CONFIDENT_INCORRECT, MALICIOUS]

    sample = {
        'cc': [0.0, 0.25, 0.5, 0.75],
        'up': [0.0, 0.25, 0.5, 0.75],
        'ci': [0.0, 0.25, 0.5, 0.75],
        'ma': [0.0, 0.25, 0.5, 0.75],
    }
    data = []

    def append_if_possible(r, value) -> bool:
        if sum(r) + value <= 1:
            r.append(value)
            return True
        else:
            return False

    for cc in sample['cc']:
        row = [cc]
        for up in sample['up']:
            if not append_if_possible(row, up):
                continue
            for ci in sample['ci']:
                if not append_if_possible(row, ci):
                    continue
                for ma in sample['ma']:
                    if not append_if_possible(row, ma):
                        continue
                    if sum(row) == 1:
                        data.append(row)
                    row = row[:-1]
                row = row[:-1]
            row = row[:-1]
    return data


def generate_targets(benign: int, malicious: int) -> Dict[Target, Score]:
    benign = [(f"BENIGN #{i}", 1) for i in range(benign)]
    malicious = [(f"MALICIOUS #{i}", -1) for i in range(malicious)]

    all_targets = benign + malicious

    random.shuffle(all_targets)
    return {target: score for (target, score) in all_targets}


def generate_peers(
        service_history_size: int,
        recommendation_history_size: int,
        distribution: Dict[PeerBehavior, int],
        malicious_lie_about: List[Target],
        malicious_start_lie_at: Click
) -> List[Peer]:
    peers = []

    for idx, (peer_type, count) in enumerate(distribution.items()):
        if peer_type == PeerBehavior.CONFIDENT_CORRECT:
            p = [ConfidentCorrectPeer(PeerInfo(f"CONFIDENT_CORRECT #{i}", []), service_history_size,
                                      recommendation_history_size)
                 for i in range(count)]
        elif peer_type == PeerBehavior.UNCERTAIN_PEER:
            p = [UncertainPeer(PeerInfo(f"UNCERTAIN_PEER #{i}", []), service_history_size, recommendation_history_size)
                 for i in range(count)]
        elif peer_type == PeerBehavior.CONFIDENT_INCORRECT:
            p = [ConfidentIncorrectPeer(PeerInfo(f"CONFIDENT_INCORRECT #{i}", []), service_history_size,
                                        recommendation_history_size)
                 for i in range(count)]
        elif peer_type == PeerBehavior.MALICIOUS_PEER:
            p = [MaliciousPeer(
                PeerInfo(f"MALICIOUS_PEER #{i}", []),
                service_history_size, recommendation_history_size, malicious_lie_about, malicious_start_lie_at)
                for i in range(count)]
        else:
            raise ValueError()

        peers.extend(p)

    random.shuffle(peers)
    return peers
