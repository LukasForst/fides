import random
from typing import List

from fides.evaluation.ti_aggregation import AverageConfidenceTIAggregation, \
    WeightedAverageConfidenceTIAggregation
from fides.evaluation.ti_evaluation import MaxConfidenceTIEvaluation, DistanceBasedTIEvaluation, ThresholdTIEvaluation
from fides.utils.logger import Logger
from simulations.environment import generate_and_run
from simulations.peer import PeerBehavior
from simulations.setup import SimulationConfiguration
from simulations.visualisation import plot_simulation_result

logger = Logger(__name__)


def sample_simulation_definitions() -> List[SimulationConfiguration]:
    peers_count = [10]
    pre_trusted_peers = [0.2]
    # [CONFIDENT_CORRECT, UNCERTAIN_PEER, CONFIDENT_INCORRECT, MALICIOUS]
    peers_distribution = [
        # CC,  UP,  CI,  MA
        [0.4, 0.2, 0.0, 0.4]
    ]

    targets = [2]
    malicious_targets = [0.5]
    malicious_peers_lie_abouts = [1.0]
    gaining_trust_periods = [50]

    simulation_lengths = [200]
    service_history_sizes = [100]
    evaluation_strategies = [
        MaxConfidenceTIEvaluation(),
        DistanceBasedTIEvaluation(),
        ThresholdTIEvaluation(threshold=0.5),
    ]
    ti_aggregation_strategies = [
        AverageConfidenceTIAggregation(),
        WeightedAverageConfidenceTIAggregation(),
        # StdevFromScoreTIAggregation()
    ]
    initial_reputations = [0.0, 0.5, 0.95]
    local_slips_acts_ass = [PeerBehavior.UNCERTAIN_PEER]

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
                for target in targets:
                    for malicious_target in malicious_targets:
                        malicious_targets_count = int(target * malicious_target)
                        being_targets_count = target - malicious_targets_count
                        for malicious_peers_lie_about in malicious_peers_lie_abouts:
                            for gaining_trust_period in gaining_trust_periods:
                                for simulation_length in simulation_lengths:
                                    for service_history_size in service_history_sizes:
                                        for evaluation_strategy in evaluation_strategies:
                                            for ti_aggregation_strategy in ti_aggregation_strategies:
                                                for initial_reputation in initial_reputations:
                                                    for local_slips_acts_as in local_slips_acts_ass:
                                                        simulation_configuration = SimulationConfiguration(
                                                            being_targets=being_targets_count,
                                                            malicious_targets=malicious_targets_count,
                                                            malicious_peers_lie_about_targets=malicious_peers_lie_about,
                                                            peers_distribution=p_distribution,
                                                            simulation_length=simulation_length,
                                                            malicious_peers_lie_since=gaining_trust_period,
                                                            service_history_size=service_history_size,
                                                            pre_trusted_peers_count=int(peer_count * pre_trusted_peer),
                                                            initial_reputation=initial_reputation,
                                                            local_slips_acts_as=local_slips_acts_as,
                                                            evaluation_strategy=evaluation_strategy,
                                                            ti_aggregation_strategy=ti_aggregation_strategy,
                                                        )
                                                        simulations.append(simulation_configuration)
    return simulations


def execute_configuration(configuration: SimulationConfiguration):
    config, peer_trust_history, targets_history = generate_and_run(configuration)

    title = f'Interaction Evaluation: {type(config.interaction_evaluation_strategy).__name__}\n' + \
            f'TI Aggregation: {type(config.ti_aggregation_strategy).__name__}\n' + \
            f'Local Slips is {configuration.local_slips_acts_as.name}\n' + \
            f'There\'re {configuration.pre_trusted_peers_count} pre-trusted peers\n' + \
            f'Peers had initial reputation of {configuration.initial_reputation}'

    plot_simulation_result(title, peer_trust_history, targets_history)


if __name__ == '__main__':
    sims = sample_simulation_definitions()
    logger.info(f"Number of simulations: {len(sims)}")
    # sims = [s for s in sims if s.initial_reputation == 0.5]
    # logger.info(f"Number of filtered simulations: {len(sims)}")

    random.shuffle(sims)
    for simulation in sims:
        execute_configuration(simulation)
