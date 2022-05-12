import shutil
from typing import List

from fides.evaluation.ti_aggregation import AverageConfidenceTIAggregation, \
    WeightedAverageConfidenceTIAggregation
from fides.evaluation.ti_evaluation import MaxConfidenceTIEvaluation, DistanceBasedTIEvaluation, ThresholdTIEvaluation
from fides.utils.logger import Logger
from simulations.environment import execute_all_parallel_simulation_configurations
from simulations.evaluation import evaluate_hardness_avg_accumulated_trust, generate_peer_labels_plot
from simulations.evaluation import evaluate_hardness_avg_peers_diff
from simulations.evaluation import evaluate_hardness_avg_target_diff
from simulations.evaluation import read_and_evaluate_all_files
from simulations.generators import generate_peers_distributions, generate_simulations
from simulations.model import SimulationConfiguration
from simulations.peer import PeerBehavior
from simulations.utils import ensure_folder_created_and_clean
from simulations.visualisation import plot_hardness_evaluation_all, HardnessPlotParams

logger = Logger(__name__)


def sample_simulation_definitions() -> List[SimulationConfiguration]:
    peers_count = [8]

    # CHANGE ME for test cases in evaluation section
    # figure 6.2 [0.25]
    pre_trusted_peers = [0.25]
    # figure 8.2 [0]
    # pre_trusted_peers = [0]
    # figure 8.3 [0.5]
    # pre_trusted_peers = [0.5]

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
    output_folder = '../results/temp_test'

    ensure_folder_created_and_clean(output_folder)
    sims = sample_simulation_definitions()
    pretrusted_distribution = {s.pre_trusted_peers_count / sum(s.peers_distribution.values()) for s in sims}
    assert len(pretrusted_distribution) == 1
    pretrusted_percentage = round(pretrusted_distribution.pop() * 100)

    logger.warn(f"Generated number of simulations: {len(sims)}")
    execute_all_parallel_simulation_configurations(sims, output_folder=output_folder)
    logger.warn("Simulations done, evaluating...")

    evaluations = read_and_evaluate_all_files(output_folder)
    logger.info('Creating matrices..')

    plot_hardness_evaluation_all([
        HardnessPlotParams(
            evaluate_hardness_avg_target_diff(evaluations),
            plot_level_one_line=True,
            y_label='Target Detection Performance',
            scatter_instead_of_plot=True
        ),
        HardnessPlotParams(
            evaluate_hardness_avg_peers_diff(evaluations),
            y_label='Peer\'s Behavior Detection Performance',
            scatter_instead_of_plot=False,
            moving_mean_window=1
        ),
        HardnessPlotParams(
            evaluate_hardness_avg_accumulated_trust(evaluations),
            y_label='Peer\'s Average Trust',
            moving_mean_window=1
        ),
        HardnessPlotParams(
            generate_peer_labels_plot(evaluations),
            y_label='Percentage of Correct Peers in Network',
        )
    ],
        title=f'Performance of all setups, {pretrusted_percentage}% of PRE-TRUSTED PEERS',
        save_output=f'{pretrusted_percentage}_all_metrics.png'
    )
    # cleanup
    shutil.rmtree(output_folder)
