import sys

sys.path.append("./")

from blocksim import Miner, Simulation, alpha_beta_step_payoff
from forktwodistanceminer import ForkTwoDistanceMiner

if __name__ == "__main__":
    players = []

    players.append(ForkTwoDistanceMiner('Fork Two Distance Miner'))
    players.append(Miner('Default Random Miner'))

    h = {'Fork Two Distance Miner': 1,
        'Default Random Miner': 1}

    sim = Simulation(players, h, 10000, safe_dist=0, payoff=alpha_beta_step_payoff(1, 1, 1))
    sim.simulate()
    sim.print_results()