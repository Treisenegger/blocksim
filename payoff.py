def constant_payoff(start_block, end_block, base):
    payoff_dict = {}
    
    block = start_block

    while (block != end_block) and (block != base):
        if block.owner.name not in payoff_dict:
            payoff_dict[block.owner.name] = {"block_number": 0, "payoff": 0}
        payoff_dict[block.owner.name]["block_number"] += 1
        payoff_dict[block.owner.name]["payoff"] += 1
        block = block.parent

    return payoff_dict

def alpha_beta_payoff(alpha, beta):
    def constant_payoff(start_block, end_block, base):
        payoff_dict = {}
        
        block = start_block

        while (block != end_block) and (block != base):
            if block.owner.name not in payoff_dict:
                payoff_dict[block.owner.name] = {"block_number": 0, "payoff": 0}
            payoff_dict[block.owner.name]["block_number"] += 1
            payoff_dict[block.owner.name]["payoff"] += (alpha**block.tstamp)*(beta**block.depth)
            block = block.parent

        return payoff_dict
    return constant_payoff