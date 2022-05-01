import random
from concurrent.futures import ProcessPoolExecutor
from os import listdir
from os.path import isfile, join
from typing import Optional, List, Dict

from fides.utils.logger import Logger
from simulations.evaluation import SimulationEvaluation, evaluate_simulation
from simulations.storage import read_simulation
from simulations.utils import argmin, argmax
from simulations.visualisation import plot_simulation_result

logger = Logger(__name__)


def read_and_evaluate(file_name: str) -> Optional[SimulationEvaluation]:
    evl = None
    try:
        sim = read_simulation(file_name)
        evl = evaluate_simulation(sim)
    except Exception as ex:
        logger.error(f'Error during processing {file_name} -> {ex}')
    return evl


def process(directory: str):
    files = [join(directory, f) for f in listdir(directory) if
             isfile(join(directory, f)) and not f.startswith('.')]

    random.shuffle(files)
    files = files[:1000]

    with ProcessPoolExecutor() as executor:
        evaluations = executor.map(read_and_evaluate, files)

    evaluations = [e for e in evaluations if e]

    grouped = group_simulations_per_group(evaluations)

    for group_key, data in grouped.items():
        smallest_target_diff: SimulationEvaluation = argmin(data, lambda x: x.accumulated_target_diff)
        biggest_target_diff: SimulationEvaluation = argmax(data, lambda x: x.accumulated_target_diff)
        smallest_peers_diff: SimulationEvaluation = argmin(data, lambda x: x.accumulated_peers_diff)
        max_accumulated_trust: SimulationEvaluation = argmax(data, lambda x: x.accumulated_peer_trust)
        logger.info(
            f'Group: {group_key} '
            f'Best: {smallest_target_diff.simulation_id} '
            f'Worst: {biggest_target_diff.simulation_id}'
        )

    # s = read_simulation(join(directory, f'{m_el}.json'))
    # plot_simulation_result(s)


def group_simulations_per_group(data: List[SimulationEvaluation]) -> Dict[str, List[SimulationEvaluation]]:
    d = dict()
    for simulation in data:
        group_list = d.get(simulation.simulation_group, [])
        group_list.append(simulation)
        d[simulation.simulation_group] = group_list
    return d


if __name__ == '__main__':
    # process('results/')
    s = read_simulation('results/64e25246-df3e-4123-8848-baa7dd61106a.json')
    plot_simulation_result(s)

    s = read_simulation('results/78373f0a-da1d-4505-877e-03c6e5a14177.json')
    plot_simulation_result(s)
