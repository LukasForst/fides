import os

from fides.evaluation.ti_aggregation import AverageConfidenceTIAggregation
from fides.evaluation.ti_evaluation import MaxConfidenceTIEvaluation
from fides.model.configuration import RecommendationsConfiguration
from simulations.environment import generate_and_run
from simulations.model import SimulationConfiguration, NewPeersJoiningLater
from simulations.peer import PeerBehavior
from simulations.storage import store_simulation_result, read_simulation
from simulations.visualisation import plot_simulation_result


def test_working_serialization():
    simulation_configuration = SimulationConfiguration(
        benign_targets=1,
        malicious_targets=1,
        malicious_peers_lie_about_targets=1.0,
        peers_distribution={
            PeerBehavior.CONFIDENT_CORRECT: 2,
            PeerBehavior.UNCERTAIN_PEER: 1,
            PeerBehavior.CONFIDENT_INCORRECT: 0,
            PeerBehavior.MALICIOUS_PEER: 1,
        },
        simulation_length=200,
        malicious_peers_lie_since=25,
        service_history_size=100,
        pre_trusted_peers_count=0,
        initial_reputation=0.0,
        local_slips_acts_as=PeerBehavior.CONFIDENT_CORRECT,
        evaluation_strategy=MaxConfidenceTIEvaluation(),
        ti_aggregation_strategy=AverageConfidenceTIAggregation(),
        new_peers_join_between=NewPeersJoiningLater(
            number_of_peers_joining_late=1,
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
    plot_simulation_result(result, save_output='original.png')

    store_simulation_result(f'{result.simulation_id}.json', result)
    sim = read_simulation(f'{result.simulation_id}.json')
    plot_simulation_result(sim, save_output='loaded.png')

    # now cleanup
    os.remove("original.png")
    os.remove("loaded.png")
    os.remove(f"{result.simulation_id}.json")
