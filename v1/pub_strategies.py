def default_pub_strat(self, block, payoff):
    return True

def catch_up(self, block, payoff):
    return True if self.struct.depth >= block.depth else False