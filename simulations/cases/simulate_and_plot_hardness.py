import shutil
from typing import List

from fides.evaluation.ti_aggregation import AverageConfidenceTIAggregation, \
    WeightedAverageConfidenceTIAggregation
from fides.evaluation.ti_evaluation import MaxConfidenceTIEvaluation, DistanceBasedTIEvaluation, ThresholdTIEvaluation, \
    LocalCompareTIEvaluation, EvenTIEvaluation
from fides.utils.logger import Logger
from simulations.environment import execute_all_parallel_simulation_configurations
from simulations.evaluation import read_and_evaluate_all_files
from simulations.generators import generate_peers_distributions, generate_simulations
from simulations.model import SimulationConfiguration
from simulations.peer import PeerBehavior
from simulations.utils import ensure_folder_created_and_clean
from simulations.visualisation import plot_hardness_evaluation

logger = Logger(__name__)


def sample_simulation_definitions() -> List[SimulationConfiguration]:
    peers_count = [8]
    pre_trusted_peers = [0.25]

    # CC,  UP,  CI,  MA
    peers_distribution = generate_peers_distributions()

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
        LocalCompareTIEvaluation(),
        EvenTIEvaluation()
    ]
    ti_aggregation_strategies = [
        AverageConfidenceTIAggregation(),
        WeightedAverageConfidenceTIAggregation(),
    ]
    initial_reputations = [0.0, 0.5, 0.95]
    local_slips_acts_ass = [PeerBehavior.UNCERTAIN_PEER]

    return generate_simulations(evaluation_strategies, gaining_trust_periods, initial_reputations, local_slips_acts_ass,
                                malicious_peers_lie_abouts, malicious_targets, peers_count, peers_distribution,
                                pre_trusted_peers, service_history_sizes, simulation_lengths, targets,
                                ti_aggregation_strategies)


if __name__ == '__main__':
    output_folder = 'results/temp_test'

    ensure_folder_created_and_clean(output_folder)
    sims = sample_simulation_definitions()
    logger.warn(f"Generated number of simulations: {len(sims)}")
    execute_all_parallel_simulation_configurations(sims, output_folder=output_folder)
    logger.warn("Simulations done, evaluating...")

    evaluations = read_and_evaluate_all_files(output_folder)

    logger.info('Creating matrices..')

    from simulations.evaluation import evaluate_hardness_avg_target_diff

    plot_hardness_evaluation(evaluate_hardness_avg_target_diff(evaluations),
                             title_override='Performance of each interaction evaluation function ' +
                                            'with respect to the Target Detection Performance metric',
                             plot_level_one_line=True,
                             y_label='Target Detection Performance',
                             scatter_instead_of_plot=True
                             )

    from simulations.evaluation import evaluate_hardness_avg_peers_diff

    plot_hardness_evaluation(evaluate_hardness_avg_peers_diff(evaluations),
                             title_override='Performance of each interaction evaluation function ' +
                                            'with respect to the Behavior Detection Performance metric',
                             y_label='Peer\'s Behavior Detection Performance',
                             scatter_instead_of_plot=False
                             )

    # from simulations.evaluation import evaluate_hardness_evaluation
    #
    # plot_hardness_evaluation(evaluate_hardness_evaluation(evaluations),
    #                          title_override='Performance of each interaction evaluation function ' +
    #                                         'with respect to the Simulation Evaluation metric',
    #                          y_label='Simulation Evaluation',
    #                          scatter_instead_of_plot=True
    #                          )

    from simulations.evaluation import evaluate_hardness_avg_accumulated_trust

    plot_hardness_evaluation(evaluate_hardness_avg_accumulated_trust(evaluations),
                             title_override='Performance of each interaction evaluation function ' +
                                            'with respect to the Average Accumulated Trust metric',
                             y_label='Peer\'s Average Trust',
                             scatter_instead_of_plot=False
                             )

    # cleanup
    shutil.rmtree(output_folder)
