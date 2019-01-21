from simulation import Player, Simulation
from pub_strategies import selfish_pub_strat
from place_strategies import selfish_strat
from payoff import alpha_beta_payoff


if __name__ == "__main__":
    players = []

    players.append(Player('1', 2))
    players.append(Player('2', 2))
    players.append(Player('3', 3, strat=selfish_strat, publish=selfish_pub_strat))

    # players = players[::-1]
    
    sim = Simulation(players, 10000, payoff=alpha_beta_payoff(1, 1))
    sim.simulate()
    sim.print_results()
    # sim.print_struct()