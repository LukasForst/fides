from fides.utils.logger import Logger
from simulations.storage import read_simulation
from simulations.visualisation import plot_simulation_result

logger = Logger(__name__)

if __name__ == '__main__':
    sim_id = '419c2a05-bf19-44dd-a2bc-a1698f348339'
    s = read_simulation(f'../../../simulation-results-04/{sim_id}.json')
    plot_simulation_result(s)
