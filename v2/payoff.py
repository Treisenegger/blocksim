def alpha_payoff(self, start_block, end_block):
    payoff_dict = {player: {"block_number": 0, "payoff": 0} for player in self.players}
    
    block = start_block

    while (block != end_block) and (block != self.tree):
        payoff_dict[block.owner]["block_number"] += 1
        payoff_dict[block.owner]["payoff"] += self.alpha ** block.depth
        block = block.parent

    return payoff_dict

# def constant_payoff(self, block):
#     return 1

# def alpha_block_payoff(self, block):
#     return self.alpha ** block.depth