import random
from concurrent.futures import ProcessPoolExecutor

from fides.utils.logger import Logger
from simulations.evaluation import create_evaluation_matrix, matrix_to_csv, read_and_evaluate
from simulations.storage import get_file_names

logger = Logger(__name__)


def process(directory: str):
    files = get_file_names(directory)

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
