import random
from concurrent.futures import ProcessPoolExecutor

from fides.utils.logger import Logger
from simulations.evaluation import create_evaluation_matrix, matrix_to_csv, \
    read_and_evaluate
from simulations.storage import get_file_names

logger = Logger(__name__)

if __name__ == '__main__':
    directory_with_results = '../../../simulation-results-04'

    files = get_file_names(directory_with_results)
    random.shuffle(files)

    logger.info(f'Evaluating {len(files)} simulations...')
    with ProcessPoolExecutor() as executor:
        evaluations = executor.map(read_and_evaluate, files)

    logger.info('Evaluation submitted to executor, creating matrix..')
    matrix = create_evaluation_matrix(evaluations)

    logger.info('Matrix ready, saving..')
    matrix_to_csv('results/matrix.csv', matrix)

    # s = read_simulation('results/64e25246-df3e-4123-8848-baa7dd61106a.json')
    # plot_simulation_result(s)
