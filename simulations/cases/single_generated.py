from fides.evaluation.ti_aggregation import AverageConfidenceTIAggregation
from fides.evaluation.ti_evaluation import MaxConfidenceTIEvaluation
from fides.model.configuration import RecommendationsConfiguration
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
            PeerBehavior.CONFIDENT_CORRECT: 5,
            PeerBehavior.UNCERTAIN_PEER: 5,
            PeerBehavior.CONFIDENT_INCORRECT: 1,
            PeerBehavior.MALICIOUS_PEER: 0,
        },
        simulation_length=200,
        malicious_peers_lie_since=25,
        service_history_size=100,
        pre_trusted_peers_count=2,
        initial_reputation=0.0,
        local_slips_acts_as=PeerBehavior.CONFIDENT_CORRECT,
        # evaluation_strategy=LocalCompareTIEvaluation(),
        evaluation_strategy=MaxConfidenceTIEvaluation(),
        # evaluation_strategy=DistanceBasedTIEvaluation(),
        # evaluation_strategy=ThresholdTIEvaluation(threshold=0.5),
        # evaluation_strategy=EvenTIEvaluation(),
        ti_aggregation_strategy=AverageConfidenceTIAggregation(),
        # ti_aggregation_strategy=WeightedAverageConfidenceTIAggregation(),
        # ti_aggregation_strategy=StdevFromScoreTIAggregation(),
        new_peers_join_between=(2, (10, 50)),
        recommendation_setup=RecommendationsConfiguration(
            enabled=False,
            only_connected=False,
            only_preconfigured=True,
            required_trusted_peers_count=1,
            trusted_peer_threshold=0.5,
            peers_max_count=1,
            history_max_size=10
        )
    )

    config, peer_trust_history, targets_history = generate_and_run(simulation_configuration)
    title = f'Interaction Evaluation: {type(config.interaction_evaluation_strategy).__name__}\n' + \
            f'TI Aggregation: {type(config.ti_aggregation_strategy).__name__}\n' + \
            f'Local Slips is {simulation_configuration.local_slips_acts_as.name}\n' + \
            f'There\'re {simulation_configuration.pre_trusted_peers_count} pre-trusted peers\n' + \
            f'Peers had initial reputation of {simulation_configuration.initial_reputation}'

    plot_simulation_result(title, simulation_configuration, peer_trust_history, targets_history)


if __name__ == '__main__':
    run()
