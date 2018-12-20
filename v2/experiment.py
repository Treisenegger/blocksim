from simulation import Player, Simulation
from strategies import default_strat
from payoff import constant_payoff


if __name__ == "__main__":
    players = []

    for i in range(1, 4):
        players.append(Player(str(i), i*1000, default_strat))
    
    sim = Simulation(players, constant_payoff, 10000000)
    sim.simulate()
    sim.print_results()
    # sim.print_struct()