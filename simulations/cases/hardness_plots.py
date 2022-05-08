import random
from concurrent.futures import ProcessPoolExecutor

from fides.utils.logger import Logger
from simulations.evaluation import evaluate_hardness_avg_target_diff, evaluate_hardness_avg_peers_diff, \
    evaluate_hardness_evaluation, read_and_evaluate
from simulations.storage import get_file_names
from simulations.visualisation import plot_hardness_evaluation

logger = Logger(__name__)

if __name__ == '__main__':
    directory_with_simulation_results = 'results'

    files = get_file_names(directory_with_simulation_results)
    random.shuffle(files)

    logger.info(f'Evaluating {len(files)} simulations...')
    with ProcessPoolExecutor() as executor:
        evaluations = executor.map(read_and_evaluate, files)

    logger.info('Evaluation submitted to executor, creating matrix..')

    evaluations = list(evaluations)
    plot_hardness_evaluation(evaluate_hardness_avg_target_diff(evaluations),
                             title_override='Performance of each interaction evaluation function ' +
                                            'with respect to the Target Detection Performance metric',
                             plot_level_one_line=True,
                             y_label='Target Detection Performance')

    plot_hardness_evaluation(evaluate_hardness_avg_peers_diff(evaluations),
                             title_override='Performance of each interaction evaluation function ' +
                                            'with respect to the Behavior Detection Performance metric',
                             y_label='Peer\'s Behavior Detection Performance')

    plot_hardness_evaluation(evaluate_hardness_evaluation(evaluations),
                             title_override='Performance of each interaction evaluation function ' +
                                            'with respect to the Simulation Evaluation metric',
                             y_label='Simulation Evaluation')
