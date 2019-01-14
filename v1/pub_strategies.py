def default_pub_strat(self, block, payoff, end=False):
    if end:
        return True
        
    self.hidden_blocks.remove(block)
    return True

def catch_up(self, block, payoff, end=False):
    if end:
        return True

    if self.struct.depth >= block.depth:
        self.hidden_blocks.remove(block)
        return True
    else:
        return False