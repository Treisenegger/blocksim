from simulation import Player, Simulation
from pub_strategies import catch_up
from payoff import alpha_beta_payoff


if __name__ == "__main__":
    players = []

    for i in range(1, 4):
        players.append(Player(str(i), i))

    players.append(Player('4', 6, publish=catch_up))
    
    sim = Simulation(players, 30, payoff=alpha_beta_payoff(0.9, 0.9))
    sim.simulate()
    sim.print_results()
    sim.print_struct()