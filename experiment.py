from blocksim import DefPlayerRandom, DefPlayer, SelfPlayer, Simulation, alpha_beta_step_payoff


if __name__ == "__main__":
    players = []

    players.append(DefPlayerRandom('1'))
    players.append(DefPlayerRandom('2'))
    players.append(SelfPlayer('3'))

    h = {'1': 1, '2': 1, '3': 1}
    
    sim = Simulation(players, h, 30, safe_dist=0, payoff=alpha_beta_step_payoff(1, 1, 1))
    sim.simulate()
    sim.print_results()
    # sim.print_struct()
