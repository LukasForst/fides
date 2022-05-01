from fides.utils.logger import Logger
from simulations.storage import read_simulation
from simulations.visualisation import plot_simulation_result

logger = Logger(__name__)

if __name__ == '__main__':
    sim_id = '92980951-cab9-46d1-8288-fc66929eee08'
    s = read_simulation(f'../../../simulation-results-02/{sim_id}.json')
    plot_simulation_result(s)
