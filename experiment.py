from blocksim import Miner, DefaultMiner, SelfishMiner, Simulation, alpha_beta_step_payoff


if __name__ == "__main__":
    players = []

    players.append(Miner('Default Random Miner'))
    players.append(DefaultMiner('Default Miner'))
    players.append(SelfishMiner('Selfish Miner'))

    h = {'Default Random Miner': 1,
        'Default Miner': 1,
        'Selfish Miner': 1}
    
    sim = Simulation(players, h, 10000, safe_dist=0, payoff=alpha_beta_step_payoff(1, 1, 1))
    sim.simulate()
    sim.print_results()
    # sim.print_struct()
