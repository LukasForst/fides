from fides.evaluation.ti_aggregation import StdevFromScoreTIAggregation
from fides.evaluation.ti_evaluation import MaxConfidenceTIEvaluation
from fides.utils.logger import Logger
from simulations.environment import generate_and_run
from simulations.peer import PeerBehavior
from simulations.setup import SimulationConfiguration
from simulations.visualisation import plot_simulation_result

logger = Logger(__name__)


def run():
    simulation_configuration = SimulationConfiguration(
        being_targets=1,
        malicious_targets=1,
        malicious_peers_lie_about_targets=1.0,
        peers_distribution={
            PeerBehavior.CONFIDENT_CORRECT: 2,
            PeerBehavior.UNCERTAIN_PEER: 0,
            PeerBehavior.CONFIDENT_INCORRECT: 0,
            PeerBehavior.MALICIOUS_PEER: 1,
        },
        simulation_length=200,
        malicious_peers_lie_since=50,
        service_history_size=100,
        pre_trusted_peers_count=0,
        initial_reputation=0.5,
        local_slips_acts_as=PeerBehavior.CONFIDENT_CORRECT,
        # evaluation_strategy=LocalCompareTIEvaluation(),
        evaluation_strategy=MaxConfidenceTIEvaluation(),
        # evaluation_strategy=DistanceBasedTIEvaluation(),
        # evaluation_strategy=ThresholdTIEvaluation(threshold=0.5),
        # evaluation_strategy=EvenTIEvaluation(),
        # ti_aggregation_strategy=AverageConfidenceTIAggregation(),
        # ti_aggregation_strategy=WeightedAverageConfidenceTIAggregation(),
        ti_aggregation_strategy=StdevFromScoreTIAggregation(),
    )

    config, peer_trust_history, targets_history = generate_and_run(simulation_configuration)
    title = f'{type(config.interaction_evaluation_strategy).__name__}  +  ' + \
            f'{type(config.ti_aggregation_strategy).__name__}'

    plot_simulation_result(title, peer_trust_history, targets_history)


if __name__ == '__main__':
    run()
