def default_pub_strat(self, payoff, end=False):
    prev_blocks = self.hidden_blocks
    self.hidden_blocks = []
    return set(prev_blocks)

def catch_up(self, payoff, end=False):
    if end:
        prev_hidden = self.hidden_blocks
        self.hidden_blocks = list(filter(lambda x: x.parent.hidden, self.hidden_blocks))
        return set(filter(lambda x: not x.parent.hidden, prev_hidden))
    else:
        prev_hidden = self.hidden_blocks
        self.hidden_blocks = list(filter(lambda x: x.parent.hidden or self.struct.depth < x.depth, self.hidden_blocks))
        return set(filter(lambda x: not x.parent.hidden and self.struct.depth >= x.depth, prev_hidden))