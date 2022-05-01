import concurrent
import random
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple

from fides.evaluation.ti_aggregation import AverageConfidenceTIAggregation, \
    WeightedAverageConfidenceTIAggregation
from fides.evaluation.ti_evaluation import MaxConfidenceTIEvaluation, DistanceBasedTIEvaluation, ThresholdTIEvaluation
from fides.utils.logger import Logger, LoggerPrintCallbacks
from simulations.environment import generate_and_run
from simulations.generators import generate_peers_distributions, generate_simulations
from simulations.peer import PeerBehavior
from simulations.setup import SimulationConfiguration
from simulations.storage import store_simulation_result

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


def execute_configuration(i: Tuple[int, SimulationConfiguration]):
    try:
        idx, configuration = i
        logger.warn(f'#{idx}/{sims_number} - executing')
        result = generate_and_run(configuration)
        store_simulation_result(f'results/{result.simulation_id}.json', result)
        logger.warn(f'#{idx}/{sims_number} - done id {result.simulation_id}')
    except Exception as ex:
        logger.error("error during execution", ex)


def log_callback(level: str, msg: str):
    if level in {'ERROR', 'WARN'}:
        print(f'{level}: {msg}\n')


if __name__ == '__main__':
    LoggerPrintCallbacks[0] = log_callback

    sims = sample_simulation_definitions()
    random.shuffle(sims)

    logger.warn(f"Number of simulations: {len(sims)}")
    sims_number = len(sims)
    enumerated_sims = [(idx, sim) for idx, sim in enumerate(sims)]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(execute_configuration, enumerated_sims)
