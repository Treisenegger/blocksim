from simulation import Simulation
from players import DefPlayerRandom, DefPlayer, SelfPlayer, AFPlayer
from payoff import alpha_beta_payoff


if __name__ == "__main__":
    players = []

    players.append(DefPlayerRandom('1'))
    # players.append(DefPlayer('2'))
    players.append(DefPlayerRandom('2'))
    # players.append(AFPlayer('2'))
    players.append(SelfPlayer('3'))

    h = {'1': 1, '2': 1, '3': 1}
    
    sim = Simulation(players, h, 10000, payoff=alpha_beta_payoff(1, 1))
    sim.simulate()
    sim.print_results()
    # sim.print_struct()