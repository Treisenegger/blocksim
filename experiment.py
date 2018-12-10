from simulation import Player, Simulation
from strategies import default_strat, one_fork_giveup_strat, always_fork_strat
from payoff import alpha_payoff


if __name__ == "__main__":
    players = []

    for i in range(1, 4):
        players.append(Player(str(i), i, default_strat))
    

    players.append(Player("4", 6, always_fork_strat))

    # players.append(Player("1", 2, one_fork_giveup_strat))
    # players.append(Player("2", 1, default_strat))
    
    sim = Simulation(players, alpha_payoff, 30, alpha=0.999999)
    sim.simulate()
    sim.print_results()
    sim.print_struct()