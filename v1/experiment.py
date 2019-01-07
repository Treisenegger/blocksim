from simulation import Player, Simulation
from payoff import constant_payoff
from pub_strategies import catch_up


if __name__ == "__main__":
    players = []

    for i in range(1, 4):
        players.append(Player(str(i), i))

    players.append(Player('4', 4, dec_publish=catch_up))
    
    sim = Simulation(players, constant_payoff, 30)
    sim.simulate()
    sim.print_results()
    sim.print_struct()