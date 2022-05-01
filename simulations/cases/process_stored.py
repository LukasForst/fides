import random
from concurrent.futures import ProcessPoolExecutor
from os import listdir
from os.path import isfile, join
from typing import Optional

from fides.utils.logger import Logger
from simulations.evaluation import SimulationEvaluation, evaluate_simulation, create_evaluation_matrix, matrix_to_csv
from simulations.storage import read_simulation

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

    logger.info(f'Evaluating {len(files)} simulations...')
    with ProcessPoolExecutor() as executor:
        evaluations = executor.map(read_and_evaluate, files)

    logger.info('Evaluation submitted to executor, creating matrix..')
    matrix = create_evaluation_matrix(evaluations)

    logger.info('Matrix ready, saving..')
    matrix_to_csv('results/matrix.csv', matrix)
    # s = read_simulation(join(directory, f'{m_el}.json'))
    # plot_simulation_result(s)


if __name__ == '__main__':
    process('../../../simulation-results-04')
    # s = read_simulation('results/64e25246-df3e-4123-8848-baa7dd61106a.json')
    # plot_simulation_result(s)
    #
    # s = read_simulation('results/78373f0a-da1d-4505-877e-03c6e5a14177.json')
    # plot_simulation_result(s)
