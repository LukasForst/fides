from fides.evaluation.ti_aggregation import AverageConfidenceTIAggregation
from fides.evaluation.ti_evaluation import LocalCompareTIEvaluation
from fides.model.configuration import RecommendationsConfiguration
from fides.utils.logger import Logger
from simulations.environment import generate_and_run
from simulations.model import SimulationConfiguration, NewPeersJoiningLater
from simulations.peer import PeerBehavior
from simulations.visualisation import plot_simulation_result

logger = Logger(__name__)

if __name__ == '__main__':
    simulation_configuration = SimulationConfiguration(
        benign_targets=1,
        malicious_targets=1,
        malicious_peers_lie_about_targets=1.0,
        peers_distribution={
            PeerBehavior.CONFIDENT_CORRECT: 1,
            PeerBehavior.UNCERTAIN_PEER: 0,
            PeerBehavior.CONFIDENT_INCORRECT: 0,
            PeerBehavior.MALICIOUS_PEER: 0,
        },
        simulation_length=200,
        malicious_peers_lie_since=25,
        service_history_size=100,
        pre_trusted_peers_count=0,
        initial_reputation=0.0,
        local_slips_acts_as=PeerBehavior.CONFIDENT_CORRECT,
        evaluation_strategy=LocalCompareTIEvaluation(),
        # evaluation_strategy=MaxConfidenceTIEvaluation(),
        # evaluation_strategy=DistanceBasedTIEvaluation(),
        # evaluation_strategy=ThresholdTIEvaluation(threshold=0.5),
        # evaluation_strategy=EvenTIEvaluation(),
        ti_aggregation_strategy=AverageConfidenceTIAggregation(),
        # ti_aggregation_strategy=WeightedAverageConfidenceTIAggregation(),
        # ti_aggregation_strategy=StdevFromScoreTIAggregation(),
        new_peers_join_between=NewPeersJoiningLater(
            number_of_peers_joining_late=0,
            start_joining=20,
            stop_joining=50,
            peers_selector=lambda x: x.label == PeerBehavior.CONFIDENT_CORRECT
        ),
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

    result = generate_and_run(simulation_configuration)
    plot_simulation_result(result)
