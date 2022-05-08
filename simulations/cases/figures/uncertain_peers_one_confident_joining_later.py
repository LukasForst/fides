from fides.evaluation.ti_aggregation import WeightedAverageConfidenceTIAggregation
from fides.evaluation.ti_evaluation import MaxConfidenceTIEvaluation
from simulations.environment import generate_and_run
from simulations.model import SimulationConfiguration, NewPeersJoiningLater
from simulations.peer import PeerBehavior
from simulations.visualisation import plot_simulation_result

if __name__ == '__main__':
    simulation_configuration = SimulationConfiguration(
        benign_targets=1,
        malicious_targets=1,
        malicious_peers_lie_about_targets=1.0,
        peers_distribution={
            PeerBehavior.CONFIDENT_CORRECT: 1,
            PeerBehavior.UNCERTAIN_PEER: 5,
            PeerBehavior.CONFIDENT_INCORRECT: 0,
            PeerBehavior.MALICIOUS_PEER: 0,
        },
        simulation_length=200,
        malicious_peers_lie_since=25,
        service_history_size=100,
        pre_trusted_peers_count=0,
        initial_reputation=0.0,
        local_slips_acts_as=PeerBehavior.UNCERTAIN_PEER,
        evaluation_strategy=MaxConfidenceTIEvaluation(),
        ti_aggregation_strategy=WeightedAverageConfidenceTIAggregation(),
        new_peers_join_between=NewPeersJoiningLater(
            number_of_peers_joining_late=1,
            start_joining=20,
            stop_joining=100,
            peers_selector=lambda x: x.label == PeerBehavior.CONFIDENT_CORRECT
        )
    )

    result = generate_and_run(simulation_configuration)
    plot_simulation_result(result)
