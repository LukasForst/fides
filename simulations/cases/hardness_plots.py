from fides.utils.logger import Logger
from simulations.evaluation import evaluate_hardness_avg_target_diff, evaluate_hardness_avg_peers_diff, \
    evaluate_hardness_evaluation, read_and_evaluate_all_files
from simulations.visualisation import plot_hardness_evaluation

logger = Logger(__name__)

if __name__ == '__main__':
    directory_with_simulation_results = 'results'

    evaluations = read_and_evaluate_all_files(directory_with_simulation_results)

    logger.info('Creating matrix..')
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
