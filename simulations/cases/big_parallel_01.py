from typing import List

from fides.evaluation.ti_aggregation import AverageConfidenceTIAggregation, \
    WeightedAverageConfidenceTIAggregation
from fides.evaluation.ti_evaluation import MaxConfidenceTIEvaluation, DistanceBasedTIEvaluation, ThresholdTIEvaluation
from fides.utils.logger import Logger
from simulations.environment import execute_all_parallel_simulation_configurations
from simulations.generators import generate_peers_distributions, generate_simulations
from simulations.model import SimulationConfiguration
from simulations.peer import PeerBehavior

logger = Logger(__name__)


def sample_simulation_definitions() -> List[SimulationConfiguration]:
    peers_count = [8]
    pre_trusted_peers = [0.0, 0.25, 0.5, 0.75]

    # CC,  UP,  CI,  MA
    peers_distribution = generate_peers_distributions()

    targets = [2]
    malicious_targets = [0.5]
    malicious_peers_lie_abouts = [1.0]
    gaining_trust_periods = [50]

    simulation_lengths = [200]
    service_history_sizes = [100, 200]
    evaluation_strategies = [
        MaxConfidenceTIEvaluation(),
        DistanceBasedTIEvaluation(),
        ThresholdTIEvaluation(threshold=0.5),
    ]
    ti_aggregation_strategies = [
        AverageConfidenceTIAggregation(),
        WeightedAverageConfidenceTIAggregation(),
    ]
    initial_reputations = [0.0, 0.5, 0.95]
    local_slips_acts_ass = [PeerBehavior.CONFIDENT_CORRECT, PeerBehavior.UNCERTAIN_PEER,
                            PeerBehavior.CONFIDENT_INCORRECT]

    return generate_simulations(evaluation_strategies, gaining_trust_periods, initial_reputations, local_slips_acts_ass,
                                malicious_peers_lie_abouts, malicious_targets, peers_count, peers_distribution,
                                pre_trusted_peers, service_history_sizes, simulation_lengths, targets,
                                ti_aggregation_strategies)


if __name__ == '__main__':
    sims = sample_simulation_definitions()
    logger.warn(f"Generated number of simulations: {len(sims)}")
    execute_all_parallel_simulation_configurations(sims, output_folder='results')
    logger.warn("Simulations done")
