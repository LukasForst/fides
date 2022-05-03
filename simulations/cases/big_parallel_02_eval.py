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
             isfile(join(directory, f)) and not f.startswith('.') and f.endswith('.json')]

    random.shuffle(files)

    logger.info(f'Evaluating {len(files)} simulations...')
    with ProcessPoolExecutor() as executor:
        evaluations = executor.map(read_and_evaluate, files)

    logger.info('Evaluation submitted to executor, creating matrix..')
    matrix = create_evaluation_matrix(evaluations)

    logger.info('Matrix ready, saving..')
    matrix_to_csv('results/matrix.csv', matrix)


if __name__ == '__main__':
    process('results')
