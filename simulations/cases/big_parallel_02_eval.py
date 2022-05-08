from fides.utils.logger import Logger
from simulations.evaluation import create_evaluation_matrix, matrix_to_csv, read_and_evaluate_all_files

logger = Logger(__name__)

if __name__ == '__main__':
    directory = 'results'

    evaluations = read_and_evaluate_all_files(directory)

    logger.info('Creating matrix..')
    matrix = create_evaluation_matrix(evaluations)

    logger.info('Matrix ready, saving..')
    matrix_to_csv('results/matrix.csv', matrix)
